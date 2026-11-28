"""Conservative, non-billing estimates for draft-first film production.

Snapshot rates are planning references, NOT provider quotes. No network is used.
All totals use USD, with no silent currency conversion to EUR.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from .io import ShotloomError

SNAPSHOT_DATE = "2026-11-28"
CREDIT_USD = Decimal("0.03")  # base pack, excludes payment fees, sales tax, FX
# Higgscheap: explicit 5-second dry-run quotes for 16:9 settings, not live guarantees.
HIGGSCHEAP_5S = {
    ("seedance-2-5", "480p", True, False): Decimal("14.7"),
    ("seedance-2-5", "480p", True, True): Decimal("19.0"),
    ("seedance-2-5", "720p", True, False): Decimal("32.7"),
    ("seedance-2-5", "1080p", True, False): Decimal("101.0"),
    ("kling-3", "720p", False, False): Decimal("11.7"),
    ("kling-3", "1080p", False, False): Decimal("15.0"),
    ("kling-3", "720p", True, False): Decimal("16.7"),
    ("kling-3", "1080p", True, False): Decimal("22.5"),
    ("kling-3", "4k", False, False): Decimal("55.9"),
}
# Official Higgsfield API self-serve rates for draft -> 1080p finalization.
# Video input incurs a different rate. Access/actual account charges unverified.
HIGGSFIELD_API_SECOND = {
    ("preview", False): Decimal("0.1177"),
    ("preview", True): Decimal("0.1387"),
    ("finalize", False): Decimal("0.6518"),
    ("finalize", True): Decimal("0.7858"),
}


def usd(value: Decimal | float | str) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def cost_for(provider: str, model: str, resolution: str, duration: float,
             audio: bool = False, draft: bool = False, video_input: bool = False,
             phase: str = "preview") -> Decimal:
    """Indicative cost. Paid orders must use a fresh, exact provider quote."""
    seconds = Decimal(str(duration))
    if seconds <= 0:
        raise ShotloomError("Dauer muss positiv sein")
    if provider == "higgscheap":
        key = (model, resolution, audio, draft)
        if key not in HIGGSCHEAP_5S:
            raise ShotloomError(f"Kein Snapshotpreis für {key}. Live-Angebot anfordern")
        return HIGGSCHEAP_5S[key] * CREDIT_USD * seconds / Decimal(5)
    if provider == "higgsfield_api" and model == "seedance-2-5" and resolution in ("480p", "1080p"):
        if phase not in ("preview", "finalize") or (phase == "preview") != (resolution == "480p"):
            raise ShotloomError("Offizielle API-Referenz deckt nur Draft 480p -> Finalize 1080p ab")
        return HIGGSFIELD_API_SECOND[(phase, video_input)] * seconds
    raise ShotloomError("Für diese Konfiguration ist kein Offline-Referenzpreis vorhanden")


def risk_for(shot: dict) -> tuple[str, list[str]]:
    """Only structured evidence; human/agent can set risk_tags or complexity_override."""
    spec = shot.get("production", {})
    explicit = spec.get("complexity_override")
    if explicit and explicit not in ("simple", "medium", "complex"):
        raise ShotloomError("complexity_override muss simple, medium oder complex sein")
    tags = set(spec.get("risk_tags", []))
    supported = {"physical_contact", "fight", "complex_movement", "multiple_characters",
                 "face_closeup", "lip_sync", "precise_prop", "complex_camera", "continuity"}
    unknown = tags - supported
    if unknown:
        raise ShotloomError(f"Unbekannte Produktionsrisiken: {', '.join(sorted(unknown))}")
    reasons = sorted(tags)
    if not reasons and len(shot.get("character_ids", [])) >= 2:
        reasons.append("two_or_more_characters")
    if shot.get("sound", {}).get("dialogue"):
        reasons.append("spoken_dialogue")
    major = {"physical_contact", "fight", "complex_movement", "lip_sync", "face_closeup"}
    complexity = "complex" if tags & major or len(shot.get("character_ids", [])) >= 3 else (
        "medium" if reasons or len(shot.get("action", {}).get("beats", [])) >= 3 else "simple")
    return explicit or complexity, (["manual_override"] if explicit else []) + reasons


def build_plan(project: dict, episode: dict, *, model: str = "kling-3", provider: str = "higgscheap",
               resolution: str = "1080p", preview_attempts: int = 2,
               overage_pct: int = 15, rework_pct: int = 25,
               audio: bool = False, video_input: bool = False) -> dict:
    """Scenario planner, not an authorization or claim of current provider pricing."""
    if not (0 <= preview_attempts <= 10 and 0 <= overage_pct <= 100 and 0 <= rework_pct <= 100):
        raise ShotloomError("Ungültige Parameter der Produktionsplanung")
    if project["budget"]["currency"] != "USD":
        raise ShotloomError("Planung in USD: budget.currency auf USD setzen oder separat dokumentierte FX-Umrechnung vornehmen")
    if provider == "higgsfield_api" and (model != "seedance-2-5" or resolution != "1080p"):
        raise ShotloomError("API-Snapshot unterstützt ausschließlich Seedance 2.5 Draft -> 1080p")
    total = Decimal(0)
    direct_comparison = Decimal(0)
    rows = []
    for shot in episode["shots"]:
        config = shot.get("production", {})
        used_model = config.get("model", model)
        used_provider = config.get("provider", provider)
        risk, reasons = risk_for(shot)
        seconds = float(shot["duration_s"])
        target = config.get("target_resolution", resolution)
        used_audio = bool(config.get("native_audio", audio))
        mode = config.get("render_strategy", "auto")
        if used_provider == "higgsfield_api":
            final = cost_for(used_provider, used_model, "1080p", seconds, used_audio,
                             phase="finalize", video_input=video_input)
            preview = cost_for(used_provider, used_model, "480p", seconds, used_audio,
                               phase="preview", video_input=video_input)
            preview_resolution = "480p"
        else:
            final = cost_for(used_provider, used_model, target, seconds, used_audio)
            preview_resolution = "480p" if used_model == "seedance-2-5" else "720p"
            preview = cost_for(used_provider, used_model, preview_resolution, seconds, used_audio)
        # Preview doesn't pay off for a cheap 1080p Kling render; high complexity may
        # still benefit from a pilot, but needs deliberate override, not auto spend.
        cost_ratio = preview / final
        if mode not in ("auto", "direct", "preview_then_final"):
            raise ShotloomError("render_strategy: auto, direct oder preview_then_final")
        use_preview = mode == "preview_then_final" or (mode == "auto" and risk != "simple" and cost_ratio <= Decimal("0.60"))
        if mode == "direct" and used_provider == "higgsfield_api":
            raise ShotloomError("Higgsfield-API-Snapshot deckt direkte Finalrenders nicht ab")
        if used_provider == "higgsfield_api" and not use_preview:
            # Our API estimate only documents draft/finalize; never silently replace by direct.
            use_preview = True
        shot_cost = final + (preview * preview_attempts if use_preview else Decimal(0))
        alternative_cost = final * (preview_attempts + 1)
        rows.append({"shot": shot["id"], "duration_s": seconds, "risk": risk, "reasons": reasons,
                     "provider": used_provider, "model": used_model, "final_resolution": target,
                     "strategy": "preview_then_final" if use_preview else "direct",
                     "draft_finalization_supported": used_provider == "higgsfield_api" and used_model == "seedance-2-5",
                     "preview_resolution": preview_resolution if use_preview else None,
                     "preview_usd_each": usd(preview) if use_preview else None,
                     "final_usd_each": usd(final), "expected_usd": usd(shot_cost),
                     "all_full_resolution_usd": usd(alternative_cost),
                     "warning": "High-resolution re-generation is not deterministic" if used_provider == "higgscheap" else
                                "Draft finalization requires same Higgsfield account, accepted QA, and expiry check"})
        total += shot_cost
        direct_comparison += alternative_cost
    cut = total * Decimal(overage_pct) / Decimal(100)
    rework = total * Decimal(rework_pct) / Decimal(100)
    planned = total + cut + rework
    return {"planning_only": True, "not_a_live_quote": True, "snapshot_date": SNAPSHOT_DATE,
            "currency": "USD", "credit_usd_before_fees": str(CREDIT_USD),
            "shot_count": len(rows), "duration_s": sum(float(s["duration_s"]) for s in episode["shots"]),
            "preview_attempts_per_preview_shot": preview_attempts, "cut_overage_pct": overage_pct,
            "rework_pct": rework_pct, "base_usd": usd(total), "cut_overage_usd": usd(cut),
            "final_rework_reserve_usd": usd(rework), "projected_usd": usd(planned),
            "all_high_res_same_attempt_count_usd": usd(direct_comparison),
            "budget_limit_usd": usd(project["budget"]["max_total"]),
            "fits_project_budget": planned <= Decimal(str(project["budget"]["max_total"])),
            "assumptions": ["Linear duration scaling is indicative; actual model billing can differ",
                            "Quoted credits are not signed, and final cost includes fees/taxes separately",
                            "A preview does not guarantee that a fresh final render preserves motion",
                            "Audio, ElevenLabs, lip-sync, image references, compute, human work not included"],
            "shots": rows}
