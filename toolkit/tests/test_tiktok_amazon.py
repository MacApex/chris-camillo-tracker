"""Parser tests for TikTok and Amazon adapters. No network."""
import json
from pathlib import Path

from camillo_tracker.amazon import (
    brands_in_title,
    parse_product_bsr,
    parse_recs_list,
    signal_for_ticker as amazon_signal,
)
from camillo_tracker.signals import corroborate
from camillo_tracker.tiktok import (
    parse_challenge_info,
    parse_creative_center_list,
    quality_for,
    signal_for_ticker as tiktok_signal,
)

FX = Path(__file__).parent / "fixtures"


def test_challenge_detail_prefers_statsV2():
    raw = json.loads((FX / "tiktok_challenge_crocs.json").read_text())
    p = parse_challenge_info(raw)
    assert p["ok"] is True
    assert p["viewCount"] == 35500544935
    assert p["videoCount"] == 1927145
    assert p["viewCount_rounded"] == 35500000000
    assert p["challenge_id"] == "93006"


def test_tiktokapi_shaped_payload():
    payload = {
        "challengeInfo": {
            "challenge": {"id": "192633", "title": "lululemon", "stats": {"videoCount": 0, "viewCount": 26700000000}},
            "stats": {"videoCount": 0, "viewCount": 26700000000},
            "statsV2": {"videoCount": "1274510", "viewCount": "26698742524"},
        }
    }
    p = parse_challenge_info(payload)
    assert p["viewCount"] == 26698742524
    assert p["videoCount"] == 1274510
    assert p["viewCount_rounded"] == 26700000000


def test_creative_center_top3():
    raw = json.loads((FX / "tiktok_gethashtaglist.json").read_text())
    p = parse_creative_center_list(raw)
    assert p["ok"] is True
    assert p["totalCount"] == 3
    assert p["items"][0]["hashtag"] == "veteransday"
    assert p["items"][0]["publishCnt"] == 63021
    assert p["items"][0]["vv"] == 68790053
    assert p["items"][2]["hashtag"] == "piratetoken"
    assert p["items"][2]["vv"] == 428310388


def test_noisy_hashtags_flagged():
    assert quality_for("coach") == "noisy_generic_word"
    assert quality_for("slime") == "noisy_generic_word"
    assert quality_for("lulu") == "noisy_generic_word"
    assert quality_for("coachbag") == "specific"
    assert quality_for("lululemon") == "specific"


def test_amazon_recs_official_ranks_and_title_only():
    html = (FX / "amazon_bestsellers_womens_shoes_excerpt.html").read_text(encoding="utf-8")
    products = parse_recs_list(html)
    assert len(products) == 50
    assert products[0]["asin"] == "B0014C0LSY"
    assert products[0]["rank"] == 1
    assert "Crocs" in (products[0]["title"] or "")
    assert any(b["ticker"] == "CROX" for b in products[0]["brands_in_title"])
    # #2 is EverFoams — must NOT inherit the Crocs title
    assert products[1]["asin"] == "B0CLGNYKFR"
    assert products[1]["rank"] == 2
    title2 = products[1]["title"] or ""
    if title2:
        assert "EverFoams" in title2
        assert not any(b["ticker"] == "CROX" for b in products[1]["brands_in_title"])
    # Lined Clog #29
    lined = next(p for p in products if p["asin"] == "B01A6LUCZU")
    assert lined["rank"] == 29
    assert "Crocs" in (lined["title"] or "")


def test_brand_match_title_only_rejects_false_friends():
    assert brands_in_title("Crocs Unisex-Adult Classic Clog")
    assert not brands_in_title("EverFoams Womens Fuzzy Open-toe Slippers")
    # "elf" inside yourself / shelf / self must not match
    assert not brands_in_title("Clean Towels you can use yourself")
    assert not brands_in_title("Vanicream on the shelf")
    assert brands_in_title("e.l.f. Instant Lift Brow Pencil, Dual-Sided, Blonde")


def test_product_bsr_extracts_subcategory():
    html = (FX / "amazon_product_bsr_B01A6LUCZU.html").read_text(encoding="utf-8")
    ranks = parse_product_bsr(html)
    cats = {r["category"]: r["rank"] for r in ranks}
    assert cats["Clothing, Shoes & Jewelry"] == 455
    # Subcategory must not be dropped
    assert any(r["rank"] == 5 and "Mules" in r["category"] for r in ranks)


def test_tiktok_and_amazon_do_not_invent_z_scores():
    t = tiktok_signal("CROX")
    a = amazon_signal("CROX")
    assert t["ok"] and t["status"] == "worked"
    assert t["viewCount"] == 35500544935
    assert t.get("z_last_vs_history") is None
    assert a["ok"] and a["status"] == "worked"
    assert a["best_rank"] == 1
    assert a.get("z_last_vs_history") is None
    c = corroborate({
        "google_trends": {"status": "worked", "momentum_0_100": 43.1},
        "wikipedia": {"status": "worked", "z_last_vs_history": -1.61},
        "tiktok": t,
        "amazon_movers": a,
    })
    # Both new platforms are present but contribute no z
    present = {p["platform"] for p in c.get("platforms_present_no_z", [])}
    assert "tiktok" in present
    assert "amazon_movers" in present
    # They must not be treated as confirming a rise
    used = c["platforms_used"]
    assert "tiktok" not in used
    assert "amazon_movers" not in used
