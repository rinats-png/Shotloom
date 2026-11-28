---
name: budget-render-stage
version: 0.2.0
summary: Per-shot cost control, draft/final/4K routing, human approval and reconciled paid-job accounting
---

Read `docs/13_budget_draft_final.md` before running. Never place paid orders automatically as part of this Skill. Use `shotloom cost-plan` for rough cost estimates; get an account-specific quote from the actual provider; import the exact quote; request human approval of the concrete job; prepare handoff; execute only via an explicitly connected operator; record all costs and outcomes; run human QA on draft and final. For official Higgsfield Seedance Draft finalize only the approved unexpired `request_id` from the same account. Do not use cheap non-draft 480p as evidence that finalization exists. Exclude old promo pricing from live cost decisions.
