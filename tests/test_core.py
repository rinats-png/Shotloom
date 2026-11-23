"""Core production constraints: regression suite with no network/paid generation."""
import copy
import json
import shutil
import subprocess
from pathlib import Path
import pytest
import yaml

from shotloom.io import ROOT, ShotloomError, safe_join, load_project, read_state, sha256
from shotloom.validation import validate, preflight
from shotloom.compiler import compile_episode, shot_prompt
from shotloom.contracts import contract_hash
from shotloom.state import CRITERIA, authorize, register, review_attempt, select_attempt, sum_spend
from shotloom.media import assemble
from shotloom.cli import main


@pytest.fixture
def demo(tmp_path):
    src = ROOT / "projects" / "night-protocol"
    root = tmp_path / "night-protocol"
    shutil.copytree(src, root, ignore=shutil.ignore_patterns("compiled", "state.json", "renders", "output"))
    p, e = load_project(root, "EP01")
    return root, p, e


def test_valid_sample_and_compile(demo):
    root, p, e = demo
    assert validate(root, p, e) == []
    report = compile_episode(root, p, e)
    assert report["shots"] == 6
    assert report["duration_s"] == 33.0
    job = json.loads((root / "compiled/EP01/jobs/EP01-S001.json").read_text())
    assert job["billing_authorized"] is False
    assert job["contract_hash"] == contract_hash(p, e)
    assert (root / job["prompt_file"]).is_file()
    prompt = (root / job["prompt_file"]).read_text()
    assert "Mara Neumann" in prompt and "Physics / anatomy" in prompt


def test_preflight_refusal(demo):
    root, p, e = demo
    state = {"approvals": []}
    block = preflight(root, p, e, state)
    assert "Rechte-/Einwilligungsprüfung offen" in block["EP01-S001"]
    assert any("Startbild fehlt" in v for v in block["EP01-S001"])
    assert any("front.png" in v for v in block["EP01-S001"])


def test_drift_and_axis_invalid(demo):
    root, p, e = demo
    broken = copy.deepcopy(e)
    broken["shots"][1]["continuity"]["entry"]["MARA"]["wardrobe"] = "OTHER_COAT"
    broken["shots"][2]["camera"]["axis_side"] = "north"
    errors = validate(root, p, broken)
    assert any("Kontinuitätsbruch" in e for e in errors)
    assert any("180°-Achse" in e for e in errors)


def test_missing_ids_and_mismatching_project(demo):
    root, p, e = demo
    broken = copy.deepcopy(e)
    broken["project_id"] = "another"
    broken["shots"][0]["prop_ids"].append("MISSING")
    errors = validate(root, p, broken)
    assert any("project_id" in e for e in errors)
    assert any("unbekanntes Requisit" in e for e in errors)


def test_budget_approvals_consumed(demo):
    _, p, e = demo
    p["policy"]["rights_cleared"] = True
    st = {"approvals": [], "spend": [], "episodes": {}}
    with pytest.raises(ShotloomError):
        authorize(p, e, st, "EP01-S001", 3.0, "Tester", False)
    with pytest.raises(ShotloomError):
        authorize(p, e, st, "EP01-S001", 6.0, "Tester", True)
    authorize(p, e, st, "EP01-S001", 3.0, "Tester", True)
    assert len(st["approvals"]) == 1
    assert sum_spend(st) == 0


def test_qa_rejects_critical_and_issues(demo):
    _, _, e = demo
    st = {"episodes": {e["id"]: {"EP01-S001": {"attempts": [{"path": "a.mp4"}], "selected": None}}}}
    scores = dict.fromkeys(CRITERIA, 5)
    bad = dict(scores, anatomy_physics=3)
    report = review_attempt(st, e["id"], "EP01-S001", 1, bad, "Reviewer", [])
    assert not report["passed"]
    with pytest.raises(ShotloomError):
        select_attempt(st, e["id"], "EP01-S001", 1)
    report = review_attempt(st, e["id"], "EP01-S001", 1, scores, "Reviewer", ["face pops at 4.1s"])
    assert not report["passed"]
    report = review_attempt(st, e["id"], "EP01-S001", 1, scores, "Reviewer", [])
    assert report["passed"]
    select_attempt(st, e["id"], "EP01-S001", 1)
    assert st["episodes"]["EP01"]["EP01-S001"]["selected"] == 1


def test_hash_invalidates_old_attempt(demo):
    _, p, e = demo
    old = contract_hash(p, e)
    copy_p = copy.deepcopy(p)
    copy_p["characters"]["MARA"]["identity_lock"] += " NEW"
    assert old != contract_hash(copy_p, e)
    st = {"episodes": {"EP01": {"EP01-S001": {"attempts": [{"contract_hash": old, "review": {"passed": True}}], "selected": None}}}}
    with pytest.raises(ShotloomError):
        select_attempt(st, "EP01", "EP01-S001", 1, contract_hash(copy_p, e))


def test_safe_path_blocks_traversal(demo):
    root, _, _ = demo
    with pytest.raises(ShotloomError):
        safe_join(root, "../../outside.yaml")
    assert safe_join(root, "episodes/EP01.yaml").is_file()


def test_init_new_project_and_validate(tmp_path):
    out = tmp_path / "projects"
    assert main(["init", "--slug", "my-new-film", "--title", "Testfilm", "--out", str(out)]) == 0
    created = out / "my-new-film"
    assert main(["validate", "--project", str(created)]) == 0
    assert main(["compile", "--project", str(created), "--episode", "EP01"]) == 0
    assert main(["preflight", "--project", str(created), "--episode", "EP01"]) == 3


def test_full_single_shot_structural_flow(tmp_path):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg not installed")
    out = tmp_path / "projects"
    assert main(["init", "--slug", "one-shot", "--title", "One Shot", "--out", str(out)]) == 0
    root = out / "one-shot"
    p = yaml.safe_load((root / "project.yaml").read_text())
    p["policy"]["rights_cleared"] = True
    p["budget"]["max_total"] = 10.0
    p["budget"]["max_per_attempt"] = 4.0
    (root / "project.yaml").write_text(yaml.safe_dump(p, sort_keys=False, allow_unicode=True))
    args = ["--project", str(root), "--episode", "EP01"]
    assert main(["compile", *args]) == 0
    assert main(["authorize", *args, "--shot", "EP01-S001", "--max-cost", "1.00", "--by", "Test Human", "--confirmed"]) == 0
    assert main(["preflight", *args]) == 0
    clip = tmp_path / "generated.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=gray:s=160x90:r=24", "-t", "5.04", "-c:v", "mpeg4", "-q:v", "4", str(clip)]
    subprocess.run(cmd, check=True)
    assert main(["record", *args, "--shot", "EP01-S001", "--file", str(clip), "--provider", "test", "--model", "mpeg4-test", "--cost", "0.50"]) == 0
    assert main(["preflight", *args]) == 3  # approval consumed
    scores = [val for c in CRITERIA for val in ("--score", f"{c}=5")]
    assert main(["review", *args, "--shot", "EP01-S001", "--attempt", "1", "--reviewer", "QA", *scores]) == 0
    assert main(["select", *args, "--shot", "EP01-S001", "--attempt", "1"]) == 0
    output = root / "output" / "EP01_master.mp4"
    assert main(["assemble", *args, "--mute", "--output", str(output)]) == 0
    assert output.is_file()
    assert main(["release", *args, "--master", str(output), "--by", "Review Human", "--confirmed"]) == 0
    assert (root / "output/EP01_release.json").is_file()
    # A changed story invalidates selection/release; this is the core anti-drift invariant.
    ep_path = root / "episodes/EP01.yaml"
    ep = yaml.safe_load(ep_path.read_text())
    ep["shots"][0]["dramatic_intent"] += " CHANGED"
    ep_path.write_text(yaml.safe_dump(ep, allow_unicode=True))
    assert main(["assemble", *args, "--mute", "--output", str(output)]) == 2
