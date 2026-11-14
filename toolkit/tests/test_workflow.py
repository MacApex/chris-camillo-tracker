"""Tests for the data-acquisition workflow and research report. No live network."""
from pathlib import Path

from camillo_tracker.signals import corroborate
from camillo_tracker.workflow import (
    CATALOG,
    STEP_ORDER,
    compose_report,
    run_research,
    write_report,
)


def test_catalog_is_complete():
    required = {
        "search_interest",
        "social_tiktok",
        "social_x",
        "social_youtube",
        "social_reddit",
        "social_instagram",
        "commerce_amazon",
        "commerce_apps",
        "attention_wikipedia",
        "news",
        "street",
    }
    assert required <= set(CATALOG)
    for key, e in CATALOG.items():
        for field in ("primary", "fallback", "cross_check", "status", "metric_kind", "normalize", "reliability"):
            assert e.get(field), f"{key} missing {field}"
        assert e["primary"].get("command")
        assert e["metric_kind"] in {"flow", "stock", "position", "presence", "level", "unknown"}


def test_step_order():
    ids = [s[0] for s in STEP_ORDER]
    assert ids[0] == "discover"
    assert "street" in ids and ids.index("street") > ids.index("discover")
    assert "falsify" in ids and "horizon" in ids and "risk_exit" in ids
    assert ids.index("decision") == len(ids) - 1


def test_compose_does_not_invent_z_or_impute():
    platforms = {
        "tiktok": {
            "status": "worked",
            "ok": True,
            "viewCount": 35500544935,
            "videoCount": 1927145,
            "z_last_vs_history": None,
            "notes": "lifetime stock",
        },
        "amazon_movers": {
            "status": "worked",
            "ok": True,
            "best_rank": 1,
            "headline": "#1 in Women's Shoes",
            "z_last_vs_history": None,
        },
        "reddit": {"status": "blocked", "reason": "HTTP 403"},
    }
    c = corroborate(platforms)
    r = compose_report("Crocs", "CROX", platforms=platforms, corroboration=c, street=None, mode="test")
    assert r["recommendation"] == "not_corroborated"
    assert "imputed" not in r["markdown"].lower() or "never imputed" in (r.get("disclaimer") or "").lower() or "不填空" in r["markdown"]
    assert "35500544935" in r["markdown"]
    assert r["gates"]["corroborate"]["passed"] is False
    assert r["gates"]["materiality"]["passed"] is None  # human gate
    assert "不构成投资建议" in r["markdown"] or "Not financial advice" in r["disclaimer"]
    # TikTok must be present-no-z, not a confirming platform
    present = {p["platform"] for p in c.get("platforms_present_no_z") or []}
    assert "tiktok" in present
    assert "tiktok" not in (c.get("platforms_used") or [])


def test_offline_research_writes_report(tmp_path):
    report = run_research("Crocs", "CROX", wiki="Crocs", keywords=["Crocs"], out_dir=tmp_path, offline=True)
    assert report["mode"] == "offline-cache"
    assert report["written"]["markdown"]
    md = Path(report["written"]["markdown"]).read_text(encoding="utf-8")
    assert "CROX" in md
    assert "交叉验证" in md
    assert report["platforms"]["tiktok"]["viewCount"] == 35500544935
    assert report["platforms"]["amazon_movers"]["best_rank"] == 1
    # Offline does not invent a Street green light
    assert report["gates"]["street"]["verdict"] == "insufficient_evidence"
    assert report["gates"]["materiality"]["passed"] is None
    assert report["gates"]["risk_exit"]["passed"] is None
    assert "not earnings" in report["signal_vs_value"].lower() or "not durable" in report["signal_vs_value"].lower()
    assert "daily" not in (report.get("policy") or {}) or report["policy"]["no_daily_routine"] is True


def test_two_rising_platforms_can_pass_corroboration_gate():
    platforms = {
        "google_trends": {"status": "worked", "z_last_vs_history": 1.1},
        "wikipedia": {"status": "worked", "z_last_vs_history": 1.2},
    }
    street = {"verdict": {"label": "not_evidenced_in_reviewed_sources", "confidence": "medium", "reasons": ["not in the rows reviewed"]}}
    r = compose_report("e.l.f.", "ELF", platforms=platforms, street=street, mode="test")
    assert r["gates"]["corroborate"]["passed"] is True
    assert r["recommendation"] == "candidate_for_human_work"
