# Store Coach - Manyavar (VCH3)

Live app: https://santos1995.github.io/vch3-store-coach/

Demo highlights (43 seconds, silent screen recording): https://youtu.be/8I59mi2RoLw

Logic explanation guide (English PDF): [Manyavar-Store-Coach-Logic-English.pdf](./Manyavar-Store-Coach-Logic-English.pdf)

Built from scratch at Vibe Coders Hackathon Edition 3 (Kolkata, 21 Nov 2026) for case study A: Store Coach, Vedant Fashions Limited.

## Working demo
The first manager's brief generates automatically when the page opens. It refreshes at the next local day while the page remains open. Pick another manager to inspect their stores. The data snapshot stays fixed at 31 Oct 2026. No real messages are sent.

- Up to five manager issues, ordered by rough rupee scenarios. Each issue names its lever: more bills, bigger baskets, or more repeat customers. Their identities are retained per manager for snapshot week 2026-W44 in this browser's local storage. Other store details are diagnostics, not more assignments.
- Staffing issues are flagged when an experienced seller is no longer rostered (roster rows end 14-60 days before the snapshot, with solid recent productivity; the pack's LKO-02 demonstrates this; the roster records no exit reason, so the action asks the store lead to confirm) and when a reliable seller shows far more rostered Off days than the store norm (at least 8 Off days in the last 28, at least 2.5 above the store's own median, with at least store-median bills per day when present; the pack's BLR-04 and PAT-02 demonstrate this). The roster marks only Present or Off, with no leave types, so this is an elevated-Off-days review prompt, not a missed-shift or blame finding, and comparisons are against the store's own team.
- A city-level market note appears in a manager brief only when a whole city's conversion or footfall falls across most of its stores. This pack shows no such slowdown, so no market note is generated.
- Salespeople who avoid a whole category versus their city median (their share at most half the city's, with the city share at least 15%) get a category-coaching action naming the category and both shares.
- Store conversion and basket comparisons exclude dates marked festival or wedding in the supplied state calendar. Same-city peers use the same state calendar and period. This is a date filter, not a causal seasonal model.
- Bills exceeding footfall, zero/negative footfall and missing footfall with bills suppress that store's performance alerts. The pack's PAT-03 demonstrates this.
- Each salesperson gets a short action and a named same-store peer. Minimum samples: 7 shifts and 10 bills; 5 category bills for attachment coaching; 20 eligible customers for return-rate coaching. Actions are capped at 60 words.
- Repeat means another bill at least 30 days after the customer's first observed bill at that store or salesperson, among customers whose first bill was at least 30 days before snapshot. Cohorts are processed chronologically.
- A historical outcome replay compares 18-24 Oct with 25-31 Oct, excluding calendar events. It reports observed metric movement, not a causal effect of coaching.
- Phone views show readable salesperson cards. Rankings and actions are rule-based. The optional Sarvam note may use an honestly labelled local fallback.

## Scheduled generation
A GitHub Actions workflow (.github/workflows/daily-brief.yml) runs every morning at 05:30 IST (00:00 UTC), without anyone asking. It runs generate_briefs.js, which loads the same data.js and the exact rule code the page uses (extracted from index.html at run time, so browser and schedule can never drift), and writes:

- generated/briefs-latest.md and generated/briefs-YYYY-MM-DD.md: every manager's morning brief.
- generated/briefs-latest.json: every manager's brief plus every store's salesperson alerts and actions.
- state/weekly.json: the five-assignment weekly retention state, so assignment identity stays stable across scheduled runs.

Outputs are committed back to this repo by the workflow. It was verified with a manual dispatch (workflow_dispatch); the first unattended cron fire is due at the next 05:30 IST and had not yet been observed when this was written. Because the data snapshot is fixed at 31 Oct 2026, briefs stay identical between runs: that is expected, not a failure. Every output prints the execution time separately from the data-as-of date.

## Remaining limits
This is a fixed-data demo with an in-repo scheduled generator, not a live delivery service. The scheduled job re-runs the same fixed snapshot every morning; there is no live data refresh, cross-device weekly budget, actual coaching intervention, or new week-later observation, and briefs are committed to the repo, not delivered to managers. Clearing site data resets the page's local assignments; scheduled-run state lives in state/weekly.json. Real daily delivery to managers requires an approved live data source and destination.

Rupee figures are assumptions for ordering, not measured losses or guaranteed gains. Staffing uses a labelled 10% of average daily sales scenario. Stock is not joined; staff must check availability. Category choice is not a full assortment-avoidance model. The 43-second video was recorded before the staffing, lever-label and category additions; the live app linked above is the current build.

## Data and repository
Snapshot: 31 Oct 2026, the pack's "today", not the actual event date. The pack says its data is synthetic. Data and briefs belong to Vedant Fashions Limited. Only small derived aggregates are committed as data.js. No raw CSVs, customer IDs, passwords or keys are included. Aggregation was run locally. The supplied calendar is the source of event dates; no dates are inferred from model knowledge.

The app is static HTML and JavaScript on GitHub Pages. The optional AI note calls a separate proxy; no service secret is in browser code.

History note: the generated messages of commits 7684c1c and 3fb3596 are inaccurate. 7684c1c adds data.js and 3fb3596 replaces it with regenerated aggregates; neither changes a print statement. History is preserved rather than rewritten.
