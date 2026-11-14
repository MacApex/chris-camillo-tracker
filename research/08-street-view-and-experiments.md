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
| TGT 2011-09-13 (Target nationwide launch, not a verified fill; equity path recomputed 14 Nov 2026; 7 Sep anchor withdrawn) | +3.53% | +5.54% | +16.33% |
| GME 2021-01-25 (mid-squeeze placeholder; split-adjusted) | +19.4% | +120.0% | +139.5% |
| AMC 2021-01-25 (split-adjusted) | +105.7% | +160.2% | +811.5% |
| TPR 2021-08-16 (mention date, not entry) | −8.3% | +4.5% | −9.8% |

Limitations are listed in the JSON: small sample, storytelling bias, month precision, mid-squeeze placeholders, mention-vs-entry, puts vs equity, OTC price disagreement on Dorel (yfinance ~$0.69 vs BI screenshot $1.56 — both kept), incomplete Yahoo rating history. **Historical high-niche / low-Street quadrants were not assigned**: pytrends “today 5-y” from November 2026 does not reach 2019–2020, and we refuse to invent them. Wikipedia attention is a proxy only where the article exists (GME 2,628 / 16,446 / 57,513 mean-14d-before / on-date / mean-14d-after). ELF 2019 Wikipedia series: 404.

## Multi-platform probes

See `data/platform_status.json` and `data/provenance.csv`. Every numeric point has a source URL, timestamp, and method. Cross-checks: Wikipedia last-day Crocs 473 via two fetches; X counts from the official API; YouTube view counts from yt-dlp metadata. Unverified numbers were discarded, never estimated.


## TikTok and Amazon public-data pass (13 Nov 2026, Asia/Shanghai)

TikTok and Amazon trend figures do not have to come from official developer programs. A second pass used only public, unauthenticated routes.

**TikTok — worked.** Scrapling StealthyFetcher captured Creative Center's public `GetHashtagList` XHR (US last-7-days top 3, DOM-confirmed; unauthenticated `totalCount` is 3; sample brands were not in that list; "See analytics" appears to need a login, which we did not use). The working path for sample brands is the public `/api/challenge/detail/` endpoint, fetched in-page after a StealthyFetcher session on tiktok.com. Prefer `statsV2` (exact strings) over rounded `stats`. davidteather/TikTok-Api `hashtag.info()` (no login) returns the same challengeInfo shape and cross-checked #crocs, #lululemon, and #elfcosmetics. Two timed #crocs pulls document a live counter. Fetcher-only `__UNIVERSAL_DATA__` was a bot-detected shell without stats. hashtagradar.com and tiktokhashtags.com are the same site; their totals are lower and do not override official counts. `#coach`, `#lulu`, and `#slime` are noisy generic words.

These are **lifetime cumulative** counts — a stock, not a 7-day flow. A single snapshot is not a momentum z-score.

**Amazon — worked for Best Sellers lists and one product page.** Official `data-client-recs-list` `render.zg.rank` on public Best Sellers pages, brand match on product title only (context matches were false positives and were discarded). Crocs Classic Clog is #1 in Women's Shoes and #12 in Clothing, Shoes & Jewelry; Lined Clog is #29 in Women's Shoes and, on the product page, #455 in Clothing, Shoes & Jewelry and #5 in Women's Mules & Clogs; two e.l.f. items are #23 and #24 in Beauty. Lululemon, Coach, and Elmer's were not in the top 50 of the lists fetched. Movers & Shakers had no recs JSON via Fetcher; search returned 503; CamelCamelCamel was Cloudflare 403 (not bypassed); Keepa public PNGs are price charts, not BSR, and were not transcribed.

**Corroboration rerun.** None of the five sample tickers reach the two-platform rising-z threshold. Wikipedia last-day views are all below their own history. Only ELF's Google Trends momentum clears +0.5 (n_confirming = 1). TikTok and Amazon sit in `platforms_present_no_z`. Nothing was imputed. See `data/experiments/corroboration_sample.json` and the [street-view page](https://macapex.github.io/chris-camillo-tracker/street-view.html).
