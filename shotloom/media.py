"""Local final assembly. Refuses missing/selectless shots and ambiguous audio."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
from .io import ShotloomError, safe_join, sha256
from .contracts import contract_hash


def probe_media(path: Path) -> dict:
    if not shutil.which("ffprobe"):
        raise ShotloomError("ffprobe nicht installiert (FFmpeg benötigt)")
    p = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                       capture_output=True, text=True, check=False)
    if p.returncode:
        raise ShotloomError(f"ffprobe-Fehler für {path.name}: {p.stderr[:300]}")
    return json.loads(p.stdout)


def assemble(root: Path, project: dict, episode: dict, state: dict, audio: Path | None,
             mute: bool, output: Path | None = None) -> Path:
    if not shutil.which("ffmpeg"):
        raise ShotloomError("ffmpeg nicht installiert")
    if audio and mute:
        raise ShotloomError("--audio-master und --mute widersprechen sich")
    if not audio and not mute:
        raise ShotloomError("Freigegebenes Audio-Master mit --audio-master angeben; alternativ explizit --mute")
    if audio and not audio.is_file():
        raise ShotloomError("Audio-Master nicht gefunden")
    paths = []
    selected_meta = []
    for shot in episode["shots"]:
        sid = shot["id"]
        node = state.get("episodes", {}).get(episode["id"], {}).get(sid, {})
        index = node.get("selected")
        if not index:
            raise ShotloomError(f"{sid} hat keinen freigegebenen Clip")
        attempt = node["attempts"][index - 1]
        if attempt.get("contract_hash") != contract_hash(project, episode):
            raise ShotloomError(f"{sid}: Story/Bible seit Genehmigung verändert, Shot neu prüfen")
        path = safe_join(root, attempt["path"])
        if not path.is_file() or sha256(path) != attempt["sha256"]:
            raise ShotloomError(f"{sid}: Clip fehlt oder Prüfsumme weicht ab")
        info = probe_media(path)
        if not any(s.get("codec_type") == "video" for s in info.get("streams", [])):
            raise ShotloomError(f"{sid}: keine Videospur")
        paths.append(path)
        selected_meta.append({"shot": sid, "file": attempt["path"], "sha256": attempt["sha256"]})
    delivery = project["delivery"]
    w, h, fps = delivery["width"], delivery["height"], delivery["fps"]
    # Re-encode mixed source formats to a uniform CFR, canvas, pixel format; no audio from source clips.
    filters = []
    for i, shot in enumerate(episode["shots"]):
        filters.append(f"[{i}:v:0]trim=duration={shot['duration_s']},setpts=PTS-STARTPTS,fps={fps},scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(paths))) + f"concat=n={len(paths)}:v=1:a=0[vout]")
    output = output or root / "output" / f"{episode['id']}_master.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    for p in paths:
        cmd.extend(["-i", str(p)])
    if audio:
        cmd.extend(["-i", str(audio)])
    cmd.extend(["-filter_complex", ";".join(filters), "-map", "[vout]"])
    if audio:
        cmd.extend(["-map", f"{len(paths)}:a:0", "-c:a", "aac", "-b:a", "192k", "-af", "aresample=async=1:first_pts=0"])
    cmd.extend(["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", str(fps), "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", str(sum(s["duration_s"] for s in episode["shots"])), str(output)])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ShotloomError("FFmpeg Fehler: " + result.stderr[-1200:])
    # Human must verify audio mix, cuts and last frame before release.
    (output.parent / f"{episode['id']}_assembly_manifest.json").write_text(json.dumps({
        "project": project["id"], "episode": episode["id"], "created_from": selected_meta,
        "audio_master": str(audio) if audio else None, "muted_explicitly": mute,
        "final_file": str(output), "sha256": sha256(output),
        "release_approved": False, "human_final_screening_required": True
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
