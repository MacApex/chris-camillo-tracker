"""Collect sell-side consensus and news headlines from free Yahoo Finance data via yfinance."""

from __future__ import annotations

import datetime as dt
from typing import Any

import pandas as pd

# Yahoo recommendation grades → numeric (1 = Strong Buy … 5 = Strong Sell)
# Matches Yahoo's historical `To Grade` conventions and yfinance's 1-5 scale.
_GRADE = {
    "strong buy": 1.0,
    "buy": 2.0,
    "outperform": 2.0,
    "overweight": 2.0,
    "accumulate": 2.0,
    "add": 2.0,
    "sector outperform": 2.0,
    "positive": 2.0,
    "hold": 3.0,
    "neutral": 3.0,
    "equal-weight": 3.0,
    "equalweight": 3.0,
    "equal weight": 3.0,
    "market perform": 3.0,
    "sector perform": 3.0,
    "peer perform": 3.0,
    "in-line": 3.0,
    "sector weight": 3.0,
    "underperform": 4.0,
    "underweight": 4.0,
    "reduce": 4.0,
    "sector underperform": 4.0,
    "negative": 4.0,
    "sell": 5.0,
    "strong sell": 5.0,
}


def grade_to_score(grade: Any) -> float | None:
    if grade is None or (isinstance(grade, float) and pd.isna(grade)):
        return None
    if isinstance(grade, (int, float)):
        v = float(grade)
        if 1 <= v <= 5:
            return v
        return None
    key = str(grade).strip().lower()
    return _GRADE.get(key)


def _safe_ticker(symbol: str):
    import yfinance as yf

    return yf.Ticker(symbol)


def _df_records(df: Any, limit: int = 40) -> list[dict]:
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []
    out = df.copy()
    # Flatten index if it's a date
    if not isinstance(out.index, pd.RangeIndex):
        out = out.reset_index()
    else:
        out = out.reset_index(drop=True)
    records = []
    for _, row in out.head(limit).iterrows():
        rec = {}
        for k, v in row.items():
            if isinstance(v, (pd.Timestamp, dt.datetime, dt.date)):
                rec[str(k)] = v.isoformat()
            elif isinstance(v, (int, float)) and pd.isna(v):
                rec[str(k)] = None
            elif hasattr(v, "item"):
                try:
                    rec[str(k)] = v.item()
                except Exception:
                    rec[str(k)] = str(v)
            else:
                rec[str(k)] = v if isinstance(v, (str, int, float, bool, type(None))) else str(v)
        records.append(rec)
    return records


def _news_items(ticker) -> list[dict]:
    items = []
    try:
        raw = ticker.news or []
    except Exception as exc:
        return [{"error": f"news fetch failed: {exc}"}]
    for n in raw[:25]:
        # yfinance has used both flat and nested "content" shapes
        content = n.get("content") if isinstance(n.get("content"), dict) else n
        title = (
            content.get("title")
            or content.get("headline")
            or n.get("title")
            or n.get("headline")
            or ""
        )
        pub = (
            content.get("pubDate")
            or content.get("providerPublishTime")
            or n.get("providerPublishTime")
            or n.get("pubDate")
            or ""
        )
        provider = ""
        prov = content.get("provider") or n.get("publisher") or n.get("provider")
        if isinstance(prov, dict):
            provider = prov.get("displayName") or prov.get("name") or ""
        elif prov:
            provider = str(prov)
        url = ""
        click = content.get("canonicalUrl") or content.get("clickThroughUrl") or n.get("link") or n.get("url")
        if isinstance(click, dict):
            url = click.get("url") or ""
        elif click:
            url = str(click)
        items.append({"title": title, "publisher": provider, "published": str(pub), "url": url})
    return items


def collect_analyst(symbol: str) -> dict:
    """Pull recommendations, price targets, upgrades/downgrades, and news."""
    symbol = symbol.upper().strip()
    errors: list[str] = []
    out: dict[str, Any] = {
        "symbol": symbol,
        "source": "yfinance / Yahoo Finance (free, unofficial)",
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    try:
        t = _safe_ticker(symbol)
    except Exception as exc:
        out["error"] = f"could not construct ticker: {exc}"
        return out

    # Recommendations (monthly history of 1-5 mean + firm counts)
    rec_mean = None
    rec_latest = None
    try:
        rec = t.recommendations
        out["recommendations_history"] = _df_records(rec, 24)
        if rec is not None and isinstance(rec, pd.DataFrame) and not rec.empty:
            # Prefer a 'strongBuy'/'buy'/… count row (current API) or 'To Grade'
            row = rec.iloc[0]
            counts = {}
            for col, weight in (
                ("strongBuy", 1.0),
                ("buy", 2.0),
                ("hold", 3.0),
                ("sell", 4.0),
                ("strongSell", 5.0),
            ):
                if col in rec.columns:
                    try:
                        counts[col] = int(row[col]) if not pd.isna(row[col]) else 0
                    except Exception:
                        pass
            if counts and sum(counts.values()) > 0:
                total = sum(counts.values())
                rec_mean = sum(counts[c] * w for c, w in (
                    ("strongBuy", 1.0), ("buy", 2.0), ("hold", 3.0),
                    ("sell", 4.0), ("strongSell", 5.0),
                ) if c in counts) / total
                rec_latest = {"counts": counts, "period": str(row.get("period", "latest"))}
            elif "To Grade" in rec.columns:
                scores = [grade_to_score(g) for g in rec["To Grade"].tolist()]
                scores = [s for s in scores if s is not None]
                if scores:
                    rec_mean = sum(scores) / len(scores)
    except Exception as exc:
        errors.append(f"recommendations: {exc}")
        out["recommendations_history"] = []

    try:
        summary = getattr(t, "recommendations_summary", None)
        if callable(summary):
            summary = summary()
        out["recommendations_summary"] = _df_records(summary) if summary is not None else []
    except Exception as exc:
        errors.append(f"recommendations_summary: {exc}")
        out["recommendations_summary"] = []

    # Price targets
    targets: dict[str, Any] = {}
    try:
        pt = getattr(t, "analyst_price_targets", None)
        if callable(pt):
            pt = pt()
        if isinstance(pt, dict):
            targets = {k: (float(v) if isinstance(v, (int, float)) and v is not None else v) for k, v in pt.items()}
        elif isinstance(pt, pd.DataFrame) and not pt.empty:
            targets = _df_records(pt, 5)[0] if _df_records(pt, 5) else {}
    except Exception as exc:
        errors.append(f"price_targets: {exc}")
    out["price_targets"] = targets

    # Last close for implied upside
    last_close = None
    try:
        hist = t.history(period="5d")
        if hist is not None and not hist.empty:
            last_close = float(hist["Close"].iloc[-1])
    except Exception as exc:
        errors.append(f"history: {exc}")
    out["last_close"] = last_close
    mean_pt = None
    for key in ("mean", "current", "average", "targetMeanPrice"):
        if key in targets and isinstance(targets[key], (int, float)):
            mean_pt = float(targets[key])
            break
    if mean_pt and last_close and last_close > 0:
        out["implied_upside_pct"] = round((mean_pt / last_close - 1.0) * 100.0, 2)
    else:
        out["implied_upside_pct"] = None

    # Upgrades / downgrades
    ud_records: list[dict] = []
    action_balance = 0.0
    action_n = 0
    try:
        ud = getattr(t, "upgrades_downgrades", None)
        if callable(ud):
            ud = ud()
        ud_records = _df_records(ud, 50)
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=180)
        for rec in ud_records:
            action = str(rec.get("Action") or rec.get("action") or "").lower()
            grade = rec.get("ToGrade") or rec.get("To Grade") or rec.get("toGrade")
            ts = rec.get("GradeDate") or rec.get("Date") or rec.get("index") or rec.get("date")
            recent = True
            if ts:
                try:
                    parsed = pd.to_datetime(ts, utc=True)
                    recent = bool(parsed >= cutoff)
                except Exception:
                    recent = True
            if not recent:
                continue
            action_n += 1
            if "down" in action:
                action_balance -= 1.0
            elif "up" in action:
                action_balance += 1.0
            elif "init" in action:
                g = grade_to_score(grade)
                if g is not None:
                    action_balance += (3.0 - g) / 2.0
    except Exception as exc:
        errors.append(f"upgrades_downgrades: {exc}")
    out["upgrades_downgrades"] = ud_records
    out["recent_action_balance"] = round(action_balance, 3)
    out["recent_action_n"] = action_n

    news = _news_items(t)
    out["news"] = [n for n in news if "error" not in n]
    if news and "error" in news[0]:
        errors.append(news[0]["error"])

    out["recommendation_mean"] = round(rec_mean, 3) if rec_mean is not None else None
    out["recommendation_latest"] = rec_latest
    # Convert 1-5 (1=bullish) into a 0-100 "analyst bullishness" score
    if rec_mean is not None:
        out["analyst_bullishness"] = round(max(0.0, min(100.0, (5.0 - rec_mean) / 4.0 * 100.0)), 2)
    else:
        out["analyst_bullishness"] = None
    if errors:
        out["warnings"] = errors
    return out
