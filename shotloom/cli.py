"""The local, inspectable operator interface. Does not call paid models automatically."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone
import yaml
from .compiler import compile_episode
from .contracts import contract_hash
from .io import ROOT, ShotloomError, dump_json, load_project, read_state, write_state, sha256
from .validation import validate, preflight
from .state import CRITERIA, authorize, register, review_attempt, select_attempt, sum_spend
from .media import assemble
from .costing import build_plan
from .production import (import_quote, authorize_quote, prepare_request, record_stage,
                         production_status, settle_failed_request, void_unsubmitted_authorization)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shotloom", description="Filmproduktion mit gesperrten Identitäten, QA und Budgets")
    sub = parser.add_subparsers(dest="command", required=True)
    def project_cmd(name: str, help_text: str, episode: bool = True):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--project", type=Path, required=True)
        if episode:
            p.add_argument("--episode", default="EP01")
        return p
    p = sub.add_parser("init", help="Neues Projekt mit editierbaren Vorlagen")
    p.add_argument("--slug", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--out", type=Path, default=Path("projects"))
    p = project_cmd("validate", "Struktur, IDs, Continuity prüfen", episode=False)
    p = project_cmd("compile", "Prompts, Jobs und Timeline schreiben")
    p = project_cmd("preflight", "Sperrgründe vor Generierung auflisten")
    p = project_cmd("status", "Fortschritt, Freigaben und Kosten anzeigen")
    p = project_cmd("cost-plan", "Unverbindliche Draft-vs.-Final-Videokosten in USD simulieren (kein Livepreis)")
    p.add_argument("--provider", choices=["higgscheap", "higgsfield_api"], default="higgscheap")
    p.add_argument("--model", choices=["kling-3", "seedance-2-5"], default="kling-3")
    p.add_argument("--resolution", choices=["1080p", "4k"], default="1080p")
    p.add_argument("--previews", type=int, default=2)
    p.add_argument("--cut-overage", type=int, default=15)
    p.add_argument("--rework-reserve", type=int, default=25)
    p.add_argument("--native-audio", action="store_true")
    p.add_argument("--video-input", action="store_true", help="Offizielle API: teurerer Tarif bei Videoeingabe")
    p.add_argument("--write", action="store_true", help="Unverbindlichen Kostenplan in compiled/ speichern")
    p = project_cmd("quote-import", "Aktuelles externes dry_run/Preisresultat gegen den Shot prüfen und speichern")
    p.add_argument("--shot", required=True)
    p.add_argument("--file", required=True, type=Path, help="JSON mit tatsächlicher Provider-Kalkulation")
    p = project_cmd("stage-authorize", "Einmalige Budgetfreigabe für eine konkrete Quote")
    p.add_argument("--quote-id", required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--confirmed", action="store_true")
    p = project_cmd("stage-request", "Geprüften Request-Handoff schreiben, kostenfrei, keine Providerverbindung")
    p.add_argument("--quote-id", required=True)
    p = project_cmd("stage-record", "Existierenden Preview-/Final-Clip mit echtem Betrag und Provider-ID buchen")
    p.add_argument("--quote-id", required=True)
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--actual-usd", required=True)
    p.add_argument("--provider-request-id", required=True)
    p.add_argument("--provider-created-at", help="Seedance-Draft: tatsächlicher UTC-Erstellungszeitpunkt")
    p.add_argument("--provider-expires-at", help="Seedance-Draft: frühere providerseitige Ablaufzeit")
    p = project_cmd("stage-failure", "Tatsächlich abgerechneten Fehlversuch ohne Video verbuchen")
    p.add_argument("--quote-id", required=True)
    p.add_argument("--actual-usd", required=True)
    p.add_argument("--provider-request-id", required=True)
    p.add_argument("--reason", required=True)
    p = project_cmd("stage-void", "Nur unversandte Kostenfreigabe zurücknehmen")
    p.add_argument("--quote-id", required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--confirmed-not-submitted", action="store_true")
    p = project_cmd("production-status", "Kosten, offene Freigaben und Draft-Ablauf anzeigen")
    p = project_cmd("next", "Nächsten sinnvollen Arbeitsschritt nennen")
    p = project_cmd("authorize", "Kostenfreigabe nur nach expliziter menschlicher Zustimmung")
    p.add_argument("--shot", required=True)
    p.add_argument("--max-cost", required=True, type=float)
    p.add_argument("--by", required=True)
    p.add_argument("--confirmed", action="store_true", help="Nur mit expliziter Nutzerfreigabe")
    p = project_cmd("record", "Videoversuch mit Prüfsumme und Kosten protokollieren")
    p.add_argument("--shot", required=True)
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--provider", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--cost", type=float, required=True)
    p = project_cmd("review", "Menschliche 10-Kriterien-Sichtprüfung eines Versuchs erfassen")
    p.add_argument("--shot", required=True)
    p.add_argument("--attempt", type=int, required=True)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--score", action="append", required=True, help="z.B. --score identity=5 (10x)")
    p.add_argument("--issue", action="append", default=[])
    p = project_cmd("select", "Nur bestandenen Videoversuch für Schnitt markieren")
    p.add_argument("--shot", required=True)
    p.add_argument("--attempt", type=int, required=True)
    p = project_cmd("assemble", "Aus ausgewählten Shots ein MP4-Master machen")
    p.add_argument("--audio-master", type=Path)
    p.add_argument("--mute", action="store_true")
    p.add_argument("--output", type=Path)
    p = project_cmd("subtitles", "Entwurfs-Untertitel aus Dialogstarts erzeugen; Timing manuell kontrollieren")
    p = project_cmd("release", "Sichtung des Masters dokumentieren (keine automatische Freigabe)")
    p.add_argument("--master", type=Path, required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--confirmed", action="store_true")
    p = sub.add_parser("doctor", help="Lokal verfügbare Komponenten prüfen")
    return parser


def do_init(a) -> None:
    import re
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,48}", a.slug):
        raise ShotloomError("Slug: 2–49 Kleinbuchstaben, Ziffern, Bindestriche")
    out = a.out / a.slug
    if out.exists():
        raise ShotloomError(f"Projekt existiert bereits: {out}")
    (out / "episodes").mkdir(parents=True)
    project = yaml.safe_load((ROOT / "templates" / "starter-project.yaml").read_text(encoding="utf-8"))
    ep = yaml.safe_load((ROOT / "templates" / "starter-episode.yaml").read_text(encoding="utf-8"))
    project["id"] = a.slug
    project["title"] = a.title
    ep["project_id"] = a.slug
    (out / "project.yaml").write_text(yaml.safe_dump(project, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (out / "episodes" / "EP01.yaml").write_text(yaml.safe_dump(ep, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (out / "assets").mkdir()
    (out / "notes.md").write_text("# Offene Angaben / Änderungswünsche\n\n", encoding="utf-8")
    print(f"Projekt angelegt: {out}\nNächstes: project.yaml / episodes/EP01.yaml ausfüllen, dann validate + compile")


def do_validate(root, project) -> int:
    issues = validate(root, project)
    for eid, filename in project.get("episodes", {}).items():
        try:
            p, ep = load_project(root, eid)
            issues.extend(f"{eid}: {msg}" for msg in validate(root, p, ep))
        except (ShotloomError, KeyError) as err:
            issues.append(f"{eid}: {err}")
    if issues:
        for msg in issues:
            print("FEHLER:", msg)
        print(f"{len(issues)} Strukturfehler – keine Produktion starten")
        return 2
    print(f"OK: {project['id']} | {len(project['episodes'])} Episode(n) | Schema und statische Kontinuität gültig")
    return 0


def do_preflight(root, project, episode, state) -> bool:
    block = preflight(root, project, episode, state)
    found = False
    for sid, entries in block.items():
        if entries:
            found = True
            print(f"BLOCKIERT {sid}:")
            for v in entries:
                print(f"  - {v}")
        else:
            print(f"BEREIT {sid} (nur technische Freigabe, nicht tatsächliche Videoqualität)")
    return not found


def do_status(project, episode, state) -> None:
    print(f"{project['title']} | {episode['title']} | Aufwand {sum_spend(state):.2f}/{project['budget']['max_total']:.2f} {project['budget']['currency']}")
    current_hash = contract_hash(project, episode)
    for shot in episode["shots"]:
        node = state.get("episodes", {}).get(episode["id"], {}).get(shot["id"], {})
        selected = node.get("selected")
        attempts = node.get("attempts", [])
        last = attempts[-1].get("review") if attempts else None
        stale = any(attempt.get("contract_hash") != current_hash for attempt in attempts)
        label = "VERALTETER VERTRAG (neu prüfen)" if stale else ("AUSGEWÄHLT" if selected else ("QA BESTANDEN" if last and last["passed"] else "NACHARBEIT" if last else "RENDER VORHANDEN" if attempts else "GEPLANT"))
        print(f"  {shot['id']}: {label} | Versuche: {len(attempts)} | {shot['duration_s']}s")


def subtitle_draft(root: Path, episode: dict) -> Path:
    def stamp_srt(t: float) -> str:
        ms = round(t * 1000)
        h, r = divmod(ms, 3600000)
        m, r = divmod(r, 60000)
        s, ms = divmod(r, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    lines = []
    offset = 0.0
    idx = 1
    for shot in episode["shots"]:
        for d in shot["sound"]["dialogue"]:
            st = offset + float(d["at_s"])
            end = min(offset + shot["duration_s"], st + max(1.0, min(4.0, len(d["text"]) / 15)))
            if end > st:
                lines += [str(idx), f"{stamp_srt(st)} --> {stamp_srt(end)}", d["text"], ""]
                idx += 1
        offset += shot["duration_s"]
    target = root / "compiled" / episode["id"] / "subtitles_DRAFT.srt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def main(argv=None) -> int:
    parser = make_parser()
    a = parser.parse_args(argv)
    try:
        if a.command == "init":
            do_init(a)
            return 0
        if a.command == "doctor":
            print(f"Python {sys.version.split()[0]} | ffmpeg={'OK' if shutil.which('ffmpeg') else 'FEHLT'} | ffprobe={'OK' if shutil.which('ffprobe') else 'FEHLT'}")
            print("Higgsfield MCP/CLI nur durch einen verbundenen Agenten; keine Zugangsdaten im Repository")
            return 0
        root = a.project.resolve()
        project, episode = load_project(root, None if a.command == "validate" else a.episode)
        if a.command == "validate":
            return do_validate(root, project)
        issues = validate(root, project, episode)
        if issues:
            raise ShotloomError("Zuerst Validierung korrigieren:\n" + "\n".join(issues))
        state = read_state(root)
        if a.command == "compile":
            print(json.dumps(compile_episode(root, project, episode), ensure_ascii=False, indent=2))
        elif a.command == "cost-plan":
            plan = build_plan(project, episode, provider=a.provider, model=a.model, resolution=a.resolution,
                              preview_attempts=a.previews, overage_pct=a.cut_overage,
                              rework_pct=a.rework_reserve, audio=a.native_audio, video_input=a.video_input)
            if a.write:
                dump_json(root / "compiled" / episode["id"] / "cost_plan_REFERENCE_ONLY.json", plan)
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        elif a.command == "quote-import":
            content = json.loads(a.file.read_text(encoding="utf-8"))
            q = import_quote(project, episode, state, a.shot, content)
            write_state(root, state)
            print(json.dumps(q, ensure_ascii=False, indent=2))
        elif a.command == "stage-authorize":
            approval = authorize_quote(project, episode, state, a.quote_id, a.by, a.confirmed)
            write_state(root, state)
            print(json.dumps(approval, ensure_ascii=False, indent=2))
        elif a.command == "stage-request":
            payload = prepare_request(root, project, episode, state, a.quote_id)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            print("HINWEIS: Nur Handoff, kein kostenpflichtiger Provider-Aufruf.")
        elif a.command == "stage-record":
            attempt = record_stage(root, project, episode, state, a.quote_id, a.file.resolve(), a.actual_usd,
                                   a.provider_request_id, a.provider_created_at, a.provider_expires_at)
            write_state(root, state)
            print(json.dumps(attempt, ensure_ascii=False, indent=2))
        elif a.command == "stage-failure":
            obj = settle_failed_request(project, episode, state, a.quote_id, a.actual_usd,
                                        a.provider_request_id, a.reason)
            write_state(root, state)
            print(json.dumps(obj, ensure_ascii=False, indent=2))
        elif a.command == "stage-void":
            obj = void_unsubmitted_authorization(state, a.quote_id, a.by, a.confirmed_not_submitted)
            write_state(root, state)
            print(json.dumps(obj, ensure_ascii=False, indent=2))
        elif a.command == "production-status":
            print(json.dumps(production_status(project, episode, state), ensure_ascii=False, indent=2))
        elif a.command == "preflight":
            return 0 if do_preflight(root, project, episode, state) else 3
        elif a.command == "status":
            do_status(project, episode, state)
        elif a.command == "next":
            for shot in episode["shots"]:
                sid = shot["id"]
                node = state.get("episodes", {}).get(episode["id"], {}).get(sid, {})
                if node.get("selected") and node.get("attempts", [])[node["selected"] - 1].get("contract_hash") == contract_hash(project, episode):
                    continue
                if node.get("selected"):
                    print(f"Nächster Shot: {sid}: Kreativvertrag seit der Auswahl verändert; bestehenden Clip neu prüfen oder neu generieren")
                    break
                if not node.get("attempts"):
                    blockers = preflight(root, project, episode, state)[sid]
                    print(f"Nächster Shot: {sid}: " + ("BLOCKER: " + "; ".join(blockers) if blockers else "Mit freigegebenen Jobs generieren, Datei registrieren"))
                elif node["attempts"][-1].get("review", {}).get("passed"):
                    print(f"Nächster Shot: {sid}: bestandenen Versuch selektieren")
                elif node["attempts"][-1].get("review"):
                    print(f"Nächster Shot: {sid}: kritisierte Stellen gezielt nacharbeiten, neuer Versuch")
                else:
                    print(f"Nächster Shot: {sid}: Menschliche Sichtprüfung vornehmen")
                break
            else:
                print("Alle Shots selektiert: Audio-Master freigeben, assemble, finalen Film vollständig sichten und release dokumentieren")
        elif a.command == "authorize":
            if not project["policy"]["rights_cleared"]:
                raise ShotloomError("Rechteprüfung zunächst in project.yaml abschließen")
            authorize(project, episode, state, a.shot, a.max_cost, a.by, a.confirmed)
            write_state(root, state)
            print(f"Freigabe dokumentiert: {a.shot} max. {a.max_cost:.2f} {project['budget']['currency']}")
        elif a.command == "record":
            job = root / "compiled" / episode["id"] / "jobs" / f"{a.shot}.json"
            if not job.is_file() or json.loads(job.read_text(encoding="utf-8")).get("contract_hash") != contract_hash(project, episode):
                raise ShotloomError("Kein aktueller Prompt-Job vorhanden: bitte compile erneut ausführen")
            blockers = preflight(root, project, episode, state)[a.shot]
            if blockers:
                raise ShotloomError("Record-Preflight blockiert:\n" + "\n".join(blockers))
            obj = register(root, project, episode, state, a.shot, a.file.resolve(), a.provider, a.model, a.cost)
            write_state(root, state)
            print(f"Versuch {obj['attempt']} gespeichert: {obj['path']} | sha256 {obj['sha256']}")
        elif a.command == "review":
            scores = {}
            for raw in a.score:
                if "=" not in raw:
                    raise ShotloomError("Score-Syntax: --score name=4")
                name, value = raw.split("=", 1)
                if name not in CRITERIA or name in scores or not value.isdigit():
                    raise ShotloomError(f"Ungültiger oder doppelter Score: {raw}")
                scores[name] = int(value)
            rep = review_attempt(state, episode["id"], a.shot, a.attempt, scores, a.reviewer, a.issue)
            write_state(root, state)
            print(json.dumps(rep, ensure_ascii=False, indent=2))
        elif a.command == "select":
            select_attempt(state, episode["id"], a.shot, a.attempt, contract_hash(project, episode))
            write_state(root, state)
            print(f"{a.shot} Versuch {a.attempt} ausgewählt")
        elif a.command == "assemble":
            result = assemble(root, project, episode, state, a.audio_master, a.mute, a.output)
            print(f"Rohmaster: {result}\nACHTUNG: Noch keine Releasefreigabe, Audio & Frames menschlich prüfen")
        elif a.command == "subtitles":
            path = subtitle_draft(root, episode)
            print(f"Nur Entwurf: {path}. Vor Nutzung gegen Audio framegenau abgleichen.")
        elif a.command == "release":
            if not a.confirmed:
                raise ShotloomError("Release benötigt menschliche Sichtung und --confirmed")
            if not project["policy"]["rights_cleared"]:
                raise ShotloomError("Rechte ungeklärt")
            master = a.master.resolve()
            assembly_manifest = master.parent / f"{episode['id']}_assembly_manifest.json"
            if not master.is_file() or not assembly_manifest.is_file():
                raise ShotloomError("Rohmaster oder Assembly-Manifest fehlt")
            assembly = json.loads(assembly_manifest.read_text(encoding="utf-8"))
            current = contract_hash(project, episode)
            selected = state.get("episodes", {}).get(episode["id"], {})
            for shot in episode["shots"]:
                node = selected.get(shot["id"], {})
                idx = node.get("selected")
                if not idx or node["attempts"][idx - 1].get("contract_hash") != current:
                    raise ShotloomError(f"{shot['id']}: keine aktuell gültige Freigabe; neuen Schnitt erstellen")
            if len(assembly.get("created_from", [])) != len(episode["shots"]):
                raise ShotloomError("Assembly-Manifest enthält nicht alle Shots")
            for entry, shot in zip(assembly["created_from"], episode["shots"]):
                node = selected[shot["id"]]
                current_attempt = node["attempts"][node["selected"] - 1]
                if entry["shot"] != shot["id"] or entry["sha256"] != current_attempt["sha256"]:
                    raise ShotloomError("Auswahl wurde seit der Montage geändert: Master neu rendern")
            if sha256(master) != assembly["sha256"]:
                raise ShotloomError("Master seit Schnitt verändert: neue Sichtung nötig")
            if not a.by.strip():
                raise ShotloomError("Freigebende Person fehlt")
            obj = {"episode": episode["id"], "master": str(master), "sha256": sha256(master), "approved_by": a.by,
                   "at": datetime.now(timezone.utc).isoformat(), "statement": "Humane Freigabe nach kompletter Sichtung; Formate, Ton, Untertitel, Rechte geprüft"}
            dump_json(master.parent / f"{episode['id']}_release.json", obj)
            print(f"Release protokolliert: {master}")
        return 0
    except (ShotloomError, KeyError, ValueError, OSError) as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
