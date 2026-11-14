# 方法论总纲、数据工作流，与案例时间线

Companion to the site pages [方法论总纲](https://macapex.github.io/chris-camillo-tracker/methodology.html) and [知名案例时间线](https://macapex.github.io/chris-camillo-tracker/cases.html). Chinese first. Not financial advice; not affiliated with Camillo, Dumb Money, or TickerTags. Retrieved and written 13 November 2026, Asia/Shanghai.

## A. 方法论，六到八行

社会套利问的是**时差**，不是更便宜的估值。先在真实世界里看到相对于**自己基线**的异常（文化、消费、技术、政策），再把它连到一家变化大到能推动利润的上市公司，并用两到三个独立平台交叉确认——每个平台相对**自身历史**在上升。一条序列不是论点；终身播放量或单一畅销名次不是动量。然后把卖方材料当作辅助核对：须有注明日期的原文和对应的盈利假设，整体看多不等于写入该论点。无论读数如何，经济、估值和风险研究都继续，并事先写好退出：退出看的是**信息平价**（事实进入财报、研报和价格），以及论点是否被证伪。来源可靠性未经核实也要写下来（2025 年的帖子假设自动查询可能影响 Trends，并披露做空 GOOGL；没有建立 Lululemon 持仓或退出。这是假设，不是已确立的原因）。方法在消费品牌、能被普通人观察到的文化变迁上更说得通；在卖方已经覆盖、或信号无法连到利润的地方会失败。普通投资者不应复制他的 2%–30% 仓位、期权结构和无止损；审计业绩建立在高波动和一个可以承受损失的账户上。完整规则与工作流见站点总纲页，证据链到核心逻辑、手册和街景，本笔记不重复长文。

## B. 最佳数据获取工作流（按信号类型的首选）

Measured 13 Nov 2026. Rank is “what actually worked,” not a wish list. Missing platforms are listed, never imputed. There is **no daily snapshot routine**.

| 信号 | 首选（已跑通） | 退路 | 交叉 | 注意 |
|---|---|---|---|---|
| 搜索兴趣 | Google Trends via pytrends，**显式自定义时间窗** `"YYYY-MM-DD YYYY-MM-DD"`，美国 | 同一关键词、更短窗口；官方 Trends 页面（人工） | 维基浏览、商务排名 | 「today 5-y」从 2026 年 11 月只能到约 2021 年；自定义窗口在本次取数中**取到了 2016–2020 的真实序列**。0–100 是窗内相对值。2025 年的帖子假设自动查询可能影响 Trends，可靠性未经核实。urllib3 v2 需补丁去掉 `method_whitelist`。 |
| 社交 TikTok | 公开 `/api/challenge/detail/` 的 `statsV2`（精确字符串） | davidteather/TikTok-Api，无登录 | 第二个标签、YouTube | 终身播放是存量；要动量必须重复取样——本项目不做每日例行。宽泛标签不可用。Creative Center 未登录只有 3 条。 |
| 社交 X | 官方计数 API（已装连接器时） | 无登录不绕过 | — | 去掉 `$` 后 ELF 等代码会严重噪声。 |
| 社交 YouTube | yt-dlp 搜索元数据 | 官方 Data API（可选密钥） | — | 三次搜索，不是全量。 |
| 社交 Reddit | 公开 JSON（常 429） | 官方 API（可选） | — | 本次常被挡住。 |
| 社交 Instagram | 无登录则挡住 | — | — | 不使用个人登录。 |
| 商务 Amazon | 公开 Best Sellers `data-client-recs-list` 的 `metadataMap.render.zg.rank`，**只按标题匹配品牌** | Keepa 付费历史 BSR | 第二个类目 | 单一时刻的名次是存量。CCC 403，不绕过。 |
| 关注度 Wikipedia | Wikimedia REST 日浏览，2015 年起，需可识别 User-Agent | — | Trends | 条目标题要紧：ELF 用 `E.l.f._Cosmetics`（`E.l.f.` 返回 404）。新冠条目从 2020-03-12 才有数据，更早是缺失不是零。 |
| 新闻 | Google News RSS；GDELT（≥6 秒间隔） | — | — | 标题情绪不是论点。 |
| 卖方 | yfinance 评级、目标价、`upgrades_downgrades`、财报日 | 付费 FactSet / Bloomberg | 10-K 分部 | **历史不完整**；空不是「无活动」的证据。索引进先排序，不能对非单调索引直接切片。 |

端到端：发现 → 2–3 个平台交叉（各自相对自身基线上升）→ 物质性（人来判断）→ 卖方是否已定价 → 论点备忘。一条命令：

```bash
cd toolkit
python -m camillo_tracker research <brand> <ticker> [--wiki ARTICLE] [--keywords KW] [--offline] [--out DIR]
```

离线模式使用已缓存的公开数字，不编造 z 分数。物质性门永远是人工关（`passed: None`）。政策：无每日例行、只用公开数据、不插值、不登录。

## C. 知名案例时间线（真实数据）

Page: [cases.html](https://macapex.github.io/chris-camillo-tracker/cases.html). Chart payload: `docs/data/cases-charts.json`. Raw series: `data/cases/<id>.json`. Retrieved 13 Nov 2026, Asia/Shanghai.

交互图（ECharts）把四层对齐：（a）该时段 Google Trends 与维基浏览；（b）有记录的进出场标记；（c）Yahoo 评级/目标价与财报日；（d）复权股价。时差只在「有记录的进场 + 之后真实的评级上调或财报超预期」时计算，用金色色带标出。月精度会标明占位。缺失序列标为缺失，不插值。

| 案例 | Trends | 维基 | 股价 | 卖方 / 财报 | 时差 |
|---|---|---|---|---|---|
| ELF 2019 | 取到。「elf cosmetics」窗口峰值 **2019-03-03 = 100**。 | `E.l.f._Cosmetics` 取到（低流量）；另附 Jeffree Star 同期浏览（不是品牌条目，也不是视频上传日）。 | 取到 | 31 条评级，7 次财报。2 月 27 日卖方在下调目标。 | **约 19 日**（3 月月精度占位 15 日 → 4 月 3 日 Jefferies 持有→买入，目标 10→14）。从 Trends 峰值计 31 日。 |
| RBI 2019（反例） | 取到，「Tim Hortons」。 | `Restaurant_Brands_International` | 取到 | 56 条。1–3 月已有上调和开评。 | **不可用**（不是零）。卖方在 4 月买入窗口之前已经偏多。不把占位日后一天的 2 美元目标微调当成时差。 |
| COVID SPY 看跌 | 取到，「coronavirus」。1 月 19 日当周离开 0，3 月 15 日 = 100。 | `COVID-19_pandemic` 从 **2020-03-12** 开始，更早缺失。这是英文公开关注，不是他的中文一手来源。 | 取到（**不是期权损益**） | 无（ETF，404） | **不可用**。 |
| COVID WYNN 看跌 | 取到，「Wynn」。 | `Wynn_Resorts` | 取到（不是期权损益） | 29 条。1 月已有降级；3 月 30 日大幅下调目标已在自称的 3 月初退出之后。 | **不可用**。不把 2 月 20 日 3 美元微调报成 5 日时差。 |
| Dorel 2020 | 取到，「Dorel」（低搜索词，较跳）。 | `Dorel_Industries` | 取到。BI 名义价格 1.56 美元与复权收盘约 0.69 美元不能直接比较（调整因子、货币、证券身份、报价质量未对齐）。2022 年每股 12 美元特别股息只是待查的公司行为，不是已证明的解释。 | 窗口内评级 0 条：证据不足，不是沉默。发行人 2020-08-10 收盘后发布；调整后稀释 EPS 0.48 美元，报告稀释 EPS 0.34 美元。Yahoo 的 +340% 不在新闻稿里，也不是股价。 | **没有交易时差。** 4 月 24 日到发行人发布日是 108 个日历日，不是评级滞后。Yahoo 的 8 月 9 日戳记是 107 日，不是发行人的钟。 |
| Tapestry 2021 | 取到，「Coach bag」。 | `Tapestry,_Inc.` | 取到 | 82 条 | **不可用**。8 月 15 日是 BI 提及，不是建仓日。 |
| Newell / slime | 取到。「Elmer's slime」**2017-05-28 当周 = 100**（5 月中旬从接近 0 升起）。 | `Elmer's_Products` | 取到。窗口内股价整体下行，2017–18 有多次降级；不编造他的个人损益。 | 39 条 | **不可用**。只有「2017 年前后」，峰值只作背景。 |
| Crocs 多年 | 取到，「Crocs」。窗口峰值 2020-09-27 = 100。 | `Crocs`（与既有 hist 一致，n=1096） | 取到 | 28 条。2020 年 6–8 月已有上调。 | **不可用**。无核实建仓日；2022-08-03 是「仍在持有」（Benzinga），不是退出。无已审计平仓损益。 |
| Lululemon 2025 退出 | 取到，「Lululemon」（此窗在五年范围内）。 | `Lululemon` | 取到 | 241 条。**2025-06-09** 起已有降级，早于 8 月退出窗口。 | **不可用**。这是工具失效后的退出，不是领先卖方。 |

汇总图不再把 ELF 的 19 日或 Dorel 的 107 日画成交易时差。成交日未知或间隔不是卖方评级时，时差标为不可用。ELF 占位路径已撤回。TPR 与 Missoni 的股票路径已按发表日和零售上市日重算，都不是成交。短期社会信号不是利润或现金流。

出处写入 `data/provenance.csv` 与 `docs/data/provenance.csv`（追加，不覆盖既有 106 行）。断言见 `toolkit/tests/test_cases_data.py`（禁止把空评级当成 0 日时差，禁止把维基空档填零）。

## 站点语言

全站一个语言开关，在页眉最右侧：纯中文或纯英文，默认中文，`localStorage` 键 `cct-lang` 与 `?lang=`。案例页的图例、轴标签、时差说明随语言切换。技术名称（代码、命令、仓库名）可保留英文。产品名 “Chris Camillo Tracker” 可保留。
