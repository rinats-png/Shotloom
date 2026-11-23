"""Auditable approvals, attempt bookkeeping and human QA selection."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import shutil
from .io import ShotloomError, safe_join, sha256, shot_state, write_state
from .contracts import contract_hash
from .media import probe_media

CRITERIA = ("identity", "continuity", "anatomy_physics", "performance", "cinematography", "light", "editability", "sound_sync", "artifact_free", "storytelling")
CRITICAL = ("identity", "continuity", "anatomy_physics", "artifact_free")


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def sum_spend(state: dict) -> float:
    return round(sum(float(v.get("cost", 0)) for v in state.get("spend", [])), 2)


def authorize(project: dict, episode: dict, state: dict, shot_id: str, max_cost: float, by: str, confirmation: bool) -> None:
    if not project["policy"].get("rights_cleared"):
        raise ShotloomError("Rechteprüfung offen; keine Freigabe möglich")
    if not confirmation:
        raise ShotloomError("Explizite Zustimmung des Nutzers fehlt. --confirmed nur NACH realer Zustimmung setzen.")
    if shot_id not in [s["id"] for s in episode["shots"]]:
        raise ShotloomError("Shot nicht bekannt")
    if not by.strip():
        raise ShotloomError("Genehmigende Person angeben")
    if not 0 <= max_cost <= project["budget"]["max_per_attempt"]:
        raise ShotloomError("Kostenobergrenze pro Versuch überschritten")
    existing = [a for a in state["approvals"] if not (a["episode"] == episode["id"] and a["shot"] == shot_id)]
    pending = sum(float(a["max_cost"]) for a in existing if not a.get("consumed"))
    if pending + sum_spend(state) + max_cost > project["budget"]["max_total"] + 1e-9:
        raise ShotloomError("Budgetlimit inkl. offener Freigaben überschritten")
    existing.append({"episode": episode["id"], "shot": shot_id, "max_cost": max_cost,
                     "used": 0, "consumed": False, "approved_by": by, "at": stamp()})
    state["approvals"] = existing


def register(root: Path, project: dict, episode: dict, state: dict, shot_id: str,
             source: Path, provider: str, model: str, cost: float) -> dict:
    if not project["policy"].get("rights_cleared"):
        raise ShotloomError("Rechteprüfung vor Registrierung offen")
    if not source.is_file():
        raise ShotloomError(f"Mediendatei fehlt: {source}")
    if source.suffix.lower() not in (".mp4", ".mov", ".mkv", ".webm"):
        raise ShotloomError("Nur Videodateien (.mp4/.mov/.mkv/.webm) zulässig")
    if source.stat().st_size == 0:
        raise ShotloomError("Leere Mediendatei")
    if shot_id not in [s["id"] for s in episode["shots"]]:
        raise ShotloomError("Shot nicht bekannt")
    approval = next((a for a in state["approvals"] if a["episode"] == episode["id"] and a["shot"] == shot_id), None)
    if approval is None:
        raise ShotloomError("Generierung ohne vorherige Freigabe darf nicht verbucht werden")
    if approval.get("consumed"):
        raise ShotloomError("Freigabe bereits für einen Versuch genutzt. Neuen Versuch gesondert freigeben lassen")
    if not 0 <= cost <= float(approval["max_cost"]) + 1e-9:
        raise ShotloomError("Kosten überschreiten die freigegebene Restsumme")
    if sum_spend(state) + cost > float(project["budget"]["max_total"]) + 1e-9:
        raise ShotloomError("Gesamtbudget überschritten")
    info = probe_media(source)
    videos = [stream for stream in info.get("streams", []) if stream.get("codec_type") == "video"]
    if not videos:
        raise ShotloomError("Datei enthält keinen Videostream")
    try:
        media_duration = float(info.get("format", {}).get("duration", 0.0))
    except ValueError:
        raise ShotloomError("FFprobe kann die Videodauer nicht bestimmen")
    if media_duration <= 0:
        raise ShotloomError("Videodauer fehlt oder ist null")
    required_s = next(shot["duration_s"] for shot in episode["shots"] if shot["id"] == shot_id)
    if media_duration + 0.20 < float(required_s):
        raise ShotloomError(f"Quellclip ist {media_duration:.2f}s, geplante Dauer {required_s:.2f}s – neue Dauer planen oder vollständigeren Clip nutzen")
    node = shot_state(state, episode["id"], shot_id)
    idx = len(node["attempts"]) + 1
    output = root / "renders" / episode["id"] / shot_id / f"attempt-{idx:03d}{source.suffix.lower()}"
    output.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != output.resolve():
        shutil.copy2(source, output)
    rel = str(output.relative_to(root))
    obj = {"attempt": idx, "path": rel, "sha256": sha256(output), "provider": provider,
           "model": model, "cost": round(cost, 2), "at": stamp(), "review": None,
           "contract_hash": contract_hash(project, episode),
           "media": {"duration_s": round(media_duration, 3), "width": videos[0].get("width"), "height": videos[0].get("height"),
                     "fps": videos[0].get("avg_frame_rate"), "audio_in_source": any(st.get("codec_type") == "audio" for st in info.get("streams", []))}}
    node["attempts"].append(obj)
    approval["used"] = round(cost, 2)
    approval["consumed"] = True
    state["spend"].append({"episode": episode["id"], "shot": shot_id, "attempt": idx, "cost": cost, "at": stamp()})
    return obj


def review_attempt(state: dict, episode_id: str, shot_id: str, attempt_no: int, scores: dict,
                   reviewer: str, issues: list[str]) -> dict:
    node = shot_state(state, episode_id, shot_id)
    if not 1 <= attempt_no <= len(node["attempts"]):
        raise ShotloomError("Unbekannter Render-Versuch")
    if set(scores) != set(CRITERIA):
        raise ShotloomError(f"Alle {len(CRITERIA)} Kriterien erforderlich: {', '.join(CRITERIA)}")
    if any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= 5 for v in scores.values()):
        raise ShotloomError("Jede Bewertung muss eine Ganzzahl von 0 bis 5 sein")
    if not reviewer.strip():
        raise ShotloomError("Prüfende Person benennen")
    avg = round(sum(scores.values()) / len(CRITERIA), 2)
    passed = (avg >= 4.0 and all(scores[c] >= 4 for c in CRITICAL) and min(scores.values()) >= 3 and not issues)
    report = {"scores": scores, "average": avg, "passed": passed, "issues": issues,
              "reviewed_by": reviewer, "at": stamp(), "next_action": "SELECT" if passed else "REWORK"}
    node["attempts"][attempt_no - 1]["review"] = report
    if not passed and node["selected"] == attempt_no:
        node["selected"] = None
    return report


def select_attempt(state: dict, episode_id: str, shot_id: str, attempt_no: int, expected_contract_hash: str | None = None) -> None:
    node = shot_state(state, episode_id, shot_id)
    if not 1 <= attempt_no <= len(node["attempts"]):
        raise ShotloomError("Unbekannter Render-Versuch")
    if expected_contract_hash and node["attempts"][attempt_no - 1].get("contract_hash") != expected_contract_hash:
        raise ShotloomError("Kreativvertrag seit Render geändert: alte Version darf nicht ausgewählt werden")
    report = node["attempts"][attempt_no - 1].get("review")
    if not report or not report["passed"]:
        raise ShotloomError("Nur durch menschliche QA freigegebene Versuche auswählbar")
    node["selected"] = attempt_no
