"""One-shot evidence corrections. Public sources re-read 14 Nov 2026.

Does not invent observations. Rewrites claims the pages were still making.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BI_2021 = "https://www.businessinsider.com/stock-market-trading-strategies-social-arbitrage-chris-camillo-bets-picks-2021-8"
BI_2020 = "https://www.businessinsider.com/trading-strategy-market-wizard-chris-camillo-shares-secrets-to-millions-2020-12"
BROKEN = "https://www.businessinsider.com/chris-camillo-social-arbitrage-investing-strategy-ticker-tags-2021-8"
TEARSHEET = "https://tearsheet.co/podcasts/how-to-beat-wall-street-by-using-facebook-reading-tabloids-and-shopping-with-chris-camillo/"
THREAD = "https://threadreaderapp.com/thread/1957441296798298509.html"
STANS = "https://stansberryresearch.com/stansberry-investor-hour/episode-192-turning-20k-to-2-million-during-the-financial-crisis"
FOOL = "https://www.fool.com/investing/2019/04/03/analyst-optimism-sends-elf-beauty-over-14-higher-w.aspx"
ELF_PR = "https://investor.elfbeauty.com/stock-and-financial/press-releases/landing-news/2019/02-26-2019-073720920"
DOREL_PR = "https://www.dorel.com/blogs/news/dorel-reports-strong-second-quarter-revenue"
DOREL_CALL = "https://www.dorel.com/blogs/news/dorel-industries-will-hold-a-conference-call-to-discuss-its-second-quarter-results"
DOREL_DIV = "https://www.dorel.com/blogs/news/dorel-completes-sale-of-sports-segment-to-pon-holdings-for-us-810-million-and-declares-special-dividend-of-us-12-00-per-share"
TARGET = "https://corporate.target.com/press/release/2011/09/target-statement-regarding-missoni-for-target-orders-on-target-com"

ELF_EN = (
    "No single-number trading lead: the purchase day is unknown. "
    "15 Mar 2019 was only a mid-month placeholder (19 calendar days before 3 Apr) and is not execution evidence. "
    "In the 7 Dec 2020 Business Insider interview he recalled watching a Jeffree Star video in March 2019; "
    "that recollection is not a dated buy, and the video upload day was not independently sourced. "
    "The stored Google Trends point 2019-03-03 = 100 is a weekly bucket label inside a window pulled on 13 Nov 2026, "
    "not a first-signal timestamp, and this pass did not re-pull Trends. "
    "Calendar days from that label to 3 Apr 2019 are 31. That span is not his lead. "
    "Motley Fool (3 Apr 2019) reports a Jefferies upgrade that day by Stephanie Wissink with a $14 target. "
    "The original Jefferies note was not obtained. Yahoo also shows Hold to Buy and $10 to $14; those prior fields are Yahoo-only. "
    "The Fool article's reasons (activists, a new CFO, shelf space) are not the Jeffree Star observation, "
    "so the upgrade does not show the Street adopted his thesis. "
    "The issuer's 26 Feb 2019 release (fiscal 2018 net sales $267 million, down 1%) is prior context, not the social claim. "
    "A short-term search or video observation is not earnings, cash flow, or value."
)
ELF_ZH = (
    "没有单一数字的交易时差：买入日未知。2019 年 3 月 15 日只是月中占位（到 4 月 3 日相隔 19 个日历日），不是成交证据。"
    "2020 年 12 月 7 日《商业内幕》访谈里，他回忆 2019 年 3 月看过 Jeffree Star 的视频；这是事后回忆，不是有日期的买入，视频上传日也没有独立来源。"
    "库存的 Google Trends 点 2019-03-03 = 100 是 2026 年 11 月 13 日拉取窗口里的周桶标签，不是第一信号的时间戳，本次没有重拉 Trends。"
    "该标签到 2019 年 4 月 3 日是 31 个日历日，不是他的领先时间。"
    "Motley Fool（2019 年 4 月 3 日）记载当天 Jefferies 的 Stephanie Wissink 上调并给出 14 美元目标价。原始 Jefferies 报告没有取得。"
    "Yahoo 另有由持有到买入、目标价 10 到 14 美元；这两个「之前」字段只来自 Yahoo。"
    "Fool 文章里的理由（维权股东、新 CFO、货架）不是 Jeffree Star 观察，所以上调不能证明卖方采纳了他的论点。"
    "发行人 2019 年 2 月 26 日的财年业绩（净销售 2.67 亿美元，下降 1%）是此前的公司背景，不是这条社会观察。"
    "短期搜索或视频观察不是利润、现金流或价值。"
)
DOREL_EN = (
    "Not a Street-ignorance lead. Business Insider (18 Aug 2021) said screenshots showed a 24 Apr 2020 purchase at a nominal $1.56. "
    "The issuer dated the Q2 release 10 Aug 2020, after the close (call notice dated 4 Aug 2020 said the release would come the day before the 11 Aug call). "
    "24 Apr to 10 Aug is 108 calendar days: entry date to an earnings release, not a rating lag. "
    "Yahoo stamps the row 9 Aug 2020 (107 days). That is the vendor clock, not the issuer's. "
    "The release states adjusted diluted EPS of US$0.48 and reported diluted EPS of US$0.34. "
    "Yahoo Surprise(%) +340 uses estimate −0.20 and 0.48. The release does not publish that consensus, so +340% is not a confirmed beat and is not a stock return. "
    "The stored auto-adjusted close on 24 Apr 2020 is about $0.69. It is not comparable to $1.56 until adjustment factor, currency, security identity, and quote quality are reconciled. "
    "A later US$12 special dividend (issuer release 4 Jan 2022, payable 1 Feb 2022) can affect adjusted history; it is not a demonstrated explanation of this gap. "
    "Yahoo rating rows in the window are empty: insufficient evidence, not a silent Street. "
    "The adjusted-close event-study path is a different object from both the EPS line and the $1.56 to $11.38 path BI described."
)
DOREL_ZH = (
    "这不是「卖方无知」的时差。2021 年 8 月 18 日《商业内幕》称截图显示 2020 年 4 月 24 日以名义价格 1.56 美元买入。"
    "发行人把二季报日期写为 2020 年 8 月 10 日收盘后（8 月 4 日的电话会通知写明新闻稿在 8 月 11 日电话会的前一天发布）。"
    "4 月 24 日到 8 月 10 日是 108 个日历日：从有记录的买入日到财报发布，不是评级滞后。"
    "Yahoo 把该行标成 2020 年 8 月 9 日（107 日），那是供应商的时间戳，不是发行人的。"
    "新闻稿写明调整后稀释每股收益 0.48 美元，报告稀释每股收益 0.34 美元。"
    "Yahoo 的 Surprise(%) +340 用的是预期 −0.20 和 0.48。新闻稿没有公布这组一致预期，所以 +340% 不是已确认的超预期，也不是股价涨幅。"
    "库存的 2020 年 4 月 24 日自动复权收盘约 0.69 美元。在调整因子、货币、证券身份和报价质量对齐之前，不能与 1.56 美元直接比较。"
    "更晚的每股 12 美元特别股息（2022 年 1 月 4 日新闻稿，2022 年 2 月 1 日支付）可能影响复权历史；它没有被证明就是这个价差的原因。"
    "窗口内 Yahoo 评级为空：证据不足，不是「卖方沉默」。"
    "复权收盘的事件研究路径，与每股收益、以及 BI 描述的 1.56 到 11.38 美元路径，是三件不同的事。"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, obj, pretty=False):
    if pretty:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def lead_off(zh, en, measured=None):
    out = {
        "ok": False,
        "kind": None,
        "days": None,
        "from": None,
        "to": None,
        "zh": zh,
        "en": en,
        "trading_lead": "unavailable",
    }
    if measured:
        out["measured_not_a_lead"] = measured
    return out


def patch_chart(chart):
    by = {c["id"]: c for c in chart["cases"]}
    elf = by["elf-2019"]
    elf["entry"] = None
    elf["lead"] = lead_off(ELF_ZH, ELF_EN, {
        "placeholder_15_mar_to_3_apr_calendar_days": 19,
        "placeholder_is_execution": False,
        "trends_week_label": "2019-03-03",
        "trends_week_label_to_3_apr_calendar_days": 31,
        "week_label_is_first_signal": False,
        "trends_repulled_this_pass": False,
        "jefferies_note_obtained": False,
        "public_upgrade_date": "2019-04-03",
        "sources": [BI_2020, FOOL, ELF_PR],
    })
    es = elf["event_study"]["elf-2019"]
    es["display_returns"] = False
    es["anchor"] = "withdrawn_15_mar_placeholder"
    es["note"] = "Returns from 15 Mar 2019 are a placeholder path and are not shown as an entry study."
    elf["note"] = "March 2019 observation recalled in Dec 2020. Purchase day unavailable. No trading lead."
    for m in list(elf.get("markers") or []):
        if m.get("kind") == "entry":
            elf["markers"].remove(m)

    d = by["dorel-2020"]
    d["lead"] = lead_off(DOREL_ZH, DOREL_EN, {
        "purchase_date": "2020-04-24",
        "nominal_screenshot_px": 1.56,
        "issuer_release_date": "2020-08-10",
        "issuer_release_timing": "after_the_close",
        "calendar_days_entry_to_issuer_release": 108,
        "yahoo_row_date": "2020-08-09",
        "calendar_days_entry_to_yahoo_row": 107,
        "yahoo_row_is_not_the_lead": True,
        "adjusted_diluted_eps": 0.48,
        "reported_diluted_eps": 0.34,
        "yahoo_surprise_pct": 340.0,
        "yahoo_surprise_is_stock_return": False,
        "yahoo_surprise_consensus_in_release": False,
        "yfinance_adjusted_close_2020_04_24": 0.6869,
        "prices_directly_comparable": False,
        "special_dividend_usd": 12.0,
        "special_dividend_explains_gap": False,
    })
    d["note"] = "Dated purchase screenshots. Earnings release is 10 Aug 2020 after the close. 108 days is not a Street-rating lead."
    if "dorel-2020" in d.get("event_study", {}):
        d["event_study"]["dorel-2020"]["note"] = (
            "Auto-adjusted close path from the stored yfinance series. Not the BI nominal $1.56 path, not EPS surprise, not personal P&L."
        )
        d["event_study"]["dorel-2020"]["price_basis"] = "yfinance_auto_adjusted_not_comparable_to_nominal_1_56"

    lulu = by["lululemon-2025-exit"]
    lulu["exit"] = None
    lulu["entry"] = None
    lulu["role"] = "signal"
    lulu["side"] = "context"
    lulu["brand"] = "Lululemon as a Trends example"
    lulu["labels"] = {
        "zh": "Lululemon：搜索可靠性举例",
        "en": "Lululemon: search-reliability example",
        "short_zh": "LULU 信号",
        "short_en": "LULU signal",
    }
    lulu["note"] = (
        "The Threadreader mirror discusses implausible Lululemon product-term spikes versus other signals, "
        "and a hypothesis that external AI queries can leak into Trends. It discloses a short in GOOGL. "
        "It does not establish a Lululemon position or exit. AI contamination is his hypothesis, not a finding."
    )
    lulu["lead"] = lead_off(
        "没有交易时差。该帖讨论 Lululemon 产品词在 Trends 上的异常，并假设外部人工智能查询可能漏进 Trends；披露做空 GOOGL。帖子没有建立 Lululemon 的持仓或退出。人工智能污染只是假设。",
        "No trading lead. The thread discusses odd Lululemon product-term Trends readings and hypothesizes that external AI queries can leak into Trends. It discloses a short in GOOGL. It does not establish a Lululemon position or exit. AI contamination is a hypothesis only.",
    )
    lulu["markers"] = [m for m in (lulu.get("markers") or []) if m.get("kind") not in {"entry", "exit"}]
    if "lululemon-2025-exit" in (lulu.get("event_study") or {}):
        lulu["event_study"]["lululemon-2025-exit"]["display_returns"] = False
        lulu["event_study"]["lululemon-2025-exit"]["note"] = "No documented exit date, so no exit-anchored path is shown."

    tap = by["tapestry-2021"]
    tap["entry"] = {
        "date": "2021-08-18",
        "precision": "mention",
        "label": "Publication date of the 18 Aug 2021 BI article. Not a trade. 15 Aug is that article's Playa year-to-date cutoff.",
    }
    tap["markers"] = [{
        "kind": "mention",
        "date": "2021-08-18",
        "precision": "mention",
        "label": "Publication date, not a trade",
    }]
    tap["note"] = "Publication-anchored only. $3.1 million is a screenshot-viewed position size, not a closed P&L and not an entry date."
    tap["lead"] = lead_off(
        "没有进场时差。2021 年 8 月 18 日是《商业内幕》的发表日，不是成交日。8 月 15 日是同一篇文章里 Playa 年初至当日内的截止日期，不能挪来当作 TPR 的交易日。310 万美元是记者看过的持仓规模，不是已平仓盈亏。",
        "No entry lead. 18 Aug 2021 is the Business Insider publication date, not a fill. 15 Aug is that article's year-to-date cutoff for Playa, not a TPR trade date. $3.1 million is a position size a journalist viewed, not a closed P&L.",
    )
    tpr = tap["event_study"]["tpr-2021-mention"]
    tpr["display_returns"] = True
    tpr["anchor"] = "publication_2021-08-18_not_a_trade"
    tpr["note"] = "Equity path from the first session on the 18 Aug 2021 publication date. Not an entry study. Recomputed 14 Nov 2026 from Yahoo adjusted closes."
    tpr["returns"] = {
        "1m": {"ok": True, "start_date": "2021-08-18", "end_date": "2021-09-17", "start_px": 36.2817, "end_px": 35.573, "pct": -1.95},
        "3m": {"ok": True, "start_date": "2021-08-18", "end_date": "2021-11-16", "start_px": 36.2817, "end_px": 40.1429, "pct": 10.64},
        "6m": {"ok": True, "start_date": "2021-08-18", "end_date": "2022-02-16", "start_px": 36.2817, "end_px": 36.273, "pct": -0.02},
    }
    tpr["direction"] = {"1m": -1.95, "3m": 10.64, "6m": -0.02}
    tpr["retrieved_at_utc"] = "2026-11-14T15:30:00Z"
    tpr["source"] = "Yahoo chart adjusted close, public, unauthenticated. 21/63/126 sessions after 2021-08-18."

    for cid in ("covid-spy-2020", "covid-wynn-2020"):
        c = by[cid]
        c["entry"] = None
        c["exit"] = None
        c["markers"] = [m for m in (c.get("markers") or []) if m.get("kind") not in {"entry", "exit"}]
        c["note"] = (
            "February 2020 recollection of translating Chinese newspapers and blogs, then puts and outright SPY shorts "
            "(Wynn puts also named on the Stansberry transcript). Seven figures in a week around early March is self-reported "
            "and is not a verified complete exit. Equity path is not put or short P&L. No placeholder day is drawn."
        )
        c["lead"] = lead_off(
            "没有进出场时差。Stansberry 第 192 期里他说的是翻译中文报纸和博客，然后买看跌期权并直接做空 SPY（也提到 Wynn 的看跌期权）。三月初一周七位数是自述，没有核实为完整平仓。不画占位日。股价路径不是期权或做空损益。",
            "No entry or exit lead. On Stansberry episode 192 he described translating Chinese newspapers and blogs, then puts and outright SPY shorts (Wynn puts are also named). Seven figures in a week around early March is self-reported and is not a verified complete exit. No placeholder day is drawn. The equity path is not options or short P&L.",
        )

    rbi = by["rbi-2019"]
    if rbi.get("entry"):
        rbi["entry"]["label"] = "April 2019 month window. The 15th is a placeholder, not the screenshot day."
    if rbi.get("entry2"):
        rbi["entry2"]["label"] = "August 2019 month window. The 15th is a placeholder, not the screenshot day."
    rbi["note"] = (
        "18 Aug 2021 BI: he was betting on the Impossible Whopper and the Popeyes sandwich; "
        "Tim Hortons had one of its worst quarters and he called that an oversight. Not a Tim Hortons turnaround thesis. "
        "April and August 2019 purchases, screenshots viewed. About $750k loss is self-reported."
    )
    rbi["lead"] = lead_off(
        "没有领先时差。论点是 Impossible Whopper 和 Popeyes 三明治，被 Tim Hortons 的疲弱抵消，不是 Tim Hortons 翻盘赌注。4 月与 8 月的「15 日」是月中占位，不是截图上的成交日。约 75 万美元亏损是自述。",
        "No lead. The thesis was the Impossible Whopper and the Popeyes sandwich, offset by Tim Hortons weakness, not a Tim Hortons turnaround. The 15ths are month placeholders, not screenshot days. The roughly $750k loss is self-reported.",
    )

    chart["policy"] = (
        "Real historical series only. Missing series are omitted, never interpolated. "
        "A single-number Camillo trading lead is published only when the execution day and the later event are both dated. "
        "Month placeholders, weekly Trends labels, earnings-release intervals, and publication dates are not trading leads. "
        "Yahoo empty is insufficient evidence, not a silent Street. "
        "A short-term social observation is not earnings, cash flow, or value. "
        "Look-ahead: these cases were chosen after the stories were told. Peaks inside a full custom window are retrospective. "
        "Survivorship: undocumented and losing ideas are mostly absent. Selection: nine cases are the best-documented files, not the book."
    )
    chart["audit_note"] = {
        "reviewed": "2026-11-14",
        "elf_trading_lead": "unavailable",
        "dorel_issuer_span_days": 108,
        "dorel_surprise_340_status": "yahoo_vendor_statistic_not_in_issuer_release",
    }
    return chart


STAGES = {
    "elf-2019": [
        ("social_observation", "自述观察", "Self-reported observation", "2019 年 3 月看 Jeffree Star 视频并做渠道核查。来源是 2020-12-07 访谈中的回忆。", "March 2019 Jeffree Star viewing and channel checks, recalled in the 7 Dec 2020 interview."),
        ("verified_signal_timestamp", "未独立复核", "Not re-verified", "Trends 周标签 2019-03-03=100 来自 2026-11-13 的库存拉取。周起点不是可获得时间，也不是上传日。本次未重拉。", "Stored Trends week label 2019-03-03=100 from the 13 Nov 2026 pull. A week start is not availability and not an upload time. Not re-pulled."),
        ("documented_entry", "不可用", "Unavailable", "没有独立的成交日。3 月 15 日占位已撤下，不再画标记。", "No independent execution day. The 15 Mar placeholder is withdrawn and is not drawn."),
        ("first_street_response", "日期已核对，论点未核对", "Date checked, thesis not", "2019-04-03 Jefferies 上调，$14 目标价，见 Motley Fool。原始报告未取得。理由不是这条社会观察。", "3 Apr 2019 Jefferies upgrade, $14 target, in Motley Fool. Original note not obtained. The stated reasons are not this social observation."),
        ("earnings_confirmation", "不是事后确认", "Not a later confirmation", "发行人 2019-02-26 发布 2018 财年业绩，早于所述观察月。", "Issuer results on 26 Feb 2019 cover fiscal 2018 and predate the recalled observation month."),
        ("investment_outcome", "自述，非审计盈亏", "Self-reported, not audited P&L", "他说买入后六周股价涨超 50%。这不是已审计盈亏，也不是从占位日出发的路径。", "He said the stock rose more than 50% in the six weeks after his purchase. That is not an audited P&L and not a path from the placeholder."),
    ],
    "dorel-2020": [
        ("social_observation", "自述", "Self-reported", "居家对自行车和家居需求。2021-08-18 文章中的叙述。", "Stay-at-home demand for bikes and home goods, as told in the 18 Aug 2021 article."),
        ("verified_signal_timestamp", "不可用", "Unavailable", "没有与该论点匹配的、当时存档的需求序列。公司名 Trends 不是消费者需求。", "No archived demand series matched to the thesis. A company-name Trends line is not consumer demand."),
        ("documented_entry", "记者看过截图", "Screenshots viewed", "2020-04-24，名义价格 1.56 美元。不是平仓所得。", "24 Apr 2020 at a nominal $1.56. A purchase screenshot is not exit proceeds."),
        ("first_street_response", "证据不足", "Insufficient evidence", "窗口内 Yahoo 评级为空。空不是「没看见」或「未定价」。", "No Yahoo rating rows in the window. Empty is not 'unaware' or 'unpriced'."),
        ("earnings_confirmation", "发行人日期", "Issuer date", "2020-08-10 收盘后。调整后稀释 EPS 0.48 美元，报告稀释 EPS 0.34 美元。间隔 108 日，不是卖方评级滞后。", "10 Aug 2020 after the close. Adjusted diluted EPS US$0.48; reported diluted EPS US$0.34. 108 days is not a rating lag."),
        ("investment_outcome", "多套价格，勿混用", "Several prices; do not mix", "BI 描述 1.56 到 11.38 美元并称涨 629%，且他分批卖出。自述「大概 9 倍」。复权路径是另一序列。都不是已审计个人收益率。", "BI describes $1.56 to $11.38 (called 629%) with gradual selling. He said '9X I think.' The adjusted path is another series. None is an audited personal return."),
    ],
    "lululemon-2025-exit": [
        ("social_observation", "帖子里的例子", "Example in the thread", "Lululemon 产品词在夏季冲到假日级别，而刷卡、流量和到店只有温和改善。", "Lululemon product terms spiking to holiday levels while card, traffic, and store signals improved only modestly."),
        ("verified_signal_timestamp", "未重拉", "Not re-pulled", "本次没有重拉那些产品词的 Trends。", "Those product-term Trends series were not re-pulled for this pass."),
        ("documented_entry", "没有", "None", "帖子没有建立 Lululemon 持仓。", "The thread does not establish a Lululemon position."),
        ("first_street_response", "不适用", "Not applicable", "没有可核对的 Lululemon 交易论点。", "There is no Lululemon trade thesis to check against the Street."),
        ("earnings_confirmation", "不适用", "Not applicable", "搜索异常不是利润确认。", "A search anomaly is not an earnings confirmation."),
        ("investment_outcome", "没有 LULU 退出", "No LULU exit", "披露的是做空 GOOGL。人工智能污染是假设。来源不可靠意味着不确定和重新评估，不是自动判定公司论点为假。", "The disclosure is a GOOGL short. AI contamination is a hypothesis. An unreliable source means uncertainty and reassessment, not an automatic false business thesis."),
    ],
    "rbi-2019": [
        ("social_observation", "自述", "Self-reported", "Impossible Whopper 与 Popeyes 三明治。", "The Impossible Whopper and the Popeyes sandwich."),
        ("verified_signal_timestamp", "不可用", "Unavailable", "没有当时存档的产品序列。", "No contemporaneous archived product series."),
        ("documented_entry", "月份，截图被看过", "Month, screenshots viewed", "2019 年 4 月与 8 月。日未知。约 75 万美元亏损为自述。", "April and August 2019. Day unknown. The roughly $750k loss is self-reported."),
        ("first_street_response", "不是领先例子", "Not a lead example", "这是亏损反例：看不见的第三块业务（Tim Hortons）抵消了所看的产品。", "A losing counterexample: the unseen third business (Tim Hortons) offset the products he was watching."),
        ("earnings_confirmation", "公司侧的抵消", "Company-side offset", "他称 Tim Hortons 出现了历史上很差的季度之一。", "He said Tim Hortons had one of its worst quarters."),
        ("investment_outcome", "自述亏损", "Self-reported loss", "峰值 78.45 美元、到 2020 年 3 月约 −59% 是文章里的价格路径，不是精确个人盈亏。", "The $78.45 peak and about −59% by March 2020 are the article's price path, not his exact P&L."),
    ],
    "tapestry-2021": [
        ("social_observation", "自述", "Self-reported", "Coach 包的社交兴趣。", "Social interest in Coach bags."),
        ("verified_signal_timestamp", "不可用", "Unavailable", "文章没有给出可复核的信号时间戳。", "The article does not give a re-checkable signal timestamp."),
        ("documented_entry", "不是成交日", "Not a fill", "2021-08-18 是发表日。持仓规模 310 万美元，记者看过截图。", "18 Aug 2021 is the publication date. Position size $3.1 million; screenshots viewed."),
        ("first_street_response", "未作为进场研究", "Not an entry study", "发表日之后的股价路径已重算，并标明不是交易。", "The path after the publication date was recomputed and is labeled as not a trade."),
        ("earnings_confirmation", "不可用", "Unavailable", "文章没有把一季财报写成确认。", "The article does not treat one quarter as confirmation."),
        ("investment_outcome", "未平仓盈亏", "No closed P&L", "持仓规模不是退出所得。", "Position size is not exit proceeds."),
    ],
    "covid-spy-2020": [
        ("social_observation", "自述", "Self-reported", "用翻译读中文报纸和博客，不是学术论文。", "Chinese newspapers and blogs via translation, not academic papers."),
        ("verified_signal_timestamp", "不可用", "Unavailable", "那些中文原文没有作为序列存档。", "Those Chinese sources were not archived as a series."),
        ("documented_entry", "回忆中的二月", "February recollection", "他说在崩盘前约两周重仓做空并一度亏损。没有成交日。工具是看跌期权加上直接做空 SPY，以及 Wynn 看跌期权。", "He said he was short about two weeks before the crash and was losing at first. No fill date. Instruments: puts plus outright SPY shorts, and Wynn puts."),
        ("first_street_response", "不适用", "Not applicable", "这不是一条「领先卖方上调」的多头。", "This is not a long lead over a Street upgrade."),
        ("earnings_confirmation", "不适用", "Not applicable", "宏观崩盘不是单家公司的利润确认。", "A macro break is not one issuer's earnings confirmation."),
        ("investment_outcome", "自述，未核实平仓", "Self-reported, exit unverified", "三月初一周七位数。没有核实为完整退出。股价路径不是期权或做空损益。", "Seven figures in a week around early March. Not verified as a complete exit. The equity path is not options or short P&L."),
    ],
}


def stages_for(cid):
    rows = STAGES.get(cid)
    if not rows:
        return []
    return [
        {"id": a, "status_zh": b, "status_en": c, "zh": d, "en": e}
        for a, b, c, d, e in rows
    ]


def patch_trades(bundle):
    bundle["record_count_meaning"] = "research_records_not_verified_trades"
    bundle["compiled_at_asia_shanghai"] = "2026-11-14 audit pass, Asia/Shanghai"
    bundle["policy"] = (
        "43 research records, not 43 verified trades. The set includes excluded attributions, themes, "
        "misses, third-party mentions, and repeats. Do not compute a win rate, expected return, or strategy efficacy. "
        "Incomplete history cannot support those estimates. Personal P&L is self-reported unless a journalist viewed "
        "statements or screenshots, and a purchase screenshot is not exit proceeds. "
        "Schwager's review of monthly statements, as reported by Business Insider, is not a published audit of every trade "
        "or of later headline totals. This project did not audit the account."
    )
    by = {t["id"]: t for t in bundle["trades"]}

    def setr(i, **kw):
        by[i].update(kw)

    setr("snapple-puts-1980s",
         thesis="He noticed Snapple losing shelf space at a 7-Eleven (a favorite flavor gone; doors cut back) and, through his brother, bought puts on Snapple. Not a story of Snapple winning while he shorted a competitor.",
         thesis_zh="他注意到 7-Eleven 里 Snapple 货架在缩小（常喝的口味没有了，冰箱门被砍掉），并通过哥哥买入 Snapple 的看跌期权。不是「Snapple 在赢、他做空竞争对手」。",
         outcome="Personal recollection of about a 3x. The listed vehicle, the year, and the execution are unresolved. Not a verified trade.",
         outcome_zh="个人回忆大约 3 倍。上市工具、年份和成交都未解决。不是已核实交易。",
         instrument_zh="看跌期权（回忆）",
         source="Tearsheet / Tradestreaming, Zack Miller, 12 Dec 2011; same direction in Business Insider, 7 Dec 2020.",
         source_url=TEARSHEET,
         role="win",
         evidence={"identity": "snapple_named", "date": "late_1980s_unresolved", "instrument": "puts_recalled", "position": "not_verified", "closed_pnl": "self_reported_unverified", "review": "pages_reread_2026_11_14"})
    setr("target-missoni-2011",
         date="2011-09-13",
         date_precision="retail_event_not_execution",
         thesis="He recalled waiting in line, seeing a Missoni for Target sellout, and buying leveraged options that day, out the next morning. Target’s 16 Sep 2011 statement says the nationwide launch was 13 Sep 2011. The 7 Sep 2011 anchor is withdrawn. Executions and the option return are unverified.",
         thesis_zh="他回忆当天排队、看见 Missoni for Target 售罄，并买入杠杆期权，次日早上退出。Target 2011 年 9 月 16 日的声明称全国上市是 9 月 13 日。2011 年 9 月 7 日的锚点已撤回。成交和期权收益未核实。",
         outcome="Self-reported overnight double on options. Not verified. Any price path from 13 Sep is the equity path from the retail launch, not his option return.",
         outcome_zh="自述期权隔夜翻倍。未核实。从 9 月 13 日起的价格路径是零售上市日的股票路径，不是他的期权收益。",
         instrument_zh="期权（自述，未核实）",
         source_url=TEARSHEET,
         evidence={"identity": "target_named", "date": "retail_launch_13_sep_not_a_fill", "instrument": "options_unverified", "position": "not_verified", "closed_pnl": "self_reported_unverified", "review": "pages_reread_2026_11_14"})
    setr("elf-2019",
         thesis="In the 7 Dec 2020 interview he recalled a March 2019 Jeffree Star video and pharmacy sellouts, then a purchase. The purchase day is not in the interview. The video upload day is not independently dated.",
         thesis_zh="2020 年 12 月 7 日的访谈里，他回忆 2019 年 3 月的 Jeffree Star 视频和药店售罄，然后买入。访谈没有买入日。视频上传日没有独立日期。",
         outcome="He said the stock rose more than 50% in the six weeks after his initial purchase. Self-reported market path, not audited P&L. No single-number lead is published.",
         outcome_zh="他说首次买入后六周股价涨超 50%。这是自述的价格路径，不是已审计盈亏。不发布单一数字的领先时间。",
         instrument_zh="未说明",
         source="Business Insider, Christopher Competiello, 7 Dec 2020.",
         source_url=BI_2020,
         evidence={"identity": "elf_named", "date": "month_recollection_not_a_fill", "instrument": "unspecified", "position": "not_stated", "closed_pnl": "self_reported_path_not_pnl", "review": "pages_reread_2026_11_14"})
    setr("rbi-2019-apr",
         name="Restaurant Brands — April 2019",
         thesis="Impossible Whopper and Popeyes chicken sandwich, later offset by Tim Hortons weakness. Not a Tim Hortons turnaround bet. April 2019 purchase; day not published. Screenshots viewed by BI.",
         thesis_zh="Impossible Whopper 与 Popeyes 鸡肉三明治，后来被 Tim Hortons 的疲弱抵消。不是 Tim Hortons 翻盘赌注。2019 年 4 月买入；日未公布。BI 看过截图。",
         outcome="Part of a self-reported loss of about $750,000. Purchase screenshot is not exit proceeds.",
         outcome_zh="自述约 75 万美元亏损的一部分。买入截图不是退出所得。",
         instrument_zh="未说明",
         source="Business Insider, Laila Maidan, 18 Aug 2021.",
         source_url=BI_2021,
         evidence={"identity": "qsr_named", "date": "april_2019_day_unknown", "instrument": "unspecified", "position": "screenshots_viewed", "closed_pnl": "self_reported", "review": "pages_reread_2026_11_14"})
    setr("rbi-2019-aug",
         name="Restaurant Brands — August 2019",
         thesis="Second 2019 purchase, same Whopper / Popeyes thesis. August is the month BI reported; the day was not published.",
         thesis_zh="2019 年第二次买入，仍是 Whopper / Popeyes 论点。BI 报道的是 8 月；日未公布。",
         outcome="Folded into the same self-reported loss of about $750,000.",
         outcome_zh="并入同一笔自述的约 75 万美元亏损。",
         instrument_zh="未说明",
         source="Business Insider, Laila Maidan, 18 Aug 2021.",
         source_url=BI_2021)
    setr("covid-shorts-2020",
         thesis="He described translating Chinese newspapers and blogs in February 2020, not academic papers, then buying puts and shorting SPY outright, plus Wynn puts.",
         thesis_zh="他描述 2020 年 2 月翻译中文报纸和博客，不是学术论文，然后买入看跌期权并直接做空 SPY，外加 Wynn 的看跌期权。",
         outcome="Self-reported: losing at first, then seven figures in a week around early March. Not verified as a complete exit. Not put or short P&L on the equity path.",
         outcome_zh="自述：起初亏损，然后在三月初的一周赚到七位数。没有核实为完整平仓。股价路径不是期权或做空损益。",
         instrument_zh="看跌期权，以及直接做空 SPY（自述）",
         source="Stansberry Investor Hour episode 192 transcript page.",
         source_url=STANS,
         evidence={"identity": "spy_and_wynn_named", "date": "february_and_early_march_recollection", "instrument": "puts_and_outright_shorts", "position": "self_reported_size", "closed_pnl": "self_reported_not_a_verified_exit", "review": "transcript_page_reread_2026_11_14"})
    setr("dorel-2020",
         thesis="Stay-at-home demand for Dorel's bike and home lines, as told to Business Insider.",
         thesis_zh="向《商业内幕》讲述的、居家带来的 Dorel 自行车和家居需求。",
         outcome="BI: screenshots of a 24 Apr 2020 purchase at $1.56, gradual selling near $4.46 in June, and a November exit with the stock at $11.38, which the article calls a 629% rise. That is a described price path, not verified personal return and not the EPS figure. The stored adjusted close that day (~$0.69) is not directly comparable.",
         outcome_zh="BI：2020 年 4 月 24 日以 1.56 美元买入的截图，6 月在约 4.46 美元附近分批卖出，11 月退出时股价 11.38 美元，文章称之为上涨 629%。这是被描述的价格路径，不是已核实的个人收益率，也不是每股收益。当日库存复权收盘（约 0.69 美元）不能直接比较。",
         instrument_zh="股票（买入截图）",
         source="Business Insider, Laila Maidan, 18 Aug 2021. Issuer release 10 Aug 2020.",
         source_url=BI_2021,
         evidence={"identity": "dorel_named", "date": "2020-04-24_purchase", "instrument": "equity_screenshots", "position": "purchase_screenshots_viewed", "closed_pnl": "not_audited", "review": "pages_reread_2026_11_14"})
    setr("tapestry-2021",
         date="2021-08-18",
         date_precision="publication_not_trade",
         thesis="Coach / Tapestry social interest. The 18 Aug 2021 article is when BI reported a $3.1 million position. That date is not a fill. 15 Aug 2021 is the article's Playa year-to-date cutoff.",
         thesis_zh="Coach / Tapestry 的社交兴趣。2021 年 8 月 18 日的文章报道了 310 万美元持仓。该日不是成交日。2021 年 8 月 15 日是文章里 Playa 的年初至今截止日期。",
         outcome="Position size viewed by a journalist, not a closed P&L and not exit proceeds.",
         outcome_zh="记者看过的持仓规模，不是已平仓盈亏，也不是退出所得。",
         instrument_zh="股票（持仓截图）",
         source_url=BI_2021)
    setr("playa-2021",
         source_url=BI_2021,
         thesis_zh="海滩度假搜索升温后的 Playa 论点。文章给出的「年初至 8 月 15 日约涨 32%」是发表文中的市场截止日期，不是交易日。",
         outcome_zh="自述重仓。+32% 是到 2021 年 8 月 15 日的年初至今市场事实，不是他的已核实收益，也不是进场日。")
    setr("lululemon-2025-exit",
         name="Lululemon product terms (not a documented exit)",
         role="signal_note",
         date_precision="thread_not_a_trade_date",
         thesis="The thread uses Lululemon product terms as an example of Trends readings that do not match card, web, app, and store signals, and hypothesizes external AI query leakage. It does not say he held or exited Lululemon.",
         thesis_zh="该帖把 Lululemon 产品词当作 Trends 与刷卡、网页、应用和到店信号不符的例子，并假设外部人工智能查询漏进 Trends。帖子没有说他持有或退出 Lululemon。",
         outcome="No Lululemon position or exit is established. The disclosure in the thread is a short in GOOGL. AI contamination remains a hypothesis.",
         outcome_zh="没有建立 Lululemon 持仓或退出。帖子里的披露是做空 GOOGL。人工智能污染仍是假设。",
         instrument_zh="不适用",
         source_url=THREAD,
         verification="self_reported",
         evidence={"identity": "no_lulu_position", "date": "not_a_trade_date", "instrument": "none", "position": "not_established", "closed_pnl": "not_a_trade", "review": "thread_reread_2026_11_14"})
    setr("googl-short-2025",
         thesis="The same thread discloses: Short $GOOGL. It does not give size, entry, or exit.",
         thesis_zh="同一帖子披露：做空 GOOGL。没有规模、进场或退出。",
         outcome="Disclosed stance only. Not an audited position or P&L.",
         outcome_zh="只是披露的立场。不是已审计的持仓或盈亏。",
         instrument_zh="做空（仅披露）",
         source_url=THREAD,
         evidence={"identity": "googl_disclosed", "date": "thread_date_not_converted", "instrument": "short_disclosed", "position": "size_unknown", "closed_pnl": "not_stated", "review": "thread_reread_2026_11_14"})
    setr("hp-printers-2020",
         role="named_no_pnl",
         thesis="Work-from-home printer demand, named on Stansberry.",
         thesis_zh="在家办公的打印机需求，Stansberry 上点过名。",
         outcome="Named. No P&L evidence. Not a win.",
         outcome_zh="只是被点名。没有盈亏证据。不是一笔盈利记录。",
         instrument_zh="未说明")
    setr("logitech-webcams-2020",
         role="named_no_pnl",
         outcome="Named on Stansberry. No P&L evidence. Not graded as a win.",
         outcome_zh="Stansberry 上点过名。没有盈亏证据。不记为盈利。",
         thesis_zh="在家办公、网络摄像头短缺或需求。",
         instrument_zh="未说明")

    # Chinese for the remaining records. English thesis/outcome stay the archive notes.
    rest = {
        "uggs-book-era": ("UGG 靴子的文化采用早于卖方认识。", "自述的盈利例子。没有已审计盈亏。", "未说明（书中时代的股票或期权）"),
        "true-religion-book-era": ("高端牛仔的文化浪潮。", "自述的盈利例子。没有已审计盈亏。书中的营销数字（例如 1000 美元到 75 万美元）未经审计。", "未说明"),
        "nintendo-wii": ("Wii 的休闲玩家采用被相对索尼和微软低估。", "被描述为一笔大的盈利。我们取得的一手来源里没有盈亏数字。", "未说明"),
        "cerner-emr": ("电子病历采用浪潮。", "自述「我相信约 700%」，大约两年。未经审计，措辞有保留。", "未说明"),
        "chuggington-facebook": ("儿童节目在 Facebook 上出现意外热度。", "自述数月内约 50%。上市工具没有可靠识别。", "未说明"),
        "delcasse-medical-study": ("与一项医学研究有关的想法（有读者猜是 Dendreon；我们不这么定）。", "代码未证实。不要当成已核实的 Camillo 交易。", "未说明"),
        "silicon-image-hdmi": ("HDMI 采用。他后来把这笔当作个人偏见压过方法的例子。", "被描述为亏损和流程失败，不是信息本身的模型失败。", "未说明"),
        "jcrew-obama-miss": ("广为引用的营销故事（有时写成 186%）不是他的盈利。Tearsheet：他错过了。", "记为错过的机会，不是盈利交易。不要把 186% 写成他的收益。", "无"),
        "peloton-2020": ("居家健身硬件和软件。", "向 Stansberry 自述也许是一生最大的一笔：「400 万美元……相对小的投资。」未经审计。进场日不够精确。", "未说明"),
        "amazon-2020": ("电商加速。后来的评论描述一笔很大的亚马逊期权、做到财报。", "2020 年前后的访谈里点过名。1000 万美元期权数字是后来播客里的自述，不是已审计的平仓盈亏。", "股票，以及后来的期权（自述）"),
        "shopify-2020": ("封锁期间的 DTC / 电商基础设施。BI 引述一种看法：它本不该下跌。", "被点名；没有已审计的个人盈亏。", "未说明"),
        "outdoor-2020": ("新冠期间的户外需求。", "主题被点名；我们手头的来源没有把每个代码和盈亏写全。", "未说明"),
        "pets-2020-miss": ("他说自己错过了 6 到 7 个后来涨了 3 到 6 倍的宠物相关名字。", "错过的机会，自述。名字没有列出。", "无"),
        "election-biden-2020": ("围绕 2020 年美国大选的政策与文化定位。", "被点名；我们有的文字稿里没有代码表或盈亏。", "未说明"),
        "newell-slime": ("Elmer's 史莱姆热：一条产品线收入的大约 50%，公司的 1%–2%。这是他自己的物质性边界例子，他仍用杠杆做了。不是本项目的「1%–2% 通常不重要」规则。", "自述杠杆下「接近 200%」。CMC Markets 访谈，2022 年 9 月。未经审计。", "杠杆（自述）"),
        "crocs-multi-year": ("Crocs 的文化再加速，然后 HeyDude 作为「地理套利」。", "2021 年他说股票已经翻了三倍仍在加仓（自述立场；三倍是市场路径）。Benzinga 2022 年 8 月 3 日：仍持有。没有已审计的平仓盈亏。", "股票"),
        "gamestop-2021": ("他是在轧空期间买入，不是从 YouTube 标题「预测」出来的。Stansberry：大约 70 美元买入，一部分在大约 300–340 美元卖出。", "Stansberry 第 192 期自述。仅凭 YouTube 标题说他预测了轧空，证据更弱，这里不用。", "股票"),
        "amc-2021": ("相关的迷因轧空参与。", "自述约 30 万美元变成约 120–130 万美元，捐给一家儿科基金会。未经审计。", "股票"),
        "silver-2021": ("短暂参与 2021 年白银轧空。", "自述先赚 30 万美元，吐回一些后「略正」。", "未说明"),
        "aws-forums": ("开发者论坛的讨论意味着 AWS 需求强于共识。", "2026 年 VladTV 上的描述。日期含糊。未经审计。", "未说明，自述杠杆"),
        "salesforce-crm": ("销售论坛上的成交讨论。", "2026 年 VladTV。日期含糊。未经审计。", "杠杆，自述金额很大"),
        "beacon-roofing": ("用「屋顶维修」的 Google Trends 代理需求。", "自述例子。所用来源没有日期和盈亏。", "未说明"),
        "moissanite-2021": ("一个很小的莫桑石名字。他同时说过一般不投微型股——这是检验那条规则的例外。", "Stansberry 上提到。代码未点名。规模被说成很小。", "未说明"),
        "schwager-regret-calls": ("Schwager 记述他听了别人的意见、亏损砍掉三分之二的看涨期权，论点后来被验证。", "流程上的亏损。代码未点名。不要编一个代码。", "看涨期权"),
        "mattel-barbie-third-party": ("Chart Academy / Matt Ober 称为喜欢的例子。", "我们的来源里没有 Camillo 的一手盈亏。只是第三方提及。", "未说明"),
        "abercrombie-third-party": ("第三方喜欢的例子。", "没有一手盈亏。", "未说明"),
        "coors-seltzer-third-party": ("硬苏打浪潮，第三方提及。", "没有一手盈亏。", "未说明"),
        "funko-third-party": ("收藏品流行文化浪潮，第三方提及。", "没有一手盈亏。", "未说明"),
        "pabst-rejected": ("网上有时会归到他名下。我们没有找到把他和这件事连起来的来源。", "不收入这笔交易。", "无"),
        "vgk-rejected": ("网上有时会归到他名下。我们没有找到把他和这件事连起来的来源。", "不收入这笔交易。", "无"),
    }
    for i, (th, oc, ins) in rest.items():
        row = by[i]
        row["thesis_zh"] = th
        row["outcome_zh"] = oc
        row["instrument_zh"] = ins
        row.setdefault("evidence", {
            "identity": row.get("ticker_status") or "see_record",
            "date": row.get("date_precision"),
            "instrument": "see_text",
            "position": row.get("verification"),
            "closed_pnl": "not_graded_as_verified",
            "review": "archive_note_not_reread_this_pass",
        })
    # Ensure every row has Chinese thesis and outcome.
    missing = [t["id"] for t in bundle["trades"] if not t.get("thesis_zh") or not t.get("outcome_zh")]
    if missing:
        raise SystemExit(f"missing zh: {missing}")
    bundle["source_url_null_count"] = sum(1 for t in bundle["trades"] if not t.get("source_url"))
    bundle["n_records"] = len(bundle["trades"])
    return bundle


def patch_event_study(obj):
    by = {e["id"]: e for e in obj["events"]}
    m = by["tgt-missoni-2011"]
    m["date"] = "2011-09-13"
    m["precision"] = "retail_launch_not_execution"
    m["trading_start"] = "2011-09-13"
    m["note"] = (
        "Anchor is Target's stated nationwide launch, 13 Sep 2011, not a verified Camillo fill. "
        "The 7 Sep 2011 anchor is withdrawn. Equity path only. Option executions and the claimed overnight double are unverified. "
        "Recomputed 14 Nov 2026 from Yahoo adjusted closes, 21/63/126 sessions."
    )
    m["retrieved_at_utc"] = "2026-11-14T15:30:00Z"
    m["returns"] = {
        "1m": {"ok": True, "start_date": "2011-09-13", "end_date": "2011-10-12", "start_px": 32.7179, "end_px": 33.8738, "pct": 3.53},
        "3m": {"ok": True, "start_date": "2011-09-13", "end_date": "2011-12-12", "start_px": 32.7179, "end_px": 34.5314, "pct": 5.54},
        "6m": {"ok": True, "start_date": "2011-09-13", "end_date": "2012-03-14", "start_px": 32.7179, "end_px": 38.0622, "pct": 16.33},
    }
    m["return_in_direction_of_stated_side"] = {"1m": 3.53, "3m": 5.54, "6m": 16.33}
    m["withdrawn_anchor"] = {"date": "2011-09-07", "why": "Not in the Tearsheet transcript. Do not use."}

    t = by["tpr-2021-mention"]
    t["date"] = "2021-08-18"
    t["precision"] = "publication_not_trade"
    t["trading_start"] = "2021-08-18"
    t["note"] = (
        "18 Aug 2021 is the Business Insider publication timestamp, not a trade. "
        "15 Aug 2021 is the article's Playa year-to-date cutoff and is withdrawn as an anchor. "
        "Recomputed 14 Nov 2026. Not personal P&L."
    )
    t["retrieved_at_utc"] = "2026-11-14T15:30:00Z"
    t["returns"] = {
        "1m": {"ok": True, "start_date": "2021-08-18", "end_date": "2021-09-17", "start_px": 36.2817, "end_px": 35.573, "pct": -1.95},
        "3m": {"ok": True, "start_date": "2021-08-18", "end_date": "2021-11-16", "start_px": 36.2817, "end_px": 40.1429, "pct": 10.64},
        "6m": {"ok": True, "start_date": "2021-08-18", "end_date": "2022-02-16", "start_px": 36.2817, "end_px": 36.273, "pct": -0.02},
    }
    t["return_in_direction_of_stated_side"] = {"1m": -1.95, "3m": 10.64, "6m": -0.02}
    t["withdrawn_anchor"] = {"date": "2021-08-15", "why": "Playa YTD cutoff in the same article, not the publication time and not a TPR fill."}
    return obj


def patch_csv(path: Path):
    rows = list(csv.reader(path.open(encoding="utf-8")))
    header, body = rows[0], rows[1:]
    for row in body:
        if row[0] == "tgt-missoni-2011":
            row[2] = "2011-09-13"
            row[3] = "retail_launch_not_execution"
            row[5] = "2011-09-13"
            row[6] = "3.53"
            row[7] = "5.54"
            row[8] = "16.33"
            row[9] = "3.53"
            row[10] = "5.54"
            row[11] = "16.33"
            row[-1] = "Retail launch 13 Sep 2011, not a verified fill. Equity path recomputed 14 Nov 2026. Option return unverified. 7 Sep anchor withdrawn."
        if row[0] == "tpr-2021-mention":
            row[2] = "2021-08-18"
            row[3] = "publication_not_trade"
            row[5] = "2021-08-18"
            row[6] = "-1.95"
            row[7] = "10.64"
            row[8] = "-0.02"
            row[9] = "-1.95"
            row[10] = "10.64"
            row[11] = "-0.02"
            row[-1] = "Publication date 18 Aug 2021, not a trade. 15 Aug Playa cutoff withdrawn. Path recomputed 14 Nov 2026."
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows([header, *body])


def patch_corroboration(obj):
    """Drop the false (momentum-50)/10 z. Keep Wikipedia z as a stored statistic, not a fading claim."""
    for _t, block in obj["tickers"].items():
        corr = block.get("corroboration") or {}
        comps = []
        present = list(corr.get("platforms_present_no_z") or [])
        for comp in corr.get("components") or []:
            if comp.get("platform") == "google_trends":
                present.append({
                    "platform": "google_trends",
                    "status": "worked",
                    "reason": (
                        "momentum_0_100 is a 0–100 project index on normalized relative interest, "
                        "not a count flow and not a statistical z. "
                        "The old (index-50)/10 figure is withdrawn and is not a confirming score."
                    ),
                    "momentum_0_100": comp.get("momentum_0_100"),
                    "withdrawn_false_z": comp.get("z"),
                })
            else:
                comps.append(comp)
        wiki_z = next((c["z"] for c in comps if c["platform"] == "wikipedia"), None)
        rising = [c for c in comps if c.get("z") is not None and c["z"] > 0.5]
        corr["components"] = comps
        corr["platforms_present_no_z"] = present
        corr["platforms_used"] = [c["platform"] for c in comps]
        corr["n_confirming"] = len(rising)
        corr["corroborated"] = len(rising) >= corr.get("min_confirm", 2)
        corr["weighted_z"] = None if wiki_z is None else round(wiki_z, 3)
        corr["weighted_z_basis"] = "wikipedia_only_after_withdrawing_trends_index_inversion"
        corr["fading_claim"] = "not_supported"
        corr["fading_reason"] = "Last-day completeness was not archived with this sample, so a negative Wikipedia z is not a business-fading claim."
        block["corroboration"] = corr
    obj["summary"]["interpretation"] = (
        "No ticker has two real z-scores above +0.5. "
        "The previous line that ELF momentum 57.97 'clears +0.5' mixed a 0–100 index with a z threshold. "
        "(57.97-50)/10 = 0.797 is withdrawn; it is not the formula that produced 57.97. "
        "Wikipedia z figures remain descriptive. They are not a fading claim, because last-day completeness was not stored. "
        "TikTok totals and Amazon ranks stay outside the z. Two TikTok clients on the same payload are a retrieval check, not independent demand."
    )
    obj["summary"]["trends_false_z_withdrawn"] = True
    obj["audit"] = {"pass": "2026-11-14", "elf_momentum_index": 57.97, "withdrawn_false_z": 0.797}
    return obj


def patch_index(idx, chart):
    byc = {c["id"]: c for c in chart["cases"]}
    for row in idx["cases"]:
        src = byc[row["id"]]
        for key in ("lead", "entry", "exit", "note", "role", "labels", "side"):
            if key in src:
                row[key] = src[key]
    idx["audit_note"] = chart["audit_note"]
    return idx


def main():
    chart_path = ROOT / "docs/data/cases-charts.json"
    chart = patch_chart(load(chart_path))
    for c in chart["cases"]:
        if c["id"] in STAGES or c["id"] == "covid-wynn-2020":
            cid = "covid-spy-2020" if c["id"] == "covid-wynn-2020" else c["id"]
            c["stages"] = stages_for(cid)
            if c["id"] == "covid-wynn-2020":
                for s in c["stages"]:
                    if s["id"] == "documented_entry":
                        s["zh"] = "与 SPY 同一段回忆里的 Wynn 看跌期权。没有成交日，不画占位日。"
                        s["en"] = "Wynn puts named in the same recollection as the SPY shorts. No fill date, and no placeholder day is drawn."
    save(chart_path, chart, pretty=False)

    idx_path = ROOT / "data/cases/index.json"
    save(idx_path, patch_index(load(idx_path), chart), pretty=True)

    trades = patch_trades(load(ROOT / "data/trades.json"))
    text = json.dumps(trades, ensure_ascii=False, indent=2) + "\n"
    (ROOT / "data/trades.json").write_text(text, encoding="utf-8")
    (ROOT / "docs/data/trades.json").write_text(text, encoding="utf-8")

    for rel in ("docs/data/event_study.json", "data/experiments/event_study.json"):
        p = ROOT / rel
        save(p, patch_event_study(load(p)), pretty=True)
    for rel in ("docs/data/event_study.csv", "data/experiments/event_study.csv"):
        patch_csv(ROOT / rel)

    for rel in ("docs/data/corroboration_sample.json", "data/experiments/corroboration_sample.json"):
        p = ROOT / rel
        save(p, patch_corroboration(load(p)), pretty=True)

    # Header fields on the raw case files. Series stay untouched.
    replacements = {
        ROOT / "data/cases/lululemon-2025-exit.json": [
            ('"brand": "Lululemon 2025 exit"', '"brand": "Lululemon as a Trends example"'),
            ('''  "exit": {
    "date": "2025-08-15",
    "precision": "month",
    "label": "self-reported exit after concluding AI had corrupted Trends"
  },''', '  "exit": null,'),
            ('"side": "exit"', '"side": "context"'),
            ('"role": "exit"', '"role": "signal"'),
            ('"note": "This is a tool-failure / change-of-mind case, not a claim that he was ahead of the Street."',
             '"note": "Signal-reliability example only. The thread does not establish a Lululemon position or exit. AI contamination is a hypothesis."'),
        ],
        ROOT / "data/cases/tapestry-2021.json": [
            ('"date": "2021-08-15"', '"date": "2021-08-18"'),
            ('"label": "BI article mention of a $3.1M position \\u2014 NOT an entry date"',
             '"label": "18 Aug 2021 publication date, NOT a trade. 15 Aug is the Playa YTD cutoff."'),
        ],
        ROOT / "data/cases/covid-wynn-2020.json": [
            ('''  "entry": {
    "date": "2020-02-15",
    "precision": "month",
    "label": "documented window (mid-month placeholder)"
  },
  "exit": {
    "date": "2020-03-10",
    "precision": "month",
    "label": "early March 2020, self-reported"
  },''', '  "entry": null,\n  "exit": null,'),
        ],
        ROOT / "data/cases/covid-spy-2020.json": [
            ('''  "entry": {
    "date": "2020-02-15",
    "precision": "month",
    "label": "documented window (mid-month placeholder)"
  },
  "exit": {
    "date": "2020-03-10",
    "precision": "month",
    "label": "early March 2020, self-reported"
  },''', '  "entry": null,\n  "exit": null,'),
        ],
        ROOT / "data/cases/rbi-2019.json": [
            ('"label": "April purchase window"',
             '"label": "April 2019 month window. The 15th is a placeholder, not the screenshot day."'),
            ('"label": "August second purchase"',
             '"label": "August 2019 month window. The 15th is a placeholder, not the screenshot day."'),
        ],
        ROOT / "data/cases/elf-2019.json": [
            ('"label": "documented window (mid-month placeholder)"',
             '"label": "WITHDRAWN placeholder. Not an execution day and not a lead start."'),
            ('"note": "Jeffree Star / channel-check month, per BI. Entry is month-precision."',
             '"note": "March 2019 viewing is a Dec 2020 recollection. Purchase day unknown. Placeholder is not a lead."'),
        ],
    }
    for path, pairs in replacements.items():
        file_text = path.read_text(encoding="utf-8")
        for a, b in pairs:
            if a not in file_text:
                if b in file_text:
                    continue
                raise SystemExit(f"missing snippet in {path.name}: {a[:80]}")
            file_text = file_text.replace(a, b, 1)
        path.write_text(file_text, encoding="utf-8")

    # Dorel and LULU lead objects are unique enough to replace in full.
    dorel = (ROOT / "data/cases/dorel-2020.json").read_text(encoding="utf-8")
    start = dorel.index('  "lead": {')
    end = dorel.index('  "series_status":', start)
    new_lead = "  \"lead\": " + json.dumps(
        lead_off(DOREL_ZH, DOREL_EN), ensure_ascii=False, indent=2
    ).replace("\n", "\n  ")
    # indent the dumped object under two spaces — easier to drop a compact lead
    new_lead = "  \"lead\": " + json.dumps(lead_off(DOREL_ZH, DOREL_EN), ensure_ascii=False)
    (ROOT / "data/cases/dorel-2020.json").write_text(dorel[:start] + new_lead + ",\n" + dorel[end:], encoding="utf-8")

    print("source_url null", trades["source_url_null_count"], "of", trades["n_records"])
    print("ok")


if __name__ == "__main__":
    main()
