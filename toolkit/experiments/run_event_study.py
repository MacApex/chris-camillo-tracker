#!/usr/bin/env python3
"""Honest event study around documented Camillo call dates.

Forward 1/3/6-month *stock* returns (market facts, not Camillo's P&L).
Street ratings before vs after, when yfinance history exists.
Wikipedia attention around the date, when the article has pageviews.

This is NOT a proof of the strategy. Sample is small, dates are often
month-precision, selection is biased toward stories he talked about,
and losers may be under-reported. If a series is missing, we say so.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from camillo_tracker.provenance import now_utc, write_json

# Only events with a usable date AND a ticker. Precision is recorded.
# Entry is the documented call/purchase date, not a optimized look-back.
EVENTS = [
    {"id": "elf-2019", "ticker": "ELF", "date": "2019-03-15", "precision": "month",
     "side": "long", "wiki": None,  # 2019 pageviews 404 for E.l.f.
     "note": "Jeffree Star / channel-check month, per BI. Mid-month placeholder."},
    {"id": "rbi-2019-apr", "ticker": "QSR", "date": "2019-04-15", "precision": "month",
     "side": "long", "wiki": "Restaurant_Brands_International",
     "note": "First dated purchase window, later a loss."},
    {"id": "rbi-2019-aug", "ticker": "QSR", "date": "2019-08-15", "precision": "month",
     "side": "long", "wiki": "Restaurant_Brands_International",
     "note": "Second dated purchase window."},
    {"id": "covid-spy-2020", "ticker": "SPY", "date": "2020-02-15", "precision": "month",
     "side": "short", "wiki": None,
     "note": "Puts on SPY, self-reported. Underlying returns shown; put P&L is unknown."},
    {"id": "covid-wynn-2020", "ticker": "WYNN", "date": "2020-02-15", "precision": "month",
     "side": "short", "wiki": "Wynn_Resorts",
     "note": "Puts on Wynn, self-reported."},
    {"id": "dorel-2020", "ticker": "DIIBF", "date": "2020-04-24", "precision": "day",
     "side": "long", "wiki": "Dorel_Industries",
     "note": "Best-dated event: purchase screenshots at $1.56, viewed by BI."},
    {"id": "tgt-missoni-2011", "ticker": "TGT", "date": "2011-09-07", "precision": "day-approx",
     "side": "long", "wiki": None,
     "note": " collab event week. Overnight options P&L is self-reported; we only show equity path. Wiki pageviews start mid-2015."},
    {"id": "gme-2021", "ticker": "GME", "date": "2021-01-25", "precision": "month",
     "side": "long", "wiki": "GameStop",
     "note": "Self-reported buy around $70 — already mid-squeeze. Mid/late January placeholder."},
    {"id": "amc-2021", "ticker": "AMC", "date": "2021-01-25", "precision": "month",
     "side": "long", "wiki": "AMC_Theatres",
     "note": "Self-reported buy around $3."},
    {"id": "tpr-2021-mention", "ticker": "TPR", "date": "2021-08-15", "precision": "mention_date",
     "side": "long", "wiki": "Tapestry,_Inc.",
     "note": "BI mention of a $3.1M position — NOT an entry date. Forward returns from the article date only."},
]


def next_trading(px: pd.Series, when: pd.Timestamp) -> pd.Timestamp | None:
    idx = px.index
    # normalize tz-naive
    if getattr(idx, "tz", None) is not None:
        when = when.tz_localize(idx.tz) if when.tzinfo is None else when.tz_convert(idx.tz)
    later = idx[idx >= when]
    return later[0] if len(later) else None


def fwd_return(px: pd.Series, start: pd.Timestamp, trading_days: int) -> dict:
    if start is None or start not in px.index:
        return {"ok": False, "reason": "start not in index"}
    loc = px.index.get_loc(start)
    end_loc = loc + trading_days
    if end_loc >= len(px.index):
        return {"ok": False, "reason": "not enough forward history"}
    a, b = float(px.iloc[loc]), float(px.iloc[end_loc])
    if a == 0:
        return {"ok": False, "reason": "zero start price"}
    return {
        "ok": True,
        "start_date": str(px.index[loc].date()),
        "end_date": str(px.index[end_loc].date()),
        "start_px": round(a, 4),
        "end_px": round(b, 4),
        "pct": round((b / a - 1.0) * 100.0, 2),
    }


def wiki_around(article: str, date: str) -> dict | None:
    path = None
    # reuse fetched historical files
    candidates = {
        "Restaurant_Brands_International": ROOT / "data/wikipedia/hist_QSR_2019.json",
        "Wynn_Resorts": ROOT / "data/wikipedia/hist_WYNN_2020.json",
        "Dorel_Industries": ROOT / "data/wikipedia/hist_DIIBF_2020.json",
        "GameStop": ROOT / "data/wikipedia/hist_GME_2021.json",
        "AMC_Theatres": ROOT / "data/wikipedia/hist_AMC_2021.json",
        "Tapestry,_Inc.": ROOT / "data/wikipedia/hist_TPR_2021.json",
    }
    path = candidates.get(article)
    if not path or not path.exists():
        return {"ok": False, "reason": f"no local series for {article}"}
    payload = json.loads(path.read_text())
    items = payload.get("items") or []
    # timestamps like 2020042400
    def ts_to_day(t):
        s = str(t)[:8]
        return s
    target = date.replace("-", "")
    views = [(ts_to_day(i["timestamp"]), int(i["views"])) for i in items]
    if not views:
        return {"ok": False, "reason": "empty"}
    # 14-day window before and after
    import datetime as dt
    d0 = dt.datetime.strptime(target, "%Y%m%d")
    before, after, on = [], [], None
    for day, v in views:
        d = dt.datetime.strptime(day, "%Y%m%d")
        delta = (d - d0).days
        if delta == 0:
            on = v
        elif -14 <= delta < 0:
            before.append(v)
        elif 0 < delta <= 14:
            after.append(v)
    return {
        "ok": True,
        "article": article,
        "source_url": payload.get("source_url"),
        "method": payload.get("method"),
        "retrieved_at_utc": payload.get("retrieved_at_utc"),
        "views_on_date": on,
        "mean_14d_before": (sum(before) / len(before)) if before else None,
        "mean_14d_after": (sum(after) / len(after)) if after else None,
        "n_before": len(before),
        "n_after": len(after),
    }


def street_around(ticker: str, date: str) -> dict:
    """Rating actions in a ±90-day window, if yfinance has them."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        df = t.upgrades_downgrades
        if df is None or getattr(df, "empty", True):
            return {"ok": False, "reason": "no upgrades_downgrades"}
        d = df.reset_index()
        # find a date column
        date_col = None
        for c in d.columns:
            if "date" in str(c).lower() or c in ("index", "GradeDate"):
                date_col = c
                break
        if date_col is None:
            # maybe already datetime index dumped as first col
            date_col = d.columns[0]
        d["_dt"] = pd.to_datetime(d[date_col], utc=True, errors="coerce")
        d0 = pd.Timestamp(date, tz="UTC")
        win = d[(d["_dt"] >= d0 - pd.Timedelta(days=90)) & (d["_dt"] <= d0 + pd.Timedelta(days=90))]
        before = win[win["_dt"] < d0]
        after = win[win["_dt"] >= d0]
        def count_up(frame):
            if frame.empty:
                return 0
            col = None
            for c in frame.columns:
                if str(c).lower() == "action":
                    col = c
                    break
            if col is None:
                return len(frame)
            return int(frame[col].astype(str).str.lower().str.contains("up").sum())
        return {
            "ok": True,
            "n_actions_plus_minus_90d": int(len(win)),
            "n_before": int(len(before)),
            "n_after": int(len(after)),
            "upgrades_before": count_up(before),
            "upgrades_after": count_up(after),
            "method": "yfinance.Ticker.upgrades_downgrades",
            "note": "Yahoo's history is incomplete; a zero does not mean no Street activity.",
        }
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def run():
    import yfinance as yf
    results = []
    print("event study", now_utc())
    for ev in EVENTS:
        print(" ", ev["id"], ev["ticker"])
        row = dict(ev)
        row["retrieved_at_utc"] = now_utc()
        try:
            hist = yf.Ticker(ev["ticker"]).history(start="2010-01-01", end="2026-11-13", auto_adjust=True)
            if hist is None or hist.empty:
                row["returns"] = {"ok": False, "reason": "empty history"}
                results.append(row)
                continue
            px = hist["Close"].dropna()
            start = next_trading(px, pd.Timestamp(ev["date"]))
            row["trading_start"] = str(start.date()) if start is not None else None
            rets = {}
            for label, days in [("1m", 21), ("3m", 63), ("6m", 126)]:
                rets[label] = fwd_return(px, start, days)
            row["returns"] = rets
            # For shorts, favorable = negative underlying return
            fav = {}
            for k, v in rets.items():
                if v.get("ok"):
                    pct = v["pct"]
                    fav[k] = (-pct) if ev["side"] == "short" else pct
                else:
                    fav[k] = None
            row["return_in_direction_of_stated_side"] = fav
        except Exception as e:
            row["returns"] = {"ok": False, "reason": str(e)}
        row["street_window"] = street_around(ev["ticker"], ev["date"])
        if ev.get("wiki"):
            row["wikipedia_attention"] = wiki_around(ev["wiki"], ev["date"])
        else:
            row["wikipedia_attention"] = {"ok": False, "reason": "no article assigned (date too early, or 404)"}
        results.append(row)

    # Quadrant sketch: we do NOT have historical Trends for most of these
    # dates (pytrends 'today 5-y' from Nov 2026 only reaches ~Nov 2021).
    # We therefore refuse to assign high-niche/low-Street quadrants historically
    # except as an honest "cannot classify" count.
    n_ok_1m = sum(1 for r in results if (r.get("returns") or {}).get("1m", {}).get("ok"))
    summary = {
        "retrieved_at_utc": now_utc(),
        "retrieved_at_asia_shanghai": "2026-11-13 Asia/Shanghai",
        "n_events_attempted": len(EVENTS),
        "n_with_1m_return": n_ok_1m,
        "method": (
            "Forward close-to-close returns from the first trading day on or after the "
            "documented date, using yfinance auto-adjusted closes, 21/63/126 trading days. "
            "These are market-path facts, not Camillo's personal P&L. Dates with only "
            "month precision use mid-month placeholders, labeled as such."
        ),
        "limitations": [
            "Sample is small and is drawn from stories he later discussed — survivorship and storytelling bias.",
            "Several dates are month-precision; GME/AMC placeholders are mid-squeeze, which can flatten or reverse forward returns.",
            "TPR uses the BI article date, which is a mention, not an entry.",
            "RBI is a documented losing thesis; it is included so the study is not winners-only.",
            "COVID positions were puts — equity-index forward returns are not put P&L.",
            "Target × Missoni was an overnight options trade; the equity 1/3/6-month path is a different instrument.",
            "pytrends 'today 5-y' from November 2026 does not reach 2019–2020, so we cannot honestly classify historical events into high-niche/low-Street quadrants. Wikipedia attention is a proxy only where the article exists.",
            "Yahoo upgrades/downgrades history is incomplete. Zeros are not proof of inactivity.",
            "No transaction costs, borrow fees, or options Greeks. Not a backtest of a tradable rule.",
        ],
        "quadrant_classification": {
            "status": "not_performed",
            "reason": "Historical Google Trends and complete historical Street consensus at event dates are not available from the free sources we can verify. We refuse to invent quadrant labels.",
        },
        "events": results,
    }
    dest = ROOT / "data" / "experiments" / "event_study.json"
    write_json(dest, summary)
    # also a slim CSV
    import csv
    csv_path = ROOT / "data" / "experiments" / "event_study.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "id","ticker","date","precision","side","trading_start",
            "r1m","r3m","r6m","r1m_in_side","r3m_in_side","r6m_in_side",
            "street_ok","wiki_ok","note",
        ])
        w.writeheader()
        for r in results:
            rets = r.get("returns") or {}
            fav = r.get("return_in_direction_of_stated_side") or {}
            def pct(block, k="pct"):
                if isinstance(block, dict) and block.get("ok"):
                    return block.get(k)
                return ""
            w.writerow({
                "id": r["id"], "ticker": r["ticker"], "date": r["date"],
                "precision": r["precision"], "side": r["side"],
                "trading_start": r.get("trading_start"),
                "r1m": pct(rets.get("1m") if isinstance(rets, dict) else {}),
                "r3m": pct(rets.get("3m") if isinstance(rets, dict) else {}),
                "r6m": pct(rets.get("6m") if isinstance(rets, dict) else {}),
                "r1m_in_side": fav.get("1m"), "r3m_in_side": fav.get("3m"), "r6m_in_side": fav.get("6m"),
                "street_ok": (r.get("street_window") or {}).get("ok"),
                "wiki_ok": (r.get("wikipedia_attention") or {}).get("ok"),
                "note": r.get("note"),
            })
    print("WROTE", dest)
    for r in results:
        rets = r.get("returns") or {}
        def fmt(k):
            b = rets.get(k) if isinstance(rets, dict) else None
            return f"{b['pct']:+.1f}%" if isinstance(b, dict) and b.get("ok") else "n/a"
        print(f"  {r['id']:22} {r['ticker']:6} 1m={fmt('1m'):8} 3m={fmt('3m'):8} 6m={fmt('6m'):8}")
    return summary

if __name__ == "__main__":
    run()
