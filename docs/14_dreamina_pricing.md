# Dreamina/CapCut: Price scenarios and provider restrictions

Research snapshot **2026-11-28**, region: publicly displayed US-store prices. **Do not assume the same plans, eligibility or checkout values apply in Germany.** This is a pricing guide, *not* an implemented, programmable Dreamina billing or generation adapter.

## Current promotion: Nov 17–30, 2026 (conditional)

Official US pricing page shows:

| Term (US, account-dependent) | Intro payment | Renewal | Included credits/month | Temporary Seedance 2.5 Unlimited |
| --- | ---: | ---: | ---: | --- |
| Basic monthly | $5 | $15/month | 1,575 | Not included |
| Standard monthly | $21 | $36/month | 3,885 | **480p, 7 days** |
| Advanced monthly (8.6k tier) | $24 | $79/month | 8,645 | **720p, 7 days** |
| Ultra monthly | $130 | $520/month | 59,000 | **720p, 7 days** |
| Ultra quarterly | $300 first quarter | $1,500/quarter | 59,000 | **1080p, 14 days** |

**Conflicting official information (purchase blocker):** The current US pricing page advertises 480p Seedance 2.5 unlimited on **monthly Standard** and 720p Seedance 2.5 unlimited on **monthly Advanced**. However, the separately published official [Dreamina Unlimited Generation FAQ](https://dreamina.capcut.com/resource/dreamina-unlimited-generation-faq) says that **monthly Standard gets no unlimited video benefit** and shows **no Seedance 2.5 (full model) benefit for monthly Advanced** (only Seedance 2.0 Fast/Mini). The source information is inconsistent. Treat monthly Seedance 2.5 web benefits as **unverified** until your signed-in checkout, account benefit panel, and model-resolution picker confirm the "Credit-free" label; obtain confirmation before a substantial purchase. Do not book a professional production budget on these contradictory benefits. The FAQ and price page do agree on the **Ultra quarterly** 1080p 14-day offer, subject to eligibility and other restrictions.

**Important conditions:** Eligible customer/account, purchase during Nov 17–30, 2026 promotion and active subscription; benefit may be granted only once per account. Higher-tier offers and checkout terms may change. The subscription benefit is unavailable via MCP, CLI, scripts, plugins and Agent Mode, including non-official browser automation. **Unlimited is explicitly for personal use only**; automated tools, account sharing and resale are prohibited. The UI also enforces one simultaneous generation per eligible model and may throttle or dynamically limit output. A zero-credit job is therefore not a free, scalable or commercially authorized API call.

The 1080p unlimited offer shown above is an **Ultra quarterly** web benefit, not a feature of the $24 Advanced monthly subscription. Account access, availability and output limitations must be checked *before* payment. If you intend paid client work or professional release, do not assume the personal-only unlimited program grants commercial production rights.

## Credited vs unlimited production for 15 minutes

Working example: **900 seconds delivered video**, average 5-second shots (= 180 shots), two previews plus one approved final (= 540 generated clips; 2,700 output seconds). This is a planning hypothesis, not a claim that every scene takes three attempts or that concurrent throughput will meet the time window.

### Unlimited-eligible personal web workflow

- If eligible for the **$24 Advanced monthly** offer, the entire **720p preview stage** could theoretically use **0 incremental generation credits for 7 days** (but still costs the subscription). Final 1080p is **not** included, and its on-site credit rate must be quoted separately; time/queue/quality remain constraints.
- If eligible for the **$300 Ultra quarterly** offer, **Seedance 2.5 1080p unlimited for 14 days** could *theoretically* cover previews and finals within the credit-free web benefit. One concurrent job, queue limits, and legal/eligibility restrictions make this **not a guaranteed full film for $300**. This option is NOT an autonomous Shotloom workflow and is not suitable to assume for commercial work.
- For a professional agentic workflow, use **individually paid, properly authorized generations** through a documented connector/API and separate paid job approvals; do not programmatically consume Dreamina unlimited credits.

### Short-duration Unlimited Generation Store passes (manual personal web use)

Dreamina also advertises *separately purchased* unlimited-generation passes for eligible members, subject to the same web-only, personal-only, non-automation restrictions. Its official FAQ lists **Seedance 2.5 1080p** US pass prices after the initial launch-week discount as **$126 for one day**, **$294 for three days**, or **$567 for seven days** (list prices $180/$540/$1,260; launch-week rates are expired). A **720p** Seedance 2.5 pass is **$84/$196/$378** after the launch week. These are **pass fees, not necessarily total account costs**: a qualifying paid membership may also be required. They are not API per-second rates and must not be used by SHOTLOOM to automate generations. See [Dreamina official unlimited FAQ](https://dreamina.capcut.com/resource/dreamina-unlimited-generation-faq).

For 900 s of finished film with 5 s average shots and 3 attempts each, there are **540 generation jobs**. A 1-day pass would require a completed manual job every **2.7 min**, around the clock, with no planning/QA/retries or provider throttling; impractical. Three days allow ~8 min/job; seven days ~18.7 min/job, still without guaranteed throughput. A $300 first-quarter Ultra 1080p 14-day benefit may be more practical *if the offer is actually available to the account*, but is also not a commercial or automatic license.

### Credit-based example without Unlimited — illustrative, not live billable quote

An independent pricing snapshot dated **Nov 4, 2026** reports 720p Dreamina credits per output second: Seedance 2.5 **37**, Seedance 2.0 Fast **8**, Seedance 2.0 Mini **5**. An actual account may see different prices on Nov 28, especially with temporary discounts. At US **renewal** Basic $15/1,575 credits (~$0.009524 per credit), the nominal consumption would be:

| 900 seconds delivered | Video credits | Approx USD equivalent at Basic renewal rate |
| --- | ---: | ---: |
| One 720p Seedance 2.5 pass | 33,300 | $317.14 |
| 3 × 720p Seedance 2.5 | 99,900 | $951.43 |
| 2 × 720p Seedance 2.0 Fast + 1 × 720p Seedance 2.5 | 47,700 | $454.29 |
| 3 × 720p Seedance 2.0 Mini | 13,500 | $128.57 |

These are **credit-equivalent planning estimates**, not the price of an actual purchase. Monthly subscription quantities are insufficient for the larger scenarios; you would need multiple periods/credit purchases at actual checkout terms, and credit rollover/top-up eligibility is not verified. These rows are **720p only**. Public pages do not establish an account-confirmed, universally valid **1080p final-generation credit price**, so no exact professional Full-HD total can be honestly calculated without a signed-in quote. Neither does a Dreamina low-res output qualify for official Higgsfield Draft Finalize.

### Expired historical promo is not today's quote

A September/October promotion published 720p Seedance 2.5 **$0.035 per second** and Seedance 2.0 Fast **$0.008 per second** as effective *first-month* subscription utilization, ending Oct 9, 2026. A naive 2,700-second calculation gives $94.50 or $21.60 respectively, but is **inapplicable** to new purchases on Nov 28. Do not mix expired promo unit prices with today's first-month plan promotions.

## SHOTLOOM policy

Dreamina's web-only unlimited is a **manual, non-agent option** and cannot be scheduled, scripted or charged as a provider API job. SHOTLOOM may plan or import already legally produced offline clips for ordinary review only; it must not claim to execute or obtain Unlimited credits through CLI, MCP or its orchestrator. Any possible official Dreamina API adapter requires a publicly documented, supported programmatic interface and a validated business/commercial license; at present **none is implemented**.

## Sources

- Official US pricing page, viewed Nov 28: https://dreamina.capcut.com/pricing/dreamina-price?store_region=us (includes Nov 17–30 promotion, US plans, 1080p Ultra quarterly, personal-only & no automation, queue limitations)
- Independent renewal-credit snapshot, Nov 4: https://www.ai-media-studio.com/dreamina-pricing (also a competing seller, cross-check before payment)
- Expired September/October promotion: https://dreamina.capcut.com/resource/dreamina-september-offer-faq-2026
- Model overview: https://dreamina.capcut.com/seedance/seedance-2-5-vs-kling-3-0
- Separate BytePlus/ModelArk API (not Dreamina web billing): https://docs.byteplus.com/en/docs/modelark/model-pricing
