# Sample divergence run

**Generated:** 13 November 2026, 01:51 Asia/Shanghai (13:51 UTC on 12 November 2026).  
**Command:** `python -m camillo_tracker scan CROX LULU ELF NWL TPR`  
**Full JSON:** [sample_run.json](sample_run.json)

Not financial advice. A snapshot of free, unofficial data. Google Trends is a relative index and was available on this run. Reddit’s public JSON returned HTTP 403 from the build network (datacenter block); social scores therefore rest on Trends only. X was skipped (no bearer token). VADER scored analyst headlines.

Five consumer names tied to Camillo stories. **No `opportunity_flag`** fired — at this date, search momentum was not running ahead of a lukewarm Street. For names he made famous years ago, that is a plausible outcome: the imbalance may already have closed.

| Ticker | Close | Implied upside (mean target) | Consensus (1=Strong Buy) | Social (Trends) | Street | Divergence | Flag |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| CROX | $158.77 | +3.7% | 2.33 (3 Strong Buy, 5 Buy, 6 Hold, 1 Sell) | 42.8 (flat) | 63.9 | −21.1 | late or crowded |
| LULU | $105.14 | −0.8% | 3.16 (1 Buy, 30 Hold, 5 Sell, 1 Strong Sell) | 32.4 (fading) | 47.5 | −15.1 | watch |
| ELF | $114.42 | +14.5% | 2.28 (1 Strong Buy, 11 Buy, 6 Hold) | 37.8 (fading) | 61.5 | −23.7 | late or crowded |
| NWL | $5.84 | +9.7% | 2.56 (2 Strong Buy, 1 Buy, 5 Hold, 1 Sell) | 38.6 (fading) | 54.5 | −15.9 | watch |
| TPR | $133.90 | +22.2% | 2.05 (6 Strong Buy, 11 Buy, 4 Hold, 1 Strong Sell) | 59.8 (flat) | 63.7 | −3.9 | aligned |

### Reading the interesting corners

- **TPR (Tapestry / Coach).** The keyword “Coach bag” is the one Trends series that is actually *up*: recent average 32.6 versus 26.2 a year earlier and a 20.2 baseline (momentum 69.7). Combined with a dead “Tapestry Coach” series it averages to 59.8, almost exactly in line with a already-bullish Street (mean target $163.55, +22% implied upside). The 2021 “Coach comeback” Camillo described to Business Insider is, on this screen, **no longer an information gap**.
- **LULU.** Search for “Lululemon” is down versus a year ago (30.6 vs 44.5). The Street is cautious: thirty Holds, a slightly negative implied upside, recent action balance −2. Social is fading *with* a soft consensus — a watch, not a contrarian flag. (Camillo himself exited a Trends-led Lululemon thesis in 2025 after suspecting AI-polluted search.)
- **CROX and ELF.** Analysts are constructive; brand-term Trends sit below their longer baselines. The scanner labels that `late_or_crowded`: if there was a social-arbitrage window, this snapshot is not showing it open.
- **NWL.** Elmer’s / Newell search is similarly below last year. A mild Street score, a watch.

Prices, targets, and recommendation counts came from Yahoo Finance via yfinance at the timestamp above and will be stale the next morning. Re-run the toolkit for a fresh cut. Trends keywords are brand language (see `DEFAULT_KEYWORDS` in `divergence.py`), following Camillo’s habit of searching for the *product*, not the ticker.
