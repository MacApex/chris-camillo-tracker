# Divergence scanner

A research toolkit that contrasts **Wall Street analyst consensus** with **niche and social signals**, then scores the gap. It is inspired by Chris Camillo's "information imbalance" idea: look for places where culture and conversation may be moving before sell-side models catch up.

**This is not financial advice, not a trading bot, and not a recreation of Camillo's results.** His edge is discretionary observation, catalyst timing, and a high-variance options book. A numeric score cannot substitute for that. See the [root disclaimer](../DISCLAIMER.md).

## What it does

1. **Analyst leg (a).** Pulls, from free Yahoo Finance data via [`yfinance`](https://github.com/ranaroussi/yfinance):
   - recommendation counts and a 1–5 consensus mean
   - analyst price targets and implied upside versus the last close
   - recent upgrades / downgrades
   - news headlines
2. **Sentiment (b).** Scores analyst-action text and headlines with [VADER](https://github.com/cjhutto/vaderSentiment). Optional [FinBERT](https://github.com/ProsusAI/finBERT) if you set `CCT_USE_FINBERT=1` and install `transformers` + `torch`. If neither is available, a small finance lexicon is used.
3. **Social / niche leg (c).**
   - Google Trends interest-over-time via [`pytrends`](https://github.com/GeneralMills/pytrends), using a five-year window and a year-over-year comparison — the seasonal adjustment Camillo described to Business Insider (2021). Trends is unofficial and often rate-limited.
   - Reddit mentions via the public JSON search endpoints (no API key), with VADER on post text.
   - Optional X/Twitter recent search if `CCT_X_BEARER` is set; skipped otherwise.
4. **Divergence (d).** `social_score − analyst_score`, both on a 0–100 scale. A ticker is flagged `opportunity_flag` only when social momentum is rising **and** the Street is flat or negative. The opposite shape is tagged `late_or_crowded`.

## Install

```bash
cd toolkit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run from the `toolkit/` directory (or set `PYTHONPATH`).

## Example

```bash
cd toolkit
python -m camillo_tracker scan CROX LULU ELF NWL TPR --out examples/sample_run.json
```

A real run from 13 November 2026 (Asia/Shanghai) is saved at [`examples/sample_run.json`](examples/sample_run.json), with a short write-up in [`examples/sample_run.md`](examples/sample_run.md). Network-dependent sources (especially Google Trends and Reddit) can fail; the scanner degrades gracefully and records the gap in the JSON.

## Interpreting a flag

A flag is a **prompt for human work**, the kind Camillo actually does: talk to store clerks, read comments against a baseline of what "normal" looks like, check whether the change can move the needle at a company of that size, and ask whether the information is already priced in. The scanner cannot do any of that.

Google Trends in particular should be treated with care. In 2025 Camillo publicly argued that AI-generated queries were corrupting Trends for some consumer brands, and he exited a Lululemon thesis after other signals failed to confirm a Trends spike.

## Disclaimer

Not financial advice. For research and education only. Free data vendors can be delayed, incomplete, or wrong. Past patterns, including Camillo's audited record, do not predict future results. You can lose money, especially with options and concentration — two features of his personal book that this toolkit deliberately does **not** automate.

## Street-view and multi-platform signals

```bash
python -m camillo_tracker street CROX
python -m camillo_tracker signals CROX --wiki Crocs
python experiments/run_event_study.py
python -m pytest -q
```

- `camillo_tracker.street_view` — Street Consensus Profile and priced-in verdict.
- `camillo_tracker.signals` — Wikipedia pageviews, Google Trends, Google News RSS, GDELT (respect the 5-second limit), YouTube metadata via yt-dlp, iTunes Search, corroboration (two rising z-scores, no imputation). Platforms that worked but have no baseline (TikTok lifetime totals, a single Amazon BSR) are listed under `platforms_present_no_z`, not scored as a z.
- `camillo_tracker.tiktok` — public `/api/challenge/detail/` (StealthyFetcher in-page fetch, prefer `statsV2`) and Creative Center `GetHashtagList`. Cached verified sample by default; set `CCT_LIVE_TIKTOK=1` to refetch. davidteather/TikTok-Api is a second official-shaped method (no login).
- `camillo_tracker.amazon` — public Best Sellers `data-client-recs-list` official `zg.rank`, title-only brand match, and product-page BSR phrases. Cached sample by default; `CCT_LIVE_AMAZON=1` to refetch.
- Optional scrapers already attempted in `scripts/probe_platforms.py`: Scrapling Fetcher, instaloader (no login), twscrape (skipped — needs accounts; we will not log into user credentials), yt-dlp `--skip-download`. Status lives in `../data/platform_status.json`. Verified numbers: `../data/tiktok/sample_hashtag_counts.json`, `../data/amazon/sample_bsr.json`.

### Environment variables

| Variable | Purpose |
|---|---|
| `CCT_X_BEARER` | Official X / Twitter recent-search bearer for `social.x_mentions`. Without it, skip or use the MCP sample in `data/x_counts_sample.json`. |
| `TWITTER_BEARER_TOKEN` | Same, fallback name. |
| `CCT_USE_FINBERT=1` | Enable FinBERT if `transformers` and `torch` are installed. |
| `YOUTUBE_API_KEY` | Optional official YouTube Data API. The default YouTube path is yt-dlp metadata search, no key. |
| `CCT_LIVE_TIKTOK=1` | Live StealthyFetcher refetch of `/api/challenge/detail/` instead of the verified cache. |
| `CCT_LIVE_AMAZON=1` | Live Fetcher refetch of a Best Sellers page instead of the verified cache. |

Public data only. Do not put personal login cookies in this toolkit.
