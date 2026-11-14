"""Trades database integrity — no invented required fields, rejected claims stay rejected."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRADES = json.loads((ROOT / "data" / "trades.json").read_text())


def test_trades_load_and_count():
    assert len(TRADES["trades"]) >= 30


def test_every_row_has_verification_and_source():
    for t in TRADES["trades"]:
        assert t.get("verification"), t["id"]
        assert t.get("source"), t["id"]
        assert t["verification"] in TRADES["verification_levels"], t["id"]


def test_rejected_claims_are_not_wins():
    rejected = [t for t in TRADES["trades"] if t["verification"] == "rejected_no_source"]
    assert any(t["id"] == "pabst-rejected" for t in rejected)
    assert any(t["id"] == "vgk-rejected" for t in rejected)
    for t in rejected:
        assert t["role"] == "rejected"


def test_unconfirmed_tickers_are_labeled():
    for t in TRADES["trades"]:
        if t["verification"] == "unconfirmed_ticker":
            assert t["ticker_status"] in {"unconfirmed", "vehicle_uncertain", "unnamed_microcap", "unnamed"} or "uncertain" in str(t["ticker_status"])


def test_records_are_not_a_verified_trade_census():
    assert TRADES["n_records"] == 43
    assert TRADES["record_count_meaning"] == "research_records_not_verified_trades"
    assert "win rate" in TRADES["policy"].lower()
    assert TRADES["source_url_null_count"] == 30
    broken = "chris-camillo-social-arbitrage-investing-strategy-ticker-tags-2021-8"
    assert all(broken not in (t.get("source_url") or "") for t in TRADES["trades"])
    hp = next(t for t in TRADES["trades"] if t["id"] == "hp-printers-2020")
    assert hp["role"] == "named_no_pnl"
    lulu = next(t for t in TRADES["trades"] if t["id"] == "lululemon-2025-exit")
    assert lulu["role"] == "signal_note"
    assert "exit" not in lulu["thesis"].lower() or "does not say he held or exited" in lulu["thesis"]
    for t in TRADES["trades"]:
        assert t.get("thesis_zh") and t.get("outcome_zh")
        assert t["thesis_zh"] != t.get("thesis")


def test_dorel_has_day_precision_and_screenshot_level():
    d = next(t for t in TRADES["trades"] if t["id"] == "dorel-2020")
    assert d["date"] == "2020-04-24"
    assert d["date_precision"] == "day"
    assert d["verification"] == "screenshots_viewed_by_journalist"
    assert "629" in (d["outcome"] or "")  # stock-path figure is explained, not personal return
