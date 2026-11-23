"""Deterministic structural and cross-shot checks; never pretends to assess visuals."""
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from .io import ROOT, ShotloomError, safe_join


def schema_validate(data: dict, filename: str) -> list[str]:
    schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
    errs = Draft202012Validator(schema).iter_errors(data)
    return [f"{'.'.join(str(v) for v in e.absolute_path) or '$'}: {e.message}" for e in sorted(errs, key=lambda e: str(list(e.absolute_path)))]


def validate(root: Path, project: dict, episode: dict | None = None) -> list[str]:
    issues = [f"PROJECT: {e}" for e in schema_validate(project, "project.schema.json")]
    if episode is None:
        return issues
    issues.extend(f"EPISODE: {e}" for e in schema_validate(episode, "episode.schema.json"))
    if issues:
        return issues
    if episode["project_id"] != project["id"]:
        issues.append("episode.project_id passt nicht zur Projekt-ID")
    for group in ("characters", "locations", "props"):
        for key, value in project[group].items():
            if key != value.get("id"):
                issues.append(f"{group}.{key}: ID stimmt nicht mit Schlüssel überein")
    if episode["id"] not in project["episodes"]:
        issues.append("Episode ist nicht im Projekt registriert")
    seen = set()
    prior_by_scene: dict[str, dict] = {}
    scene_lookup = {s["id"]: s for s in episode["scenes"]}
    if len(scene_lookup) != len(episode["scenes"]):
        issues.append("Szenen-IDs sind nicht eindeutig")
    for shot in episode["shots"]:
        sid = shot["id"]
        if sid in seen:
            issues.append(f"{sid}: Shot-ID doppelt")
        seen.add(sid)
        scene = scene_lookup.get(shot["scene_id"])
        if not scene:
            issues.append(f"{sid}: scene_id fehlt in scenes")
            continue
        if scene["location_id"] not in project["locations"]:
            issues.append(f"{sid}: Standort {scene['location_id']} unbekannt")
        for cid in shot["character_ids"]:
            if cid not in project["characters"]:
                issues.append(f"{sid}: unbekannter Character {cid}")
        for pid in shot["prop_ids"]:
            if pid not in project["props"]:
                issues.append(f"{sid}: unbekanntes Requisit {pid}")
        for d in shot["sound"]["dialogue"]:
            if d["character_id"] not in shot["character_ids"]:
                issues.append(f"{sid}: Sprecher nicht im Shot (Off-Stimme separat kennzeichnen)")
            if d["at_s"] >= shot["duration_s"]:
                issues.append(f"{sid}: Dialogbeginn außerhalb des Shots")
        if len(shot["action"]["beats"]) == 0:
            issues.append(f"{sid}: zeitliche Beats fehlen")
        for beat in shot["action"]["beats"]:
            if beat["at_s"] >= shot["duration_s"]:
                issues.append(f"{sid}: Beat liegt hinter Shotende")
        # Direct continuity of a visible character, within a scene, cannot silently drift.
        previous = prior_by_scene.get(shot["scene_id"])
        if previous is not None and shot["continuity"]["bridge"] == "direct":
            pre = shot["continuity"]["entry"]
            post = previous["continuity"]["exit"]
            for cid in set(pre).intersection(post):
                for key in ("wardrobe", "hand_left", "hand_right", "position", "facing"):
                    if key in pre[cid] and key in post[cid] and pre[cid][key] != post[cid][key]:
                        issues.append(f"{sid}: Kontinuitätsbruch {cid}.{key}: {post[cid][key]} -> {pre[cid][key]}")
        prior_by_scene[shot["scene_id"]] = shot
        if shot["camera"]["axis_side"] != scene["axis_side"] and not shot["camera"].get("axis_exception_reason"):
            issues.append(f"{sid}: 180°-Achse gebrochen; begründete Ausnahme nötig")
        for ref in shot["generation"].get("references", []):
            try:
                safe_join(root, ref)
            except ShotloomError as e:
                issues.append(f"{sid}: {e}")
    if abs(sum(s["duration_s"] for s in episode["shots"]) - episode["target_duration_s"]) > episode.get("duration_tolerance_s", 2.0):
        issues.append("Gesamtlänge der Shots weicht außerhalb der Toleranz von target_duration_s ab")
    return issues


def preflight(root: Path, project: dict, episode: dict, state: dict) -> dict[str, list[str]]:
    """Return per-shot blockers. A generator must honor them."""
    blockers: dict[str, list[str]] = {}
    for shot in episode["shots"]:
        sid = shot["id"]
        current = []
        if project["policy"].get("rights_cleared") is not True:
            current.append("Rechte-/Einwilligungsprüfung offen")
        char_ids = shot["character_ids"]
        scene = next(s for s in episode["scenes"] if s["id"] == shot["scene_id"])
        refs = list(shot["generation"].get("references", []))
        for cid in char_ids:
            refs += project["characters"][cid].get("references", [])
        refs += project["locations"][scene["location_id"]].get("references", [])
        for pid in shot["prop_ids"]:
            refs += project["props"][pid].get("references", [])
        # Image-to-video requires an approved first-frame input, no silent text-only fallback.
        if shot["generation"]["mode"] == "image_to_video" and not shot["generation"].get("first_frame"):
            current.append("Freigegebenes Startbild fehlt")
        for path in refs + [s for s in (shot["generation"].get("first_frame"), shot["generation"].get("last_frame")) if s]:
            try:
                if not safe_join(root, path).is_file():
                    current.append(f"Referenz nicht vorhanden: {path}")
            except ShotloomError as err:
                current.append(str(err))
        approved = [a for a in state.get("approvals", []) if a["episode"] == episode["id"] and a["shot"] == sid and not a.get("consumed")]
        if not approved:
            current.append("Freigabe vor bezahlter Generierung fehlt")
        blockers[sid] = sorted(set(current))
    return blockers
