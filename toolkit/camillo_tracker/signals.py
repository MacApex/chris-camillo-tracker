"""Multi-platform niche-signal adapters and corroboration.

Public data only. Every numeric point should already sit in provenance
or carry source_url / retrieved_at / method. Adapters return honest
status: worked, partial, blocked, skipped, error. They never invent a count.

Reliability weights are documented opinions about source *quality as a
Camillo-style observational input*, not about statistical efficiency.
"""
from __future__ import annotations

import datetime as dt
import math
import os
import statistics
from typing import Any

from .provenance import now_utc

# PROJECT convention, not a rule Camillo published and not a validated model.
# Higher = this archive's opinion of source quality when the adapter returns data.
# Missing data is weight 0. Weights never become a trade.
RELIABILITY = {
    "wikipedia": 0.70,       # official, stable, attention not sentiment
    "google_trends": 0.75,   # Camillo's own tool; 2025 AI-pollution caveat
    "google_news": 0.55,     # mainstream volume — often LAGS the niche
    "gdelt_news": 0.55,
    "x": 0.80,               # official counts when the query is clean
    "youtube": 0.65,
    "reddit": 0.70,
    "tiktok": 0.85,          # high Camillo relevance; official challenge/detail when available
    "instagram": 0.75,
    "pinterest_trends": 0.70,
    "amazon_movers": 0.70,
    "app_store": 0.40,       # presence, not a demand rank, in our adapter
}

USER_AGENT = "ChrisCamilloTracker/1.0 (research; https://github.com/MacApex/chris-camillo-tracker)"


def _z(values: list[float], current: float) -> float | None:
    if len(values) < 4:
        return None
    mu = statistics.mean(values)
    sd = statistics.pstdev(values)
    if sd == 0:
        return 0.0
    return (current - mu) / sd


def wikipedia_pageviews(article: str, start: str = "20251013", end: str = "20261112") -> dict:
    """Official Wikimedia REST API. `article` is the English Wikipedia title."""
    import requests
    from urllib.parse import quote

    art = quote(article.replace(" ", "_"), safe="()_,.%")
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/user/{art}/daily/{start}/{end}"
    )
    out: dict[str, Any] = {
        "platform": "wikipedia",
        "ok": False,
        "status": "error",
        "source_url": url,
        "method": "Wikimedia REST API",
        "retrieved_at_utc": now_utc(),
        "article": article,
    }
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, timeout=20)
        out["http_status"] = r.status_code
        if r.status_code != 200:
            out["status"] = "blocked"
            out["reason"] = f"HTTP {r.status_code} {r.text[:160]}"
            return out
        items = r.json().get("items") or []
        views = [int(i.get("views") or 0) for i in items]
        if not views:
            out["status"] = "partial"
            out["reason"] = "empty series"
            return out
        # The UTC day still in progress is not a complete observation.
        # An incomplete last point cannot support a fading (or rising) claim.
        today = now_utc()[:10].replace("-", "")
        complete_items = list(items)
        last_ts = str((items[-1] or {}).get("timestamp") or "")
        dropped = None
        if len(last_ts) >= 8 and last_ts[:8] >= today:
            dropped = last_ts
            complete_items = items[:-1]
        if len(complete_items) < 5:
            out.update({
                "ok": False,
                "status": "partial",
                "reason": "No complete pageview day left after dropping an in-progress UTC day."
                if dropped else "Series too short for a z.",
                "dropped_incomplete_day": dropped,
                "n_days": len(complete_items),
                "z_last_vs_history": None,
            })
            return out
        views = [int(i.get("views") or 0) for i in complete_items]
        recent, prior = views[-13:], views[-26:-13] or views[:-13]
        out.update({
            "ok": True,
            "status": "worked",
            "last_day": views[-1],
            "last_timestamp": complete_items[-1].get("timestamp"),
            "last_day_complete": True,
            "dropped_incomplete_day": dropped,
            "sum_13d": sum(recent),
            "sum_prior_13d": sum(prior) if prior else None,
            "z_last_vs_history": _z(views[:-1], views[-1]),
            "z_note": "z uses complete days only. A negative z is not a business-fading claim.",
            "n_days": len(views),
            "series": [{"date": i.get("timestamp"), "views": i.get("views")} for i in complete_items[-90:]],
        })
        return out
    except Exception as e:
        out["reason"] = str(e)
        return out


def google_news_rss(query: str) -> dict:
    import requests
    url = "https://news.google.com/rss/search?q=%s&hl=en-US&gl=US&ceid=US:en" % query.replace(" ", "+")
    out: dict[str, Any] = {
        "platform": "google_news",
        "ok": False,
        "status": "error",
        "source_url": url,
        "method": "Google News RSS",
        "retrieved_at_utc": now_utc(),
        "query": query,
    }
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        n = r.text.count("<item>") if r.status_code == 200 else 0
        if r.status_code == 200 and n:
            out.update({"ok": True, "status": "worked", "rss_item_count": n, "http_status": 200})
        else:
            out.update({"status": "blocked", "http_status": r.status_code, "reason": f"items={n}"})
        return out
    except Exception as e:
        out["reason"] = str(e)
        return out


def gdelt_timeline(query: str, start="20261001000000", end="20261112000000", pause: float = 6.0) -> dict:
    """Official GDELT DOC API. Default pause respects their 1-req/5s guidance."""
    import time
    import requests
    if pause:
        time.sleep(pause)
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {"query": query, "mode": "TimelineVol", "startdatetime": start,
              "enddatetime": end, "format": "json", "timesmooth": "3"}
    out: dict[str, Any] = {
        "platform": "gdelt_news", "ok": False, "status": "error",
        "source_url": url, "method": "GDELT DOC API TimelineVol",
        "retrieved_at_utc": now_utc(), "query": query,
    }
    try:
        r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
        out["http_status"] = r.status_code
        out["source_url"] = r.url
        text = r.text.strip()
        if r.status_code == 429:
            out.update({"status": "blocked", "reason": "HTTP 429 rate limit (need ≥5s between calls)"})
            return out
        if r.status_code == 200 and text.startswith("{"):
            data = r.json()
            series = ((data.get("timeline") or [{}])[0]).get("data") or []
            out.update({
                "ok": True, "status": "worked",
                "n_points": len(series),
                "last": series[-1] if series else None,
                "series": series,
            })
        else:
            out.update({"status": "blocked", "reason": text[:200]})
        return out
    except Exception as e:
        out["reason"] = str(e)
        return out


def youtube_search(query: str, n: int = 3) -> dict:
    """Metadata only, via yt-dlp. No video download."""
    import json, shutil, subprocess
    out: dict[str, Any] = {
        "platform": "youtube", "ok": False, "status": "error",
        "source_url": "https://www.youtube.com/results?search_query=" + query.replace(" ", "+"),
        "method": "yt-dlp ytsearch --dump-json --skip-download",
        "retrieved_at_utc": now_utc(), "query": query,
    }
    exe = shutil.which("yt-dlp")
    if not exe:
        out.update({"status": "skipped", "reason": "yt-dlp not on PATH"})
        return out
    try:
        proc = subprocess.run(
            [exe, f"ytsearch{n}:{query}", "--dump-json", "--skip-download",
             "--no-warnings", "--socket-timeout", "20"],
            capture_output=True, text=True, timeout=90,
        )
        results = []
        for ln in proc.stdout.splitlines():
            if not ln.startswith("{"):
                continue
            p = json.loads(ln)
            results.append({
                "id": p.get("id"), "title": p.get("title"),
                "view_count": p.get("view_count"),
                "upload_date": p.get("upload_date"),
                "webpage_url": p.get("webpage_url") or p.get("original_url"),
            })
        if results:
            out.update({"ok": True, "status": "worked", "results": results, "n": len(results)})
        else:
            out.update({"status": "blocked", "reason": (proc.stderr or "empty")[:240]})
        return out
    except Exception as e:
        out["reason"] = str(e)
        return out


def itunes_search(term: str) -> dict:
    import requests
    url = "https://itunes.apple.com/search"
    out: dict[str, Any] = {
        "platform": "app_store", "ok": False, "status": "error",
        "source_url": url, "method": "iTunes Search API",
        "retrieved_at_utc": now_utc(), "term": term,
    }
    try:
        r = requests.get(url, params={"term": term, "entity": "software", "limit": 5},
                         headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            js = r.json()
            out.update({
                "ok": True, "status": "worked", "source_url": r.url,
                "result_count": js.get("resultCount"),
                "names": [x.get("trackName") for x in (js.get("results") or [])],
                "notes": "Official search is presence, not a live top-chart rank.",
            })
        else:
            out.update({"status": "blocked", "http_status": r.status_code})
        return out
    except Exception as e:
        out["reason"] = str(e)
        return out


def z_and_momentum(series: list[float]) -> dict:
    if not series:
        return {"z": None, "momentum_0_100": None, "n": 0}
    last = series[-1]
    z = _z(series[:-1], last) if len(series) > 4 else None
    # Map z to a 0–100-ish score without inventing missing data
    if z is None:
        mom = None
    else:
        mom = max(0.0, min(100.0, 50.0 + 10.0 * z))
    return {"z": z, "momentum_0_100": mom, "last": last, "n": len(series)}


def corroborate(platform_results: dict[str, dict], min_confirm: int = 2) -> dict:
    """Combine available platform z-scores. Missing platforms are recorded, not imputed."""
    scores = []
    missing = []
    present_no_z = []
    used = []
    for name, res in platform_results.items():
        if not res:
            missing.append({"platform": name, "reason": "no result object"})
            continue
        st = res.get("status") or ("worked" if res.get("ok") else "blocked")
        z = res.get("z_last_vs_history")
        mom = res.get("momentum_0_100") if isinstance(res.get("momentum_0_100"), (int, float)) else None
        # momentum_0_100 is a separate 0–100 heuristic on normalized relative
        # interest (see social.google_trends). It is NOT 50+10*z. Do not invert
        # it with (score-50)/10 and call the result a statistical z.
        if z is None and mom is not None and st in {"worked", "partial"}:
            present_no_z.append({
                "platform": name,
                "status": st,
                "reason": (
                    "momentum_0_100 is a project heuristic index on normalized "
                    "relative interest, not a count flow and not a statistical z. "
                    "Formula in social.google_trends: 50 + 50 * clip(0.6*yoy + 0.4*vs_baseline). "
                    "(index-50)/10 is not that formula and is not used."
                ),
                "momentum_0_100": mom,
                "headline": res.get("headline"),
            })
            continue
        if st in {"worked", "partial"} and z is not None:
            w = RELIABILITY.get(name, 0.5)
            scores.append({"platform": name, "z": z, "momentum_0_100": mom, "weight": w, "status": st})
            used.append(name)
        elif st in {"worked", "partial"} and z is None:
            present_no_z.append({
                "platform": name,
                "status": st,
                "reason": res.get("reason") or res.get("notes") or "worked, but no z-score (single snapshot / lifetime total / list position)",
                "headline": res.get("headline"),
                "viewCount": res.get("viewCount"),
                "videoCount": res.get("videoCount"),
                "best_rank": res.get("best_rank"),
            })
        else:
            missing.append({"platform": name, "status": st, "reason": res.get("reason") or res.get("notes") or "no z-score"})
    if not scores:
        return {
            "ok": False,
            "corroborated": False,
            "n_confirming": 0,
            "platforms_used": [],
            "platforms_present_no_z": present_no_z,
            "platforms_missing": missing,
            "weighted_z": None,
            "composite_0_100": None,
            "note": "No platform produced a usable z-score. Nothing was imputed.",
        }
    wsum = sum(s["weight"] for s in scores)
    wz = sum(s["z"] * s["weight"] for s in scores) / wsum
    # Confirming = z > 0.5 (rising vs own baseline)
    rising = [s for s in scores if s["z"] is not None and s["z"] > 0.5]
    falling = [s for s in scores if s["z"] is not None and s["z"] < -0.5]
    return {
        "ok": True,
        "corroborated": len(rising) >= min_confirm,
        "n_confirming": len(rising),
        "n_fading": len(falling),
        "min_confirm": min_confirm,
        "platforms_used": used,
        "platforms_present_no_z": present_no_z,
        "platforms_missing": missing,
        "components": scores,
        "weighted_z": round(wz, 3),
        "composite_0_100": round(max(0.0, min(100.0, 50.0 + 10.0 * wz)), 2),
        "interpretation": (
            f"{len(rising)} platform(s) show a rise vs their own baseline"
            + ("; treated as corroborated." if len(rising) >= min_confirm else "; below the 2-platform confirmation threshold.")
        ),
    }


def collect_signals(symbol: str, keywords: list[str] | None = None, wiki_article: str | None = None) -> dict:
    """Live multi-platform pull for one ticker. Degrades honestly."""
    from .social import google_trends

    kws = keywords or [symbol]
    primary = kws[0]
    out: dict[str, Any] = {
        "symbol": symbol,
        "keywords": kws,
        "retrieved_at_utc": now_utc(),
        "platforms": {},
    }
    # Trends
    try:
        tr = google_trends(kws, geo="US", timeframe="today 5-y")
        mom = (tr.get("momentum") or {}).get(primary) or {}
        out["platforms"]["google_trends"] = {
            "status": "worked" if tr.get("ok") else "blocked",
            "ok": bool(tr.get("ok")),
            "momentum_0_100": mom.get("momentum_0_100"),
            "reason": tr.get("error"),
            "method": "pytrends unofficial API",
            "source_url": "https://trends.google.com/trends/",
            "retrieved_at_utc": now_utc(),
        }
    except Exception as e:
        out["platforms"]["google_trends"] = {"status": "error", "reason": str(e)}

    if wiki_article:
        out["platforms"]["wikipedia"] = wikipedia_pageviews(wiki_article)
    out["platforms"]["google_news"] = google_news_rss(primary)

    # TikTok / Amazon: default to the verified public-sample cache.
    # Lifetime hashtag totals and a single BSR do not produce a z-score.
    # Set CCT_LIVE_TIKTOK=1 or CCT_LIVE_AMAZON=1 only when a live refetch is wanted.
    import os
    from . import tiktok as tiktok_mod
    from . import amazon as amazon_mod

    if os.environ.get("CCT_LIVE_TIKTOK") == "1":
        tag = tiktok_mod.PREFERRED_HASHTAG.get(symbol.upper()) or primary
        out["platforms"]["tiktok"] = tiktok_mod.fetch_challenge_detail_inpage(tag)
    else:
        out["platforms"]["tiktok"] = tiktok_mod.signal_for_ticker(symbol)

    if os.environ.get("CCT_LIVE_AMAZON") == "1":
        out["platforms"]["amazon_movers"] = amazon_mod.fetch_bestsellers(
            "https://www.amazon.com/gp/bestsellers/"
        )
    else:
        out["platforms"]["amazon_movers"] = amazon_mod.signal_for_ticker(symbol)

    out["corroboration"] = corroborate(out["platforms"])
    return out
