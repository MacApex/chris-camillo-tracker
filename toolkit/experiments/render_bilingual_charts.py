#!/usr/bin/env python3
"""Render street-view charts in pure Chinese and pure English (Noto Sans CJK SC)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter, LogLocator

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "data"
OUT = ROOT / "docs" / "assets" / "charts"

FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(FONT_PATH)
# Bold face if present
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
try:
    font_manager.fontManager.addfont(BOLD)
except Exception:
    pass

# After addfont the registered name for SC Regular is typically "Noto Sans CJK SC"
plt.rcParams.update(
    {
        "font.family": "Noto Sans CJK SC",
        "font.size": 11,
        "axes.unicode_minus": False,
        "figure.facecolor": "#090a0d",
        "axes.facecolor": "#101218",
        "axes.edgecolor": "#2a2e38",
        "axes.labelcolor": "#d8d4cc",
        "xtick.color": "#c4c0b6",
        "ytick.color": "#c4c0b6",
        "text.color": "#e8e4dc",
        "grid.color": "#2a2e38",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.9,
        "legend.facecolor": "#14171e",
        "legend.edgecolor": "#2a2e38",
        "legend.fontsize": 10,
        "axes.titleweight": "medium",
        "savefig.facecolor": "#090a0d",
        "savefig.edgecolor": "#090a0d",
    }
)

GOLD = "#c9a66b"
GOLD_B = "#e4c88a"
CREAM = "#f0e6d0"
TEAL = "#6aa8a0"
ROSE = "#c45c5c"
SAGE = "#7dcea0"
SLATE = "#7a8494"
TEXT = "#e8e4dc"

HORIZONS = [
    ("1m", {"zh": "1 个月", "en": "1 month"}, GOLD),
    ("3m", {"zh": "3 个月", "en": "3 months"}, GOLD_B),
    ("6m", {"zh": "6 个月", "en": "6 months"}, CREAM),
]


def _save(fig, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=140, bbox_inches="tight", pad_inches=0.35)
    plt.close(fig)
    print("wrote", path, path.stat().st_size)


def _load_events():
    bundle = json.loads((DATA / "event_study.json").read_text(encoding="utf-8"))
    return bundle["events"]


def _pct(block):
    if block and block.get("ok") and isinstance(block.get("pct"), (int, float)):
        return float(block["pct"])
    return None


def _event_label(ev, lang):
    ticker = ev["ticker"]
    date = ev["date"][:7] if ev.get("precision") == "month" else ev["date"]
    side = ev.get("side")
    if side == "short":
        tag = "空" if lang == "zh" else "short"
        return f"{ticker} · {tag}\n{date}"
    return f"{ticker}\n{date}"


def chart_forward(events, lang: str) -> None:
    labels = [_event_label(e, lang) for e in events]
    x = np.arange(len(events))
    width = 0.26
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    for i, (key, lab, color) in enumerate(HORIZONS):
        CAP = 200.0
        vals = []
        raws = []
        for e in events:
            v = _pct((e.get("returns") or {}).get(key))
            raws.append(v)
            if v is None:
                vals.append(0.0)
            else:
                vals.append(max(min(v, CAP), -CAP))
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=lab[lang], color=color, edgecolor="none", zorder=3)
        for bar, v in zip(bars, raws):
            if v is None:
                bar.set_alpha(0)
                continue
            if v < 0:
                bar.set_color(ROSE if key != "6m" else "#a34d4d")
            h = bar.get_height()
            # Horizontal labels for modest bars; vertical at the cap for clipped ones.
            tall = abs(v) >= CAP
            ax.annotate(
                f"{v:+.1f}%" + (" ↑" if v > CAP else ""),
                (bar.get_x() + bar.get_width() / 2, h),
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=7,
                color=TEXT,
                rotation=90 if (tall or abs(v) > 40) else 0,
                xytext=(0, 5 if h >= 0 else -5),
                textcoords="offset points",
            )
    ax.axhline(0, color="#3a3f4c", linewidth=0.8, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", zorder=0)
    ax.set_axisbelow(True)
    if lang == "zh":
        ax.set_title("有记录日期起 1、3、6 个月的市场前瞻回报", fontsize=15, color=GOLD_B, pad=12)
        ax.set_ylabel("复权收盘回报（%）")
        footnote = "空头已标明。不是个人损益。纵轴截于 200%，Dorel 与 AMC 的更高数值标在柱顶箭头处。取数于 2026 年 11 月 13 日（Asia/Shanghai），经 yfinance。"
    else:
        ax.set_title("Forward 1, 3 and 6 month market returns from documented dates", fontsize=14, color=GOLD_B, pad=12)
        ax.set_ylabel("Adjusted close return (%)")
        footnote = "Shorts are marked. Not personal P&L. Axis clipped at 200%; higher Dorel and AMC figures are labelled at the arrows. Retrieved 13 Nov 2026, Asia/Shanghai, via yfinance."
    ax.legend(loc="upper left", framealpha=0.95, ncol=3)
    fig.text(0.01, 0.01, footnote, fontsize=8, color=SLATE, ha="left")
    # Clip the axis so smaller (and negative) moves stay readable. True values stay on the labels.
    ax.set_ylim(-90, 210)
    _save(fig, f"event-forward-returns-{lang}.png")


def chart_signed(events, lang: str) -> None:
    labels = [_event_label(e, lang) for e in events]
    x = np.arange(len(events))
    width = 0.26
    fig, ax = plt.subplots(figsize=(12.5, 5.4))
    for i, (key, lab, color) in enumerate(HORIZONS):
        CAP = 200.0
        vals = []
        raws = []
        for e in events:
            side = (e.get("return_in_direction_of_stated_side") or {})
            v = side.get(key)
            v = float(v) if v is not None else None
            raws.append(v)
            if v is None:
                vals.append(0.0)
            else:
                vals.append(max(min(v, CAP), -CAP))
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=lab[lang], color=color, edgecolor="none", zorder=3)
        for bar, v in zip(bars, raws):
            if v is None:
                bar.set_alpha(0)
                continue
            if v < 0:
                bar.set_color(ROSE if key != "6m" else "#a34d4d")
            else:
                bar.set_color(SAGE if key == "1m" else (TEAL if key == "3m" else GOLD))
            h = bar.get_height()
            tall = abs(v) >= CAP
            ax.annotate(
                f"{v:+.1f}%" + (" ↑" if v > CAP else ""),
                (bar.get_x() + bar.get_width() / 2, h),
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=7,
                color=TEXT,
                rotation=90 if (tall or abs(v) > 40) else 0,
                xytext=(0, 5 if h >= 0 else -5),
                textcoords="offset points",
            )
    ax.axhline(0, color="#3a3f4c", linewidth=0.8, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", zorder=0)
    ax.set_axisbelow(True)
    if lang == "zh":
        ax.set_title("按所标方向签署后的同样回报", fontsize=15, color=GOLD_B, pad=12)
        ax.set_ylabel("方向签署回报（%）")
        footnote = "空头 = 标的涨跌取反。新冠数字仍是股票或指数路径，不是期权损益。纵轴截于 200%，更高数值标在柱顶箭头处。"
    else:
        ax.set_title("Same returns signed in the direction of the stated side", fontsize=14, color=GOLD_B, pad=12)
        ax.set_ylabel("Side-signed return (%)")
        footnote = "Short = flipped underlying. COVID figures remain equity-index moves, not option P&L. Axis clipped at 200%; higher figures are labelled at the arrows."
    ax.legend(loc="upper left", framealpha=0.95, ncol=3)
    fig.text(0.01, 0.01, footnote, fontsize=8, color=SLATE, ha="left")
    ax.set_ylim(-90, 210)
    _save(fig, f"event-side-signed-{lang}.png")


def chart_wiki(events, lang: str) -> None:
    rows = [e for e in events if (e.get("wikipedia_attention") or {}).get("ok")]
    labels = [_event_label(e, lang) for e in rows]
    series = [
        ("mean_14d_before", {"zh": "日前 14 日均值", "en": "14-day mean before"}, TEAL),
        ("views_on_date", {"zh": "当日", "en": "on the date"}, GOLD_B),
        ("mean_14d_after", {"zh": "日后 14 日均值", "en": "14-day mean after"}, GOLD),
    ]
    x = np.arange(len(rows))
    width = 0.26
    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    for i, (key, lab, color) in enumerate(series):
        vals = []
        for e in rows:
            v = (e.get("wikipedia_attention") or {}).get(key)
            vals.append(max(float(v), 0.5) if isinstance(v, (int, float)) else np.nan)
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=lab[lang], color=color, edgecolor="none", zorder=3, log=True)
        for bar, v in zip(bars, vals):
            if not np.isfinite(v):
                continue
            raw = v
            ax.annotate(
                f"{raw:,.0f}",
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center",
                va="bottom",
                fontsize=7,
                color=TEXT,
                rotation=90,
                xytext=(0, 4),
                textcoords="offset points",
            )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.grid(axis="y", which="major", zorder=0)
    ax.set_axisbelow(True)
    if lang == "zh":
        ax.set_title("有记录日期前后的维基百科浏览量（对数刻度）", fontsize=15, color=GOLD_B, pad=12)
        ax.set_ylabel("英文维基用户浏览（对数）")
        footnote = "官方 Wikimedia REST API。缺测不插值。GME 与 AMC 的关注在 2021 年 1 月 25 日之后爆发——滞后的公开痕迹，不是原始信号。"
    else:
        ax.set_title("Wikipedia pageviews around documented dates (log scale)", fontsize=14, color=GOLD_B, pad=12)
        ax.set_ylabel("English Wikipedia user pageviews (log)")
        footnote = "Official Wikimedia REST API. Missing values are not interpolated. GME and AMC attention exploded after 25 Jan 2021 — a lagging public trace, not the original signal."
    ax.legend(loc="upper left", framealpha=0.95)
    fig.text(0.01, 0.01, footnote, fontsize=8, color=SLATE, ha="left")
    _save(fig, f"wiki-attention-{lang}.png")


def chart_live(lang: str) -> None:
    corr = json.loads((DATA / "corroboration_sample.json").read_text(encoding="utf-8"))
    wiki = json.loads((DATA / "wiki13_corrected.json").read_text(encoding="utf-8"))
    xraw = json.loads((DATA / "x_counts_sample.json").read_text(encoding="utf-8"))
    tickers = ["CROX", "LULU", "ELF", "TPR", "NWL"]
    trends = []
    wiki_sum = []
    for t in tickers:
        plat = (corr.get("tickers") or {}).get(t, {}).get("platforms", {})
        m = (plat.get("google_trends") or {}).get("momentum_0_100")
        trends.append(m if isinstance(m, (int, float)) else np.nan)
        s = (wiki.get("sum_13d") or {}).get(t)
        wiki_sum.append(s if isinstance(s, (int, float)) else np.nan)
    x_map = {s["ticker"]: s["total_tweet_count"] for s in xraw.get("series") or []}
    x_counts = [x_map.get(t, np.nan) for t in tickers]

    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.7))
    panels = [
        (
            trends,
            {"zh": "Google Trends 动量（0–100）", "en": "Google Trends momentum (0–100)"},
            GOLD,
            False,
        ),
        (
            wiki_sum,
            {"zh": "维基 13 日浏览合计", "en": "Wikipedia 13-day pageview sum"},
            TEAL,
            False,
        ),
        (
            x_counts,
            {"zh": "X 近 7 日计数", "en": "X posts, last ~7 days"},
            GOLD_B,
            True,
        ),
    ]
    for ax, (vals, title, color, is_x) in zip(axes, panels):
        x = np.arange(len(tickers))
        colors = []
        for i, t in enumerate(tickers):
            if is_x and t == "ELF":
                colors.append(ROSE)  # noisy query
            else:
                colors.append(color)
        bars = ax.bar(x, [0 if not np.isfinite(v) else v for v in vals], color=colors, edgecolor="none", zorder=3)
        for i, (bar, v, t) in enumerate(zip(bars, vals, tickers)):
            if not np.isfinite(v):
                bar.set_height(0)
                bar.set_alpha(0)
                miss = "缺测" if lang == "zh" else "missing"
                ax.annotate(miss, (bar.get_x() + bar.get_width() / 2, 8000),
                            ha="center", va="bottom", fontsize=9, color=SLATE, rotation=0)
                continue
            label = f"{v:,.0f}" if v >= 10 else f"{v:.2f}".rstrip("0").rstrip(".")
            if is_x and t == "ELF":
                label = ("90,164*" if lang == "en" else "90,164*")
            ax.annotate(
                label,
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center",
                va="bottom",
                fontsize=8,
                color=TEXT,
                xytext=(0, 3),
                textcoords="offset points",
            )
        ax.set_xticks(x)
        xticklabels = [t + ("*" if is_x and t == "ELF" else "") for t in tickers]
        ax.set_xticklabels(xticklabels, fontsize=10)
        ax.set_title(title[lang], fontsize=11, color=GOLD_B, pad=8)
        ax.grid(axis="y", zorder=0)
        ax.set_axisbelow(True)
        if is_x:
            ax.ticklabel_format(axis="y", style="plain")
    if lang == "zh":
        fig.suptitle("2026 年 11 月 13 日 Trends、维基与 X 计数的即时快照", fontsize=15, color=GOLD_B, y=1.03)
        footnote = "ELF* 在 X 上去掉 $ 之后是噪声查询——不要把 90,164 当成干净的品牌计数。NWL 的 X 计数未取到，标为缺测。维基 ELF / TPR 使用更正后的条目标题。"
    else:
        fig.suptitle("Live snapshot of Trends, Wikipedia, and X counts on 13 Nov 2026", fontsize=14, color=GOLD_B, y=1.03)
        footnote = "ELF* on X is a noisy query after X strips the $ character — do not treat 90,164 as a clean brand count. NWL X count was not retrieved (shown as missing). Wikipedia ELF/TPR use corrected article titles."
    fig.text(0.01, -0.04, footnote, fontsize=8, color=SLATE, ha="left", wrap=True)
    fig.tight_layout()
    _save(fig, f"live-snapshot-{lang}.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    events = _load_events()
    for lang in ("zh", "en"):
        chart_forward(events, lang)
        chart_signed(events, lang)
        chart_wiki(events, lang)
        chart_live(lang)
    print("done")


if __name__ == "__main__":
    main()
