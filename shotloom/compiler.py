"""Compiler: immutable production facts -> provider-neutral shot briefs and job handoffs."""
from __future__ import annotations
from pathlib import Path
from .io import dump_json, safe_join
from .contracts import contract_hash


def _lines(items: list) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- Keine"


def shot_prompt(project: dict, episode: dict, shot: dict) -> str:
    scene = next(s for s in episode["scenes"] if s["id"] == shot["scene_id"])
    location = project["locations"][scene["location_id"]]
    characters = [project["characters"][cid] for cid in shot["character_ids"]]
    props = [project["props"][pid] for pid in shot["prop_ids"]]
    cam = shot["camera"]
    action = shot["action"]
    perf = shot["performance"]
    sound = shot["sound"]
    gen = shot["generation"]
    char_lines = [f"{c['id']} ({c['name']}): {c['identity_lock']}. Wardrobe: {c['wardrobe_lock']}. Voice: {c.get('voice_lock', '')}." for c in characters]
    prop_lines = [f"{p['id']}: {p['identity_lock']}" for p in props]
    dialogue_lines = [f"At {d['at_s']}s {d['character_id']} ({d.get('delivery', 'natural')}): \"{d['text']}\"" for d in sound["dialogue"]]
    beat_lines = [f"{b['at_s']}s: {b['description']}" for b in action["beats"]]
    continuity = shot["continuity"]
    return f"""# {shot['id']} | {episode['title']} | {shot['duration_s']}s

## Immutable identity and world constraints
Characters (same person in every frame, not similar-looking substitutes):
{_lines(char_lines)}
Location {scene['location_id']}: {location['spatial_lock']}
Time / world state: {scene['time_of_day']}; {scene['world_state']}
Props (exactly as referenced):
{_lines(prop_lines)}
Style bible: {project['creative']['look_lock']}

## Dramatic purpose
{shot['dramatic_intent']}

## Visual blocking & movement
{action['blocking']}
Performance: {perf['intention']}
Facial micro-expression: {perf['face']}
Eyes: {perf['eyeline']}
Hands and gesture: {perf['gesture']}
Timing (seconds relative to THIS shot):
{_lines(beat_lines)}
Physics / anatomy / contacts: {action['physics']}

## Camera & light
Framing: {cam['framing']}; focal length intent: {cam['focal_mm']}mm full-frame equivalent
Camera height: {cam['height_m']}m; axis side: {cam['axis_side']}; screen direction: {cam['screen_direction']}
Movement: {cam['movement']}; stability: {cam['stabilization']}; focus: {cam['focus']}
Lens/shutter intent is guidance, NOT a promise of exact optical simulation.
Lighting: {shot['look']['lighting']}; grade: {shot['look']['color']}; material/render: {shot['look']['texture']}

## Audio production cue (not assumed to be rendered)
Dialogue:
{_lines(dialogue_lines)}
Foley: {', '.join(sound['foley']) or 'none'}
Ambient: {', '.join(sound['ambience']) or 'none'}
Music: {sound['music']}
AUDIO POLICY: if native audio is available it is only a provisional track. Final mix is separately approved.

## Film continuity (MUST match the shot before/after)
At start: {continuity['entry']}
At end: {continuity['exit']}
Bridge type: {continuity['bridge']}; note: {continuity.get('note','')}

## Generation contract
Mode: {gen['mode']}
Preferred providers/models (validate live capabilities and tariffs): {', '.join(gen['model_preferences']) or 'provider chooses'}
First frame: {gen.get('first_frame') or 'NOT APPROVED'}
Last frame: {gen.get('last_frame') or 'not specified'}
Additional references: {', '.join(gen['references']) or 'none'}
Avoid: {', '.join(gen['avoid']) or 'none'}
Do not invent characters, props, camera cuts, wardrobe, speech or physics not in the locked specification.
No extra action after the last beat. Preserve orientation, contact geometry, temporal order and face identity.
Generate ONLY this shot. One coherent movement per shot unless prescribed; no unintended cuts.

## Acceptance criteria
{_lines(shot['acceptance_criteria'])}
"""


def compile_episode(root: Path, project: dict, episode: dict) -> dict:
    base = root / "compiled" / episode["id"]
    prompts = base / "prompts"
    jobs = base / "jobs"
    prompts.mkdir(parents=True, exist_ok=True)
    jobs.mkdir(parents=True, exist_ok=True)
    timeline = []
    t = 0.0
    for shot in episode["shots"]:
        sid = shot["id"]
        prompt_file = prompts / f"{sid}.md"
        prompt_file.write_text(shot_prompt(project, episode, shot), encoding="utf-8")
        scene = next(s for s in episode["scenes"] if s["id"] == shot["scene_id"])
        references = list(shot["generation"].get("references", []))
        references += [p for cid in shot["character_ids"] for p in project["characters"][cid].get("references", [])]
        references += project["locations"][scene["location_id"]].get("references", [])
        references += [p for pid in shot["prop_ids"] for p in project["props"][pid].get("references", [])]
        gen = shot["generation"]
        job = {
            "schema_version": 1, "id": sid, "episode": episode["id"], "duration_s": shot["duration_s"],
            "contract_hash": contract_hash(project, episode),
            "mode": gen["mode"], "prompt_file": str(prompt_file.relative_to(root)),
            "first_frame": gen.get("first_frame"), "last_frame": gen.get("last_frame"),
            "references": list(dict.fromkeys(references)),
            "preferred_models": gen["model_preferences"], "provider": "manual_agent_handoff",
            "execution_status": "NOT_SUBMITTED", "billing_authorized": False,
            "note": "A connected coding agent must select a documented tool, verify model limits, get approval, execute and record the artifact. This job file is NOT an API request."
        }
        dump_json(jobs / f"{sid}.json", job)
        timeline.append({"shot": sid, "start_s": round(t, 3), "end_s": round(t + shot["duration_s"], 3),
                         "dialogue": shot["sound"]["dialogue"], "sound": shot["sound"], "transition": shot["editorial"]["transition"]})
        t += shot["duration_s"]
    dump_json(base / "timeline.json", {"episode": episode["id"], "duration_s": round(t, 3), "shots": timeline,
                                        "note": "Audio/dialogue timing is editorial intent, not automatically aligned to phonemes."})
    (base / "HANDOFF.md").write_text(
        "# Production handoff\n\n"
        "1. Read AGENTS.md, source bibles and each job.\n"
        "2. Run `shotloom preflight` and fix all blockers.\n"
        "3. Confirm price AND explicit user approval before invoking a paid provider.\n"
        "4. Pass full prompt+approved references using the actual Higgsfield MCP/CLI skill or another provider.\n"
        "5. Download outputs locally; record each file with `shotloom record`.\n"
        "6. Do frame-by-frame human QA, log `shotloom review`, then `shotloom select`.\n"
        "7. Assemble with an approved audio master and inspect the final master.\n",
        encoding="utf-8")
    return {"shots": len(episode["shots"]), "duration_s": round(t, 3), "directory": str(base)}
