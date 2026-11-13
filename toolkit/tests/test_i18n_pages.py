"""Structural checks: every docs page has dual language bodies and a single global toggle."""
from pathlib import Path
import re

import pytest

DOCS = Path(__file__).resolve().parents[2] / "docs"
PAGES = sorted(DOCS.glob("*.html"))
PAGE_NAMES = [p.name for p in PAGES]


@pytest.mark.parametrize("name", PAGE_NAMES)
def test_page_has_titles_and_global_toggle(name):
    t = (DOCS / name).read_text(encoding="utf-8")
    assert 'data-title-zh="' in t
    assert 'data-title-en="' in t
    assert "data-lang-switch" in t
    assert 'data-lang="zh"' in t and 'data-lang="en"' in t
    # boot script before paint
    head = t.split("</head>", 1)[0]
    assert "cct-lang" in head
    # both bodies exist
    assert "lang-zh" in t and "lang-en" in t
    # no per-page 对照 three-way toggle
    assert "data-lang-both" not in t
    assert "lang-toggle" not in t  # old per-page toggle class


def test_all_twelve_pages_present():
    expected = {
        "index.html",
        "methodology.html",
        "cases.html",
        "core-logic.html",
        "trades.html",
        "dimensions.html",
        "street-view.html",
        "track-record.html",
        "playbook.html",
        "divergence.html",
        "resources.html",
        "sources.html",
    }
    assert expected <= set(PAGE_NAMES)


def test_street_view_bilingual_charts_exist():
    charts = DOCS / "assets" / "charts"
    for stem in (
        "event-forward-returns",
        "event-side-signed",
        "wiki-attention",
        "live-snapshot",
    ):
        for lang in ("zh", "en"):
            p = charts / f"{stem}-{lang}.png"
            assert p.is_file() and p.stat().st_size > 10000, p


def test_street_view_tables_are_paired():
    t = (DOCS / "street-view.html").read_text(encoding="utf-8")
    assert t.count('class="table-wrap lang-zh"') == 4
    assert t.count('class="table-wrap lang-en"') == 4
    assert "data-platforms-static" in t
    # Chinese headers
    assert "<th>事件</th>" in t
    assert "<th>平台</th>" in t
    assert "<th>播放（statsV2）</th>" in t
    assert "<th>榜单 / 类目</th>" in t
    # English headers
    assert "<th>Event</th>" in t
    assert "<th>Platform</th>" in t
