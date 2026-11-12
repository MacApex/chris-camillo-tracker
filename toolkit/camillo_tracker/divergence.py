"""Cross-reference analyst consensus with niche/social momentum.

A high positive divergence flags tickers where social/niche momentum is
rising while sell-side sentiment is flat or negative — the information-
imbalance shape Chris Camillo describes. This is a heuristic screen, not
a trade signal and not a recreation of his judgment.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from .analyst import collect_analyst
from .sentiment import score_texts
from .social import google_trends, reddit_mentions, x_mentions


# Default keyword map so Trends queries use brand language, not just tickers.
# Callers can override via the keywords argument.
DEFAULT_KEYWORDS: dict[str, list[str]] = {
    "CROX": ["Crocs shoes", "Hey Dude shoes"],
    "LULU": ["Lululemon", "Lululemon bag"],
    "NWL": ["Elmer's glue", "Newell Brands"],
    "ELF": ["elf cosmetics", "elf primer"],
    "TPR": ["Coach bag", "Tapestry Coach"],
    "PLYA": ["Playa Hotels", "all inclusive Mexico"],
    "PTON": ["Peloton"],
    "DIIBF": ["Cannondale bike", "Schwinn bike"],
    "QSR": ["Burger King Impossible", "Popeyes sandwich"],
    "MAT": ["Barbie movie", "Mattel Barbie"],
    "AAPL": ["iPhone", "Apple iPhone"],
    "AMZN": ["Amazon Prime", "Amazon shopping"],
    "NKE": ["Nike sneakers"],
    "SBUX": ["Starbucks", "pumpkin spice latte"],
    "DECK": ["Ugg boots", "Ugg mini"],
}


def _analyst_sentiment_text(bundle: dict) -> dict:
    headlines = [n.get("title") or "" for n in bundle.get("news") or [] if n.get("title")]
    grades = []
    for rec in bundle.get("upgrades_downgrades") or []:
        firm = rec.get("Firm") or rec.get("firm") or ""
        action = rec.get("Action") or rec.get("action") or ""
        to = rec.get("ToGrade") or rec.get("To Grade") or rec.get("toGrade") or ""
        fr = rec.get("FromGrade") or rec.get("From Grade") or rec.get("fromGrade") or ""
        if action or to:
            grades.append(f"{firm} {action} {fr} to {to}".strip())
    texts = headlines + grades
    sent = score_texts(texts, source="analyst_news")
    return {
        "score": sent.score,
        "label": sent.label,
        "engine": sent.engine,
        "n_texts": sent.n_texts,
        "sample": sent.details[:8],
    }


def _composite_analyst(bundle: dict, text_sent: dict) -> dict:
    """0-100 analyst stance. High = Street is already constructive."""
    pieces = []
    weights = []
    bull = bundle.get("analyst_bullishness")
    if bull is not None:
        pieces.append(float(bull))
        weights.append(0.50)
    # Recent upgrade/downgrade balance: each net upgrade lifts the score
    bal = bundle.get("recent_action_balance")
    n = bundle.get("recent_action_n") or 0
    if n:
        # scale: +N all upgrades → toward 100; -N all downgrades → toward 0
        action_score = 50.0 + 50.0 * max(-1.0, min(1.0, (bal or 0) / max(3.0, n * 0.6)))
        pieces.append(action_score)
        weights.append(0.25)
    # Text sentiment
    if text_sent.get("n_texts"):
        pieces.append(50.0 + 50.0 * float(text_sent["score"]))
        weights.append(0.15)
    # Implied upside: already-high targets can mean the Street is on board
    up = bundle.get("implied_upside_pct")
    if isinstance(up, (int, float)):
        # 0% upside → 50; +40% → ~90; -20% → ~25
        pieces.append(max(0.0, min(100.0, 50.0 + up * 1.0)))
        weights.append(0.10)
    if not pieces:
        return {"score": None, "stance": "unknown", "components": {}}
    s = sum(p * w for p, w in zip(pieces, weights)) / sum(weights)
    s = round(max(0.0, min(100.0, s)), 2)
    if s >= 65:
        stance = "bullish"
    elif s <= 40:
        stance = "bearish"
    else:
        stance = "neutral"
    return {"score": s, "stance": stance, "components": {
        "consensus_bullishness": bull,
        "recent_actions": bal,
        "text_sentiment": text_sent.get("score"),
        "implied_upside_pct": up,
    }}


def _composite_social(trends: dict, reddit: dict, x: dict) -> dict:
    pieces = []
    weights = []
    notes = []
    if trends.get("ok") and trends.get("combined_momentum") is not None:
        pieces.append(float(trends["combined_momentum"]))
        weights.append(0.50)
    else:
        notes.append("Google Trends unavailable; social score leans on Reddit / X only.")
    if reddit.get("combined_0_100") is not None:
        pieces.append(float(reddit["combined_0_100"]))
        weights.append(0.40 if trends.get("ok") else 0.80)
    else:
        notes.append("Reddit unavailable or empty.")
    if x.get("ok") and x.get("sentiment"):
        pieces.append(50.0 + 50.0 * float(x["sentiment"]["score"]))
        weights.append(0.10)
    if not pieces:
        return {"score": None, "label": "unavailable", "notes": notes}
    s = sum(p * w for p, w in zip(pieces, weights)) / sum(weights)
    s = round(max(0.0, min(100.0, s)), 2)
    if s >= 62:
        label = "rising"
    elif s <= 42:
        label = "fading"
    else:
        label = "flat"
    return {"score": s, "label": label, "notes": notes}


def divergence_score(social: dict, analyst: dict) -> dict:
    """Positive = social leading a lukewarm Street (Camillo-shaped flag)."""
    ss, aa = social.get("score"), analyst.get("score")
    if ss is None or aa is None:
        return {
            "score": None,
            "flag": "insufficient_data",
            "interpretation": "Need both social and analyst legs to compute a divergence.",
        }
    raw = round(ss - aa, 2)
    # Flag only when social is actually rising and analysts are not already hot
    if raw >= 18 and ss >= 58 and aa <= 60:
        flag = "opportunity_flag"
        interp = (
            f"Social/niche momentum ({ss}) is running ahead of sell-side stance ({aa}). "
            "This is the shape of an information-imbalance screen — a prompt for "
            "human due diligence, not a recommendation to buy."
        )
    elif raw <= -18 and aa >= 60 and ss <= 50:
        flag = "late_or_crowded"
        interp = (
            f"Analysts are already constructive ({aa}) while social momentum is "
            f"softer ({ss}). The imbalance, if any, may already be closing."
        )
    elif abs(raw) < 10:
        flag = "aligned"
        interp = "Social and Street readings are roughly in line; no clear divergence."
    else:
        flag = "watch"
        interp = (
            f"Moderate gap (social {ss} vs analyst {aa}). Worth watching, not a flag."
        )
    return {"score": raw, "flag": flag, "interpretation": interp}


def scan_ticker(symbol: str, keywords: list[str] | None = None, company: str | None = None) -> dict:
    symbol = symbol.upper().strip()
    kws = keywords or DEFAULT_KEYWORDS.get(symbol) or [symbol]
    analyst = collect_analyst(symbol)
    text_sent = _analyst_sentiment_text(analyst)
    analyst_comp = _composite_analyst(analyst, text_sent)
    trends = google_trends(kws)
    reddit = reddit_mentions(symbol, company=company)
    x = x_mentions(symbol)
    social_comp = _composite_social(trends, reddit, x)
    div = divergence_score(social_comp, analyst_comp)
    return {
        "symbol": symbol,
        "keywords": kws,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "disclaimer": (
            "Not financial advice. Heuristic research screen inspired by "
            "Camillo's information-imbalance idea. Data comes from free, "
            "unofficial sources and can be incomplete, delayed, or wrong."
        ),
        "analyst": {
            "raw": {
                "recommendation_mean": analyst.get("recommendation_mean"),
                "analyst_bullishness": analyst.get("analyst_bullishness"),
                "recommendation_latest": analyst.get("recommendation_latest"),
                "price_targets": analyst.get("price_targets"),
                "implied_upside_pct": analyst.get("implied_upside_pct"),
                "last_close": analyst.get("last_close"),
                "recent_action_balance": analyst.get("recent_action_balance"),
                "recent_action_n": analyst.get("recent_action_n"),
                "upgrades_downgrades": (analyst.get("upgrades_downgrades") or [])[:8],
                "news": (analyst.get("news") or [])[:8],
                "warnings": analyst.get("warnings") or [],
            },
            "text_sentiment": text_sent,
            "composite": analyst_comp,
        },
        "social": {
            "trends": {
                "ok": trends.get("ok"),
                "error": trends.get("error"),
                "combined_momentum": trends.get("combined_momentum"),
                "momentum": trends.get("momentum"),
                "note": trends.get("note"),
                # Keep series compact for JSON
                "series_tail": {
                    k: v[-16:] for k, v in (trends.get("series") or {}).items()
                },
            },
            "reddit": {
                "ok": reddit.get("ok"),
                "n_posts": reddit.get("n_posts"),
                "sentiment": reddit.get("sentiment"),
                "volume_0_100": reddit.get("volume_0_100"),
                "combined_0_100": reddit.get("combined_0_100"),
                "errors": reddit.get("errors"),
                "sample_posts": (reddit.get("posts") or [])[:6],
            },
            "x": x,
            "composite": social_comp,
        },
        "divergence": div,
    }


def scan_many(symbols: list[str], keyword_map: dict[str, list[str]] | None = None) -> dict:
    rows = []
    for i, sym in enumerate(symbols):
        kws = None
        if keyword_map:
            kws = keyword_map.get(sym.upper()) or keyword_map.get(sym)
        try:
            rows.append(scan_ticker(sym, keywords=kws))
        except Exception as exc:
            rows.append({
                "symbol": sym.upper(),
                "error": str(exc),
                "divergence": {"score": None, "flag": "error", "interpretation": str(exc)},
            })
        if i < len(symbols) - 1:
            import time
            time.sleep(1.2)  # be polite to Yahoo / Google / Reddit
    flags = [r for r in rows if (r.get("divergence") or {}).get("flag") == "opportunity_flag"]
    return {
        "title": "Chris Camillo Tracker — divergence scan",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "disclaimer": (
            "NOT FINANCIAL ADVICE. This is a research screen that contrasts "
            "free sell-side consensus data with public social/search signals. "
            "It does not execute, recommend, or value any security. Camillo's "
            "edge is discretionary observation plus catalyst timing; a numeric "
            "score cannot substitute for that."
        ),
        "n": len(rows),
        "n_opportunity_flags": len(flags),
        "results": rows,
    }
