"""Sentiment scoring with VADER, optional FinBERT, and a lexicon fallback."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable, Sequence

# Lightweight finance-aware lexicon used if VADER is unavailable, and as
# a modest overlay on short analyst-style phrases.
_POS = {
    "upgrade": 1.4, "upgraded": 1.4, "outperform": 1.2, "overweight": 0.9,
    "buy": 1.0, "strong buy": 1.6, "accumulate": 0.8, "initiate": 0.3,
    "beat": 1.1, "beats": 1.1, "raised": 0.9, "raises": 0.9, "raise": 0.8,
    "bullish": 1.2, "positive": 0.8, "growth": 0.5, "surge": 1.0,
    "record": 0.6, "momentum": 0.5, "outperformed": 1.0, "exceeded": 0.9,
    "exceeds": 0.9, "optimistic": 0.8, "upside": 0.7, "strength": 0.5,
}
_NEG = {
    "downgrade": -1.6, "downgraded": -1.6, "underperform": -1.2,
    "underweight": -0.9, "sell": -1.1, "strong sell": -1.6, "reduce": -0.9,
    "miss": -1.1, "misses": -1.1, "missed": -1.1, "cut": -0.8, "cuts": -0.8,
    "lowered": -0.9, "lowers": -0.9, "bearish": -1.2, "negative": -0.8,
    "weak": -0.7, "weakness": -0.8, "slowdown": -0.8, "warning": -0.9,
    "lawsuit": -0.7, "recall": -1.0, "fraud": -1.6, "bankruptcy": -2.0,
    "plunge": -1.2, "crash": -1.4, "disappoint": -0.9, "disappoints": -0.9,
    "downside": -0.7, "concern": -0.5, "concerns": -0.5, "risk": -0.3,
}


@dataclass
class SentimentResult:
    score: float  # -1 to 1
    label: str
    engine: str
    n_texts: int
    details: list[dict]


def _label(score: float) -> str:
    if score >= 0.15:
        return "positive"
    if score <= -0.15:
        return "negative"
    return "neutral"


def _lexicon_score(text: str) -> float:
    t = (text or "").lower()
    if not t.strip():
        return 0.0
    # Multi-word first
    raw = 0.0
    hits = 0
    for phrase, w in list(_POS.items()) + list(_NEG.items()):
        if " " in phrase and phrase in t:
            raw += w
            hits += 1
            t = t.replace(phrase, " ")
    tokens = re.findall(r"[a-z][a-z\-']+", t)
    for tok in tokens:
        if tok in _POS:
            raw += _POS[tok]
            hits += 1
        elif tok in _NEG:
            raw += _NEG[tok]
            hits += 1
    if hits == 0:
        return 0.0
    # squash into [-1, 1]
    return max(-1.0, min(1.0, raw / (hits ** 0.6) / 2.0))


def _vader():
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        return SentimentIntensityAnalyzer()
    except Exception:
        return None


def _finbert():
    if os.environ.get("CCT_USE_FINBERT", "").strip() not in {"1", "true", "yes"}:
        return None
    try:
        from transformers import pipeline

        return pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            truncation=True,
            max_length=128,
        )
    except Exception:
        return None


_VADER = None
_FINBERT = None
_INIT = False


def _engines():
    global _VADER, _FINBERT, _INIT
    if not _INIT:
        _VADER = _vader()
        _FINBERT = _finbert()
        _INIT = True
    return _VADER, _FINBERT


def score_text(text: str) -> tuple[float, str]:
    """Return (score in [-1, 1], engine name) for a single string."""
    text = (text or "").strip()
    if not text:
        return 0.0, "empty"
    vader, finbert = _engines()
    if finbert is not None:
        try:
            out = finbert(text[:512])[0]
            label = (out.get("label") or "").lower()
            conf = float(out.get("score") or 0.0)
            if "pos" in label:
                return conf, "finbert"
            if "neg" in label:
                return -conf, "finbert"
            return 0.0, "finbert"
        except Exception:
            pass
    if vader is not None:
        try:
            c = float(vader.polarity_scores(text)["compound"])
            return c, "vader"
        except Exception:
            pass
    return _lexicon_score(text), "lexicon"


def score_texts(texts: Iterable[str], source: str = "") -> SentimentResult:
    items: list[dict] = []
    engines: list[str] = []
    for raw in texts:
        t = (raw or "").strip()
        if not t:
            continue
        s, eng = score_text(t)
        items.append({"text": t[:280], "score": round(s, 4), "engine": eng, "source": source})
        engines.append(eng)
    if not items:
        return SentimentResult(0.0, "neutral", "none", 0, [])
    avg = sum(i["score"] for i in items) / len(items)
    engine = max(set(engines), key=engines.count)
    return SentimentResult(round(avg, 4), _label(avg), engine, len(items), items)
