# Store Coach - Manyavar (VCH3)

Live app: https://santos1995.github.io/vch3-store-coach/

Demo highlights (47 seconds, silent screen recording): https://youtu.be/AnyTYkc0PUc

Built from scratch at Vibe Coders Hackathon Edition 3 (Kolkata, 21 Nov 2026) for case study A: Store Coach, Vedant Fashions Limited.

## Working prototype
Pick an area manager to generate an on-demand brief. The app shows up to five assigned issues ranked by rough rupee estimates, with diagnostic store details and one short action per salesperson. Open a store to see its team. It does not send any messages or run a daily schedule.

Conversion, items per bill, and 30-day return-customer rates come from local preprocessing of the synthetic pack. Salesperson comparisons use the same store's recent roster and sales rates. Store comparisons use same-city peers. Rules, not an LLM, choose issues and actions.

## Limits, not completed features
- No autonomous morning delivery or week-later outcome check.
- The five-item list is generated per view, not an enforced persistent weekly budget.
- Rupee figures are scenarios for ordering, not observed losses or guaranteed gains. Staffing uses an explicit 10% assumption.
- Same-window city comparisons are not proven seasonal adjustment. Calendar events are context. Prior-period conversion declines are diagnostic-only, excluded from the priority list.
- Stock availability is not verified; attachment actions ask staff to check sizes first.
- Staff actions do not yet consistently name a same-store role model, and salesperson-level repeat behavior is not included.
- The optional Sarvam manager note may fall back to a rule-based template. The badge reports which happened. The demo video shows fallback, not successful AI generation.

## Data and repository
Snapshot: 31 Oct 2026, the pack's "today", not the actual event date. The pack says its data is synthetic. Data and briefs belong to Vedant Fashions Limited. Only small derived aggregates are committed as data.js. No raw CSVs, customer IDs, passwords or keys are included. Aggregation was run locally; the preprocessing script is not in this repository.

The app is static HTML and JavaScript on GitHub Pages. The optional AI note calls a separate proxy; no service secret is in browser code.

History note: commit 7684c1c's generated message is inaccurate. Its actual change adds data.js, not a print-statement update. History is preserved rather than rewritten.
