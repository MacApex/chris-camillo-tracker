"""Evidence-based data-acquisition workflow and research-report composer.

Catalog entries reflect what this project actually ran on 13 Nov 2026
(Asia/Shanghai): see data/platform_status.json and data/provenance.csv.
No daily snapshot routine is implied. A lifetime total or a single BSR
is a stock / a position, not a momentum z-score.

This is a research instrument, not financial advice.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .provenance import now_utc

# ---------------------------------------------------------------------------
# Ranked catalog — primary / fallback / cross-check, from live tests
# ---------------------------------------------------------------------------

CATALOG: dict[str, dict[str, Any]] = {
    "search_interest": {
        "label_zh": "搜索兴趣",
        "label_en": "Search interest",
        "primary": {
            "name": "Google Trends via pytrends (5-year US window, YoY)",
            "tool": "camillo_tracker.social.google_trends (pytrends)",
            "command": "python -m camillo_tracker signals CROX --keywords 'Crocs,Crocs shoes' --wiki Crocs",
        },
        "fallback": {
            "name": "Manual Google Trends UI, same 5-year window (do not use the default 12-month view)",
            "tool": "https://trends.google.com/trends/",
            "command": "(browser; no official free API)",
        },
        "cross_check": {
            "name": "Wikipedia daily pageviews z-score; a second Trends keyword; never news volume alone",
            "tool": "camillo_tracker.signals.wikipedia_pageviews",
            "command": "python -m camillo_tracker signals CROX --wiki Crocs",
        },
        "status": "worked",
        "reliability": "Worked 5/5 sample keywords on 13 Nov 2026. Unofficial; often rate-limited. A 2025 thread says Trends may be affected by automated queries; reliability unverified. That thread does not establish a Lululemon position or exit.",
        "cost": "free",
        "rate_limits": "pytrends 429s are common; back off and retry. No official quota.",
        "blockers": "Unofficial endpoint can change. A spike that contradicts clerks, card data, or other platforms is not a thesis.",
        "metric_kind": "flow",
        "metric_means": "Relative interest index 0–100 in the chosen window — a flow-like series, not an absolute query count.",
        "normalize": "Five-year window so seasonality (Uggs every October) is visible; year-over-year as Camillo described to BI (2021); z-score versus the series’ own history. Do not compare raw 0–100 across unrelated keywords.",
    },
    "social_tiktok": {
        "label_zh": "社交 · TikTok",
        "label_en": "Social · TikTok",
        "primary": {
            "name": "Public /api/challenge/detail/ (StealthyFetcher in-page fetch); prefer statsV2",
            "tool": "camillo_tracker.tiktok (Scrapling StealthyFetcher)",
            "command": "CCT_LIVE_TIKTOK=1 python -m camillo_tracker signals CROX   # or use the verified cache by default",
        },
        "fallback": {
            "name": "davidteather/TikTok-Api hashtag.info() (no login, Playwright session)",
            "tool": "TikTokApi (6,744 GitHub stars, 13 Nov 2026)",
            "command": "Python: TikTokApi() → hashtag('crocs').info()  # same challengeInfo shape",
        },
        "cross_check": {
            "name": "Run both official-shaped methods; Creative Center GetHashtagList only for the public US 7-day top 3 (not brand analytics without login)",
            "tool": "camillo_tracker.tiktok.parse_creative_center_list",
            "command": "# cached in data/tiktok/sample_hashtag_counts.json",
        },
        "status": "worked",
        "reliability": "Exact statsV2 for 14 sample hashtags on 13 Nov 2026; TikTokApi cross-checked three preferred tags. Fetcher-only __UNIVERSAL_DATA__ was a bot-shell (blocked). hashtagradar is one site under two hostnames and must not override official counts. Prefer specific tags (#coachbag, not #coach).",
        "cost": "free (public pages; no login)",
        "rate_limits": "Be gentle with Chromium sessions; do not hammer challenge/detail.",
        "blockers": "Creative Center brand analytics appear to need a login (we did not log in). Public list capped at totalCount=3. No Max credentials.",
        "metric_kind": "stock",
        "metric_means": "Lifetime cumulative views and video counts — a stock, not a 7-day flow. A single snapshot is not a momentum z-score.",
        "normalize": "To get a flow, take repeated snapshots at a cadence *you* choose (this project does not run a daily routine) and difference them. Use specific hashtags; flag noisy generic words. Prefer statsV2 exact strings over rounded stats.",
    },
    "social_x": {
        "label_zh": "社交 · X",
        "label_en": "Social · X",
        "primary": {
            "name": "Official X recent-search tweet counts (7-day)",
            "tool": "Grok Bot MCP get_posts_counts_recent, or social.x_mentions with CCT_X_BEARER",
            "command": "CCT_X_BEARER=…  python -m camillo_tracker scan CROX   # or read data/x_counts_sample.json",
        },
        "fallback": {
            "name": "None without credentials. twscrape was skipped — it needs user accounts; we will not log into Max’s.",
            "tool": "—",
            "command": "# do not pass personal cookies",
        },
        "cross_check": {
            "name": "Google Trends and Wikipedia (independent); inspect query cleanliness (ELF is noisy after $ is stripped)",
            "tool": "camillo_tracker.signals",
            "command": "python -m camillo_tracker signals ELF --keywords 'e.l.f.,elf cosmetics' --wiki 'E.l.f.'",
        },
        "status": "worked",
        "reliability": "Official 7-day counts worked via MCP on 13 Nov 2026 (Crocs 42,056; Lululemon 172,939; Coach bag 2,029). ELF 90,164 is a noisy query — do not treat it as a clean brand count.",
        "cost": "free with a bearer / MCP; otherwise skipped",
        "rate_limits": "Official recent-search window is 7 days; respect API quotas.",
        "blockers": "No bearer → adapter skipped. twscrape requires logins (policy: skip).",
        "metric_kind": "flow",
        "metric_means": "Tweet counts over a recent window — a short-horizon flow.",
        "normalize": "Clean queries (avoid ticker collisions). Compare versus a prior 7-day window if you have one; a single window is a level, not a z-score.",
    },
    "social_youtube": {
        "label_zh": "社交 · YouTube",
        "label_en": "Social · YouTube",
        "primary": {
            "name": "yt-dlp metadata search, no download",
            "tool": "yt-dlp",
            "command": "yt-dlp 'ytsearch3:Crocs shoes' --dump-json --skip-download --no-warnings",
        },
        "fallback": {
            "name": "Official YouTube Data API (optional key)",
            "tool": "YouTube Data API v3",
            "command": "# set YOUTUBE_API_KEY if you want the official path",
        },
        "cross_check": {
            "name": "Trends + Wikipedia; treat a few video view counts as presence, not a cultural z-score",
            "tool": "camillo_tracker.signals.youtube_search",
            "command": "python -m camillo_tracker signals CROX --keywords 'Crocs shoes'",
        },
        "status": "worked",
        "reliability": "3 public results for “Crocs shoes” on 13 Nov 2026 (metadata only). This is search presence plus per-video lifetime views, not a hashtag-style trend series.",
        "cost": "free (yt-dlp); official API has a free quota if keyed",
        "rate_limits": "yt-dlp can be blocked; official API has daily quotas.",
        "blockers": "No YOUTUBE_API_KEY in this environment (optional). Do not download videos.",
        "metric_kind": "stock",
        "metric_means": "Per-video view_count is a lifetime stock. A three-result search is presence, not a flow.",
        "normalize": "Prefer recent upload_date; do not sum a handful of viral videos into a brand z-score. For a flow, you would need a repeated search or the official API’s time-bounded statistics.",
    },
    "social_reddit": {
        "label_zh": "社交 · Reddit",
        "label_en": "Social · Reddit",
        "primary": {
            "name": "Not usable from this project’s datacenter IP. Recommended later: official Reddit API, or public JSON from a residential network.",
            "tool": "camillo_tracker.social (public JSON path exists; returned 403 here)",
            "command": "# www.reddit.com/search.json — HTTP 403 from our probe; do not bypass",
        },
        "fallback": {
            "name": "PullPush archive API — also failed here (HTTP 526)",
            "tool": "https://api.pullpush.io/",
            "command": "# blocked 13 Nov 2026",
        },
        "cross_check": {
            "name": "Do not invent a Reddit count. Use Trends / Wikipedia / X instead, and record Reddit as missing.",
            "tool": "corroborate() lists missing platforms; never imputes",
            "command": "python -m camillo_tracker signals CROX --wiki Crocs",
        },
        "status": "blocked",
        "reliability": "www 403, old.reddit 403, PullPush 526, Scrapling 403 — 13 Nov 2026. Datacenter IP is a known issue. Status is blocked, not “zero mentions.”",
        "cost": "public JSON is free when it works; official API may need a key",
        "rate_limits": "n/a until a path works",
        "blockers": "403/526. We will not use Max’s Reddit login.",
        "metric_kind": "flow",
        "metric_means": "When it works, recent-post counts are a flow. We have no verified Reddit numbers to report.",
        "normalize": "If a path opens, VADER on post text versus a prior window; still requires a second platform.",
    },
    "social_instagram": {
        "label_zh": "社交 · Instagram",
        "label_en": "Social · Instagram",
        "primary": {
            "name": "Manual observation only. Automated hashtag counts were login_required.",
            "tool": "—",
            "command": "# instaloader Hashtag.from_name without login → 403 login_required",
        },
        "fallback": {
            "name": "None without credentials. We will not log in.",
            "tool": "instaloader (attempted, blocked)",
            "command": "# skipped",
        },
        "cross_check": {
            "name": "TikTok specific hashtags + Amazon BSR + Trends",
            "tool": "camillo_tracker.tiktok / amazon / social",
            "command": "python -m camillo_tracker research Crocs CROX --wiki Crocs",
        },
        "status": "blocked",
        "reliability": "Scrapling 200 on a public URL, but instaloader returned login_required. No count was estimated.",
        "cost": "free only if public; we did not use a login",
        "rate_limits": "n/a",
        "blockers": "login_required. Policy: no Max credentials.",
        "metric_kind": "unknown",
        "metric_means": "No verified Instagram metric in this project.",
        "normalize": "Treat as a manual channel-check surface, same as talking to clerks — qualitative, not a z-score.",
    },
    "commerce_amazon": {
        "label_zh": "商业 · 亚马逊 BSR",
        "label_en": "Commerce · Amazon BSR",
        "primary": {
            "name": "Public Best Sellers official data-client-recs-list zg.rank; title-only brand match",
            "tool": "camillo_tracker.amazon (Scrapling Fetcher)",
            "command": "python -c \"from camillo_tracker.amazon import fetch_bestsellers; print(fetch_bestsellers('https://www.amazon.com/gp/bestsellers/fashion/679337011'))\"",
        },
        "fallback": {
            "name": "Public product-page Best Sellers Rank phrases (worked for 1 of 4 ASINs)",
            "tool": "camillo_tracker.amazon.parse_product_bsr",
            "command": "# Fetcher GET https://www.amazon.com/dp/ASIN",
        },
        "cross_check": {
            "name": "Same ASIN on two lists (Women’s Shoes vs department) and/or the product-page subcategory rank. Do not use CamelCamelCamel (Cloudflare 403, not bypassed) or a Keepa price chart as BSR.",
            "tool": "sample in data/amazon/sample_bsr.json",
            "command": "python -m camillo_tracker research Crocs CROX --offline",
        },
        "status": "worked",
        "reliability": "Official zg.rank worked 13 Nov 2026 (Crocs Classic Clog #1 Women’s Shoes / #12 Clothing; two e.l.f. items #23/#24 Beauty). Context-matching caused false positives — title-only is mandatory. Movers & Shakers had no recs JSON. Search HTTP 503.",
        "cost": "free (public pages)",
        "rate_limits": "Pause between Fetcher calls; Amazon may return empty 3781-byte shells.",
        "blockers": "CCC 403 Cloudflare (not bypassed). Keepa PNG is price, not BSR. Lululemon/Coach/Elmer’s absence from a top-50 is a fact, not an estimated rank.",
        "metric_kind": "position",
        "metric_means": "A Best Sellers rank is a position on one list at one moment (lower is stronger). It is not a unit-sales figure and not a z-score.",
        "normalize": "Compare the same ASIN on the same list over repeated snapshots (you choose the cadence; no daily routine here). Never average ranks across categories. Title-only brand match.",
    },
    "commerce_apps": {
        "label_zh": "商业 · 应用商店",
        "label_en": "Commerce · App stores",
        "primary": {
            "name": "Official iTunes Search API — presence only, not a live top-chart rank",
            "tool": "camillo_tracker.signals.itunes_search",
            "command": "python -c \"from camillo_tracker.signals import itunes_search; print(itunes_search('Crocs'))\"",
        },
        "fallback": {
            "name": "Manual App Store / Play Store browse (qualitative)",
            "tool": "—",
            "command": "# no public free live top-chart API was verified",
        },
        "cross_check": {
            "name": "Do not treat a search hit as demand. Optional paid chart vendors (Sensor Tower, data.ai) would upgrade this — not required.",
            "tool": "—",
            "command": "# optional, keyed, not used",
        },
        "status": "worked",
        "reliability": "iTunes Search worked 13 Nov 2026 and is honestly labelled presence, not a chart rank.",
        "cost": "free",
        "rate_limits": "Be polite; official public endpoint.",
        "blockers": "No live top-chart rank without a paid vendor.",
        "metric_kind": "presence",
        "metric_means": "A search hit means an app exists in the store, not that it is climbing a chart.",
        "normalize": "Do not convert presence into a z-score. If a paid chart API is added later, treat ranks like Amazon BSR (position, repeated snapshots).",
    },
    "attention_wikipedia": {
        "label_zh": "注意力 · 维基百科",
        "label_en": "Attention · Wikipedia",
        "primary": {
            "name": "Official Wikimedia REST pageviews API, identified User-Agent",
            "tool": "camillo_tracker.signals.wikipedia_pageviews",
            "command": "python -m camillo_tracker signals ELF --wiki 'E.l.f.'",
        },
        "fallback": {
            "name": "Same API, corrected article title (e.l.f._Cosmetics and Coach_(company) were thin or empty)",
            "tool": "Wikimedia REST",
            "command": "# ELF → E.l.f. ; TPR → 'Tapestry, Inc.'",
        },
        "cross_check": {
            "name": "Google Trends (independent official-ish series). Wikipedia is attention, not sentiment.",
            "tool": "pytrends",
            "command": "python -m camillo_tracker signals TPR --wiki 'Tapestry, Inc.' --keywords Tapestry,Coach",
        },
        "status": "worked",
        "reliability": "5/5 daily series on 13 Nov 2026 after title corrections. Stable official API.",
        "cost": "free",
        "rate_limits": "Identify yourself in the User-Agent (this toolkit does). Do not flood.",
        "blockers": "Wrong article title → empty or tiny series. That is a title error, not “no attention.”",
        "metric_kind": "flow",
        "metric_means": "Daily user pageviews — a flow of attention, not sentiment and not sales.",
        "normalize": "z-score of the last day versus the rest of the series; 13-day sums versus the prior 13. Always name the article title used.",
    },
    "news": {
        "label_zh": "新闻",
        "label_en": "News",
        "primary": {
            "name": "Google News RSS item counts",
            "tool": "camillo_tracker.signals.google_news_rss",
            "command": "python -c \"from camillo_tracker.signals import google_news_rss; print(google_news_rss('Crocs'))\"",
        },
        "fallback": {
            "name": "GDELT DOC API TimelineVol, with a ≥6 second pause (1 req / 5s guidance)",
            "tool": "camillo_tracker.signals.gdelt_timeline",
            "command": "python -c \"from camillo_tracker.signals import gdelt_timeline; print(gdelt_timeline('Crocs', pause=6))\"",
        },
        "cross_check": {
            "name": "Street news headlines via yfinance (street_view). In Camillo’s frame, mainstream news volume often LAGS the niche — use it as a “is it already public?” check, not as a leading signal.",
            "tool": "camillo_tracker.street_view",
            "command": "python -m camillo_tracker street CROX",
        },
        "status": "worked",
        "reliability": "Google News RSS 5/5 on 13 Nov 2026. GDELT first pass 429, then worked for “Crocs” after 6s (partial — not all tickers retried). “e.l.f.” rejected by GDELT as too short.",
        "cost": "free",
        "rate_limits": "GDELT: ≥5–6 seconds between calls.",
        "blockers": "Short or common queries. RSS item counts are not a quality-weighted sentiment series.",
        "metric_kind": "flow",
        "metric_means": "Headline volume over a window — usually a lagging public-attention trace.",
        "normalize": "Use as a priced-in / already-public check. A rising news count *against* a cold Street and a rising niche is different from news leading the idea. Do not treat raw RSS counts as a z without a baseline.",
    },
    "street": {
        "label_zh": "卖方街景",
        "label_en": "Street view",
        "primary": {
            "name": "Street Consensus Profile via yfinance (ratings, targets, revisions, recency, headlines, coverage, surprises)",
            "tool": "camillo_tracker.street_view.street_profile",
            "command": "python -m camillo_tracker street ELF",
        },
        "fallback": {
            "name": "Company IR / latest 10-K for segment size (materiality) — a 10-K is for the needle test, not a DCF",
            "tool": "SEC EDGAR (manual)",
            "command": "# open the 10-K segment note; do not invent a share of sales",
        },
        "cross_check": {
            "name": "Google News / GDELT for whether the fact is already in the press. Verdicts are conservative: missing components lower confidence, never fill numbers.",
            "tool": "priced_in_verdict",
            "command": "python -m camillo_tracker street CROX --out /tmp/street.json",
        },
        "status": "worked",
        "reliability": "yfinance is free and delayed; it is not a Bloomberg terminal. Labels, for one stated thesis: explicitly_reflected / partly_reflected / not_evidenced_in_reviewed_sources / insufficient_evidence. Silence is not 'unaware' or 'unpriced'.",
        "cost": "free (yfinance). Paid estimate vendors (FactSet, Bloomberg) would upgrade revision quality — optional, not required.",
        "rate_limits": "Yahoo may throttle; cache a profile rather than polling.",
        "blockers": "Thin coverage → insufficient_evidence. That is not a green light and not proof of an information gap.",
        "metric_kind": "level",
        "metric_means": "Consensus ratings, implied upside, revision direction — a snapshot of what the Street already has in the model.",
        "normalize": "Use the rule-based verdict; do not average a “buy” share with a niche z-score into one magic number. The workflow asks a yes/no: is it clearly priced?",
    },
}

# Project research order. These gates are this archive's conventions.
# They are not rules Camillo published, and they are not a validated model.
# Street work is auxiliary: it checks one thesis. It does not discover the name.
STEP_ORDER = [
    ("discover", "社会观察", "Start from a real-world or social observation, not from a Street screen. Log what was seen, where, and by whom."),
    ("evidence", "证据质量", "Separate self-report, journalist-viewed screenshot, and independent document. Record the timestamp class. A week label is not the moment the series became available."),
    ("corroborate", "独立交叉", "Project heuristic only: two platforms with a real z versus their own baseline. A Trends momentum index, a lifetime TikTok total, one Amazon rank, and a second client on the same TikTok payload do not count. Missing stays missing."),
    ("materiality", "收入桥", "Walk paying customers to units, net price, recognized revenue, incremental profit, offsets, tax and share count, then dated expectations. Unknowns stay unknown. No 1–2% cutoff."),
    ("falsify", "证伪", "Write the measurable prediction, the deadline, and the contrary evidence that would make you drop the claim. A dirty source means reassess, not an automatic false business."),
    ("horizon", "期限", "State the horizon before any action. A catalyst can be late. Timing alone is not causation."),
    ("risk_exit", "风险与退出", "Information parity is only one exit idea he has described. It does not replace liquidity, solvency, valuation, gap risk, correlation, or a portfolio limit. A lower price alone is not a reason to add. Options can expire worthless. No leverage by default."),
    ("street", "辅助卖方核对", "Ask whether THIS thesis is explicitly reflected, partly reflected, not evidenced in the rows reviewed, or insufficient. Do not screen the market by consensus. Do not read silence as ignorance."),
    ("decision", "人工关口", "A person decides. The memo is not a buy, a sell, or a position size."),
]


OPTIONAL_KEYS = [
    {
        "var": "CCT_X_BEARER",
        "upgrade": "Official X recent-search from the adapter itself, without depending on MCP.",
    },
    {
        "var": "YOUTUBE_API_KEY",
        "upgrade": "Official YouTube Data API (time-bounded stats) instead of a three-result yt-dlp search.",
    },
    {
        "var": "Keepa API key (paid, third-party)",
        "upgrade": "Historical BSR as a true flow. Public Keepa PNGs are price charts; we did not transcribe them and did not bypass anything.",
    },
    {
        "var": "Reddit official API",
        "upgrade": "Would reopen a blocked platform. Public JSON was 403 from our datacenter.",
    },
    {
        "var": "Sensor Tower / data.ai (paid)",
        "upgrade": "Live app-chart ranks. iTunes Search is presence only.",
    },
    {
        "var": "FactSet / Bloomberg (paid)",
        "upgrade": "Higher-quality estimate revisions for the Street profile. yfinance remains the default free path.",
    },
]


def catalog_entry(key: str) -> dict:
    return CATALOG[key]


def recommended_primary(key: str) -> str:
    return CATALOG[key]["primary"]["name"]


def _gate_corroboration(corr: dict) -> dict:
    ok = bool(corr.get("corroborated"))
    return {
        "gate": "corroborate",
        "passed": ok,
        "detail": corr.get("interpretation")
        or ("corroborated" if ok else "below the 2-platform rising-z threshold, or no z available"),
        "n_confirming": corr.get("n_confirming"),
        "weighted_z": corr.get("weighted_z"),
        "platforms_used": corr.get("platforms_used") or [],
        "platforms_present_no_z": corr.get("platforms_present_no_z") or [],
        "platforms_missing": corr.get("platforms_missing") or [],
    }


def _gate_street(profile: dict | None, niche_rising: bool | None) -> dict:
    """Auxiliary thesis check. `passed` is not a buy and not the discovery screen."""
    if not profile:
        return {
            "gate": "street",
            "role": "auxiliary_thesis_check",
            "passed": None,
            "detail": "Street profile not run. insufficient_evidence — not a green light and not proof of a gap.",
            "verdict": "insufficient_evidence",
        }
    v = profile.get("verdict") or {}
    label = v.get("label") or "insufficient_evidence"
    # None means "this check does not itself authorize work."
    # False means the reviewed rows already reflect a bullish version of the thesis.
    if label == "explicitly_reflected":
        passed = False
        detail = "Reviewed rows explicitly reflect a bullish version of this thesis. Not a trade instruction."
    elif label == "not_evidenced_in_reviewed_sources":
        passed = None
        detail = "Not evidenced in the rows reviewed. Silence is not proof the Street is unaware."
    else:
        passed = None
        detail = f"Auxiliary label {label}. niche_observation_rising={niche_rising}. Not a screen and not a buy."
    return {
        "gate": "street",
        "role": "auxiliary_thesis_check",
        "passed": passed,
        "verdict": label,
        "confidence": v.get("confidence"),
        "reasons": v.get("reasons") or [],
        "detail": detail,
    }


def _human_gate(name: str, detail: str) -> dict:
    return {"gate": name, "passed": None, "detail": detail, "convention": "project_not_camillo_rule"}


def compose_report(
    brand: str,
    ticker: str,
    *,
    platforms: dict | None = None,
    corroboration: dict | None = None,
    street: dict | None = None,
    wiki_article: str | None = None,
    keywords: list[str] | None = None,
    mode: str = "cache",
    retrieved_at_utc: str | None = None,
) -> dict:
    """Build a dated research report dict. Never invents a count or a z."""
    from .signals import corroborate

    platforms = platforms or {}
    corr = corroboration or corroborate(platforms)
    retrieved = retrieved_at_utc or now_utc()
    ticker = ticker.upper()
    niche_rising = bool(corr.get("corroborated"))
    g_corr = _gate_corroboration(corr)
    g_street = _gate_street(street, niche_rising if corr.get("ok") else None)

    g_mat = _human_gate(
        "materiality",
        "Human gate. Bridge: paying customers → units × net price → recognized revenue → "
        "incremental gross profit → opex and other offsets → tax and share count → EPS or cash flow → "
        "dated expectations → valuation and downside. Name the owner, channel, geography, sell-through "
        "versus stocking, supply, promotions, and other divisions. Unknowns stay unknown. "
        "No blanket 1–2% materiality cutoff.",
    )
    g_evidence = _human_gate(
        "evidence",
        "Separate social observation, verified signal timestamp, claimed trade, first public disclosure, "
        "and retrieval date. Week-start labels are not availability. Full-window peaks are look-ahead.",
    )
    g_falsify = _human_gate(
        "falsify",
        "Write a measurable prediction, a deadline, and contrary evidence. "
        "An unreliable source means uncertainty and a reassessment, not an automatic false business thesis.",
    )
    g_horizon = _human_gate(
        "horizon",
        "State the horizon. A late catalyst is not the same thing as a wrong observation.",
    )
    g_risk = _human_gate(
        "risk_exit",
        "Project convention, not a verified Camillo rule: information parity is only one exit criterion. "
        "Also write liquidity, solvency, valuation, gap risk, correlated exposures, portfolio-loss limit, "
        "and, if options are even discussed, expiry, implied volatility, and total premium loss. "
        "A lower price alone never warrants adding. Separate accounts do not remove household risk. "
        "1–3% is not a universal size. No leverage as an educational default.",
    )
    g_decision = _human_gate(
        "decision",
        "Human decision. This report never emits a buy, a sell, or a position.",
    )

    street_label = g_street.get("verdict")
    if not g_corr["passed"]:
        recommendation = "not_corroborated"
    elif street_label == "explicitly_reflected":
        recommendation = "corroborated_but_explicitly_reflected"
    elif street is None or street_label == "insufficient_evidence":
        recommendation = "corroborated_but_street_incomplete"
    elif street_label == "not_evidenced_in_reviewed_sources":
        recommendation = "candidate_for_human_work"
    else:
        recommendation = "stand_down_or_watch"

    report = {
        "title": f"Research report · {brand} ({ticker})",
        "brand": brand,
        "ticker": ticker,
        "wiki_article": wiki_article,
        "keywords": keywords or [brand],
        "retrieved_at_utc": retrieved,
        "mode": mode,
        "disclaimer": (
            "Not financial advice. This is a research memo produced by Chris Camillo Tracker. "
            "It is not a trade, not affiliated with Camillo / Dumb Money / TickerTags, "
            "and it does not copy his 2–30% sizing or options book. "
            "Missing data is listed, never imputed. Lifetime totals are not momentum."
        ),
        "workflow_steps": STEP_ORDER,
        "catalog_primary": {k: recommended_primary(k) for k in CATALOG},
        "platforms": platforms,
        "corroboration": corr,
        "street": {
            "verdict": (street or {}).get("verdict"),
            "how_it_feeds_the_tree": (street or {}).get("how_it_feeds_the_tree"),
            "ran": bool(street),
        } if street is not None or True else None,
        "gates": {
            "evidence": g_evidence,
            "corroborate": g_corr,
            "materiality": g_mat,
            "falsify": g_falsify,
            "horizon": g_horizon,
            "risk_exit": g_risk,
            "street": g_street,
            "decision": g_decision,
        },
        "signal_vs_value": (
            "A short-term social or search observation is not durable earnings, cash flow, or value. "
            "Those require the revenue bridge, a dated expectation, and an explicit horizon. "
            "This memo does not supply them."
        ),
        "recommendation": recommendation,
        "recommendation_zh": {
            "candidate_for_human_work": "社会观察已过本项目的交叉启发式，且已审阅的卖方材料未见该论点：只进入人工研究。不是买卖。短期社交信号不是利润或现金流。",
            "corroborated_but_explicitly_reflected": "社会观察有交叉，但已审阅材料已反映一个看多版本。信息差主张在这些材料里不成立。不是买卖。",
            "corroborated_but_street_incomplete": "社会观察已过交叉启发式，但卖方核对未完成。证据不足不是未被定价。不是买卖。",
            "not_corroborated": "未达到本项目的两平台 z 启发式（动量指数、终身播放、单一名次都不算）。不进入交易准备。",
            "stand_down_or_watch": "继续观察。没有通过的人工关口，也没有买卖指令。",
        }.get(recommendation, recommendation),
        "optional_keys": OPTIONAL_KEYS,
        "policy": {
            "no_daily_routine": True,
            "public_data_only": True,
            "no_imputation": True,
            "no_login": True,
        },
    }
    report["markdown"] = render_markdown(report)
    return report


def render_markdown(report: dict) -> str:
    """Chinese-first markdown, with an English brief at the end."""
    c = report.get("corroboration") or {}
    gates = report.get("gates") or {}
    lines = [
        f"# 研究备忘 · {report['brand']}（{report['ticker']}）",
        "",
        f"- 生成时间（UTC）：{report['retrieved_at_utc']}",
        f"- 模式：{report.get('mode')}",
        f"- 维基条目：{report.get('wiki_article') or '（未指定）'}",
        f"- 关键词：{', '.join(report.get('keywords') or [])}",
        "",
        f"> {report['disclaimer']}",
        "",
        "## 结论（不是交易指令）",
        "",
        f"**{report['recommendation']}** — {report.get('recommendation_zh')}",
        "",
        "## 工作流关口",
        "",
        f"短期社交或搜索信号不是可持续的利润、现金流或价值。收入桥、已标明日期的预期和明确期限都还空着。",
        "",
        f"1. **证据质量：** 人工 — {gates.get('evidence', {}).get('detail')}",
        f"2. **交叉验证（项目启发式，不是 Camillo 的规则，也不是已验证模型）：** {'通过' if gates.get('corroborate', {}).get('passed') else '未通过'} — {gates.get('corroborate', {}).get('detail')}",
        f"   - 确认平台数 n_confirming = {gates.get('corroborate', {}).get('n_confirming')}",
        f"   - 加权 z = {gates.get('corroborate', {}).get('weighted_z')}",
        f"   - 用于 z 的平台：{', '.join(gates.get('corroborate', {}).get('platforms_used') or []) or '无'}",
        f"3. **收入桥：** 人工 — {gates.get('materiality', {}).get('detail')}",
        f"4. **证伪：** 人工 — {gates.get('falsify', {}).get('detail')}",
        f"5. **期限：** 人工 — {gates.get('horizon', {}).get('detail')}",
        f"6. **风险与退出：** 人工 — {gates.get('risk_exit', {}).get('detail')}",
        f"7. **卖方核对（辅助，不是选股器）：** {(gates.get('street') or {}).get('verdict')} — {(gates.get('street') or {}).get('detail')}",
        f"8. **决定：** 人工 — {gates.get('decision', {}).get('detail')}",
        "",
        "## 各平台（有来源，不填空）",
        "",
    ]
    for name, res in (report.get("platforms") or {}).items():
        if not res:
            lines.append(f"- `{name}`：无结果对象")
            continue
        st = res.get("status") or ("worked" if res.get("ok") else "unknown")
        bits = [f"- `{name}`：**{st}**"]
        if res.get("viewCount") is not None:
            bits.append(f"viewCount={res.get('viewCount')}  videoCount={res.get('videoCount')}  (lifetime stock；无 z)")
        if res.get("best_rank") is not None:
            bits.append(f"best_rank=#{res.get('best_rank')} {res.get('headline') or ''}  (position；无 z)")
        if res.get("momentum_0_100") is not None:
            bits.append(f"momentum_0_100={res.get('momentum_0_100')}")
        if res.get("z_last_vs_history") is not None:
            bits.append(f"z={res.get('z_last_vs_history')}")
        if res.get("last_day") is not None:
            bits.append(f"last_day={res.get('last_day')}  sum_13d={res.get('sum_13d')}")
        if res.get("method"):
            bits.append(f"method={res.get('method')}")
        if res.get("source_url"):
            bits.append(f"url={res.get('source_url')}")
        if res.get("retrieved_at_utc"):
            bits.append(f"at={res.get('retrieved_at_utc')}")
        if res.get("reason"):
            bits.append(f"reason={res.get('reason')}")
        lines.append("  ".join(bits))
    present = c.get("platforms_present_no_z") or []
    missing = c.get("platforms_missing") or []
    lines += [
        "",
        "有结果但无 z 的平台（存量 / 单一名次，不编造动量）：",
    ]
    if present:
        for p in present:
            lines.append(f"- {p.get('platform')}: {p.get('reason') or p.get('headline') or 'no z'}")
    else:
        lines.append("- （无）")
    lines += ["", "缺失或被挡住的平台（不填空）："]
    if missing:
        for p in missing:
            lines.append(f"- {p.get('platform')}: {p.get('status')} — {p.get('reason')}")
    else:
        lines.append("- （无）")

    lines += [
        "",
        "## 推荐的主路径（按本项目实测）",
        "",
    ]
    for key, entry in CATALOG.items():
        lines.append(
            f"- **{entry['label_zh']}**（{entry['status']}）：{entry['primary']['name']}  "
            f"— `{entry['primary']['command']}`  "
            f"[{entry['metric_kind']}]"
        )

    lines += [
        "",
        "## 下一步（人工）",
        "",
        "- 把收入桥里未知的格子留空。",
        "- 写出可检验的预测、截止日期和相反证据。",
        "- 写出期限、流动性、偿债、估值、跳空、相关敞口和组合亏损上限。",
        "- 本备忘不是下单指令。信息平价不能代替上述风险。",
        "",
        "## English brief",
        "",
        f"Recommendation: **{report['recommendation']}**. "
        f"{report.get('signal_vs_value')} "
        f"Corroborated={c.get('corroborated')} (project heuristic, not a Camillo rule), "
        f"n_confirming={c.get('n_confirming')}, weighted_z={c.get('weighted_z')}. "
        f"Street verdict={(gates.get('street') or {}).get('verdict')} (auxiliary to this thesis; silence is not unawareness). "
        "A Trends momentum index, a lifetime total, and one Amazon rank are not z-scores. "
        "Nothing was imputed. Human gates for the revenue bridge, falsification, horizon, and risk are unfilled. "
        "Not financial advice.",
        "",
    ]
    return "\n".join(lines) + "\n"


def write_report(report: dict, out_dir: Path) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    day = (report.get("retrieved_at_utc") or now_utc())[:10]
    slug = f"{day}_{report['ticker']}_{_slug(report['brand'])}"
    md_path = out_dir / f"{slug}.md"
    js_path = out_dir / f"{slug}.json"
    md_path.write_text(report["markdown"], encoding="utf-8")
    payload = {k: v for k, v in report.items() if k != "markdown"}
    js_path.write_text(json.dumps(payload, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
    return {"markdown": str(md_path), "json": str(js_path), "slug": slug}


def run_research(
    brand: str,
    ticker: str,
    *,
    wiki: str | None = None,
    keywords: list[str] | None = None,
    out_dir: str | Path | None = None,
    offline: bool = False,
) -> dict:
    """Execute the workflow. `--offline` uses verified caches only (no new network)."""
    ticker = ticker.upper()
    kws = keywords or [brand]
    retrieved = now_utc()
    street = None
    platforms: dict[str, Any] = {}
    mode = "offline-cache" if offline else "live-degrade"

    if offline:
        from .tiktok import signal_for_ticker as tiktok_sig
        from .amazon import signal_for_ticker as amazon_sig
        from .signals import corroborate, _z

        platforms["tiktok"] = tiktok_sig(ticker)
        platforms["amazon_movers"] = amazon_sig(ticker)
        # Cached Wikipedia series if present
        wiki_path = _repo_root() / "data" / "wikipedia"
        article_file = {
            "CROX": "CROX.json",
            "LULU": "LULU.json",
            "ELF": "ELF_correct.json",
            "NWL": "NWL.json",
            "TPR": "TPR_tapestry.json",
        }.get(ticker)
        if article_file and (wiki_path / article_file).exists():
            data = json.loads((wiki_path / article_file).read_text(encoding="utf-8"))
            items = data.get("items") or []
            views = [int(i.get("views") or 0) for i in items]
            if views:
                platforms["wikipedia"] = {
                    "platform": "wikipedia",
                    "status": "worked",
                    "ok": True,
                    "last_day": views[-1],
                    "sum_13d": sum(views[-13:]),
                    "z_last_vs_history": _z(views[:-1], views[-1]),
                    "n_days": len(views),
                    "method": "Wikimedia REST API (cached series)",
                    "source_url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/",
                    "article": wiki or article_file,
                }
        # Trends momentum from the published 13 Nov 2026 snapshot (not a live pull)
        trends_mom = {"CROX": 43.1, "LULU": 35.56, "ELF": 57.97, "NWL": 40.16, "TPR": 54.37}
        if ticker in trends_mom:
            platforms["google_trends"] = {
                "platform": "google_trends",
                "status": "worked",
                "ok": True,
                "momentum_0_100": trends_mom[ticker],
                "method": "pytrends, US, today 5-y — cached 13 Nov 2026 snapshot already on the site (offline mode does not refetch)",
                "source_url": "https://trends.google.com/trends/",
                "retrieved_at_utc": "2026-11-12T18:09:07Z",
            }
        corr = corroborate(platforms)
        # Street is a live Yahoo pull — skip honestly in offline mode
        street = None
    else:
        from .signals import collect_signals
        from .street_view import street_profile

        bundle = collect_signals(ticker, keywords=kws, wiki_article=wiki)
        platforms = bundle.get("platforms") or {}
        corr = bundle.get("corroboration") or {}
        retrieved = bundle.get("retrieved_at_utc") or retrieved
        try:
            street = street_profile(ticker)
        except Exception as e:
            street = {"verdict": {"label": "insufficient_data", "reasons": [str(e)], "confidence": "low"}}

    report = compose_report(
        brand,
        ticker,
        platforms=platforms,
        corroboration=corr,
        street=street,
        wiki_article=wiki,
        keywords=kws,
        mode=mode,
        retrieved_at_utc=retrieved,
    )
    paths = None
    if out_dir:
        paths = write_report(report, Path(out_dir))
        report["written"] = paths
    return report


def _slug(s: str) -> str:
    out = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in (s or "").strip())
    return out.strip("-") or "brand"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]
