"""Budgeted preview/final workflow; offline handoffs, never paid API calls.

Manual/operator-supplied quotes are NOT cryptographically provider-verified. A linked
agent must independently inspect the current provider dry_run and account charges.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import shutil
import uuid
from .contracts import contract_hash
from .costing import HIGGSFIELD_API_SECOND, usd, risk_for, cost_for
from .io import ShotloomError, dump_json, safe_join, sha256, shot_state
from .media import probe_media
from .state import stamp, sum_spend

SUPPORTED_PHASES = {"preview", "final", "finalize"}
DRAFT_ENDPOINT = "bytedance/seedance-2.5/finalize-draft"
DRAFT_MAX_AGE = timedelta(days=7)
QUOTE_MAX_AGE = timedelta(minutes=30)


def utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("requires offset")
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, AttributeError) as err:
        raise ShotloomError(f"Ungültiges UTC-Zeitformat: {value!r} ({err})") from err


def money(value: object) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError) as err:
        raise ShotloomError("Ungültiger Geldbetrag") from err
    if not amount.is_finite() or amount < 0:
        raise ShotloomError("Kosten müssen endlich und nichtnegativ sein")
    return amount


def production_state(state: dict) -> dict:
    section = state.setdefault("production", {"quotes": [], "authorizations": [], "dispatches": []})
    for key in ("quotes", "authorizations", "dispatches"):
        section.setdefault(key, [])
    return section


def require_usd(project: dict) -> None:
    if project["budget"]["currency"] != "USD":
        raise ShotloomError("Providerpreise in USD: kein automatischer EUR/USD-Wechselkurs; Budget für diesen Workflow explizit in USD führen")


def get_shot(episode: dict, shot_id: str) -> dict:
    return next((s for s in episode["shots"] if s["id"] == shot_id), None) or (
        _raise(f"Unbekannter Shot {shot_id}"))


def _raise(message: str):
    raise ShotloomError(message)


def quote_by_id(state: dict, quote_id: str) -> dict:
    return next((q for q in production_state(state)["quotes"] if q["id"] == quote_id), None) or _raise("Quote-ID unbekannt")


def auth_by_id(state: dict, quote_id: str) -> dict:
    return next((a for a in production_state(state)["authorizations"] if a["quote_id"] == quote_id), None) or _raise("Keine Freigabe für diese Quote")


def _validate_common(project: dict, episode: dict, shot_id: str, data: dict, now: datetime):
    require_usd(project)
    shot = get_shot(episode, shot_id)
    if not isinstance(data, dict):
        raise ShotloomError("Quote muss ein JSON-Objekt sein")
    provider, model, phase = data.get("provider"), data.get("model"), data.get("phase")
    if provider not in ("higgscheap", "higgsfield_api") or model not in ("kling-3", "seedance-2-5") or phase not in SUPPORTED_PHASES:
        raise ShotloomError("Provider/Modell/Phase nicht unterstützt")
    if provider == "higgsfield_api" and model != "seedance-2-5":
        raise ShotloomError("Higgsfield-API-Referenz implementiert nur Seedance 2.5")
    if phase == "finalize" and provider != "higgsfield_api":
        raise ShotloomError("Providerinterne Draft-Finalisierung nur für die offizielle Higgsfield-API dokumentiert")
    account = data.get("account_alias", "")
    if not isinstance(account, str) or not account.strip() or len(account) > 80:
        raise ShotloomError("account_alias für Draft-Kontobindung erforderlich (kein API-Schlüssel)")
    checked = utc(data.get("checked_at", ""))
    if checked > now + timedelta(minutes=2) or checked + QUOTE_MAX_AGE <= now:
        raise ShotloomError("Providerpreis ist veraltet (>30 Minuten) oder liegt in der Zukunft")
    if float(shot["duration_s"]) != int(shot["duration_s"]):
        raise ShotloomError("Für eine Provider-Quote muss die Shotdauer eine ganze Sekundenzahl sein")
    return provider, model, phase, shot, checked


def import_quote(project: dict, episode: dict, state: dict, shot_id: str,
                 data: dict, *, now: datetime | None = None) -> dict:
    """Record an operator-supplied price result with short TTL and exact params."""
    now = now or datetime.now(timezone.utc)
    provider, model, phase, shot, checked = _validate_common(project, episode, shot_id, data, now)
    duration = int(shot["duration_s"])
    if provider == "higgscheap":
        raw = data.get("dry_run")
        if not isinstance(raw, dict) or raw.get("dry_run") is not True or raw.get("valid") is not True:
            raise ShotloomError("Higgscheap verlangt ein erfolgreiches generate_video-dry_run-Ergebnis")
        if raw.get("model") != model:
            raise ShotloomError("Modell stimmt nicht mit der Preisabfrage überein")
        price = raw.get("price", {})
        if price.get("unit") != "credits" or price.get("tasks") != 1:
            raise ShotloomError("Nur exakt eine einzeln bepreiste Generierung erlaubt")
        params = raw.get("state", {}).get("params", {})
        if not isinstance(params, dict):
            raise ShotloomError("Normalisierte Providerparameter fehlen")
        res = params.get("resolution")
        if res not in ("480p", "720p", "1080p", "4k"):
            raise ShotloomError("Unbekannte Auflösung")
        if params.get("duration") != duration:
            raise ShotloomError("Preisabfrage passt nicht zur Shotdauer")
        if params.get("aspect") != project["delivery"]["aspect_ratio"]:
            raise ShotloomError("Preisabfrage verwendet ein anderes Seitenverhältnis")
        if not isinstance(params.get("audio"), bool):
            raise ShotloomError("Audio-Parameter muss ausdrücklich in der Quote stehen")
        configured_audio = shot.get("production", {}).get("native_audio")
        if configured_audio is not None and params["audio"] != configured_audio:
            raise ShotloomError("Providerquote widerspricht dem gesperrten nativen Audio-Modus")
        slots = raw.get("state", {}).get("slots", {})
        if shot["generation"]["mode"] == "image_to_video" and not (slots.get("start", 0) or slots.get("refs", 0)):
            raise ShotloomError("Preisabfrage enthält kein Startbild/Referenzmedium für den geplanten I2V-Modus")
        if bool(params.get("draft", False)) and model != "seedance-2-5":
            raise ShotloomError("Draftoption bei diesem Modell nicht unterstützt")
        if phase == "final" and bool(params.get("draft", False)):
            raise ShotloomError("Ein Draft kann nicht als finaler Render abgerechnet werden")
        if phase == "preview" and res not in ("480p", "720p"):
            raise ShotloomError("Vorschau-Auflösung muss 480p/720p sein")
        if phase == "final":
            target = shot.get("production", {}).get("target_resolution")
            if target is None:
                target = "4k" if int(project["delivery"]["height"]) >= 2160 else "1080p"
            if res != target or data.get("final_resolution", target) != target:
                raise ShotloomError("Final-Auflösung stimmt nicht mit dem Projekt-/Shot-Ziel überein")
        if model == "kling-3" and res == "480p":
            raise ShotloomError("Kling 3.0 bietet bei Higgscheap kein 480p")
        credits = money(price.get("total"))
        if credits <= 0 or money(price.get("per_task")) != credits:
            raise ShotloomError("Credits unplausibel")
        # Credits can be bought in packs at different effective rates; approval uses the
        # user's explicitly stated fully-loaded USD/credit rate, never inferred taxes.
        credit_usd = money(data.get("effective_usd_per_credit"))
        if credit_usd <= 0:
            raise ShotloomError("effective_usd_per_credit einschließlich Gebühren angeben")
        estimated = credits * credit_usd
        source = "operator_supplied_higgscheap_dry_run"
        draft = bool(params.get("draft", False))
        request_spec = {"params": {"resolution": res, "duration": duration,
                                   "audio": params["audio"], "aspect": params["aspect"], "draft": draft},
                        "inputs": raw.get("state", {}).get("slots", {}), "credits": str(credits),
                        "effective_usd_per_credit": str(credit_usd)}
    else:
        if phase not in ("preview", "finalize"):
            raise ShotloomError("Higgsfield-API-Snapshot unterstützt nur draft/finalize, nicht reguläres Finalrender")
        res = "480p" if phase == "preview" else "1080p"
        draft = phase == "preview"
        if not data.get("acknowledge_published_rate_not_live"):
            raise ShotloomError("Higgsfield-Preis ist ein öffentlicher Referenzpreis, keine Live-Quote")
        has_video_input = data.get("video_input", False)
        if not isinstance(has_video_input, bool):
            raise ShotloomError("video_input muss boolesch sein")
        if phase == "finalize" and not data.get("draft_request_id"):
            raise ShotloomError("Finalisierung benötigt die öffentliche draft_request_id")
        if phase == "preview" and shot["generation"]["mode"] == "image_to_video":
            if not isinstance(data.get("image_url"), str) or not data["image_url"].startswith("https://"):
                raise ShotloomError("Higgsfield I2V-Draft benötigt eine tatsächliche HTTPS-Bild-URL")
        expected = HIGGSFIELD_API_SECOND[(phase, has_video_input)] * Decimal(duration)
        if money(data.get("estimated_usd")) != expected:
            raise ShotloomError(f"Offizieller Referenzpreis geändert/abweichend: {expected} USD für {duration}s")
        estimated = expected
        source = "official_published_rate_not_live"
        request_spec = {"params": {"resolution": res, "duration": duration, "draft": draft,
                                   "video_input": has_video_input},
                        "draft_request_id": data.get("draft_request_id"),
                        "image_url": data.get("image_url")}
    q = {"id": uuid.uuid4().hex, "shot": shot_id, "episode": episode["id"],
         "provider": provider, "model": model, "account_alias": data["account_alias"],
         "phase": phase, "resolution": res, "draft": draft, "duration_s": duration,
         "quote_usd": usd(estimated), "quote_usd_unrounded": str(estimated),
         "source": source, "externally_verified": False, "checked_at": checked.isoformat(),
         "expires_at": (checked + QUOTE_MAX_AGE).isoformat(),
         "contract_hash": contract_hash(project, episode), "request_spec": request_spec,
         "caveat": "Operator-supplied evidence; verify the exact current provider offer and all fees before paying"}
    production_state(state)["quotes"].append(q)
    return q


def quote_usable(project: dict, episode: dict, q: dict, *, now: datetime | None = None):
    now = now or datetime.now(timezone.utc)
    require_usd(project)
    if q["contract_hash"] != contract_hash(project, episode):
        raise ShotloomError("Quote ungültig: Shot/Bible seit der Preisprüfung geändert")
    if utc(q["expires_at"]) <= now:
        raise ShotloomError("Preisquote abgelaufen; neue Live-Abfrage erforderlich")
    if q["episode"] != episode["id"]:
        raise ShotloomError("Quote für andere Episode")
    return q


def reserved_total(state: dict) -> Decimal:
    prod = production_state(state)
    pending_v1 = sum(Decimal(str(a["max_cost"])) for a in state.get("approvals", []) if not a.get("consumed"))
    pending_v2 = sum(money(a["reserved_usd"]) for a in prod["authorizations"] if a["status"] == "reserved")
    return pending_v1 + pending_v2


def authorize_quote(project: dict, episode: dict, state: dict, quote_id: str,
                    by: str, confirmed: bool, *, now: datetime | None = None) -> dict:
    if not project["policy"].get("rights_cleared"):
        raise ShotloomError("Rechtefreigabe fehlt")
    if not confirmed or not by.strip():
        raise ShotloomError("Individuelle menschliche Zustimmung erforderlich; --confirmed nur nach realem Ja")
    q = quote_usable(project, episode, quote_by_id(state, quote_id), now=now)
    prod = production_state(state)
    if any(a["quote_id"] == quote_id for a in prod["authorizations"]):
        raise ShotloomError("Quote bereits genehmigt/verbraucht; für weiteren Versuch neue Quote")
    max_attempt = money(project["budget"]["max_per_attempt"])
    amount = money(q["quote_usd"])
    if amount > max_attempt:
        raise ShotloomError("Quote übersteigt max_per_attempt")
    limit = money(project["budget"]["max_total"])
    if money(sum_spend(state)) + reserved_total(state) + amount > limit:
        raise ShotloomError("Gesamtbudget inkl. offener Freigaben überschritten")
    result = {"id": uuid.uuid4().hex, "quote_id": quote_id, "shot": q["shot"],
              "episode": q["episode"], "reserved_usd": q["quote_usd"],
              "approved_by": by, "at": (now or datetime.now(timezone.utc)).isoformat(),
              "status": "reserved", "contract_hash": q["contract_hash"]}
    prod["authorizations"].append(result)
    return result


def _approved_preview(state: dict, episode: dict, q: dict, *, require_draft: bool = False,
                      now: datetime | None = None) -> dict:
    node = shot_state(state, episode["id"], q["shot"])
    previews = [a for a in node["attempts"] if a.get("phase") == "preview" and
                (a.get("review") or {}).get("passed") and a.get("contract_hash") == q["contract_hash"] and
                a.get("provider") == q["provider"] and a.get("account_alias") == q["account_alias"]]
    if not previews:
        raise ShotloomError("Kein aktueller, menschlich geprüfter Preview-Shot bei diesem Provider/Konto")
    best = previews[-1]
    if require_draft:
        drafts = [a for a in previews if a.get("draft") and a.get("provider_request_id") == q["request_spec"].get("draft_request_id")]
        if not drafts:
            raise ShotloomError("Keine passende, geprüfte Seedance-Draft-Request-ID vorhanden")
        best = drafts[-1]
        created = utc(best["provider_created_at"])
        expires = min(created + DRAFT_MAX_AGE, utc(best["provider_expires_at"]) if best.get("provider_expires_at") else created + DRAFT_MAX_AGE)
        if expires <= (now or datetime.now(timezone.utc)):
            raise ShotloomError("Draft ist abgelaufen (früheste 7-Tage-/Anbieterfrist)")
    return best


def prepare_request(root: Path, project: dict, episode: dict, state: dict, quote_id: str,
                    *, now: datetime | None = None) -> dict:
    """Prepare handoff JSON; does NOT send it. Fresh quote and prior human approval required."""
    now = now or datetime.now(timezone.utc)
    q = quote_usable(project, episode, quote_by_id(state, quote_id), now=now)
    auth = auth_by_id(state, quote_id)
    if auth["status"] != "reserved" or auth["contract_hash"] != q["contract_hash"]:
        raise ShotloomError("Freigabe schon verbraucht oder ungültig")
    if not project["policy"].get("rights_cleared"):
        raise ShotloomError("Rechteprüfung ungültig")
    compiled_job = root / "compiled" / episode["id"] / "jobs" / f"{q['shot']}.json"
    if not compiled_job.is_file():
        raise ShotloomError("Zuerst compile ausführen")
    job = json.loads(compiled_job.read_text(encoding="utf-8"))
    if job.get("contract_hash") != q["contract_hash"]:
        raise ShotloomError("Compiled Job ist veraltet")
    from .validation import preflight
    blockers = [b for b in preflight(root, project, episode, state)[q["shot"]]
                if b != "Freigabe vor bezahlter Generierung fehlt"]
    # Existing legacy approval gate replaced by this exact per-quote approval.
    if blockers:
        raise ShotloomError("Preflight sperrt bezahlten Schritt: " + "; ".join(blockers))
    if q["phase"] == "finalize":
        draft = _approved_preview(state, episode, q, require_draft=True, now=now)
        if q["model"] != "seedance-2-5" or q["provider"] != "higgsfield_api":
            raise ShotloomError("Finalize nur mit demselben Seedance-2.5-Higgsfield-Konto")
    else:
        draft = None
        if q["phase"] == "final":
            shot = get_shot(episode, q["shot"])
            rule = shot.get("production", {}).get("render_strategy", "auto")
            past = shot_state(state, episode["id"], q["shot"])["attempts"]
            prior_preview = any(a.get("phase") == "preview" and a.get("contract_hash") == q["contract_hash"] for a in past)
            complexity, _ = risk_for(shot)
            predicted_preview = False
            try:
                pv_res = "480p" if q["model"] == "seedance-2-5" else "720p"
                predicted_preview = cost_for(q["provider"], q["model"], pv_res, q["duration_s"]) / cost_for(q["provider"], q["model"], q["resolution"], q["duration_s"]) <= Decimal("0.60")
            except ShotloomError:
                pass
            if rule == "preview_then_final" or (rule != "direct" and (prior_preview or (complexity != "simple" and predicted_preview))):
                draft = _approved_preview(state, episode, q, now=now)
    if q["provider"] == "higgsfield_api":
        if q["phase"] == "finalize":
            body = {"draft_id": draft["provider_request_id"], "resolution": "1080p"}
            endpoint = "https://api.higgsfield.ai/" + DRAFT_ENDPOINT
            operation = "POST"
        else:
            shot = get_shot(episode, q["shot"])
            mode = shot["generation"]["mode"]
            if mode not in ("text_to_video", "image_to_video"):
                raise ShotloomError("Für diesen Modus ist kein verifizierter Higgsfield-API-Request-Builder vorhanden")
            endpoint = "https://api.higgsfield.ai/bytedance/seedance-2.5/" + ("text-to-video" if mode == "text_to_video" else "image-to-video")
            body = {"prompt": (root / job["prompt_file"]).read_text(encoding="utf-8"),
                    "duration": q["duration_s"], "draft": True, "resolution": "480p",
                    "aspect_ratio": project["delivery"]["aspect_ratio"], "output_format": "mp4",
                    "generate_audio": bool(shot.get("production", {}).get("native_audio", False))}
            if mode == "image_to_video":
                image_url = q["request_spec"].get("image_url")
                if not isinstance(image_url, str) or not image_url.startswith("https://"):
                    raise ShotloomError("Image-to-Video benötigt eine zuvor hochgeladene öffentliche HTTPS-Bild-URL")
                body["image_url"] = image_url
            operation = "POST"
    else:
        operation = "AGENT_MCP_HANDOFF"
        endpoint = "Higgscheap models_explore(get) -> generate_video(dry_run) -> generate_video"
        params = dict(q["request_spec"]["params"])
        if q["model"] != "seedance-2-5":
            params.pop("draft", None)  # Kling does not expose a draft flag.
        body = {"model": q["model"], "params": params,
                "prompt_file": job["prompt_file"], "required_inputs": job["references"],
                "first_frame": job["first_frame"], "last_frame": job["last_frame"],
                "actual_media_ids": "REQUIRED_FROM_PROVIDER_BEFORE_SUBMISSION",
                "request_id": "shotloom_" + q["id"]}
    payload = {"schema_version": 1, "quote_id": q["id"], "episode": episode["id"],
               "shot": q["shot"], "phase": q["phase"], "provider": q["provider"],
               "model": q["model"], "account_alias": q["account_alias"],
               "contract_hash": q["contract_hash"], "authorization_id": auth["id"],
               "approved_max_usd": q["quote_usd"], "price_source": q["source"],
               "prepared_at": now.isoformat(), "quote_expires_at": q["expires_at"],
               "operation": operation, "endpoint": endpoint, "body": body,
               "linked_preview_request_id": draft.get("provider_request_id") if draft else None,
               "execution_status": "PREPARED_NOT_SUBMITTED", "execute_automatically": False,
               "security": "Human approval recorded locally; connector must repeat price/account/preflight checks before paid call. Never log credentials, do not submit twice."}
    out = root / "compiled" / episode["id"] / "requests" / f"{q['id']}.json"
    dump_json(out, payload)
    return payload


def record_stage(root: Path, project: dict, episode: dict, state: dict, quote_id: str,
                 source: Path, actual_usd: object, provider_request_id: str,
                 provider_created_at: str | None = None, provider_expires_at: str | None = None) -> dict:
    """Record an existing result only; charges are NEVER started by this function."""
    require_usd(project)
    if not project["policy"].get("rights_cleared"):
        raise ShotloomError("Rechtefreigabe nach Jobvorbereitung widerrufen")
    q = quote_by_id(state, quote_id)
    if q["contract_hash"] != contract_hash(project, episode) or q["episode"] != episode["id"]:
        raise ShotloomError("Kreativvertrag seit Quote geändert")
    auth = auth_by_id(state, quote_id)
    if auth["status"] != "reserved":
        raise ShotloomError("Freigabe verbraucht oder storniert")
    if q["phase"] == "finalize":
        # The expiry guard applies both when preparing and when registering a result.
        # Provider jobs may outlive the 7-day window; operators must verify that
        # the *finalization request was submitted* before this deadline.
        _approved_preview(state, episode, q, require_draft=True)
    request_file = root / "compiled" / episode["id"] / "requests" / f"{q['id']}.json"
    if not request_file.is_file():
        raise ShotloomError("Zuerst kostenfreien Request-Handoff vorbereiten")
    prepared = json.loads(request_file.read_text(encoding="utf-8"))
    if prepared["authorization_id"] != auth["id"] or prepared["contract_hash"] != q["contract_hash"]:
        raise ShotloomError("Requestmanifest passt nicht zur Freigabe")
    if not provider_request_id or not isinstance(provider_request_id, str) or len(provider_request_id) > 200:
        raise ShotloomError("Provider-Request-ID für Reconciliation erforderlich")
    if any(a.get("provider_request_id") == provider_request_id and a.get("provider") == q["provider"]
           for shots in state.get("episodes", {}).values() for node in shots.values() for a in node.get("attempts", [])):
        raise ShotloomError("Dieser Provider-Request ist bereits registriert")
    amount = money(actual_usd)
    if amount > money(q["quote_usd"]) or amount > money(auth["reserved_usd"]):
        raise ShotloomError("Tatsächliche Kosten liegen über der individuellen Freigabe")
    if money(sum_spend(state)) + reserved_total(state) - money(auth["reserved_usd"]) + amount > money(project["budget"]["max_total"]):
        raise ShotloomError("Gesamtbudget einschließlich anderer offener Freigaben überschritten")
    if not source.is_file() or source.suffix.lower() not in (".mp4", ".mov", ".mkv", ".webm") or source.stat().st_size == 0:
        raise ShotloomError("Lokale, nichtleere Videodatei erforderlich")
    info = probe_media(source)
    videos = [x for x in info.get("streams", []) if x.get("codec_type") == "video"]
    if not videos:
        raise ShotloomError("Quellmedium besitzt keine Videospur")
    duration = float(info.get("format", {}).get("duration", 0))
    if duration + 0.20 < q["duration_s"]:
        raise ShotloomError("Video zu kurz für geplante Shotdauer")
    res = q["resolution"]
    min_dim = {"480p": 432, "720p": 648, "1080p": 972, "4k": 1944}[res]
    if min(int(videos[0].get("width") or 0), int(videos[0].get("height") or 0)) < min_dim:
        raise ShotloomError("Videoauflösung ist niedriger als der behauptete Produktionsmodus")
    if q["draft"] and q["provider"] == "higgsfield_api":
        if not provider_created_at:
            raise ShotloomError("Ein API-Draft benötigt seinen tatsächlichen Erstellungszeitpunkt")
        created = utc(provider_created_at)
        if created > datetime.now(timezone.utc) + timedelta(minutes=2):
            raise ShotloomError("Draft-Erstellung liegt in der Zukunft")
        if provider_expires_at and utc(provider_expires_at) < created:
            raise ShotloomError("Draft-Ablauf liegt vor Draft-Erstellung")
        try:
            uuid.UUID(provider_request_id)
        except ValueError as err:
            raise ShotloomError("Higgsfield-Draft-ID muss die öffentliche UUID sein") from err
    node = shot_state(state, episode["id"], q["shot"])
    index = len(node["attempts"]) + 1
    target = root / "renders" / episode["id"] / q["shot"] / f"attempt-{index:03d}{source.suffix.lower()}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    attempt = {"attempt": index, "phase": q["phase"], "path": str(target.relative_to(root)),
               "sha256": sha256(target), "provider": q["provider"], "model": q["model"],
               "resolution": res, "draft": q["draft"], "account_alias": q["account_alias"],
               "provider_request_id": provider_request_id, "provider_created_at": provider_created_at,
               "provider_expires_at": provider_expires_at, "quote_id": quote_id,
               "linked_preview_request_id": prepared.get("linked_preview_request_id"),
               "cost": float(amount), "contract_hash": q["contract_hash"], "at": stamp(),
               "review": None, "media": {"duration_s": duration,
                                       "width": videos[0]["width"], "height": videos[0]["height"],
                                       "audio_in_source": any(x.get("codec_type") == "audio" for x in info.get("streams", []))}}
    node["attempts"].append(attempt)
    auth["status"] = "settled"
    auth["spent_usd"] = usd(amount)
    state.setdefault("spend", []).append({"episode": episode["id"], "shot": q["shot"], "attempt": index,
                                           "cost": float(amount), "currency": "USD", "phase": q["phase"],
                                           "quote_id": quote_id, "at": stamp()})
    return attempt


def settle_failed_request(project: dict, episode: dict, state: dict, quote_id: str,
                          actual_usd: object, provider_request_id: str, reason: str) -> dict:
    """Settle a failed or canceled provider task with confirmed actual charge.

    Never assume that failed generations are free. The human/operator must
    reconcile the provider invoice before entering a charge (including 0 USD).
    """
    require_usd(project)
    q = quote_by_id(state, quote_id)
    if q["episode"] != episode["id"] or q["contract_hash"] != contract_hash(project, episode):
        raise ShotloomError("Quote gehört nicht zu diesem aktuellen Kreativvertrag")
    auth = auth_by_id(state, quote_id)
    if auth["status"] != "reserved":
        raise ShotloomError("Freigabe bereits abgeglichen")
    if not reason.strip() or not provider_request_id.strip():
        raise ShotloomError("Fehlergrund und Provider-Request-ID angeben")
    amount = money(actual_usd)
    if amount > money(auth["reserved_usd"]):
        raise ShotloomError("Tatsächliche Kosten liegen über dem Limit; manuelle Eskalation")
    if money(sum_spend(state)) + reserved_total(state) - money(auth["reserved_usd"]) + amount > money(project["budget"]["max_total"]):
        raise ShotloomError("Budget einschließlich offener Freigaben überschritten")
    prod = production_state(state)
    if any(d.get("provider_request_id") == provider_request_id for d in prod["dispatches"]):
        raise ShotloomError("Provider-Request-ID bereits als Fehlschlag dokumentiert")
    auth["status"] = "settled_failed"
    auth["spent_usd"] = usd(amount)
    obj = {"quote_id": quote_id, "shot": q["shot"], "episode": q["episode"],
           "provider": q["provider"], "provider_request_id": provider_request_id,
           "cost": float(amount), "status": "failed", "reason": reason,
           "at": stamp()}
    prod["dispatches"].append(obj)
    if amount:
        state.setdefault("spend", []).append({"episode": episode["id"], "shot": q["shot"],
                                               "attempt": None, "cost": float(amount),
                                               "currency": "USD", "phase": q["phase"],
                                               "quote_id": quote_id, "outcome": "failed", "at": stamp()})
    return obj


def void_unsubmitted_authorization(state: dict, quote_id: str, by: str, confirmed: bool) -> dict:
    """Only for tasks *never submitted* to the paid provider."""
    if not confirmed or not by.strip():
        raise ShotloomError("Nutzerbestätigung erforderlich, dass kein bezahlter Request versendet wurde")
    auth = auth_by_id(state, quote_id)
    if auth["status"] != "reserved":
        raise ShotloomError("Freigabe bereits verbraucht oder storniert")
    auth["status"] = "void_unsubmitted"
    auth["voided_by"] = by
    auth["voided_at"] = stamp()
    return auth


def production_status(project: dict, episode: dict, state: dict, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    prod = production_state(state)
    pending = [{"quote_id": a["quote_id"], "shot": a["shot"], "reserved_usd": a["reserved_usd"]}
               for a in prod["authorizations"] if a["status"] == "reserved"]
    drafts = []
    for shot in episode["shots"]:
        for a in shot_state(state, episode["id"], shot["id"])["attempts"]:
            if a.get("draft") and a.get("provider") == "higgsfield_api" and a.get("provider_created_at"):
                created = utc(a["provider_created_at"])
                deadline = min(created + DRAFT_MAX_AGE, utc(a["provider_expires_at"]) if a.get("provider_expires_at") else created + DRAFT_MAX_AGE)
                used = any(b.get("linked_preview_request_id") == a.get("provider_request_id") and
                           b.get("phase") == "finalize" for b in shot_state(state, episode["id"], shot["id"])["attempts"])
                drafts.append({"shot": shot["id"], "request_id": a["provider_request_id"],
                               "expires_at": deadline.isoformat(), "expired": deadline <= now,
                               "remaining_hours": round(max(0, (deadline - now).total_seconds()) / 3600, 1),
                               "review_passed": bool((a.get("review") or {}).get("passed")), "finalized": used})
    return {"currency": project["budget"]["currency"], "spent": usd(sum_spend(state)),
            "reserved": usd(reserved_total(state)), "max_total": usd(project["budget"]["max_total"]),
            "uncommitted": usd(max(Decimal(0), money(project["budget"]["max_total"]) - money(sum_spend(state)) - reserved_total(state))),
            "open_approvals": pending, "drafts": drafts,
            "note": "Local accounting only, not a provider invoice. Expiration checked from provider-created timestamp."}
