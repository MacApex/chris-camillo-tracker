"""Street Consensus Profile — a structured 'is it already priced in?' test.

Supports Camillo's step of asking whether an observed niche trend has already
entered sell-side estimates, ratings, and notes. Free Yahoo data via yfinance
only. Missing pieces are labeled, never filled in.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

from .provenance import now_utc


def _safe(symbol: str):
    import yfinance as yf
    return yf.Ticker(symbol)


def _records(df, limit=40) -> list[dict]:
    if df is None:
        return []
    try:
        if getattr(df, "empty", True):
            return []
        return df.reset_index().head(limit).to_dict(orient="records")
    except Exception:
        return []


def _num(x):
    try:
        if x is None:
            return None
        f = float(x)
        if f != f:  # NaN
            return None
        return f
    except Exception:
        return None


def _grade_bucket(grade: str | None) -> str | None:
    if not grade:
        return None
    g = str(grade).strip().lower()
    buys = {"buy", "strong buy", "overweight", "outperform", "positive", "accumulate", "add", "top pick"}
    holds = {"hold", "neutral", "equal-weight", "equal weight", "market perform", "sector perform", "in-line", "peer perform"}
    sells = {"sell", "strong sell", "underweight", "underperform", "negative", "reduce"}
    if g in buys or "buy" in g or "outperform" in g or "overweight" in g:
        return "buy"
    if g in sells or "sell" in g or "underperform" in g or "underweight" in g:
        return "sell"
    if g in holds or "hold" in g or "neutral" in g:
        return "hold"
    return "other"


def street_profile(symbol: str) -> dict:
    """Build a Street Consensus Profile and a priced-in verdict."""
    out: dict[str, Any] = {
        "symbol": symbol,
        "retrieved_at_utc": now_utc(),
        "method": "yfinance (Yahoo Finance free endpoints)",
        "source_url": f"https://finance.yahoo.com/quote/{symbol}",
        "components": {},
        "verdict": {"label": "insufficient_evidence", "reasons": [], "confidence": "low"},
    }
    try:
        t = _safe(symbol)
    except Exception as e:
        out["error"] = str(e)
        return out

    # 1. Consensus rating distribution
    rec = {}
    try:
        recs = t.recommendations
        rows = _records(recs, 8)
        # yfinance 1.8 period rows often have strongBuy, buy, hold, sell, strongSell
        latest = rows[0] if rows else {}
        # keys may be period-indexed
        def pick(d, *names):
            for n in names:
                for k, v in d.items():
                    if str(k).lower().replace(" ", "") == n.lower().replace(" ", ""):
                        return _num(v)
            return None
        dist = {
            "strong_buy": pick(latest, "strongBuy", "strong_buy"),
            "buy": pick(latest, "buy"),
            "hold": pick(latest, "hold"),
            "sell": pick(latest, "sell"),
            "strong_sell": pick(latest, "strongSell", "strong_sell"),
            "period": latest.get("period") or latest.get("Period"),
        }
        total = sum(v for v in dist.values() if isinstance(v, (int, float)))
        buy_n = (dist["strong_buy"] or 0) + (dist["buy"] or 0)
        sell_n = (dist["sell"] or 0) + (dist["strong_sell"] or 0)
        rec = {
            "status": "worked" if total else "partial",
            "distribution": dist,
            "n_ratings": total or None,
            "buy_share": (buy_n / total) if total else None,
            "sell_share": (sell_n / total) if total else None,
            "hold_share": ((dist["hold"] or 0) / total) if total else None,
            "raw_preview": rows[:3],
        }
    except Exception as e:
        rec = {"status": "error", "reason": str(e)}
    out["components"]["consensus_distribution"] = rec

    # 2. Price-target dispersion and implied upside
    pt = {}
    try:
        raw = t.analyst_price_targets
        # may be a dict {current, mean, median, high, low} or a DataFrame
        if isinstance(raw, dict):
            d = {k: _num(v) for k, v in raw.items()}
        else:
            d = {}
            for rec_ in _records(raw, 5):
                d.update({k: _num(v) if not isinstance(v, str) else v for k, v in rec_.items()})
        last = d.get("current") or d.get("Current")
        mean = d.get("mean") or d.get("Mean")
        high = d.get("high") or d.get("High")
        low = d.get("low") or d.get("Low")
        median = d.get("median") or d.get("Median")
        upside = None
        if last and mean and last != 0:
            upside = (mean - last) / last * 100.0
        dispersion = None
        if high is not None and low is not None and mean:
            dispersion = (high - low) / mean * 100.0 if mean else None
        pt = {
            "status": "worked" if mean else "partial",
            "last_close": last, "mean": mean, "median": median, "high": high, "low": low,
            "implied_upside_pct": upside, "dispersion_pct_of_mean": dispersion,
        }
    except Exception as e:
        pt = {"status": "error", "reason": str(e)}
    out["components"]["price_targets"] = pt

    # 3. Estimate revisions (EPS trend / revisions)
    revs = {}
    try:
        trend = t.eps_trend
        revisions = t.eps_revisions
        revs = {
            "status": "worked",
            "eps_trend": _records(trend, 12),
            "eps_revisions": _records(revisions, 12),
            "notes": "yfinance eps_trend typically has 7d/30d/60d/90d current and 7/30/60/90 days ago.",
        }
        # try to detect direction
        rows = revs["eps_trend"]
        direction = None
        if rows:
            # prefer current quarter 0q or current year 0y
            row = rows[0]
            cur = _num(row.get("current") or row.get("Current"))
            ago30 = _num(row.get("30daysAgo") or row.get("30DaysAgo") or row.get("30days Ago"))
            if cur is not None and ago30 is not None and ago30 != 0:
                direction = "up" if cur > ago30 * 1.01 else ("down" if cur < ago30 * 0.99 else "flat")
                revs["current_vs_30d"] = {"current": cur, "ago30": ago30, "direction": direction}
        revs["revision_direction"] = direction
    except Exception as e:
        revs = {"status": "error", "reason": str(e)}
    out["components"]["estimate_revisions"] = revs

    # 4. Rating-change recency
    recent = {}
    try:
        ud = t.upgrades_downgrades
        rows = _records(ud, 60)
        # GradeDate may be index
        actions = []
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)
        n90_up = n90_down = 0
        last_date = None
        for row in rows:
            action = str(row.get("Action") or row.get("action") or "").lower()
            to_g = row.get("ToGrade") or row.get("toGrade") or row.get("To Grade")
            from_g = row.get("FromGrade") or row.get("fromGrade")
            when = row.get("GradeDate") or row.get("gradeDate") or row.get("Date") or row.get("index")
            actions.append({"date": str(when) if when is not None else None, "action": action,
                            "from": from_g, "to": to_g, "firm": row.get("Firm") or row.get("firm")})
            parsed = None
            if when is not None:
                try:
                    import pandas as pd
                    parsed = pd.to_datetime(when, utc=True)
                except Exception:
                    parsed = None
            if parsed is not None:
                if last_date is None or parsed > last_date:
                    last_date = parsed
                if parsed.to_pydatetime() >= cutoff:
                    if "up" in action or _grade_bucket(str(to_g)) == "buy" and _grade_bucket(str(from_g)) != "buy":
                        n90_up += 1
                    if "down" in action or _grade_bucket(str(to_g)) == "sell":
                        n90_down += 1
        recent = {
            "status": "worked" if rows else "partial",
            "n_actions_captured": len(rows),
            "n_upgrades_90d": n90_up,
            "n_downgrades_90d": n90_down,
            "last_action_date": str(last_date) if last_date is not None else None,
            "recent_preview": actions[:8],
        }
    except Exception as e:
        recent = {"status": "error", "reason": str(e)}
    out["components"]["rating_changes"] = recent

    # 5. News / note sentiment — reused from sentiment module if headlines exist
    news = {}
    try:
        from .analyst import _news_items
        from .sentiment import score_texts
        items = _news_items(t)
        texts = [i.get("title") or i.get("headline") or "" for i in items]
        scored = score_texts([x for x in texts if x]) if texts else {"ok": False}
        news = {
            "status": "worked" if items else "partial",
            "n_headlines": len(items),
            "sentiment": scored,
            "headlines_preview": texts[:6],
        }
    except Exception as e:
        news = {"status": "error", "reason": str(e)}
    out["components"]["news_sentiment"] = news

    # 6. Coverage count
    coverage = {
        "status": "worked" if rec.get("n_ratings") else "partial",
        "n_ratings": rec.get("n_ratings"),
        "notes": "Yahoo's recommendation snapshot is a coverage proxy, not a complete IBES universe.",
    }
    out["components"]["coverage"] = coverage

    # 7. Earnings-surprise history
    surprise = {}
    try:
        eh = t.earnings_history
        rows = _records(eh, 16)
        surprises = []
        for row in rows:
            s = _num(row.get("surprisePercent") or row.get("surprise_percent") or row.get("Surprise(%)"))
            if s is not None:
                surprises.append(s)
        surprise = {
            "status": "worked" if rows else "partial",
            "n": len(rows),
            "surprise_pct_history": surprises,
            "mean_surprise_pct": (sum(surprises) / len(surprises)) if surprises else None,
            "n_beats": sum(1 for s in surprises if s > 0),
            "n_misses": sum(1 for s in surprises if s < 0),
            "preview": rows[:6],
        }
    except Exception as e:
        surprise = {"status": "error", "reason": str(e)}
    out["components"]["earnings_surprises"] = surprise

    out["verdict"] = priced_in_verdict(out["components"])
    out["how_it_feeds_the_tree"] = (
        "Street rows are an auxiliary check on one stated thesis, not a stock screen. "
        "Labels say whether that thesis is reflected in the sources reviewed. "
        "A missing row is insufficient_evidence, not proof the Street is unaware or that the name is unpriced."
    )
    return out


def priced_in_verdict(components: dict) -> dict:
    """Rule-based verdict. Conservative: missing data lowers confidence, never fills numbers."""
    reasons = []
    points = 0  # higher = more likely already priced
    pieces = 0

    rec = components.get("consensus_distribution") or {}
    if isinstance(rec.get("buy_share"), (int, float)):
        pieces += 1
        if rec["buy_share"] >= 0.7:
            points += 2
            reasons.append(f"buy-side share {rec['buy_share']:.0%} — Street already constructive")
        elif rec["buy_share"] <= 0.35:
            points -= 2
            reasons.append(f"buy-side share {rec['buy_share']:.0%} — Street is not clearly on board")
        else:
            points += 0
            reasons.append(f"buy-side share {rec['buy_share']:.0%} — mixed consensus")

    pt = components.get("price_targets") or {}
    if isinstance(pt.get("implied_upside_pct"), (int, float)):
        pieces += 1
        u = pt["implied_upside_pct"]
        if u >= 20:
            points += 1
            reasons.append(f"mean PT implies {u:.0f}% upside — Street already models a bull case")
        elif u <= 0:
            points -= 1
            reasons.append(f"mean PT implies {u:.0f}% — Street is not embedding a bullish gap")
        else:
            reasons.append(f"mean PT implies {u:.0f}% upside")

    revs = components.get("estimate_revisions") or {}
    direction = revs.get("revision_direction")
    if direction:
        pieces += 1
        if direction == "up":
            points += 2
            reasons.append("EPS estimates revised up over ~30 days — information may already be entering models")
        elif direction == "down":
            points -= 1
            reasons.append("EPS estimates revised down — Street may be leaning the other way")
        else:
            reasons.append("EPS estimates roughly unchanged over ~30 days")

    recent = components.get("rating_changes") or {}
    if recent.get("status") == "worked":
        pieces += 1
        up, down = recent.get("n_upgrades_90d") or 0, recent.get("n_downgrades_90d") or 0
        if up >= 3 and up > down:
            points += 2
            reasons.append(f"{up} upgrades in 90 days — the fact may already be migrating to the Street")
        elif down >= 3 and down > up:
            points -= 1
            reasons.append(f"{down} downgrades in 90 days")
        else:
            reasons.append(f"rating-change flow in 90d: {up} up / {down} down")

    cov = (components.get("coverage") or {}).get("n_ratings")
    if isinstance(cov, (int, float)):
        pieces += 1
        if cov >= 20:
            reasons.append(f"coverage {int(cov)} is thick — information usually reaches the tape faster")
            points += 1
        elif cov <= 5:
            reasons.append(f"coverage {int(cov)} is thin — slower absorption is plausible")
            points -= 1

    if pieces == 0:
        return {"label": "insufficient_evidence", "reasons": ["No Street component returned usable numbers."],
                "confidence": "low", "priced_in_points": None, "n_components": 0,
                "scale": "Heuristic point total on the rows reviewed. Not a validated pricing model. Silence is not 'ignored'."}

    if points >= 4:
        label = "explicitly_reflected"
    elif points >= 2:
        label = "partly_reflected"
    elif abs(points) <= 1:
        label = "partly_reflected"
    else:
        label = "not_evidenced_in_reviewed_sources"

    confidence = "high" if pieces >= 5 else ("medium" if pieces >= 3 else "low")
    return {
        "label": label,
        "reasons": reasons,
        "confidence": confidence,
        "priced_in_points": points,
        "n_components": pieces,
        "scale": "Project heuristic on reviewed Street rows. Not a Camillo rule and not a stock-selection model.",
        "reading": {
            "explicitly_reflected": "The reviewed ratings, revisions, or targets already look like they contain a bullish version of this fact. That is not a buy or a sell.",
            "partly_reflected": "Some reviewed Street channels have moved and others have not. The thesis is not shown to be either fully in or fully absent.",
            "not_evidenced_in_reviewed_sources": "The reviewed Street rows do not show this thesis. That is not proof the Street is unaware, and it is not proof the price is wrong.",
            "insufficient_evidence": "Not enough reviewed rows to say whether this thesis is reflected.",
        }.get(label),
    }


def profile_and_scan_context(symbol: str, niche_rising: bool | None = None) -> dict:
    """Workflow: niche signal → ticker → Street profile → priced-in verdict."""
    profile = street_profile(symbol)
    verdict = profile.get("verdict") or {}
    action = "street_check_inconclusive"
    if verdict.get("label") == "explicitly_reflected" and niche_rising:
        action = "thesis_already_reflected_in_reviewed_rows"
    elif verdict.get("label") == "not_evidenced_in_reviewed_sources" and niche_rising:
        action = "candidate_for_human_work"
    elif verdict.get("label") == "partly_reflected" and niche_rising:
        action = "watch_partial_reflection"
    elif verdict.get("label") == "not_evidenced_in_reviewed_sources" and niche_rising is False:
        action = "no_social_corroboration"
    profile["workflow_action"] = action
    profile["niche_rising"] = niche_rising
    return profile
