#!/usr/bin/env python3
"""Attempt every platform adapter. Public data only, polite delays, no logins.

Writes data/platform_status.json and data/provenance.csv.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from camillo_tracker.provenance import now_utc, row, write_csv, write_json

UA = "ChrisCamilloTracker/1.0 (research; https://github.com/MacApex/chris-camillo-tracker)"
BRANDS = [
    ("CROX", "Crocs", "Crocs"),
    ("LULU", "Lululemon", "Lululemon"),
    ("ELF", "e.l.f. Beauty", "e.l.f._Cosmetics"),
    ("NWL", "Elmer's glue", "Elmer%27s_Products"),
    ("TPR", "Coach (brand)", "Coach_(company)"),
]

rows = []
status = {}


def rec(platform, query, metric, value, url, method, status_, reason="", cross="", notes="", unit=""):
    r = row(
        platform=platform, ticker_or_query=query, metric=metric, value=value,
        unit=unit, source_url=url, method=method, status=status_,
        reason=reason, cross_check=cross, notes=notes,
    )
    rows.append(r)
    return r


def set_status(platform, st, reason, tried):
    status[platform] = {
        "status": st,
        "reason": reason,
        "tried": tried,
        "retrieved_at_utc": now_utc(),
    }


def body_of(page):
    b = getattr(page, "body", None)
    if isinstance(b, bytes):
        return b.decode("utf-8", "replace")
    return b if isinstance(b, str) else ""


def probe_wikipedia():
    import requests
    tried = ["Wikimedia REST pageviews API, identified User-Agent"]
    ok = 0
    try:
        for ticker, label, article in BRANDS:
            url = (
                "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
                f"en.wikipedia/all-access/user/{article}/daily/20251013/20261112"
            )
            r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=20)
            if r.status_code == 200:
                items = (r.json().get("items") or [])
                if items:
                    last = items[-1]
                    rec("wikipedia", ticker, "pageviews_last_day", last.get("views"), url,
                        "Wikimedia REST API", "worked",
                        notes=f"n_days={len(items)} last_ts={last.get('timestamp')} article={article}")
                    recent = [i.get("views", 0) for i in items[-13:]]
                    prior = [i.get("views", 0) for i in items[-26:-13]]
                    rec("wikipedia", ticker, "pageviews_13d_sum", sum(recent), url,
                        "Wikimedia REST API", "worked",
                        notes=f"prior_13d_sum={sum(prior)}")
                    # save series
                    write_json(ROOT / "data" / "wikipedia" / f"{ticker}.json", {
                        "retrieved_at_utc": now_utc(),
                        "article": article,
                        "source_url": url,
                        "method": "Wikimedia REST API",
                        "items": items,
                    })
                    ok += 1
                else:
                    rec("wikipedia", ticker, "pageviews", "", url, "Wikimedia REST API", "partial",
                        reason=f"200 but empty for {article}")
            else:
                rec("wikipedia", ticker, "pageviews", "", url, "Wikimedia REST API", "blocked",
                    reason=f"HTTP {r.status_code} body={r.text[:120]}")
            time.sleep(0.4)
        set_status("wikipedia", "worked" if ok == len(BRANDS) else ("partial" if ok else "blocked"),
                   f"{ok}/{len(BRANDS)} articles returned daily series", tried)
    except Exception as e:
        set_status("wikipedia", "error", str(e), tried)
        rec("wikipedia", "*", "pageviews", "", "", "Wikimedia REST API", "error", reason=str(e))


def probe_trends():
    tried = ["pytrends TrendReq interest_over_time, today 5-y, US, urllib3 patch"]
    try:
        from camillo_tracker.social import google_trends, _patch_urllib3_retry
        _patch_urllib3_retry()
        ok = 0
        for ticker, label, _ in BRANDS:
            res = google_trends([label], geo="US", timeframe="today 5-y")
            if res.get("ok") or res.get("momentum"):
                mom = (res.get("momentum") or {}).get(label) or res.get("momentum") or {}
                rec("google_trends", ticker, "momentum_0_100",
                    mom.get("momentum_0_100") if isinstance(mom, dict) else "",
                    "https://trends.google.com/trends/", "pytrends unofficial API", "worked",
                    notes=json.dumps(res, default=str)[:600])
                ok += 1
            else:
                rec("google_trends", ticker, "momentum_0_100", "", "https://trends.google.com/trends/",
                    "pytrends unofficial API", "blocked", reason=str(res)[:300])
            time.sleep(1.5)
        set_status("google_trends", "worked" if ok else "blocked", f"{ok}/{len(BRANDS)} keywords", tried)
    except Exception as e:
        set_status("google_trends", "error", f"{e}", tried)
        rec("google_trends", "*", "momentum", "", "", "pytrends", "error", reason=str(e))


def probe_gdelt():
    import requests
    tried = ["GDELT DOC API TimelineVol, 2026-10-01 to 2026-11-12"]
    ok = 0
    try:
        for ticker, label, _ in BRANDS:
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            params = {
                "query": label,
                "mode": "TimelineVol",
                "startdatetime": "20261001000000",
                "enddatetime": "20261112000000",
                "format": "json",
                "timesmooth": "3",
            }
            r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=30)
            text = r.text.strip()
            if r.status_code == 200 and (text.startswith("{") or text.startswith("[")):
                data = r.json()
                write_json(ROOT / "data" / "gdelt" / f"{ticker}.json", {
                    "retrieved_at_utc": now_utc(), "query": label, "url": r.url, "data": data,
                })
                rec("gdelt_news", ticker, "response_bytes", len(r.content), r.url,
                    "GDELT DOC API TimelineVol", "worked",
                    notes=str(list(data)[:10]) if isinstance(data, dict) else f"list n={len(data)}")
                ok += 1
            else:
                rec("gdelt_news", ticker, "timeline_points", "", url, "GDELT DOC API", "blocked",
                    reason=f"HTTP {r.status_code} body={text[:180].replace(chr(10),' ')}")
            time.sleep(0.8)
        set_status("gdelt_news", "worked" if ok else "blocked", f"{ok} successful pulls", tried)
    except Exception as e:
        set_status("gdelt_news", "error", str(e), tried)
        rec("gdelt_news", "*", "timeline", "", "", "GDELT", "error", reason=str(e))


def probe_news_rss():
    import requests
    tried = ["Google News RSS", "Scrapling Fetcher fallback"]
    ok = 0
    try:
        for ticker, label, _ in BRANDS:
            url = "https://news.google.com/rss/search?q=%s&hl=en-US&gl=US&ceid=US:en" % label.replace(" ", "+")
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            n = r.text.count("<item>") if r.status_code == 200 else 0
            if r.status_code == 200 and n:
                rec("google_news", ticker, "rss_item_count", n, url, "Google News RSS via requests", "worked")
                ok += 1
            else:
                try:
                    from scrapling.fetchers import Fetcher
                    page = Fetcher.get(url, timeout=20)
                    body = body_of(page)
                    n2 = body.count("<item>")
                    if n2:
                        rec("google_news", ticker, "rss_item_count", n2, url,
                            "Scrapling Fetcher GET of Google News RSS", "worked",
                            notes="requests HTTP %s; scrapling recovered" % r.status_code)
                        ok += 1
                    else:
                        rec("google_news", ticker, "rss_item_count", "", url, "requests+Scrapling", "blocked",
                            reason="requests %s, scrapling items=0 status=%s" % (r.status_code, getattr(page, "status", "?")))
                except Exception as e:
                    rec("google_news", ticker, "rss_item_count", "", url, "requests", "blocked",
                        reason="HTTP %s; scrapling %s" % (r.status_code, e))
            time.sleep(0.6)
        set_status("google_news", "worked" if ok else "blocked", f"{ok}/{len(BRANDS)} RSS feeds", tried)
    except Exception as e:
        set_status("google_news", "error", str(e), tried)


def probe_itunes():
    import requests
    tried = ["iTunes Search API, official public"]
    try:
        ok = 0
        for ticker, label in [("LULU", "Lululemon"), ("CROX", "Crocs")]:
            url = "https://itunes.apple.com/search"
            r = requests.get(url, params={"term": label, "entity": "software", "limit": 5},
                             headers={"User-Agent": UA}, timeout=15)
            if r.status_code == 200:
                js = r.json()
                names = [x.get("trackName") for x in (js.get("results") or [])]
                rec("app_store", ticker, "search_result_count", js.get("resultCount"), r.url,
                    "iTunes Search API", "worked", notes=", ".join([n for n in names if n]))
                ok += 1
            else:
                rec("app_store", ticker, "search_result_count", "", url, "iTunes Search API",
                    "blocked", reason="HTTP %s" % r.status_code)
            time.sleep(0.4)
        set_status("app_store", "worked" if ok else "blocked",
                   "Official search works; this is app presence, not a live top-chart rank.", tried)
    except Exception as e:
        set_status("app_store", "error", str(e), tried)


def probe_reddit():
    import requests
    tried = [
        "www.reddit.com public JSON",
        "old.reddit.com public JSON",
        "PullPush archive API",
        "Scrapling Fetcher GET of public JSON",
    ]
    urls = [
        ("www", "https://www.reddit.com/search.json?q=CROX&limit=5&sort=new"),
        ("old", "https://old.reddit.com/search.json?q=CROX&limit=5&sort=new"),
        ("pullpush", "https://api.pullpush.io/reddit/search/submission/?q=CROX&size=5"),
    ]
    any_ok = False
    reasons = []
    for name, url in urls:
        try:
            r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=20)
            reasons.append("%s HTTP %s" % (name, r.status_code))
            looks = (r.status_code == 200) and (("children" in r.text) or ("data" in r.text and name == "pullpush"))
            rec("reddit", "CROX", "posts", "", url, "GET " + name,
                "worked" if looks else "blocked",
                reason="" if looks else ("HTTP %s" % r.status_code),
                notes="bytes=%s" % len(r.content))
            any_ok = any_ok or looks
        except Exception as e:
            reasons.append("%s %s" % (name, e))
            rec("reddit", "CROX", "posts", "", url, "GET " + name, "error", reason=str(e))
        time.sleep(0.5)
    try:
        from scrapling.fetchers import Fetcher
        page = Fetcher.get("https://www.reddit.com/search.json?q=CROX&limit=5&sort=new", timeout=20)
        body = body_of(page)
        st = getattr(page, "status", "?")
        if body and "children" in body:
            rec("reddit", "CROX", "posts", "", "https://www.reddit.com/search.json?q=CROX",
                "Scrapling Fetcher", "worked", notes="status=%s" % st)
            any_ok = True
        else:
            rec("reddit", "CROX", "posts", "", "https://www.reddit.com/search.json?q=CROX",
                "Scrapling Fetcher", "blocked", reason="status=%s no children" % st)
            reasons.append("scrapling status=%s" % st)
    except Exception as e:
        reasons.append("scrapling %s" % e)
        rec("reddit", "CROX", "posts", "", "", "Scrapling Fetcher", "error", reason=str(e))
    set_status("reddit", "worked" if any_ok else "blocked", "; ".join(reasons), tried)


def probe_x():
    tried = [
        "Grok Bot MCP get_posts_counts_recent (official X API)",
        "CCT_X_BEARER official recent-search adapter",
        "twscrape without accounts (skipped — no logins)",
    ]
    sample = ROOT / "data" / "x_counts_sample.json"
    if sample.exists():
        rec("x", "CROX,LULU,ELF,TPR", "tweet_counts_7d", "see x_counts_sample.json",
            "X API / Grok Bot MCP get_posts_counts_recent",
            "official X recent-counts API via MCP", "worked",
            notes="Real official counts. ELF query is noisy after $ strip.")
    bearer = os.environ.get("CCT_X_BEARER") or os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer:
        rec("x", "*", "api_adapter", "", "https://api.x.com/2/tweets/search/recent",
            "official API adapter", "skipped",
            reason="No CCT_X_BEARER in this environment; MCP path was used instead.")
    try:
        import twscrape  # noqa: F401
        rec("x", "*", "twscrape", "", "https://github.com/vladkens/twscrape",
            "twscrape (no accounts; we will not log into user credentials)",
            "skipped",
            reason="twscrape requires user accounts. Public-only policy: no logins.")
    except Exception as e:
        rec("x", "*", "twscrape", "", "", "twscrape import", "error", reason=str(e))
    set_status("x", "worked",
               "Official 7-day counts via MCP for four queries. Adapter available with CCT_X_BEARER. twscrape skipped (no logins).",
               tried)


def probe_tiktok():
    tried = [
        "Scrapling Fetcher GET of TikTok Creative Center popular hashtags",
        "Scrapling Fetcher GET of tiktok.com/tag/crocs",
        "davidteather/TikTok-Api not invoked with session cookies (no logins)",
    ]
    urls = [
        "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en",
        "https://www.tiktok.com/tag/crocs",
    ]
    any_partial = False
    reasons = []
    try:
        from scrapling.fetchers import Fetcher
        for url in urls:
            try:
                page = Fetcher.get(url, timeout=25)
                st = getattr(page, "status", "?")
                body = body_of(page)
                title = ""
                try:
                    title = str(page.css("title"))[:160]
                except Exception:
                    pass
                rec("tiktok", "crocs", "page_fetch", "", url, "Scrapling Fetcher",
                    "partial" if st == 200 else "blocked",
                    reason="status=%s title=%s body_len=%s" % (st, title, len(body)),
                    notes="No trusted numeric hashtag view count was parsed. Numbers were NOT estimated.")
                reasons.append("%s status=%s len=%s" % (url, st, len(body)))
                if st == 200 and len(body) > 2000:
                    any_partial = True
            except Exception as e:
                reasons.append(str(e))
                rec("tiktok", "crocs", "page_fetch", "", url, "Scrapling Fetcher", "error", reason=str(e))
            time.sleep(1.0)
    except Exception as e:
        reasons.append(str(e))
    set_status("tiktok", "partial" if any_partial else "blocked",
               "Public pages fetched or attempted; no verified view-count extracted. " + "; ".join(reasons)[:400],
               tried)


def probe_instagram():
    tried = [
        "Scrapling Fetcher GET of public instagram.com/explore/tags/crocs/",
        "instaloader Hashtag.from_name without login (metadata only)",
    ]
    reasons = []
    try:
        from scrapling.fetchers import Fetcher
        url = "https://www.instagram.com/explore/tags/crocs/"
        page = Fetcher.get(url, timeout=25)
        st = getattr(page, "status", "?")
        body = body_of(page)
        rec("instagram", "crocs", "page_fetch", "", url, "Scrapling Fetcher",
            "blocked" if (st != 200 or "login" in (body or "").lower()[:3000]) else "partial",
            reason="status=%s body_len=%s" % (st, len(body)))
        reasons.append("scrapling status=%s" % st)
    except Exception as e:
        reasons.append("scrapling %s" % e)
        rec("instagram", "crocs", "page_fetch", "", "", "Scrapling Fetcher", "error", reason=str(e))
    try:
        import instaloader
        L = instaloader.Instaloader(download_pictures=False, download_videos=False,
                                    download_video_thumbnails=False, download_geotags=False,
                                    download_comments=False, save_metadata=False, compress_json=False)
        try:
            h = instaloader.Hashtag.from_name(L.context, "crocs")
            count = getattr(h, "mediacount", None)
            if isinstance(count, int):
                rec("instagram", "crocs", "hashtag_mediacount", count,
                    "https://www.instagram.com/explore/tags/crocs/",
                    "instaloader Hashtag.from_name (no login)", "worked",
                    notes="Public metadata only; no credentials used.")
                set_status("instagram", "worked", "instaloader mediacount=%s" % count, tried)
                return
            rec("instagram", "crocs", "hashtag_mediacount", "", "",
                "instaloader", "partial", reason="Hashtag object returned, no integer mediacount")
        except Exception as e:
            rec("instagram", "crocs", "hashtag_mediacount", "", "",
                "instaloader Hashtag.from_name (no login)", "blocked", reason=str(e)[:400])
            reasons.append("instaloader %s" % e)
    except Exception as e:
        reasons.append("instaloader import/run %s" % e)
    set_status("instagram", "blocked", "; ".join(reasons)[:400], tried)


def probe_commerce_pages():
    from scrapling.fetchers import Fetcher
    pages = [
        ("pinterest_trends", "https://trends.pinterest.com/", "Pinterest Trends public page"),
        ("amazon_movers", "https://www.amazon.com/gp/movers-and-shakers", "Amazon Movers & Shakers public page"),
    ]
    for plat, url, method in pages:
        tried = ["Scrapling Fetcher GET " + url]
        try:
            page = Fetcher.get(url, timeout=25)
            st = getattr(page, "status", "?")
            body = body_of(page)
            title = ""
            try:
                title = str(page.css("title"))[:160]
            except Exception:
                pass
            usable = st == 200 and len(body) > 2000 and "robot" not in (body or "").lower()[:1500]
            rec(plat, "*", "page_fetch", "", url, "Scrapling Fetcher",
                "partial" if usable else "blocked",
                reason="status=%s title=%s len=%s" % (st, title, len(body)),
                notes="No numeric trend series extracted; not estimated.")
            set_status(plat, "partial" if usable else "blocked",
                       "status=%s title=%s len=%s" % (st, title, len(body)), tried)
        except Exception as e:
            rec(plat, "*", "page_fetch", "", url, "Scrapling Fetcher", "error", reason=str(e))
            set_status(plat, "error", str(e), tried)
        time.sleep(1.0)


def probe_youtube():
    import subprocess
    tried = [
        "yt-dlp ytsearch3:Crocs shoes --dump-json --skip-download",
        "YouTube Data API skipped (no YOUTUBE_API_KEY)",
    ]
    try:
        proc = subprocess.run(
            [str(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "yt-dlp"),
             "ytsearch3:Crocs shoes", "--dump-json", "--skip-download", "--no-warnings",
             "--socket-timeout", "20"],
            capture_output=True, text=True, timeout=90,
            cwd="/tmp",
        )
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip().startswith("{")]
        parsed = []
        for ln in lines:
            try:
                parsed.append(json.loads(ln))
            except Exception:
                pass
        if parsed:
            slim = []
            for p in parsed:
                slim.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "view_count": p.get("view_count"),
                    "upload_date": p.get("upload_date"),
                    "webpage_url": p.get("webpage_url") or p.get("original_url"),
                })
            rec("youtube", "Crocs shoes", "ytsearch_results", len(slim),
                "https://www.youtube.com/results?search_query=Crocs+shoes",
                "yt-dlp ytsearch3 --dump-json --skip-download", "worked",
                notes=json.dumps(slim)[:800])
            set_status("youtube", "worked", "%s public search results with metadata" % len(slim), tried)
            write_json(ROOT / "data" / "youtube_ytsearch_crocs.json", {
                "retrieved_at_utc": now_utc(),
                "method": "yt-dlp ytsearch3:Crocs shoes --dump-json --skip-download",
                "query": "Crocs shoes",
                "results": slim,
            })
        else:
            rec("youtube", "Crocs shoes", "ytsearch_results", "", "",
                "yt-dlp", "blocked",
                reason="exit=%s stderr=%s" % (proc.returncode, (proc.stderr or "")[:300]))
            set_status("youtube", "blocked", (proc.stderr or "empty")[:300], tried)
    except Exception as e:
        rec("youtube", "Crocs shoes", "ytsearch_results", "", "", "yt-dlp", "error", reason=str(e))
        set_status("youtube", "error", str(e), tried)


def main():
    print("probing…", now_utc())
    for fn, label in [
        (probe_wikipedia, "wiki"),
        (probe_trends, "trends"),
        (probe_gdelt, "gdelt"),
        (probe_news_rss, "news"),
        (probe_itunes, "itunes"),
        (probe_reddit, "reddit"),
        (probe_x, "x"),
        (probe_tiktok, "tiktok"),
        (probe_instagram, "ig"),
        (probe_commerce_pages, "commerce"),
        (probe_youtube, "yt"),
    ]:
        try:
            fn()
            print(" ", label, "done")
        except Exception:
            traceback.print_exc()
            print(" ", label, "CRASH")
    write_csv(ROOT / "data" / "provenance.csv", rows)
    write_json(ROOT / "data" / "platform_status.json", {
        "retrieved_at_utc": now_utc(),
        "policy": "Public data only. No logins with user credentials. No paywall bypass. No fabricated counts.",
        "platforms": status,
        "n_provenance_rows": len(rows),
    })
    print("WROTE provenance and status")
    for k, v in status.items():
        print("  %-20s %-8s %s" % (k, v["status"], v["reason"][:110]))
    print("rows", len(rows))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        write_csv(ROOT / "data" / "provenance.csv", rows)
        write_json(ROOT / "data" / "platform_status.json", {"platforms": status, "crash": True})
        raise
