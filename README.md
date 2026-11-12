# Chris Camillo Tracker

A researched, cited archive of Chris Camillo's **social-arbitrage** investing — the independently reviewed track record, a bilingual core-logic playbook, a trade database, a Street-view “is it priced in?” framework with an honest event study, multi-platform signal adapters (with a provenance log), and a working Python **divergence scanner**.

**[Open the site](https://macapex.github.io/chris-camillo-tracker/)** · **[核心逻辑 · Core logic](https://macapex.github.io/chris-camillo-tracker/core-logic.html)** · Research notes in [`research/`](research/) · Toolkit in [`toolkit/`](toolkit/)

This project is **not affiliated with** Chris Camillo, Dumb Money, TickerTags, M Science, Jack Schwager, or Business Insider. **It is not financial advice.** You can lose money, especially with options and concentration. Read [DISCLAIMER.md](DISCLAIMER.md) before anything else.

## The audited core, in brief

The only numbers we treat as independently reviewed are from Jack Schwager's audit of monthly brokerage statements, reported and partly re-examined by *Business Insider* (Laila Maidan, 18 August 2021), with a second reading by Prof. Biljana Adebambo:

- Statements from **August 2006**, starting balance **$84,000**.
- **77%** average annual compounded return, 2006–2020, against **7.6%** for the S&P 500 in the same window.
- More than **$21 million** by May 2020, including withdrawals; **$42 million** cumulative profits by May 2021.
- Portfolio volatility almost **five times** an S&P 500 ETF; options were a likely ingredient.
- Later headline totals ($70 million, $80 million) and single-trade P&Ls are **self-reported** unless we say otherwise. The popular "$20,000 to $2 million" origin is a sleeve (or at least not Schwager's starting balance). Details: [`research/01-track-record.md`](research/01-track-record.md).

## Strategy essence

Social arbitrage is **information-gap investing**. Observe a real change in culture, consumption, technology, or policy — often on the ground or in unpolished social conversation — connect it to a public company large enough for the change to *matter* and early enough that the Street has not priced it, and exit as the fact reaches earnings, notes, and the tape. Camillo ignores charts and traditional fundamentals (except size), does not use stop-losses, sizes by conviction (he has said 2–30%), often uses **options** for leverage inside a separate "big money" account, and scales out as information reaches parity. The edge is **being early**, not being clever on the same model as everyone else. Full playbook: [`research/02-methodology-and-playbook.md`](research/02-methodology-and-playbook.md).

## Repository map

```
research/     Cited notes, bilingual core-logic companion, dimensions, Street-view write-up, thesis templates
data/         trades.json, provenance.csv, platform_status.json, experiment results, live samples
toolkit/      Scanner, street_view, multi-platform signals, event study, pytest
docs/         GitHub Pages site (core-logic, trades, dimensions, street-view, original pages)
DISCLAIMER.md Not financial advice; verification policy
```

## Divergence scanner

```bash
cd toolkit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m camillo_tracker scan CROX LULU ELF NWL TPR --out examples/sample_run.json
```

The scanner (a) pulls Yahoo Finance recommendations, price targets, upgrades/downgrades and headlines via yfinance; (b) scores the text with VADER (optional FinBERT); (c) pulls Google Trends via pytrends and Reddit via public JSON (optional X); (d) emits a divergence score that flags names where **niche momentum is rising while analyst sentiment is flat or negative**. That flag is a prompt for human work, not a trade. See [`toolkit/README.md`](toolkit/README.md) and [`research/04-wall-street-lag.md`](research/04-wall-street-lag.md).

## What we could not verify

Pabst Blue Ribbon and Vegas Golden Knights stories: **no source** linking them to Camillo. GameStop as a *prediction* from YouTube titles alone: **insufficient**. A self-reported personal GME trade ($70 → $300–340) and an AMC trade appear in the Stansberry Investor Hour ep. 192 transcript and are logged as self-reported in [`data/trades.json`](data/trades.json). The 2014 accountant's PDF: cited by Wikipedia, **not retrieved**. Lifetime totals beyond the May 2021 Schwager update: **self-reported**. See the [sources and gaps log](research/05-sources.md).



## 核心投资逻辑 (bilingual column)

A dedicated, Chinese-first column distills the method into a reusable playbook: first principles, a decision tree, a signal rubric, materiality and priced-in tests, an exit checklist, risk rules for a *normal* investor (do not copy 2–30% sizing or the COVID put book), five sourced case studies, and pitfalls.

**https://macapex.github.io/chris-camillo-tracker/core-logic.html**

Companion note: [`research/06-core-logic-playbook.md`](research/06-core-logic-playbook.md). Templates: [`research/templates/`](research/templates/).

## Trade database

[`data/trades.json`](data/trades.json) — 43 sourced records (including two explicit rejections: Pabst and the Vegas Golden Knights), each with date precision, ticker status, thesis, instrument, outcome, source, and a verification level. Site table: [交易库](https://macapex.github.io/chris-camillo-tracker/trades.html).

## Street-view framework and event study

`camillo_tracker.street_view` builds a Street Consensus Profile (ratings, targets, revisions, recency, news, coverage, surprises) and a conservative priced-in verdict. An event study on 10 dated calls reports *market-path* forward 1/3/6-month returns — not Camillo's P&L — and honestly refuses historical niche/Street quadrants where free Trends history does not reach. Results and charts: [街景](https://macapex.github.io/chris-camillo-tracker/street-view.html). Pytest: 11 passed, 13 Nov 2026.

```bash
cd toolkit
python -m camillo_tracker street ELF
python experiments/run_event_study.py
python -m pytest -q
```

## Multi-platform signals and provenance

Adapters in `camillo_tracker.signals` (Wikipedia, Google Trends, Google News, GDELT, YouTube via yt-dlp metadata, iTunes, optional official X with `CCT_X_BEARER`). Corroboration requires two rising z-scores versus each platform's own baseline; missing platforms are listed, never imputed.

On 13 Nov 2026 (Asia/Shanghai) we actually ran Scrapling, instaloader, twscrape (skipped — no logins), yt-dlp, and the official X counts API. Per-platform status (worked / partial / blocked, with reasons) is in [`data/platform_status.json`](data/platform_status.json); every numeric point is in [`data/provenance.csv`](data/provenance.csv). Reddit and Instagram hashtag counts were blocked without credentials, which we will not use. TikTok pages returned HTTP 200 but no trusted view count was parsed — we did not estimate one.

Env vars, documented in [`toolkit/README.md`](toolkit/README.md): `CCT_X_BEARER`, `CCT_USE_FINBERT`, `YOUTUBE_API_KEY` (optional).

## More dimensions

Sizing, options, timing, idea flow, losses, failure regimes, ethos 2006–present, the Dumb Money team, and comparisons with Peter Lynch, alt-data firms, and the academic literature (Da, Engelberg & Gao 2011; Hong & Kubik; McNichols & O’Brien, and others): [维度](https://macapex.github.io/chris-camillo-tracker/dimensions.html), [`research/07-dimensions.md`](research/07-dimensions.md).

## License and use

Research and education only. Quoted passages are brief and attributed. Please do not treat this archive as a product, a signal service, or a substitute for *Laughing at Wall Street* or *Unknown Market Wizards*.
