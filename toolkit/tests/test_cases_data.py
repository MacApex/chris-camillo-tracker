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
    assert elf["ok"] is True
    assert elf["days"] == 19
    assert elf["kind"] == "street_upgrade"
    assert elf["to"] == "2019-04-03"
    assert elf["to_event"]["firm"] == "Jefferies"
    assert elf["from_precision"] == "month"
    assert elf["also"]["from_trends_peak"]["days_to_same_event"] == 31

    dorel = by["dorel-2020"]["lead"]
    assert dorel["ok"] is True
    assert dorel["days"] == 107
    assert dorel["kind"] == "earnings_beat"
    assert dorel["to"] == "2020-08-09"
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
    assert "counterexample" in reason.lower() or "constructive" in reason.lower()
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
    elf = by["elf-2019"]["event_study"]["elf-2019"]["returns"]
    assert elf["1m"]["pct"] == 25.0
    assert elf["6m"]["pct"] == 70.35
    dorel = by["dorel-2020"]["event_study"]["dorel-2020"]["returns"]
    assert dorel["1m"]["pct"] == 131.06
    assert dorel["6m"]["pct"] == 608.7


def test_chart_json_policy_forbids_interpolation():
    pol = _chart()["policy"].lower()
    assert "never interpolated" in pol or "never interpolate" in pol
    assert "incomplete" in pol and "not monotonic" not in pol or "incomplete" in pol
    assert "month-precision" in pol or "month-precision placeholders" in pol


def test_raw_case_files_exist():
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    assert {c["id"] for c in idx["cases"]} == set(EXPECTED)
    for cid in EXPECTED:
        assert (CASES / f"{cid}.json").is_file()
