"""Command-line entry: python -m camillo_tracker scan CROX LULU ELF --out results.json"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _print_table(bundle: dict) -> None:
    rows = bundle.get("results") or []
    print()
    print(bundle.get("title", "Divergence scan"))
    print(f"generated: {bundle.get('generated_at')}")
    print("-" * 96)
    hdr = f"{'TICKER':<8} {'SOCIAL':>8} {'STREET':>8} {'DIV':>8} {'FLAG':<20} {'CLOSE':>10} {'UPSIDE':>8}"
    print(hdr)
    print("-" * 96)
    for r in rows:
        if r.get("error") and not r.get("analyst"):
            print(f"{r.get('symbol','?'):<8} ERROR: {r['error'][:70]}")
            continue
        social = ((r.get("social") or {}).get("composite") or {}).get("score")
        street = ((r.get("analyst") or {}).get("composite") or {}).get("score")
        div = (r.get("divergence") or {}).get("score")
        flag = (r.get("divergence") or {}).get("flag") or ""
        close = ((r.get("analyst") or {}).get("raw") or {}).get("last_close")
        up = ((r.get("analyst") or {}).get("raw") or {}).get("implied_upside_pct")
        def fmt(x, n=7):
            return f"{x:{n}.1f}" if isinstance(x, (int, float)) else f"{'—':>{n}}"
        close_s = f"{close:,.2f}" if isinstance(close, (int, float)) else "—"
        up_s = f"{up:+.1f}%" if isinstance(up, (int, float)) else "—"
        print(f"{r.get('symbol',''):<8} {fmt(social):>8} {fmt(street):>8} {fmt(div):>8} {flag:<20} {close_s:>10} {up_s:>8}")
    print("-" * 96)
    print()
    for r in rows:
        d = r.get("divergence") or {}
        if d.get("interpretation"):
            print(f"  {r.get('symbol')}: {d['interpretation']}")
    print()
    print(bundle.get("disclaimer"))
    print()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="camillo_tracker",
        description=(
            "Scan tickers for a social-vs-Street divergence score. "
            "Research only — not financial advice."
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="Run a divergence scan on one or more tickers")
    s.add_argument("tickers", nargs="+", help="Ticker symbols, e.g. CROX LULU ELF")
    s.add_argument("--out", "-o", help="Write full JSON to this path")
    s.add_argument(
        "--keywords",
        action="append",
        default=[],
        metavar="TICKER=kw1,kw2",
        help="Override Google Trends keywords, e.g. --keywords CROX='Crocs shoes,Hey Dude'",
    )
    args = p.parse_args(argv)

    # Import here so `--help` does not require deps to be fully happy
    from .divergence import scan_many

    kw_map = {}
    for item in args.keywords:
        if "=" not in item:
            print(f"ignore malformed --keywords {item}", file=sys.stderr)
            continue
        k, v = item.split("=", 1)
        kw_map[k.upper().strip()] = [x.strip() for x in v.split(",") if x.strip()]

    bundle = scan_many([t.upper() for t in args.tickers], keyword_map=kw_map or None)
    _print_table(bundle)
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(bundle, indent=2, default=str), encoding="utf-8")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
