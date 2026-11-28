# Cost-aware Draft → Final production (operational specification)

**Status (2026-11-28): local CLI and provider-specific handoff implemented. No paid-generation or Dreamina API adapter is included.** This is an auditable workflow, not a fully autonomous video generator. A connected and authorized human/operator agent must execute the provider call.

## Non-negotiable rules

1. First use the screenplay, shot list, character/wardrobe locks, reference images, edit plan, rough audio and **animatic**. These save more than making every candidate a paid clip.
2. Render **only shots worth testing**. Classify complexity and choose `auto`, `direct`, or `preview_then_final` in `shot.production` (optional extension field). Never assert that a preview is a final video.
3. The **provider and account** belong to each quote/attempt. Do not mix a Dreamina web render with a Higgsfield API draft, or a Higgscheap non-draft preview with an official `finalize-draft` request.
4. A normal low-resolution Kling or Seedance output may *not* preserve choreography in a new high-resolution generation. Treat that transition as **regeneration**, not as deterministic upscale.
5. The official **Higgsfield Seedance 2.5 Draft** is a distinct, documented capability: create `draft:true` at 480p, inspect the completed result, and finalize its request UUID into 1080p on the **same Higgsfield account**, within seven days and before any shorter retention deadline. Finalization incurs a separate charge; no credit is deducted for already-paid drafts. Verify provider status and terms immediately before finalization.
6. A Higgscheap `draft:true` option is **not proof** that the user's Higgscheap connector exposes the same official finalization API. The current connector advertises ordinary generation and reuse. Route Higgscheap previews into an independently charged final generation unless you have tested a real provider finalization feature.
7. Use `models_explore(get)`, then an exact **`generate_video(dry_run:true)`**, including source media and normalized parameters. Confirm account identity, price and charge. Only after a **per-attempt human approval** may an operator issue a paid call, using a stable idempotency key and a hard max-credit limit.
8. Budget in a single explicit currency. USD costs should not silently be counted against an EUR budget. Distinguish provider credits, USD/credit, taxes, fees, FX, provider minimum billing, subscriptions and volume purchases.
9. Record paid failures at actual charged cost. Do **not** release reserved spending merely because a provider is still processing. A void is only for a definitively *unsubmitted* request.
10. Preview QA and final QA are **separate**; perform full-resolution checks on identity, hands, body physics, lip sync, dialogue timing, lighting, cut points, and legal/rights compliance. Never use a preview to assemble the final film.

## Routing matrix

| Shot type | Preview strategy | Final | Important constraint |
| --- | --- | --- | --- |
| Simple static / one-character walk | Often render directly | Kling 1080p | At Higgscheap, 720p vs 1080p saving is small; extra draft can increase cost |
| Dialogue / two-person interaction | Animatic + quick targeted test | Kling or Seedance 1080p | Lock voices before lip-sync; close-up QA required |
| Fight / demanding contact / tracking | Physically described blocking + motion reference + preview | Highest-performing model for that exact motion | 480p cannot prove hand/foot contact is good |
| Official Seedance 2.5 draft-final | One or more 480p drafts, score + approve | Higgsfield API `finalize-draft` 1080p | Only verified draft UUID, same account, unexpired |
| Kling 4K master | 720p rough cut then high-res selected shots | 4K only where needed | 4K cost per second substantially higher |
| Dreamina web | User-account priced, on-platform | Separate download / export | Promotional unlimited web-only: **not** CLI/MCP/API rights |

## Cost planning with the CLI (not a live quote)

The `cost-plan` command uses documented snapshot data (`shotloom/costing.py`, 2026-11-28), per output second, and returns a reference-only JSON file. The snapshot **must not** be interpreted as a provider guarantee.

```bash
# Prepare a project with an explicitly USD-denominated budget in project.yaml.
python -m shotloom.cli validate --project projects/my-film
python -m shotloom.cli compile --project projects/my-film --episode EP01
python -m shotloom.cli cost-plan --project projects/my-film --episode EP01 \
  --provider higgscheap --model kling-3 --resolution 1080p \
  --previews 2 --cut-overage 15 --rework-reserve 25 --write
python -m shotloom.cli cost-plan --project projects/my-film --episode EP01 \
  --provider higgsfield_api --model seedance-2-5 --resolution 1080p --previews 2
```

Notes: Not every shot works with every provider or duration; provider validation remains mandatory. A simple Kling shot may route directly; the `auto` choice avoids buying a redundant preview when the preview/final price ratio is poor. Add `production: {render_strategy: preview_then_final, risk_tags: [fight, physical_contact]}` to a shot if a specific proof-of-motion preview is required. Edit the storyboard/animatic before paid previews.

## Safe per-quote handoff

1. Create a fresh quote for **one shot and one attempt**. For Higgscheap, import an actual `generate_video(dry_run:true)` result with the exact selected model/params/media. `examples/quote_higgscheap_template.json` shows the required envelope. This tool **does not independently verify** an operator-supplied JSON file: the linked agent/operator must match it to the provider result and account.
2. For Higgsfield API, the `examples/quote_higgsfield_template.json` envelope takes the published *reference rate*, not a live quote. Perform provider/account price check before placing an order.
3. Import the source data: `shotloom quote-import --project ... --shot EP01-S001 --file price.json`.
4. Ask a human to approve **the quoted USD total, the named account/model and the precise one-shot request**. Document that approval using `shotloom stage-authorize ... --quote-id ID --by "Approver" --confirmed`. This `--confirmed` flag cannot serve as its own consent.
5. Prepare a non-sending handoff: `shotloom stage-request ... --quote-id ID`. Output `compiled/EP01/requests/ID.json` has `execution_status: PREPARED_NOT_SUBMITTED` and `execute_automatically:false`. A connected operator must map actual `media_id`s and rerun provider verification before any paid call.
6. The operator makes the **one** approved paid generation, then waits for completion. Never send a duplicate request after a timeout; use the **same idempotency key** on retries and look up the original job first.
7. After downloading the actual output, record the charge and video using `shotloom stage-record ... --actual-usd A --provider-request-id R`. If no usable result was generated, reconcile the invoice using `shotloom stage-failure ... --actual-usd A --provider-request-id R --reason ...`. Cancel a reservation with `shotloom stage-void ... --confirmed-not-submitted` **only** if not submitted to the provider.
8. Run `shotloom review ...` with all ten quality criteria, then `shotloom select ...` for **final** or **finalize** outputs only. A 480p/720p preview is blocked from being selected as final.
9. A Higgsfield finalize quote needs the **approved, unexpired original draft's `request_id`**. The first request returns a draft UUID, finalization creates a new UUID, and both must be stored. Check deadline with `shotloom production-status ...`.

## Budget model for 15 minutes

For illustration, `900` seconds of finished footage, three attempts per used shot, **no lip-sync fees, music, human work or tax**, with constant shot length:

| Strategy | Illustrative result | Caveat |
|---|---:|---|
| Kling 3.0, always 1080p, audio off | $243 | three full-resolution passes |
| Kling 3.0, 2 × 720p then 1080p | $207 | $36 saving (~14.7%); not worth it for every easy shot |
| Seedance 2.5 Higgscheap, 3 × 1080p | ~$1,636 | specific 16:9 snapshot rates |
| Seedance 2.5 Higgscheap, 2 × regular 480p then 1080p | ~$704 | **regeneration**, not verified deterministic finalize |
| Official Higgsfield API Seedance 2.5, 2 × draft then one finalize | ~$798 | official provider self-serve rates; separate billing |

Price comparisons depend on actual per-account pricing and assumptions. The cheapest **usable** plan can change if failure rates, shot lengths, reference costs, provider expiry, finalization feasibility, 4K targets or audio requirements change.

## Provider and source references

- Higgsfield official Draft / Finalize: https://open.higgsfield.ai/models/bytedance/seedance-2.5/finalize-draft/api-reference (480p draft, same-account 1080p finalize, 7-day maximum, separate billing)
- Higgscheap model catalog and exact dry-run: via connected models_explore / generate_video tools; model and prices account-dependent.
- Dreamina plans / credit limits: https://dreamina.capcut.com/pricing/dreamina-price (vary by country/account/time; web-only unlimited is not API availability)
- Dreamina Sept 2026 promo history: https://dreamina.capcut.com/resource/dreamina-september-offer-faq-2026 (expired: never treat as today's API unit price)
- BytePlus/ModelArk: https://docs.byteplus.com/en/docs/modelark/model-pricing (separate API, not Dreamina site or subscription billing)

## Next implementation opportunities

A fully automated paid dispatch must be a **separate** opt-in component with authenticated provider verification and explicit authorization, job-status reconciliation, secured secrets and replay protection. In the current release, every provider call is a handoff, not a payment or rendering operation. No automatic Dreamina UI automation or undocumented browser payment flow.
