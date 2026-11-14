"""Public TikTok hashtag adapters. No login, no paywall bypass.

Preferred path: the public `/api/challenge/detail/` endpoint, fetched
in-page after a Scrapling StealthyFetcher session on tiktok.com (or via
davidteather/TikTok-Api `hashtag.info()`, which returns the same
challengeInfo shape). Prefer `statsV2` (exact string counts) over
`stats` (rounded; `videoCount` overflows to 0 on large tags).

Lifetime totals are a stock, not a short-window flow. A single snapshot
does not produce a momentum z-score. Creative Center's public
GetHashtagList returns only the unauthenticated top 3 (further rows
behind login); sample brands are looked up via challenge/detail instead.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .provenance import now_utc

# Generic words that collide with the brand. Recorded, but not used as
# the preferred ticker tag.
NOISY_HASHTAGS = frozenset({"coach", "lulu", "slime"})

PREFERRED_HASHTAG = {
    "CROX": "crocs",
    "LULU": "lululemon",
    "ELF": "elfcosmetics",
    "TPR": "coachbag",
    "NWL": "elmersslime",
}

SAMPLE_HASHTAGS = {
    "CROX": ["crocs", "crocsshoes", "crocsclassicclog"],
    "LULU": ["lululemon", "lulu"],
    "ELF": ["elfcosmetics", "elfbeauty", "elfmakeup"],
    "TPR": ["coach", "coachbag", "coachnewyork"],
    "NWL": ["elmersslime", "elmersglue", "slime"],
}

CHALLENGE_DETAIL = (
    "https://www.tiktok.com/api/challenge/detail/"
    "?challengeName={name}&aid=1988&app_name=tiktok_web"
    "&channel=tiktok_web&device_platform=web_pc"
)
CC_PAGE = "https://ads.tiktok.com/creative/creativeCenter/trends/hashtag?period=7&region=US"
CC_API = "https://ads.tiktok.com/CreativeOne/KnowledgeAPI/GetHashtagList"
TAG_PAGE = "https://www.tiktok.com/tag/{name}"

_REPO_DATA = Path(__file__).resolve().parents[2] / "data" / "tiktok"


def parse_challenge_info(payload: dict) -> dict:
    """Pull exact statsV2 (preferred) and rounded stats from a challenge/detail or TikTokApi payload."""
    if not isinstance(payload, dict):
        return {"ok": False, "reason": "payload is not a dict"}
    # Accept raw API body, our saved wrapper, or TikTokApi hashtag.info() dict
    body = payload
    if "challengeInfo" not in body and "info" in body:
        body = body.get("info") or body
    if "challengeInfo" not in body and "challengeInfo_slim" in body:
        # already-slimmed save
        slim = body["challengeInfo_slim"]
        stats = body.get("stats") or slim.get("stats") or {}
        stats_v2 = body.get("statsV2") or slim.get("statsV2") or {}
        ch = slim.get("challenge") or {}
        return {
            "ok": True,
            "challenge_id": body.get("challenge_id") or ch.get("id"),
            "title": body.get("title") or ch.get("title"),
            "stats": stats,
            "statsV2": stats_v2,
            "viewCount": _int(stats_v2.get("viewCount") or body.get("viewCount") or stats.get("viewCount")),
            "videoCount": _int(stats_v2.get("videoCount") or body.get("videoCount") or stats.get("videoCount")),
            "viewCount_rounded": _int(stats.get("viewCount")),
        }
    ci = body.get("challengeInfo") or {}
    ch = ci.get("challenge") or {}
    stats = ci.get("stats") or ch.get("stats") or {}
    stats_v2 = ci.get("statsV2") or {}
    if not stats_v2 and not stats:
        return {"ok": False, "reason": "no challengeInfo.stats / statsV2", "status_code": body.get("status_code")}
    return {
        "ok": True,
        "challenge_id": ch.get("id"),
        "title": ch.get("title"),
        "stats": stats,
        "statsV2": stats_v2,
        "viewCount": _int(stats_v2.get("viewCount") or stats.get("viewCount")),
        "videoCount": _int(stats_v2.get("videoCount") or stats.get("videoCount")),
        "viewCount_rounded": _int(stats.get("viewCount")),
        "status_code": body.get("status_code"),
    }


def parse_creative_center_list(payload: dict) -> dict:
    """Parse a captured GetHashtagList XHR (our wrapper with meta/body, or the raw body)."""
    if not isinstance(payload, dict):
        return {"ok": False, "items": [], "reason": "not a dict"}
    body = payload.get("body") if "body" in payload and "items" not in payload else payload
    if "items" not in body and isinstance(body, dict) and "body" in body:
        body = body["body"]
    items = []
    for it in (body.get("items") or []):
        items.append({
            "rank": _int(it.get("rankIndex")),
            "hashtag": it.get("hashtagName"),
            "hashtag_id": it.get("hashtagID"),
            "publishCnt": _int(it.get("publishCnt")),
            "vv": _int(it.get("vv")),
            "popularityCurve": it.get("popularityCurve"),
            "topCreators": it.get("topCreators"),
        })
    pag = body.get("pagination") or {}
    return {
        "ok": bool(items),
        "items": items,
        "pagination": pag,
        "totalCount": pag.get("totalCount"),
        "hasMore": pag.get("hasMore"),
        "note": (
            "Unauthenticated public list is capped at totalCount="
            f"{pag.get('totalCount')}; further Creative Center analytics appear to need a login, which we do not use."
        ),
    }


def quality_for(hashtag: str) -> str:
    return "noisy_generic_word" if hashtag.lower() in NOISY_HASHTAGS else "specific"


def load_sample(path: Path | None = None) -> dict:
    p = path or (_REPO_DATA / "sample_hashtag_counts.json")
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def signal_for_ticker(ticker: str, sample: dict | None = None) -> dict:
    """Build a corroboration-ready signal from the verified sample (no live Chromium).

    Lifetime view/video counts are returned as facts. `z_last_vs_history` is
    left unset — a single cumulative snapshot is not a momentum z-score.
    """
    sample = sample if sample is not None else load_sample()
    preferred = PREFERRED_HASHTAG.get(ticker.upper())
    primary = (sample.get("primary_challenge_detail") or {})
    rec = _lookup_tag(primary, ticker.upper(), preferred) if preferred else None
    out: dict[str, Any] = {
        "platform": "tiktok",
        "ok": False,
        "status": "partial",
        "ticker": ticker.upper(),
        "preferred_hashtag": preferred,
        "method": "cached official /api/challenge/detail/ (StealthyFetcher in-page fetch); see data/tiktok/sample_hashtag_counts.json",
        "source_url": TAG_PAGE.format(name=preferred or ""),
        "retrieved_at_utc": (rec or {}).get("retrieved_at_utc"),
        "notes": (
            "Lifetime cumulative counts (stock), not a 7-day flow. "
            "No z-score is computed from a single snapshot. "
            "TikTokApi hashtag.info() repeats the same challengeInfo upstream on #crocs, #lululemon, #elfcosmetics. That is a retrieval check, not a second demand source."
        ),
    }
    if not rec:
        out["reason"] = f"no verified sample for {ticker} / #{preferred}"
        out["status"] = "partial"
        return out
    out.update({
        "ok": True,
        "status": "worked",
        "hashtag": rec.get("hashtag"),
        "quality": rec.get("quality") or quality_for(rec.get("hashtag") or ""),
        "viewCount": _int(rec.get("viewCount")),
        "videoCount": _int(rec.get("videoCount")),
        "statsV2": rec.get("statsV2"),
        "challenge_id": rec.get("challenge_id"),
        "api_url": rec.get("api_url"),
        "source_url": rec.get("source_url") or out["source_url"],
        "method": rec.get("method") or out["method"],
        # Explicitly no z
        "z_last_vs_history": None,
    })
    # Sibling tags for the same ticker
    siblings = []
    for name, row in primary.items():
        tag = (row.get("hashtag") or name.split(":")[-1])
        if row.get("ticker") == ticker.upper() and tag != preferred:
            siblings.append({
                "hashtag": tag,
                "viewCount": _int(row.get("viewCount")),
                "videoCount": _int(row.get("videoCount")),
                "quality": row.get("quality") or quality_for(tag),
            })
    out["other_tags"] = siblings
    cross = (sample.get("crosscheck_tiktokapi") or {}).get(preferred or "")
    if cross:
        out["tiktokapi_crosscheck"] = {
            "viewCount": _int((cross.get("statsV2") or {}).get("viewCount")),
            "videoCount": _int((cross.get("statsV2") or {}).get("videoCount")),
            "viewCount_rounded": _int((cross.get("stats") or {}).get("viewCount")),
            "retrieved_at_utc": cross.get("retrieved_at_utc"),
            "method": cross.get("method"),
        }
    return out


def fetch_challenge_detail_inpage(hashtag: str, headless: bool = True) -> dict:
    """Live public fetch via StealthyFetcher + in-page fetch(). Optional; needs scrapling + patchright.

    Set CCT_LIVE_TIKTOK=1 to use this from collect_signals. Rate-limit yourself.
    """
    out: dict[str, Any] = {
        "platform": "tiktok",
        "hashtag": hashtag,
        "ok": False,
        "status": "error",
        "source_url": TAG_PAGE.format(name=hashtag),
        "api_url": CHALLENGE_DETAIL.format(name=hashtag),
        "method": "StealthyFetcher in-page fetch of public /api/challenge/detail/",
        "retrieved_at_utc": now_utc(),
    }
    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError as e:
        out.update({"status": "skipped", "reason": f"scrapling not installed: {e}"})
        return out

    api = CHALLENGE_DETAIL.format(name=hashtag)

    def page_action(page):
        return page.evaluate(
            """async (url) => {
                const r = await fetch(url, {credentials: 'include'});
                return {status: r.status, body: await r.text()};
            }""",
            api,
        )

    try:
        # Navigate to the public tag page first so the in-page fetch carries a real session.
        res = StealthyFetcher.fetch(
            TAG_PAGE.format(name=hashtag),
            headless=headless,
            network_idle=True,
            page_action=page_action,
        )
        action = getattr(res, "page_action_result", None) or getattr(res, "action_result", None)
        # scrapling may return the evaluate result directly from page_action
        if action is None:
            # Some versions return the page_action value as the fetch result body
            action = res
        payload = action
        if isinstance(payload, dict) and "body" in payload:
            status = payload.get("status")
            raw = payload.get("body")
            body = json.loads(raw) if isinstance(raw, str) else raw
            out["http_status"] = status
        elif isinstance(payload, dict) and ("challengeInfo" in payload or "status_code" in payload):
            body = payload
        else:
            out.update({"status": "partial", "reason": f"unexpected page_action result: {type(payload)}"})
            return out
        parsed = parse_challenge_info(body)
        if parsed.get("ok"):
            out.update(parsed)
            out["ok"] = True
            out["status"] = "worked"
        else:
            out.update({"status": "partial", "reason": parsed.get("reason"), "raw_keys": list(body)[:12] if isinstance(body, dict) else None})
        return out
    except Exception as e:
        out["reason"] = str(e)
        return out


def _lookup_tag(primary: dict, ticker: str, hashtag: str) -> dict | None:
    if not hashtag:
        return None
    if hashtag in primary:
        return primary[hashtag]
    key = f"{ticker}:{hashtag}"
    if key in primary:
        return primary[key]
    for _k, row in primary.items():
        if (row or {}).get("hashtag") == hashtag and (
            not ticker or (row.get("ticker") == ticker)
        ):
            return row
    return None


def _int(v) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None
