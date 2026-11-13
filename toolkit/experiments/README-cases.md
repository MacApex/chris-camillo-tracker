# Documented-case series

Raw JSON: `../../data/cases/<id>.json`. Chart payload: `../../docs/data/cases-charts.json`. Index and lead summary: `../../data/cases/index.json`.

Collected 13 Nov 2026 (Asia/Shanghai):

- Prices, `upgrades_downgrades` (sorted, then date-filtered — the Yahoo index is not monotonic), earnings dates: yfinance 1.8.
- Wikipedia daily pageviews: Wikimedia REST, identified User-Agent. ELF article is `E.l.f._Cosmetics` (`E.l.f.` is 404).
- Google Trends: `camillo_tracker.social.google_trends` with an **explicit** timeframe `"YYYY-MM-DD YYYY-MM-DD"`, US, urllib3 `method_whitelist` patch. Custom windows returned real 2016–2020 series in this run.
- Lead times are revised by hand against honest rules (see `research/09-methodology-and-workflow.md`): no 1-day RBI lead from a $2 same-rating trim; no 5-day Wynn lead from a $3 trim; Dorel uses the first earnings beat, not an empty ratings series; month-precision is labeled; mention/era/multi-year/exit-only cases do not get a lead.

Do not interpolate missing series. Re-fetching requires network and may 429 on Trends; prefer the saved JSON for the site. Tests: `../tests/test_cases_data.py`.
