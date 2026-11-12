# Data and provenance

All numbers in this folder were fetched or compiled with a source, a timestamp, and a method. Nothing here is an estimate of a blocked count.

| File | What |
|---|---|
| `trades.json` | 43 sourced Camillo / Dumb Money records, with verification levels. |
| `provenance.csv` | One row per probe: platform, metric, value, URL, method, status, reason. |
| `platform_status.json` | Per-platform worked / partial / blocked, with what was tried. |
| `x_counts_sample.json` | Official X 7-day counts, 13 Nov 2026, via Grok Bot MCP. ELF query is noisy. |
| `youtube_ytsearch_crocs.json` | yt-dlp metadata, no download. |
| `wikipedia/` | Official Wikimedia REST pageviews, including historical event windows. |
| `gdelt/CROX.json` | GDELT TimelineVol after a rate-limit retry. |
| `experiments/` | Event-study JSON and CSV (market paths, not personal P&L). |

Site copies of the public files live in `docs/data/` for GitHub Pages.
