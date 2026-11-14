"""Unit tests for priced-in verdict and corroboration. No network."""
from camillo_tracker.street_view import priced_in_verdict
from camillo_tracker.signals import corroborate


def test_already_priced_when_street_is_bullish_and_revising_up():
    components = {
        "consensus_distribution": {"buy_share": 0.85, "n_ratings": 24},
        "price_targets": {"implied_upside_pct": 25.0},
        "estimate_revisions": {"revision_direction": "up"},
        "rating_changes": {"status": "worked", "n_upgrades_90d": 5, "n_downgrades_90d": 0},
        "coverage": {"n_ratings": 24},
    }
    v = priced_in_verdict(components)
    assert v["label"] == "explicitly_reflected"
    assert v["n_components"] >= 4
    assert v["priced_in_points"] >= 4


def test_not_clearly_priced_when_street_is_cold():
    components = {
        "consensus_distribution": {"buy_share": 0.20, "n_ratings": 8},
        "price_targets": {"implied_upside_pct": -5.0},
        "estimate_revisions": {"revision_direction": "flat"},
        "rating_changes": {"status": "worked", "n_upgrades_90d": 0, "n_downgrades_90d": 1},
        "coverage": {"n_ratings": 8},
    }
    v = priced_in_verdict(components)
    assert v["label"] in {"not_evidenced_in_reviewed_sources", "partly_reflected"}
    assert v["label"] != "explicitly_reflected"


def test_insufficient_data():
    v = priced_in_verdict({})
    assert v["label"] == "insufficient_evidence"
    assert v["priced_in_points"] is None


def test_corroboration_requires_two_rising_platforms():
    platforms = {
        "google_trends": {"status": "worked", "z_last_vs_history": 1.4},
        "wikipedia": {"status": "worked", "z_last_vs_history": 1.2},
        "reddit": {"status": "blocked", "reason": "HTTP 403"},
    }
    c = corroborate(platforms, min_confirm=2)
    assert c["ok"] is True
    assert c["corroborated"] is True
    assert c["n_confirming"] >= 2
    assert any(m["platform"] == "reddit" for m in c["platforms_missing"])


def test_corroboration_does_not_impute_missing():
    platforms = {
        "google_trends": {"status": "worked", "momentum_0_100": 80},
        "wikipedia": {"status": "blocked", "reason": "404"},
        "x": {"status": "skipped", "reason": "no bearer"},
    }
    c = corroborate(platforms, min_confirm=2)
    assert c["corroborated"] is False
    assert c["n_confirming"] == 0
    assert c["weighted_z"] is None
    assert any(p["platform"] == "google_trends" for p in c["platforms_present_no_z"])
    assert len(c["platforms_missing"]) == 2


def test_corroboration_empty():
    c = corroborate({"reddit": {"status": "blocked", "reason": "403"}})
    assert c["ok"] is False
    assert c["weighted_z"] is None
    assert "imputed" not in (c.get("note") or "").lower() or "not imputed" in c["note"].lower() or "Nothing was imputed" in c["note"]
