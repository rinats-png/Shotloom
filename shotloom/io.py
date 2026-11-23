"""Read/write project artifacts. Paths are always relative to project root."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


class ShotloomError(Exception):
    """An actionable user-facing error."""


def read_yaml(path: Path) -> dict:
    if not path.is_file():
        raise ShotloomError(f"Datei fehlt: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ShotloomError(f"Kein YAML-Objekt: {path}")
    return data


def dump_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # atomic replace prevents partial state files on crash
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path, fallback: object) -> object:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else fallback


def load_project(root: Path, episode_id: str | None = None) -> tuple[dict, dict | None]:
    root = root.resolve()
    project = read_yaml(root / "project.yaml")
    episode = None
    if episode_id:
        rel = project.get("episodes", {}).get(episode_id)
        if not isinstance(rel, str):
            raise ShotloomError(f"Episode {episode_id} ist nicht in project.yaml registriert")
        episode = read_yaml(safe_join(root, rel))
        if episode.get("id") != episode_id:
            raise ShotloomError("Episoden-ID stimmt nicht mit project.yaml überein")
    return project, episode


def safe_join(root: Path, value: str) -> Path:
    if not value or not isinstance(value, str):
        raise ShotloomError("Leerer oder ungültiger relativer Pfad")
    root = root.resolve()
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ShotloomError(f"Pfad außerhalb des Projekts verboten: {value}")
    return path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def state_path(root: Path) -> Path:
    return root / "state.json"


def read_state(root: Path) -> dict:
    data = load_json(state_path(root), {"version": 1, "episodes": {}, "approvals": [], "spend": []})
    if not isinstance(data, dict):
        raise ShotloomError("state.json ist ungültig")
    data.setdefault("episodes", {})
    data.setdefault("approvals", [])
    data.setdefault("spend", [])
    return data


def write_state(root: Path, state: dict) -> None:
    dump_json(state_path(root), state)


def shot_state(state: dict, episode_id: str, shot_id: str) -> dict:
    eps = state.setdefault("episodes", {})
    ep = eps.setdefault(episode_id, {})
    return ep.setdefault(shot_id, {"attempts": [], "selected": None})
