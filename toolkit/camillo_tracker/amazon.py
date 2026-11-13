"""Public Amazon Best Sellers / product-page BSR adapters. No login.

Ranks come from the official `data-client-recs-list` JSON embedded in
public Best Sellers pages (`metadataMap["render.zg.rank"]`). Brand
matches are on the PRODUCT TITLE only — matching the surrounding HTML
context caused false positives (EverFoams titled as Crocs, "elf" inside
"yourself", etc.) and those were discarded.

A single BSR is a position on one list at one moment, not a z-score.
Movers & Shakers pages often omit this JSON for a plain Fetcher (JS).
CamelCamelCamel returned Cloudflare 403; Keepa SPA HTML had no BSR
numbers; we did not bypass either.
"""
from __future__ import annotations

import html as htmlmod
import json
import re
from pathlib import Path
from typing import Any

from .provenance import now_utc

# Title-only brand tokens. "elf" must not be used alone (matches yourself/shelf);
# we look for "e.l.f." or "elf " / "elf." as a brand prefix.
BRAND_PATTERNS: list[tuple[str, str, re.Pattern]] = [
    ("CROX", "crocs", re.compile(r"\bcrocs\b", re.I)),
    ("LULU", "lululemon", re.compile(r"\blululemon\b|\blulu\s*lemon\b", re.I)),
    ("ELF", "e.l.f.", re.compile(r"\be\.l\.f\.|\belf\s+cosmetics\b|\belf\s+(instant|cream|halo|bite|glow|camo|holy|putty|poreless)", re.I)),
    ("TPR", "coach", re.compile(r"\bcoach\b", re.I)),
    ("NWL", "elmer", re.compile(r"\belmer(?:'s|s)?\b", re.I)),
]

RECS_ATTR = re.compile(r'data-client-recs-list="([^"]+)"', re.I)
BSR_ITEM = re.compile(
    r"#\s*([\d,]+)\s+in\s+([^<#(\n]+?)(?=\s*(?:\(|<|See Top|\#|$))",
    re.I,
)
_REPO_DATA = Path(__file__).resolve().parents[2] / "data" / "amazon"


def parse_recs_list(html: str) -> list[dict]:
    """Official zg.rank list from data-client-recs-list, with titles from /dp/ASIN + nearby alt."""
    m = RECS_ATTR.search(html or "")
    if not m:
        return []
    raw = htmlmod.unescape(m.group(1))
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    titles = titles_by_asin(html)
    out = []
    for it in items:
        asin = it.get("id")
        meta = it.get("metadataMap") or {}
        rank = _int(meta.get("render.zg.rank"))
        title = titles.get(asin) or ""
        out.append({
            "asin": asin,
            "rank": rank,
            "title": title,
            "brands_in_title": brands_in_title(title),
            "currentSalesRank": meta.get("render.zg.bsms.currentSalesRank") or None,
            "percentageChange": meta.get("render.zg.bsms.percentageChange") or None,
            "link": f"https://www.amazon.com/dp/{asin}" if asin else None,
        })
    return out


def titles_by_asin(html: str) -> dict[str, str]:
    """ASIN → title from img alt in a tight window around /dp/{ASIN}. First alt wins."""
    titles: dict[str, str] = {}
    for m in re.finditer(r"/dp/([A-Z0-9]{10})", html or ""):
        asin = m.group(1)
        if asin in titles:
            continue
        start, end = max(0, m.start() - 800), min(len(html), m.end() + 800)
        ctx = html[start:end]
        tm = re.search(r'\balt="([^"]{5,250})"', ctx)
        if tm:
            titles[asin] = htmlmod.unescape(tm.group(1)).strip()
    return titles


def brands_in_title(title: str) -> list[str]:
    hits = []
    for ticker, label, pat in BRAND_PATTERNS:
        if title and pat.search(title):
            hits.append({"ticker": ticker, "label": label})
    return hits


def parse_product_bsr(html: str) -> list[dict]:
    """Parse 'Best Sellers Rank #N in Category' including subcategory rows (#5 in Women's Mules & Clogs)."""
    if not html:
        return []
    # Prefer the product-details block so we don't pick up unrelated #N.
    block = html
    m = re.search(r"Best Sellers Rank(.*?)(?:ASIN|Customer Reviews|Date First|Manufacturer|$)", html, re.I | re.S)
    if m:
        block = m.group(0)
    text = htmlmod.unescape(re.sub(r"<[^>]+>", " ", block))
    text = re.sub(r"\s+", " ", text)
    ranks = []
    seen = set()
    for rm in re.finditer(r"#\s*([\d,]+)\s+in\s+([^#]+?)(?=\s*(?:#|ASIN|Customer|See Top 100|\(|$))", text, re.I):
        rank = _int(rm.group(1))
        cat = re.sub(r"\s+", " ", rm.group(2)).strip(" \t-–|()")
        cat = re.sub(r"\s*See Top.*$", "", cat, flags=re.I).strip()
        if not rank or not cat:
            continue
        key = (rank, cat.lower())
        if key in seen:
            continue
        seen.add(key)
        ranks.append({"rank": rank, "category": cat})
    return ranks


def load_sample(path: Path | None = None) -> dict:
    p = path or (_REPO_DATA / "sample_bsr.json")
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def signal_for_ticker(ticker: str, sample: dict | None = None) -> dict:
    """Corroboration-ready signal from the verified Best Sellers sample. No z-score."""
    sample = sample if sample is not None else load_sample()
    ticker = ticker.upper()
    findings = [f for f in (sample.get("findings") or []) if f.get("ticker") == ticker]
    out: dict[str, Any] = {
        "platform": "amazon_movers",
        "ok": False,
        "status": "partial",
        "ticker": ticker,
        "method": sample.get("method_primary") or "Scrapling Fetcher of public Best Sellers; official zg.rank; title-only brand match",
        "retrieved_at_utc": sample.get("retrieved_at_utc"),
        "source_url": "https://www.amazon.com/gp/bestsellers",
        "z_last_vs_history": None,
        "notes": (
            "A Best Sellers rank is a position on one public list at one moment, "
            "not a z-score vs a baseline. Lululemon, Coach, and Elmer's were not "
            "in the top 50 of the category pages we fetched. Movers & Shakers "
            "returned no data-client-recs-list via Fetcher."
        ),
        "findings": findings,
    }
    if findings:
        out.update({"ok": True, "status": "worked", "n_listings": len(findings),
                    "best_rank": min(f["rank"] for f in findings if f.get("rank") is not None)})
        # Prefer the tightest/best list mention for the source URL
        top = min(findings, key=lambda f: f.get("rank") or 10**9)
        out["source_url"] = top.get("source_url") or out["source_url"]
        out["headline"] = f"#{top['rank']} in {top.get('category')} — {top.get('title')}"
    else:
        not_found = sample.get("not_found_in_top50_of_fetched_lists") or []
        out["reason"] = f"no title-only brand hit in fetched top-50 lists ({', '.join(not_found) or 'see sample'})"
        out["status"] = "worked" if sample else "partial"
        out["ok"] = True  # the probe worked; the brand simply was not in those lists
        out["n_listings"] = 0
        out["notes"] = out["notes"] + " Absence from a top-50 list is a fact, not an estimated rank."
    return out


def fetch_bestsellers(url: str) -> dict:
    """Live Fetcher pull of a public Best Sellers (or similar) page."""
    out: dict[str, Any] = {
        "platform": "amazon_movers",
        "ok": False,
        "status": "error",
        "source_url": url,
        "method": "Scrapling Fetcher of public Best Sellers; official data-client-recs-list zg.rank",
        "retrieved_at_utc": now_utc(),
    }
    try:
        from scrapling.fetchers import Fetcher
    except ImportError as e:
        out.update({"status": "skipped", "reason": f"scrapling not installed: {e}"})
        return out
    try:
        r = Fetcher.get(url, timeout=30)
        body = getattr(r, "body", None)
        if isinstance(body, bytes):
            html = body.decode("utf-8", "replace")
        else:
            html = body or ""
        status = getattr(r, "status", None)
        out["http_status"] = status
        out["html_len"] = len(html)
        products = parse_recs_list(html)
        if not products:
            out.update({
                "status": "partial" if status == 200 else "blocked",
                "reason": "no data-client-recs-list (JS-rendered, empty, or blocked)",
                "ok": False,
            })
            return out
        out.update({
            "ok": True,
            "status": "worked",
            "n": len(products),
            "products": products,
            "brand_hits": [p for p in products if p.get("brands_in_title")],
        })
        return out
    except Exception as e:
        out["reason"] = str(e)
        return out


def _int(v) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None
