# 研究备忘 · Crocs（CROX）

- 生成时间（UTC）：2026-11-13T01:13:11Z
- 模式：offline-cache
- 维基条目：Crocs
- 关键词：Crocs

> Not financial advice. This is a research memo produced by Chris Camillo Tracker. It is not a trade, not affiliated with Camillo / Dumb Money / TickerTags, and it does not copy his 2–30% sizing or options book. Missing data is listed, never imputed. Lifetime totals are not momentum.

## 结论（不是交易指令）

**not_corroborated** — 未达到两平台上升门槛（或只有存量快照、没有 z）：不进入交易准备。继续观察或停下。

## 工作流关口

1. **交叉验证：** 未通过 — 0 platform(s) show a rise vs their own baseline; below the 2-platform confirmation threshold.
   - 确认平台数 n_confirming = 0
   - 加权 z = -1.136
   - 用于 z 的平台：wikipedia, google_trends
2. **物质性：** 人工关口。打开 10-K 分部说明。本命令不估计收入占比。
3. **卖方定价：** insufficient_data — Street profile not run (offline or error). insufficient_data — a stop, not a green light.

## 各平台（有来源，不填空）

- `tiktok`：**worked**  viewCount=35500544935  videoCount=1927145  (lifetime stock；无 z)  method=in-page fetch of public /api/challenge/detail/ after StealthyFetcher session on tiktok.com  url=https://www.tiktok.com/tag/crocs  at=2026-11-13T00:49:34Z
- `amazon_movers`：**worked**  best_rank=#1 #1 in Women's Shoes — Crocs Unisex-Adult Classic Clog, Clogs for Women and Men  (position；无 z)  method=Scrapling Fetcher of public Best Sellers pages; ranks from data-client-recs-list metadataMap.render.zg.rank; brand match on PRODUCT TITLE only (context matches discarded).  url=https://www.amazon.com/gp/bestsellers/fashion/679337011  at=2026-11-13T00:50:49Z
- `wikipedia`：**worked**  z=-1.6135535087083528  last_day=473  sum_13d=6417  method=Wikimedia REST API (cached series)  url=https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/
- `google_trends`：**worked**  momentum_0_100=43.1  method=pytrends, US, today 5-y — cached 13 Nov 2026 snapshot already on the site (offline mode does not refetch)  url=https://trends.google.com/trends/  at=2026-11-12T18:09:07Z

有结果但无 z 的平台（存量 / 单一名次，不编造动量）：
- tiktok: Lifetime cumulative counts (stock), not a 7-day flow. No z-score is computed from a single snapshot. TikTokApi hashtag.info() cross-checks the same challengeInfo on #crocs, #lululemon, #elfcosmetics.
- amazon_movers: A Best Sellers rank is a position on one public list at one moment, not a z-score vs a baseline. Lululemon, Coach, and Elmer's were not in the top 50 of the category pages we fetched. Movers & Shakers returned no data-client-recs-list via Fetcher.

缺失或被挡住的平台（不填空）：
- （无）

## 推荐的主路径（按本项目实测）

- **搜索兴趣**（worked）：Google Trends via pytrends (5-year US window, YoY)  — `python -m camillo_tracker signals CROX --keywords 'Crocs,Crocs shoes' --wiki Crocs`  [flow]
- **社交 · TikTok**（worked）：Public /api/challenge/detail/ (StealthyFetcher in-page fetch); prefer statsV2  — `CCT_LIVE_TIKTOK=1 python -m camillo_tracker signals CROX   # or use the verified cache by default`  [stock]
- **社交 · X**（worked）：Official X recent-search tweet counts (7-day)  — `CCT_X_BEARER=…  python -m camillo_tracker scan CROX   # or read data/x_counts_sample.json`  [flow]
- **社交 · YouTube**（worked）：yt-dlp metadata search, no download  — `yt-dlp 'ytsearch3:Crocs shoes' --dump-json --skip-download --no-warnings`  [stock]
- **社交 · Reddit**（blocked）：Not usable from this project’s datacenter IP. Recommended later: official Reddit API, or public JSON from a residential network.  — `# www.reddit.com/search.json — HTTP 403 from our probe; do not bypass`  [flow]
- **社交 · Instagram**（blocked）：Manual observation only. Automated hashtag counts were login_required.  — `# instaloader Hashtag.from_name without login → 403 login_required`  [unknown]
- **商业 · 亚马逊 BSR**（worked）：Public Best Sellers official data-client-recs-list zg.rank; title-only brand match  — `python -c "from camillo_tracker.amazon import fetch_bestsellers; print(fetch_bestsellers('https://www.amazon.com/gp/bestsellers/fashion/679337011'))"`  [position]
- **商业 · 应用商店**（worked）：Official iTunes Search API — presence only, not a live top-chart rank  — `python -c "from camillo_tracker.signals import itunes_search; print(itunes_search('Crocs'))"`  [presence]
- **注意力 · 维基百科**（worked）：Official Wikimedia REST pageviews API, identified User-Agent  — `python -m camillo_tracker signals ELF --wiki 'E.l.f.'`  [flow]
- **新闻**（worked）：Google News RSS item counts  — `python -c "from camillo_tracker.signals import google_news_rss; print(google_news_rss('Crocs'))"`  [flow]
- **卖方街景**（worked）：Street Consensus Profile via yfinance (ratings, targets, revisions, recency, headlines, coverage, surprises)  — `python -m camillo_tracker street ELF`  [level]

## 下一步（人工）

- 物质性：分部规模，能否推动利润。
- 若关口通过：用 `research/templates/thesis.md` 写论点与退出条件，再决定是否行动。
- 本备忘不是下单指令。

## English brief

Recommendation: **not_corroborated**. Corroborated=False, n_confirming=0, weighted_z=-1.136. Street verdict=insufficient_data. Lifetime totals and a single BSR are not z-scores. Nothing was imputed. Not financial advice.

