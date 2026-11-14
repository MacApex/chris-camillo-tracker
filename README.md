# Chris Camillo Tracker

A researched, cited archive of Chris Camillo's **social-arbitrage** investing — the independently reviewed track record, a bilingual core-logic playbook, a trade database, a Street-view “is it priced in?” framework with an honest event study, multi-platform signal adapters (with a provenance log), and a working Python **divergence scanner**.

**[Open the site](https://macapex.github.io/chris-camillo-tracker/)** · **[案例时间线](https://macapex.github.io/chris-camillo-tracker/cases.html)** · **[方法论总纲](https://macapex.github.io/chris-camillo-tracker/methodology.html)** · **[核心逻辑](https://macapex.github.io/chris-camillo-tracker/core-logic.html)** · Research notes in [`research/`](research/) · Toolkit in [`toolkit/`](toolkit/)

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
docs/         GitHub Pages site (cases timelines, methodology, core-logic, trades, street-view, …)
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

## Methodology synthesis and data-acquisition playbook

A tight, Chinese-first page states the method as a time gap (not a cheaper multiple), seven rules, when it works and fails, and what a normal investor should change. Below it is an evidence-based data-acquisition playbook from what we actually ran: primary, fallback and cross-check for each signal type, with exact tools, rate limits and metric meaning (stock versus flow). There is **no daily snapshot routine**.

**https://macapex.github.io/chris-camillo-tracker/methodology.html** (`#synthesis`, `#data-workflow`)

Companion: [`research/09-methodology-and-workflow.md`](research/09-methodology-and-workflow.md). Runner:

```bash
cd toolkit
python -m camillo_tracker research Crocs CROX --wiki Crocs --keywords Crocs --offline --out examples/reports
```

## Documented-case timelines

An interactive ECharts module aligns, for each best-documented case, (a) niche intensity — historical Google Trends with an **explicit custom timeframe**, Wikipedia pageviews from 2015, dated social evidence; (b) Camillo’s documented entry and exit; (c) Street upgrades, target moves and earnings dates from Yahoo; (d) the adjusted share price. A gold band marks **lead time** only when a real dated Street upgrade or earnings beat exists after a documented entry. Missing series are shown as missing, never interpolated. Yahoo empty is “unavailable,” not zero. Month-precision dates are labeled as placeholders. COVID equity paths are not put P&L. The Tapestry date is a BI mention, not an entry. RBI is the documented losing counterexample. The Lululemon 2025 case is a tool-failure exit, not a claim he was ahead of the Street.

Lead times we can actually support, retrieved 13 Nov 2026 (Asia/Shanghai):

- **ELF 2019:** no trading lead. The purchase day is unknown. 19 days was the gap from a withdrawn 15 Mar placeholder to 3 Apr. 31 days is the gap from a stored weekly Trends label (2019-03-03) to 3 Apr, not a first-signal time and not re-pulled this pass. Motley Fool confirms a Jefferies upgrade on 3 Apr 2019 with a $14 target. The original note was not obtained, and the article’s reasons are not the Jeffree Star recollection (Business Insider, 7 Dec 2020).
- **Dorel 2020:** 108 calendar days from the 24 Apr purchase screenshots to the issuer release dated 10 Aug 2020 after the close. That interval is not a Street-rating lag. Yahoo’s 9 Aug stamp (107 days) is the vendor clock. Adjusted diluted EPS in the release is US$0.48; reported diluted EPS is US$0.34. Yahoo’s +340% surprise is not in the release and is not a stock return. The adjusted close near $0.69 is not comparable to the nominal $1.56 until factor, currency, identity, and quote quality are reconciled. A later US$12 special dividend is a corporate event to examine, not a demonstrated explanation.

The other seven cases have lead time **unavailable**, with the reason on the page. Custom Trends windows **did** return real 2016–2020 series (Elmer’s slime peaked at 100 in the week of 28 May 2017). Wikipedia for ELF uses `E.l.f._Cosmetics` (the title `E.l.f.` was a 404). Chart data: [`docs/data/cases-charts.json`](docs/data/cases-charts.json). Raw: [`data/cases/`](data/cases/). Tests: `toolkit/tests/test_cases_data.py`.

**https://macapex.github.io/chris-camillo-tracker/cases.html**

## Language

The site has one global language switch at the far top-right of every page: pure Chinese or pure English, no side-by-side mode. Default is Chinese. The choice is stored in `localStorage` (`cct-lang`) and can be set with `?lang=zh` or `?lang=en`. Chart labels on the cases page follow the same switch. Technical names (tickers, commands, repo names) and the product name “Chris Camillo Tracker” may stay as they are.


## Trade database

[`data/trades.json`](data/trades.json) — 43 sourced records (including two explicit rejections: Pabst and the Vegas Golden Knights), each with date precision, ticker status, thesis, instrument, outcome, source, and a verification level. Site table: [交易库](https://macapex.github.io/chris-camillo-tracker/trades.html).

## Street-view framework and event study

`camillo_tracker.street_view` builds a Street Consensus Profile (ratings, targets, revisions, recency, news, coverage, surprises) and a conservative priced-in verdict. An event study on 10 dated calls reports *market-path* forward 1/3/6-month returns — not Camillo's P&L — and honestly refuses historical niche/Street quadrants where free Trends history does not reach. Results and charts: [街景](https://macapex.github.io/chris-camillo-tracker/street-view.html). Pytest: workflow and cases-data suites included; run `python -m pytest -q` from `toolkit/`. 13 Nov 2026.

```bash
cd toolkit
python -m camillo_tracker street ELF
python experiments/run_event_study.py
python -m pytest -q
```

## Multi-platform signals and provenance

Adapters in `camillo_tracker.signals`, `camillo_tracker.tiktok`, and `camillo_tracker.amazon` (Wikipedia, Google Trends, Google News, GDELT, YouTube via yt-dlp metadata, iTunes, optional official X with `CCT_X_BEARER`, TikTok public challenge/detail + Creative Center, Amazon public Best Sellers zg.rank). Corroboration requires two rising z-scores versus each platform's own baseline; missing platforms are listed, never imputed. A lifetime hashtag total or a single Amazon BSR is recorded as a fact and does **not** become a z-score.

On 13 Nov 2026 (Asia/Shanghai) we actually ran Scrapling (Fetcher and StealthyFetcher), instaloader, twscrape (skipped — no logins), yt-dlp, davidteather/TikTok-Api (no login), and the official X counts API. Per-platform and per-method status (worked / partial / blocked, with reasons) is in [`data/platform_status.json`](data/platform_status.json); every numeric point is in [`data/provenance.csv`](data/provenance.csv). Reddit and Instagram hashtag counts were blocked without credentials, which we will not use.

TikTok, same morning: public `/api/challenge/detail/` returned exact `statsV2` counts (e.g. #crocs 35,500,544,935 views / 1,927,145 videos), cross-checked by TikTokApi; Creative Center's public top-3 US 7-day list also worked but is capped at 3 without a login, which we will not use. Amazon: Crocs Classic Clog is #1 in Women's Shoes and #12 in Clothing, Shoes & Jewelry; e.l.f. products are #23 and #24 in Beauty. Lululemon, Coach, and Elmer's were not in the top 50 of the lists fetched — absence is recorded, not estimated. CamelCamelCamel was Cloudflare 403 (not bypassed). Full tables: [街景](https://macapex.github.io/chris-camillo-tracker/street-view.html).

Env vars, documented in [`toolkit/README.md`](toolkit/README.md): `CCT_X_BEARER`, `CCT_USE_FINBERT`, `YOUTUBE_API_KEY` (optional), `CCT_LIVE_TIKTOK`, `CCT_LIVE_AMAZON`.

## More dimensions

Sizing, options, timing, idea flow, losses, failure regimes, ethos 2006–present, the Dumb Money team, and comparisons with Peter Lynch, alt-data firms, and the academic literature (Da, Engelberg & Gao 2011; Hong & Kubik; McNichols & O’Brien, and others): [维度](https://macapex.github.io/chris-camillo-tracker/dimensions.html), [`research/07-dimensions.md`](research/07-dimensions.md).

## License and use

Research and education only. Quoted passages are brief and attributed. Please do not treat this archive as a product, a signal service, or a substitute for *Laughing at Wall Street* or *Unknown Market Wizards*.
