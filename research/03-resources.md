# Resources for studying and approximating social arbitrage

*URLs were verified on 13 November 2026 (Asia/Shanghai) with the GitHub API (`gh api repos/...`). Star counts are snapshots as of that check and will move. A 404 is noted. This is a toolbox, not a Camillo replica, and not financial advice.*

Camillo's method is discretionary: a human notices a meaningful change, tests whether it can move a company's needle, and acts before the fact is priced in. No repository backtests *that* judgment. What exists, and is useful, are tools for the **inputs** he uses — search interest, social conversation, financial sentiment, sell-side consensus, and options research — plus a few academic papers that justify taking those inputs seriously.

## A. Google Trends and search interest

Camillo has called Google Trends one of his favorite early-warning tools, and has said to expand the default 12-month view to a **five-year** chart so seasonal fads (Uggs every October) are not mistaken for a regime change (Business Insider, 18 August 2021). In 2025 he publicly warned that **AI-generated queries** may now pollute Trends (his Lululemon / "organic abercrombie socks" thread). Use these libraries with that caveat.

| Repository | Stars (13 Nov 2026) | Purpose | Notes |
| --- | --- | --- | --- |
| [GeneralMills/pytrends](https://github.com/GeneralMills/pytrends) | 3,730 | Unofficial Python "API" for Google Trends interest-over-time, related queries, and regional interest. | **Archived.** Still the most-cited library; urllib3 v2 removed `method_whitelist`, which this toolkit patches. Rate limits are common. |
| [akvise/trends-checker](https://github.com/akvise/trends-checker) | 404 | CLI on top of pytrends, with tighter rate-limit and cookie handling. | Actively maintained as of 2026. |
| [yiromo/pytrends-modern](https://github.com/yiromo/pytrends-modern) | 76 | A maintained Trends client claiming to merge pytrends and newer forks. | Useful if upstream pytrends stays archived. |
| [flack0x/trendspyg](https://github.com/flack0x/trendspyg) | 65 | Free, maintained Python library and CLI: trending-now, interest over time, related queries, interest by region. | Explicitly positioned as a modern pytrends alternative. |
| [mikedbjones/longtrends](https://github.com/mikedbjones/longtrends) | 16 | Download *long-term* Google Trends series (the 5-year-plus window Camillo prefers). | Last push 2023; small but on-point. |
| [Athe-kunal/Reinforcement-learning-trading-agent-using-Google-trends-data](https://github.com/Athe-kunal/Reinforcement-learning-trading-agent-using-Google-trends-data) | 44 | Research code using Trends features in a trading-agent experiment. | Academic / experimental, not a Camillo playbook. |
| [jugalm/Google-trends-stock-data](https://github.com/jugalm/Google-trends-stock-data) | 8 | Correlates Google search trends with trading volume. | Small illustrative notebook. |

**Academic companions (not GitHub, but essential):**

- Preis, Moat & Stanley, "Quantifying Trading Behavior in Financial Markets Using Google Trends," *Scientific Reports* 3, 1684 (2013). [nature.com/articles/srep01684](https://www.nature.com/articles/srep01684)
- Da, Engelberg & Gao, "In Search of Attention," *Journal of Finance* 66(5), 2011 — Google Search Volume Index and stock prices.

## B. Reddit, X, and social-sentiment pipelines

Camillo's conversational work is mostly **qualitative** (hours of TikTok comments, a baseline for what "normal" looks like). These repos quantify mention volume and polarity — a coarser, still useful screen.

| Repository | Stars (13 Nov 2026) | Purpose | Notes |
| --- | --- | --- | --- |
| [asad70/reddit-sentiment-analysis](https://github.com/asad70/reddit-sentiment-analysis) | 288 | Walks Reddit, finds the most-mentioned tickers, scores them with VADER. | The most-starred practical WSB-style pipeline we verified. |
| [asad70/wallstreetbets-sentiment-analysis](https://github.com/asad70/wallstreetbets-sentiment-analysis) | 149 | Same idea, focused on r/wallstreetbets. | Earlier, narrower sibling of the repo above. |
| [JustAnotherArchivist/snscrape](https://github.com/JustAnotherArchivist/snscrape) | 5,466 | Scrape posts from X/Twitter, Reddit, and other networks without an official API. | Often breaks when sites change; still the standard OSS scraper. Respect ToS and rate limits. |
| [dylee9/feels-trader](https://github.com/dylee9/feels-trader) | 10 | Sentiment-driven experiment using StockTwits, Twitter, and Reddit. | Small; useful as a design reference. |
| [junhuplim/Stocks-Sentiments](https://github.com/junhuplim/Stocks-Sentiments) | 16 | PRAW scrape + Wit.ai sentiment. | Requires Reddit API credentials. |

**Operational note (this box, 13 Nov 2026):** Reddit's unauthenticated JSON returned **HTTP 403** from the build environment (datacenter IP). PullPush, a Pushshift-style archive, was also down (HTTP 526). The scanner in this repo still implements the public-JSON path (and a PullPush fallback) so it will work from a residential network or with credentials. X is optional and requires `CCT_X_BEARER`.

TikTok comment scraping at the scale Camillo describes has **no high-quality, stable, officially blessed open-source library** that we could recommend. Repos named in passing (`gryphon-edm/Meme-Radar`, 1 star) are nascent. Treat TikTok as a **manual** research surface, which is how he uses it.

## C. Financial sentiment models

| Repository | Stars (13 Nov 2026) | Purpose | Notes |
| --- | --- | --- | --- |
| [cjhutto/vaderSentiment](https://github.com/cjhutto/vaderSentiment) | 5,096 | VADER: lexicon-and-rule sentiment, tuned for social media. | Default engine in this toolkit; light and dependency-friendly. |
| [nltk/nltk](https://github.com/nltk/nltk) | 14,770 | General NLP toolkit, including a VADER implementation. | Heavier than `vaderSentiment` alone. |
| [ProsusAI/finBERT](https://github.com/ProsusAI/finBERT) | 2,279 | BERT fine-tuned on financial phrasebank for positive / negative / neutral. | Optional in this toolkit via `CCT_USE_FINBERT=1`. Needs `transformers` and `torch`. |
| [huggingface/transformers](https://github.com/huggingface/transformers) | 168,908 | Model-definition framework; how you actually run FinBERT. | Infrastructure, not a trading idea. |

## D. Market data, analyst consensus, and research platforms

| Repository | Stars (13 Nov 2026) | Purpose | Notes |
| --- | --- | --- | --- |
| [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) | 25,900 | Unofficial Yahoo Finance client: prices, recommendations, price targets, upgrades/downgrades, news. | The analyst leg of this toolkit. Free, unofficial, can change without notice. |
| [OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) (listed by the API as [openbq-org/OpenBB](https://github.com/openbq-org/OpenBB) at check time) | 75,364 | Open data platform for analysts, quants, and agents, including alternative-data connectors. | Large surface; useful if you outgrow a single-script scanner. |

## E. Options research and backtesting

Camillo's audited returns almost certainly used options (Adebambo, in Business Insider, 2021; his own 2011 interview: leveraged options on "every" investment). These libraries help you **study** option structures. They do not encode his entries or exits.

| Repository | Stars (13 Nov 2026) | Purpose | Notes |
| --- | --- | --- | --- |
| [goldspanlabs/optopsy](https://github.com/goldspanlabs/optopsy) | 1,517 | A nimble Python library for options research and backtesting. | Focused and readable. |
| [Lumiwealth/lumibot](https://github.com/Lumiwealth/lumibot) | 2,229 | Broader Python trading framework: backtest, paper, and live, including options. | Heavy; includes live-trading hooks you may not want. |
| [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | 9,229 | Clean equity-strategy backtester. | Not options-native, excellent for studying simpler expressions of a thesis. |
| [sirnfs/OptionSuite](https://github.com/sirnfs/OptionSuite) | 304 | Option and stock backtester / live trader. | Verified to exist. |
| [philipodonnell/paperbroker](https://github.com/philipodonnell/paperbroker) | 282 | Simulated options brokerage for paper trading and backtests. | Last push 2018; archived in spirit if not in flag. |

A previously mentioned `OptionLab-Perg/OptionLab` URL returned **404** on 13 November 2026 and is **not** listed as a live resource.

## F. This repository's own toolkit

[toolkit/](../toolkit/README.md) is a small Python package that:

1. Pulls analyst consensus, targets, upgrades/downgrades, and headlines via yfinance.
2. Scores the text with VADER (optional FinBERT, lexicon fallback).
3. Pulls Google Trends via pytrends and Reddit via public JSON (optional X).
4. Emits a **divergence score** that flags tickers where social/search momentum is rising while the Street is flat or negative.

It is a **screen**, the beginning of Camillo's "does the Street already know?" test, not a substitute for channel checks, a needle test, or catalyst timing.

## G. Primary Camillo sources worth reading first

These are not code, but they are the highest-signal places to learn the method from him, not from a summary:

1. Laila Maidan, "Experts say Chris Camillo made $42 million…," *Business Insider*, 18 August 2021 — audited numbers, Dorel / RBI / Tapestry screenshots, exit rules, Google Trends advice.
2. Christopher Competiello, "Market wizard Chris Camillo grew his trading account by $9.7 million in 2020," *Business Insider*, 7 December 2020 — method statement, e.l.f. case, $9.7 million figure.
3. Zack Miller, Tearsheet / Tradestreaming Radio interview, 12 December 2011 — the clearest early statement of information arbitrage, the accountant-audit nuance, Target-Missoni, and the "big money" account.
4. Jack D. Schwager, *Unknown Market Wizards* (2020), chapter "Neither."
5. Chris Camillo, *Laughing at Wall Street* (St. Martin's Press, 2011).
6. CMC Markets / Opto Sessions, 1 September 2022 — slime / Newell Brands telling, 2018 Dumb Money origin.
7. Benzinga / Yahoo Finance, Chris Katje, 3 August 2022 — Crocs and HeyDude, "geographical arbitrage."
8. Camillo's August 2025 X thread on AI and Google Trends (Threadreader archive).

Full citations are in [05-sources.md](05-sources.md).
