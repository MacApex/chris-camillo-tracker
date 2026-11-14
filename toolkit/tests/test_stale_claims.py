"""Regression: withdrawn anchors and stale instructions stay out of the visible pages."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


def _text(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


def test_core_logic_drops_placeholder_elf_path():
    t = _text("core-logic.html")
    assert "+25%" not in t
    assert "+70.3%" not in t
    assert "may have been earlier" not in t.lower()
    assert "可能入场更早" not in t
    assert "the Street followed" not in t
    assert "卖方随后跟上" not in t
    assert "1–2% revenue contribution is usually too small" not in t
    assert "1–2% 的收入贡献通常不够" not in t
    assert "1–3%" not in t
    assert "audited career record" not in t
    assert "审计过的生涯回报" not in t
    assert "OTC data quality" not in t
    assert "场外报价质量" not in t
    assert "not clearly priced AND niche rising" not in t
    # Both languages carry the same risk boundaries.
    assert t.count("Information parity is only one exit idea") >= 1
    assert t.count("信息平价只是一种退出想法") >= 1
    assert "household risk" in t and "家庭风险" in t


def test_cases_page_does_not_authorize_month_leads():
    t = _text("cases.html")
    assert "month precision, the latter labeled" not in t
    assert "日或月精度，后者会标明" not in t
    assert "early-March COVID exit" not in t
    assert "新冠自称 3 月初退出" not in t
    assert "When the execution day is unknown, the lead stays unknown" in t
    assert "成交日未知时，时差保持未知" in t
    assert "first Street upgrade or earnings beat" not in t
    assert "到第一次卖方上调或财报超预期" not in t


def test_street_view_does_not_gate_on_not_clearly_priced():
    t = _text("street-view.html")
    assert "Only “niche rising and not clearly priced” survives" not in t
    assert "只有「利基上升且尚未清楚定价」才能进入" not in t
    assert "+0.5%" not in t
    assert "−28.7%" not in t
    assert "+19.4%" not in t
    assert "event-forward-returns-en.png" not in t


def test_event_study_nulls_placeholder_anchors():
    study = json.loads((DOCS / "data/event_study.json").read_text(encoding="utf-8"))
    by = {e["id"]: e for e in study["events"]}
    for eid in (
        "elf-2019",
        "rbi-2019-apr",
        "rbi-2019-aug",
        "covid-spy-2020",
        "covid-wynn-2020",
        "gme-2021",
        "amc-2021",
    ):
        ev = by[eid]
        for h in ("1m", "3m", "6m"):
            assert ev["returns"][h]["ok"] is False
            assert ev["returns"][h]["pct"] is None
        assert ev["street_window"]["ok"] is False
        assert ev["street_window"]["n_before"] is None
        assert ev["wikipedia_attention"]["ok"] is False
    # Dependent windows were not left on the old anchor.
    missoni = by["tgt-missoni-2011"]
    assert missoni["returns"]["1m"]["pct"] == 3.53
    assert missoni["street_window"]["ok"] is False
    assert missoni["street_window"]["n_before"] is None
    tpr = by["tpr-2021-mention"]
    assert tpr["date"] == "2021-08-18"
    assert tpr["returns"]["1m"]["ok"] is True
    assert tpr["street_window"]["status"] == "recomputed_from_stored_grades"
    assert tpr["street_window"]["anchor"] == "2021-08-18"
    assert tpr["wikipedia_attention"]["status"] == "recomputed_from_stored_pageviews"
    assert tpr["wikipedia_attention"]["n_before"] == 14
    assert study["n_with_1m_return"] == 3


def test_chart_export_matches_withdrawal():
    chart = json.loads((DOCS / "data/cases-charts.json").read_text(encoding="utf-8"))
    elf = next(c for c in chart["cases"] if c["id"] == "elf-2019")
    block = elf["event_study"]["elf-2019"]
    assert block["display_returns"] is False
    assert block["returns"]["6m"]["pct"] is None
    assert "70.35" not in json.dumps(block)
    rbi = next(c for c in chart["cases"] if c["id"] == "rbi-2019")
    for key in rbi["event_study"]:
        assert rbi["event_study"][key]["display_returns"] is False
        assert rbi["event_study"][key]["returns"]["1m"]["pct"] is None


def test_methodology_rules_do_not_skip_valuation_or_stand_down():
    t = _text("methodology.html")
    assert "not a valuation model" not in t
    assert "而不是做一份估值模型" not in t
    assert "If it is priced, stand down" not in t
    assert "已定价就放下" not in t
    assert "Verify incremental earnings, then evaluate valuation" in t
    assert "先核实增量利润，再评估估值" in t
    assert "report of his practice" in t
    assert "对他做法的转述" in t or "那是对他做法的转述" in t
    play = _text("playbook.html")
    assert "not a DCF" not in play
    assert "而不是做一份贴现模型" not in play
    assert "the imbalance is gone" not in play


def test_diagram_does_not_treat_bullish_as_thesis_and_both_branches_continue():
    t = _text("core-logic.html")
    assert "look bullish" not in t
    assert "已有看多版本" not in t
    assert "matching earnings assumptions" in t
    assert "盈利假设对得上" in t
    assert "Both readings continue" in t
    assert "两条都继续" in t
    assert "neither selects nor rejects" in t
    assert "不单独允许或否定选股" in t


def test_stage_labels_are_translated():
    js = (DOCS / "assets" / "cases.js").read_text(encoding="utf-8")
    assert "社会观察" in js and "Social observation" in js
    assert "投资结果" in js and "Investment outcome" in js
    assert 's.id.replaceAll' not in js


def test_memo_is_bilingual_and_not_a_buy():
    t = _text("memo.html")
    assert "cct-research-memo-v1" in t
    assert "needs research" in t
    assert "待研究" in t
    assert "not_a_buy" in t
    assert "filled, not verified" in t
    assert "已填写，未核实" in t
    assert "verified: false" in t
    assert "localStorage.removeItem" in t
    assert "password" not in t.lower()
    assert "api key" not in t.lower()
    for name in (DOCS.glob("*.html")):
        assert "memo.html" in name.read_text(encoding="utf-8")
