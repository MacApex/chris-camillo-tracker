"""Niche / social signals: Google Trends (pytrends), Reddit public JSON, optional X."""

from __future__ import annotations

import datetime as dt
import os
import time
from typing import Any
from urllib.parse import quote

import requests

USER_AGENT = (
    "ChrisCamilloTracker/1.0 (research toolkit; +https://github.com/MacApex/chris-camillo-tracker)"
)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return s


# ---------- Google Trends ----------

def _patch_urllib3_retry():
    """pytrends still passes method_whitelist, removed in urllib3 v2."""
    try:
        import urllib3.util.retry as retry_mod
        if getattr(retry_mod.Retry, "_cct_patched", False):
            return
        _orig = retry_mod.Retry.__init__

        def _init(self, *args, **kwargs):
            kwargs.pop("method_whitelist", None)
            return _orig(self, *args, **kwargs)

        retry_mod.Retry.__init__ = _init
        retry_mod.Retry._cct_patched = True
    except Exception:
        pass


def google_trends(keywords: list[str], geo: str = "US", timeframe: str = "today 5-y") -> dict:
    """Interest-over-time via pytrends. May fail under Google rate limits."""
    _patch_urllib3_retry()
    keywords = [k for k in keywords if k][:5]
    result: dict[str, Any] = {
        "keywords": keywords,
        "geo": geo,
        "timeframe": timeframe,
        "source": "Google Trends via pytrends (unofficial, rate-limited)",
        "ok": False,
    }
    if not keywords:
        result["error"] = "no keywords"
        return result
    try:
        from pytrends.request import TrendReq

        # A browser-like User-Agent reduces some 429s; still fragile.
        pytrends = TrendReq(
            hl="en-US",
            tz=480,  # Asia/Shanghai UTC+8, in minutes
            retries=3,
            backoff_factor=0.6,
            requests_args={"headers": {"User-Agent": USER_AGENT}},
        )
        pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
        df = pytrends.interest_over_time()
        if df is None or df.empty:
            result["error"] = "empty Trends response (rate limit or no data)"
            return result
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])
        series = {}
        momentum = {}
        for col in df.columns:
            vals = [int(v) for v in df[col].tolist()]
            dates = [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in df.index]
            series[col] = [{"date": d, "value": v} for d, v in zip(dates, vals)]
            # Camillo's seasonal advice: compare recent window to the same window
            # a year earlier, and to a longer baseline, using the 5-year series.
            n = len(vals)
            recent = vals[-13:]  # ~1 quarter of weekly points
            year_ago = vals[-65:-52] if n >= 65 else vals[: max(1, n // 5)]
            baseline = vals[:-13] if n > 26 else vals
            r = sum(recent) / max(1, len(recent))
            y = sum(year_ago) / max(1, len(year_ago))
            b = sum(baseline) / max(1, len(baseline))
            yoy = (r - y) / (y + 1e-6)
            vs_base = (r - b) / (b + 1e-6)
            # 0-100 momentum: 50 = flat; clip extreme spikes
            mom = 50.0 + 50.0 * max(-1.0, min(1.5, 0.6 * yoy + 0.4 * vs_base))
            momentum[col] = {
                "recent_avg": round(r, 2),
                "year_ago_avg": round(y, 2),
                "baseline_avg": round(b, 2),
                "yoy_change": round(yoy, 4),
                "vs_baseline": round(vs_base, 4),
                "momentum_0_100": round(max(0.0, min(100.0, mom)), 2),
            }
        result["series"] = series
        result["momentum"] = momentum
        # Combined: average across keywords (first keyword is usually the brand)
        moms = [m["momentum_0_100"] for m in momentum.values()]
        result["combined_momentum"] = round(sum(moms) / len(moms), 2) if moms else None
        result["ok"] = True
        result["note"] = (
            "Google Trends is relative (0-100) and can be distorted by seasonality "
            "and, as Camillo later argued (2025), by AI-generated query traffic. "
            "Treat spikes that contradict other signals with caution."
        )
        return result
    except Exception as exc:
        result["error"] = f"pytrends failed: {exc}"
        return result


# ---------- Reddit (public JSON, no API key) ----------

REDDIT_SUBS = ["wallstreetbets", "stocks", "investing", "StockMarket", "options"]


def reddit_mentions(symbol: str, company: str | None = None, limit: int = 40) -> dict:
    """Search Reddit via public JSON endpoints. No OAuth; subject to 429s."""
    session = _session()
    # Reddit prefers a distinctive UA; anonymous JSON is best-effort.
    session.headers["User-Agent"] = USER_AGENT
    queries = [f"${symbol}", symbol]
    if company:
        queries.append(f'"{company}"')
    posts: list[dict] = []
    errors: list[str] = []
    seen = set()

    def _pull(url: str) -> list[dict]:
        try:
            r = session.get(url, timeout=20)
            if r.status_code != 200:
                errors.append(f"{r.status_code} for {url[:80]}")
                return []
            data = r.json()
            children = (data.get("data") or {}).get("children") or []
            out = []
            for ch in children:
                d = ch.get("data") or {}
                pid = d.get("id")
                if not pid or pid in seen:
                    continue
                seen.add(pid)
                title = d.get("title") or ""
                body = d.get("selftext") or ""
                out.append({
                    "id": pid,
                    "subreddit": d.get("subreddit"),
                    "title": title,
                    "text": (title + "\n" + body).strip()[:500],
                    "score": d.get("score"),
                    "num_comments": d.get("num_comments"),
                    "created_utc": d.get("created_utc"),
                    "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
                })
            return out
        except Exception as exc:
            errors.append(str(exc))
            return []

    # Global search
    q = quote(f"${symbol} OR {symbol}")
    posts.extend(_pull(f"https://www.reddit.com/search.json?q={q}&sort=new&limit={limit}&t=month&restrict_sr=0"))
    time.sleep(0.6)
    # Subreddit-specific
    for sub in REDDIT_SUBS:
        url = (
            f"https://www.reddit.com/r/{sub}/search.json?q={quote(symbol)}"
            f"&restrict_sr=1&sort=new&limit=15&t=month"
        )
        posts.extend(_pull(url))
        time.sleep(0.5)
        if len(posts) >= limit:
            break

    # Datacenter IPs are often 403'd by Reddit's public JSON. Try PullPush
    # (a Pushshift-style archive) as a best-effort fallback.
    if not posts:
        try:
            pr = session.get(
                "https://api.pullpush.io/reddit/search/submission/",
                params={"q": symbol, "size": min(limit, 40), "sort": "desc", "sort_type": "created_utc"},
                timeout=20,
            )
            if pr.status_code == 200:
                for d in (pr.json().get("data") or [])[:limit]:
                    pid = str(d.get("id") or "")
                    if not pid or pid in seen:
                        continue
                    seen.add(pid)
                    title = d.get("title") or ""
                    body = d.get("selftext") or ""
                    posts.append({
                        "id": pid,
                        "subreddit": d.get("subreddit"),
                        "title": title,
                        "text": (title + "\n" + body).strip()[:500],
                        "score": d.get("score"),
                        "num_comments": d.get("num_comments"),
                        "created_utc": d.get("created_utc"),
                        "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
                        "via": "pullpush",
                    })
                if posts:
                    errors.append("Reddit public JSON blocked; used PullPush archive instead.")
            else:
                errors.append(f"PullPush fallback HTTP {pr.status_code}")
        except Exception as exc:
            errors.append(f"PullPush fallback failed: {exc}")

    from .sentiment import score_texts

    texts = [p["text"] for p in posts]
    sent = score_texts(texts, source="reddit")
    # Volume signal: more posts in a month is modest momentum; we don't have a
    # long baseline from a single pull, so we score volume on a soft curve.
    n = len(posts)
    volume_0_100 = round(max(0.0, min(100.0, 15.0 * (n ** 0.5))), 2)
    sent_0_100 = round(max(0.0, min(100.0, 50.0 + 50.0 * sent.score)), 2)
    combined = round(0.55 * sent_0_100 + 0.45 * volume_0_100, 2) if n else None

    return {
        "symbol": symbol,
        "source": "Reddit public JSON (unofficial, unauthenticated)",
        "ok": n > 0 or not errors,
        "n_posts": n,
        "posts": posts[:limit],
        "sentiment": {
            "score": sent.score,
            "label": sent.label,
            "engine": sent.engine,
            "n_texts": sent.n_texts,
        },
        "volume_0_100": volume_0_100,
        "sentiment_0_100": sent_0_100,
        "combined_0_100": combined,
        "errors": errors,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


# ---------- Optional X / Twitter ----------

def x_mentions(symbol: str) -> dict:
    """Optional X search. Requires a bearer token in CCT_X_BEARER; otherwise skipped."""
    token = os.environ.get("CCT_X_BEARER") or os.environ.get("TWITTER_BEARER_TOKEN")
    if not token:
        return {
            "ok": False,
            "skipped": True,
            "reason": "No CCT_X_BEARER / TWITTER_BEARER_TOKEN set; X is optional.",
        }
    try:
        r = requests.get(
            "https://api.x.com/2/tweets/search/recent",
            params={
                "query": f"${symbol} -is:retweet lang:en",
                "max_results": 25,
                "tweet.fields": "created_at,public_metrics,lang",
            },
            headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
            timeout=20,
        )
        if r.status_code != 200:
            return {"ok": False, "error": f"X API {r.status_code}: {r.text[:200]}"}
        data = r.json().get("data") or []
        from .sentiment import score_texts

        texts = [t.get("text") or "" for t in data]
        sent = score_texts(texts, source="x")
        return {
            "ok": True,
            "n": len(data),
            "sentiment": {"score": sent.score, "label": sent.label, "engine": sent.engine},
            "tweets": [{"id": t.get("id"), "text": (t.get("text") or "")[:240]} for t in data],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
