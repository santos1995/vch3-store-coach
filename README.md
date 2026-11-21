# Store Coach - Manyavar (VCH3)

Live app: https://santos1995.github.io/vch3-store-coach/

Demo highlights (43 seconds, silent screen recording): https://youtu.be/8I59mi2RoLw

Logic explanation guide (English PDF): [Manyavar-Store-Coach-Logic-English.pdf](./Manyavar-Store-Coach-Logic-English.pdf)

Built from scratch at Vibe Coders Hackathon Edition 3 (Kolkata, 21 Nov 2026) for case study A: Store Coach, Vedant Fashions Limited.

## Working demo
The first manager's brief generates automatically when the page opens. It refreshes at the next local day while the page remains open. Pick another manager to inspect their stores. The data snapshot stays fixed at 31 Oct 2026. No real messages are sent.

- Up to five manager issues, ordered by rough rupee scenarios. Their identities are retained per manager for snapshot week 2026-W44 in this browser's local storage. Other store details are diagnostics, not more assignments.
- Store conversion and basket comparisons exclude dates marked festival or wedding in the supplied state calendar. Same-city peers use the same state calendar and period. This is a date filter, not a causal seasonal model.
- Bills exceeding footfall, zero/negative footfall and missing footfall with bills suppress that store's performance alerts. The pack's PAT-03 demonstrates this.
- Each salesperson gets a short action and a named same-store peer. Minimum samples: 7 shifts and 10 bills; 5 category bills for attachment coaching; 20 eligible customers for return-rate coaching. Actions are capped at 60 words.
- Repeat means another bill at least 30 days after the customer's first observed bill at that store or salesperson, among customers whose first bill was at least 30 days before snapshot. Cohorts are processed chronologically.
- A historical outcome replay compares 18-24 Oct with 25-31 Oct, excluding calendar events. It reports observed metric movement, not a causal effect of coaching.
- Phone views show readable salesperson cards. Rankings and actions are rule-based. The optional Sarvam note may use an honestly labelled local fallback.

## Remaining limits
This is a browser-local fixed-data demo, not a server scheduler or daily delivery service. No live data refresh, cross-device weekly budget, actual coaching intervention, or new week-later observation is performed. Clearing site data resets local assignments. Real unattended daily delivery requires an approved data source, scheduler and destination.

Rupee figures are assumptions for ordering, not measured losses or guaranteed gains. Staffing uses a labelled 10% of average daily sales scenario. Stock is not joined; staff must check availability. Category choice is not a full assortment-avoidance model. The 43-second video shows the final working state, including the browser-runner, cohort and outcome additions.

## Data and repository
Snapshot: 31 Oct 2026, the pack's "today", not the actual event date. The pack says its data is synthetic. Data and briefs belong to Vedant Fashions Limited. Only small derived aggregates are committed as data.js. No raw CSVs, customer IDs, passwords or keys are included. Aggregation was run locally. The supplied calendar is the source of event dates; no dates are inferred from model knowledge.

The app is static HTML and JavaScript on GitHub Pages. The optional AI note calls a separate proxy; no service secret is in browser code.

History note: commit 7684c1c's generated message is inaccurate. Its actual change adds data.js, not a print-statement update. History is preserved rather than rewritten.
