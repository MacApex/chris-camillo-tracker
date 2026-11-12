# Street-view framework and event study

Companion to https://macapex.github.io/chris-camillo-tracker/street-view.html

## Framework

`camillo_tracker.street_view.street_profile(symbol)` builds a Street Consensus Profile from free yfinance data:

1. Consensus rating distribution
2. Price-target dispersion and implied upside
3. Estimate revisions (`eps_trend`, `eps_revisions`)
4. Rating-change recency (`upgrades_downgrades`, 90-day window)
5. News/note sentiment (VADER on Yahoo headlines)
6. Coverage count (Yahoo snapshot as a proxy, not a full IBES universe)
7. Earnings-surprise history

The priced-in verdict is rule-based and conservative: `already_priced`, `partially_priced`, `not_clearly_priced`, or `insufficient_data`. Missing components lower confidence; they are never filled in. Workflow: niche signal → candidate → profile → verdict. Only “niche rising and not clearly priced” becomes `candidate_for_human_work`.

Unit tests (no network) in `toolkit/tests/test_street_view.py` and `test_trades.py`: **11 passed**, 13 November 2026, Asia/Shanghai.

## Event study

Script: `toolkit/experiments/run_event_study.py`. Results: `data/experiments/event_study.json`.

Ten dated, tickered events; forward 21/63/126-trading-day close-to-close returns from the first session on or after the documented date, yfinance auto-adjusted closes, retrieved 13 Nov 2026, Asia/Shanghai. **These are market paths, not Camillo’s P&L.**

| Event | 1m | 3m | 6m |
|---|---:|---:|---:|
| ELF 2019-03-15 (month placeholder) | +25.0% | +32.5% | +70.3% |
| QSR 2019-04-15 (loss thesis, early window) | +0.5% | +9.2% | +7.1% |
| QSR 2019-08-15 | −2.2% | −7.2% | −7.3% |
| SPY 2020-02-18 (short; underlying) | −28.7% | −11.9% | +1.4% |
| WYNN 2020-02-18 (short; underlying) | −67.5% | −38.4% | −36.9% |
| DIIBF 2020-04-24 | +131.1% | +242.9% | +608.7% |
| TGT 2011-09-07 (equity path, not the overnight options) | +2.6% | +6.7% | +14.4% |
| GME 2021-01-25 (mid-squeeze placeholder; split-adjusted) | +19.4% | +120.0% | +139.5% |
| AMC 2021-01-25 (split-adjusted) | +105.7% | +160.2% | +811.5% |
| TPR 2021-08-16 (mention date, not entry) | −8.3% | +4.5% | −9.8% |

Limitations are listed in the JSON: small sample, storytelling bias, month precision, mid-squeeze placeholders, mention-vs-entry, puts vs equity, OTC price disagreement on Dorel (yfinance ~$0.69 vs BI screenshot $1.56 — both kept), incomplete Yahoo rating history. **Historical high-niche / low-Street quadrants were not assigned**: pytrends “today 5-y” from November 2026 does not reach 2019–2020, and we refuse to invent them. Wikipedia attention is a proxy only where the article exists (GME 2,628 / 16,446 / 57,513 mean-14d-before / on-date / mean-14d-after). ELF 2019 Wikipedia series: 404.

## Multi-platform probes

See `data/platform_status.json` and `data/provenance.csv`. Every numeric point has a source URL, timestamp, and method. Cross-checks: Wikipedia last-day Crocs 473 via two fetches; X counts from the official API; YouTube view counts from yt-dlp metadata. Unverified numbers were discarded, never estimated.
