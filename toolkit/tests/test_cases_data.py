"""Honesty checks on documented-case visualization data. No network."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHART = ROOT / "docs/data/cases-charts.json"
CASES = ROOT / "data/cases"
INDEX = CASES / "index.json"

EXPECTED = [
    "newell-slime",
    "elf-2019",
    "rbi-2019",
    "covid-spy-2020",
    "covid-wynn-2020",
    "dorel-2020",
    "tapestry-2021",
    "crocs-multi-year",
    "lululemon-2025-exit",
]


def _chart():
    return json.loads(CHART.read_text(encoding="utf-8"))


def test_all_nine_cases_present_in_order():
    ids = [c["id"] for c in _chart()["cases"]]
    assert ids == EXPECTED


def test_every_series_is_real_or_flagged_missing():
    for c in _chart()["cases"]:
        for name in ("prices", "trends", "wikipedia"):
            obj = c[name]
            if obj.get("ok"):
                assert obj["series"], f"{c['id']} {name} ok but empty"
                assert obj["n"] == len(obj["series"])
                dates = [p["date"] for p in obj["series"]]
                assert dates == sorted(dates), f"{c['id']} {name} not sorted"
                # no invented placeholder dates inside a gap — every point has a value
                key = "close" if name == "prices" else ("value" if name == "trends" else "views")
                for p in obj["series"]:
                    assert p[key] is not None
                    assert "YYYY" not in str(p["date"])
            else:
                assert obj["series"] in (None, [],) or not obj.get("ok")
        # missing notes must not be silent when a series failed
        st = c["series_status"]
        if st.get("trends") != "worked":
            assert any(n["series"] == "google_trends" for n in c["missing_notes"])


def test_lead_only_when_honest():
    by = {c["id"]: c for c in _chart()["cases"]}
    elf = by["elf-2019"]["lead"]
    assert elf["ok"] is False
    assert elf["days"] is None
    measured = elf["measured_not_a_lead"]
    assert measured["placeholder_15_mar_to_3_apr_calendar_days"] == 19
    assert measured["placeholder_is_execution"] is False
    assert measured["trends_week_label_to_3_apr_calendar_days"] == 31
    assert measured["week_label_is_first_signal"] is False
    assert measured["jefferies_note_obtained"] is False
    assert by["elf-2019"]["entry"] is None

    dorel = by["dorel-2020"]["lead"]
    assert dorel["ok"] is False
    assert dorel["days"] is None
    m = dorel["measured_not_a_lead"]
    assert m["calendar_days_entry_to_issuer_release"] == 108
    assert m["calendar_days_entry_to_yahoo_row"] == 107
    assert m["yahoo_row_is_not_the_lead"] is True
    assert m["yahoo_surprise_is_stock_return"] is False
    assert m["adjusted_diluted_eps"] == 0.48
    assert m["reported_diluted_eps"] == 0.34
    assert m["prices_directly_comparable"] is False
    assert m["special_dividend_explains_gap"] is False
    # empty Yahoo ratings must not become a 0-day lead
    assert by["dorel-2020"]["street"]["n"] == 0

    # These must NOT claim a lead
    for cid in (
        "rbi-2019",
        "covid-spy-2020",
        "covid-wynn-2020",
        "tapestry-2021",
        "newell-slime",
        "crocs-multi-year",
        "lululemon-2025-exit",
    ):
        ld = by[cid]["lead"]
        assert ld["ok"] is False, cid
        assert ld.get("days") is None, cid


def test_no_one_day_rbi_lead_and_no_three_dollar_wynn_lead():
    by = {c["id"]: c for c in _chart()["cases"]}
    assert "1" not in str(by["rbi-2019"]["lead"].get("days"))
    reason = (by["rbi-2019"]["lead"].get("reason") or "") + (by["rbi-2019"]["lead"].get("en") or "")
    assert "not a tim hortons turnaround" in reason.lower()
    assert by["rbi-2019"]["lead"]["ok"] is False
    wynn = by["covid-wynn-2020"]["lead"]
    assert wynn["ok"] is False
    assert "5-day" not in (wynn.get("reason") or "") or "do not report a 5-day" in (wynn.get("reason") or "")


def test_elf_trends_peak_is_real_march_2019():
    elf = next(c for c in _chart()["cases"] if c["id"] == "elf-2019")
    assert elf["trends"]["ok"]
    assert elf["trends"]["keyword"] == "elf cosmetics"
    peak = elf["trends"]["peak"]
    assert peak["date"] == "2019-03-03"
    assert peak["value"] == 100
    vals = {p["date"]: p["value"] for p in elf["trends"]["series"]}
    assert vals["2019-03-03"] == 100
    # a seasonal-looking Nov 2018 spike exists and is real, not removed
    assert vals["2018-11-25"] == 87


def test_slime_trends_peak_may_2017_not_used_as_entry():
    nwl = next(c for c in _chart()["cases"] if c["id"] == "newell-slime")
    assert nwl["trends"]["peak"]["date"] == "2017-05-28"
    assert nwl["trends"]["peak"]["value"] == 100
    assert nwl["lead"]["ok"] is False
    assert nwl["entry"]["precision"] == "era"


def test_covid_wiki_starts_mid_march_not_zero_filled():
    spy = next(c for c in _chart()["cases"] if c["id"] == "covid-spy-2020")
    first = spy["wikipedia"]["series"][0]["date"]
    assert first >= "2020-03-12"
    # must not invent Jan–Feb wiki zeros
    dates = [p["date"] for p in spy["wikipedia"]["series"]]
    assert not any(d < "2020-03-12" for d in dates)
    assert any(n.get("partial") for n in spy["missing_notes"] if n["series"] == "wikipedia")


def test_event_study_returns_are_the_published_ones():
    by = {c["id"]: c for c in _chart()["cases"]}
    elf = by["elf-2019"]["event_study"]["elf-2019"]
    assert elf["display_returns"] is False
    assert elf["returns"]["1m"]["ok"] is False
    assert elf["returns"]["1m"]["pct"] is None
    assert elf["returns"]["6m"]["pct"] is None
    dorel = by["dorel-2020"]["event_study"]["dorel-2020"]["returns"]
    assert dorel["1m"]["pct"] == 131.06
    assert dorel["6m"]["pct"] == 608.7
    assert "not comparable" in by["dorel-2020"]["event_study"]["dorel-2020"]["note"].lower() or "not the bi" in by["dorel-2020"]["event_study"]["dorel-2020"]["note"].lower()
    lulu = by["lululemon-2025-exit"]
    assert lulu["role"] == "signal"
    assert lulu["exit"] is None
    tap = by["tapestry-2021"]
    assert tap["entry"]["date"] == "2021-08-18"
    assert tap["event_study"]["tpr-2021-mention"]["returns"]["1m"]["pct"] == -1.95


def test_chart_json_policy_forbids_interpolation():
    pol = _chart()["policy"].lower()
    assert "never interpolated" in pol
    assert "insufficient evidence" in pol
    assert "not trading leads" in pol
    assert "look-ahead" in pol


def test_raw_case_files_exist():
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    assert {c["id"] for c in idx["cases"]} == set(EXPECTED)
    for cid in EXPECTED:
        assert (CASES / f"{cid}.json").is_file()
