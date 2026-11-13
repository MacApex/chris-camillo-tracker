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
    st = sub.add_parser("street", help="Street Consensus Profile and priced-in verdict")
    st.add_argument("ticker", help="Ticker symbol")
    st.add_argument("--out", "-o", help="Write JSON")
    sig = sub.add_parser("signals", help="Multi-platform niche signals and corroboration")
    sig.add_argument("ticker", help="Ticker symbol")
    sig.add_argument("--keywords", default="", help="Comma-separated Trends / news keywords")
    sig.add_argument("--wiki", default="", help="English Wikipedia article title")
    sig.add_argument("--out", "-o", help="Write JSON")
    res = sub.add_parser("research", help="End-to-end research workflow: signals, corroboration, Street view, dated report")
    res.add_argument("brand", help="Brand or observation name, e.g. Crocs")
    res.add_argument("ticker", help="Ticker symbol, e.g. CROX")
    res.add_argument("--wiki", default="", help="English Wikipedia article title")
    res.add_argument("--keywords", default="", help="Comma-separated Trends / news keywords")
    res.add_argument("--out", "-o", default="", help="Directory for the dated markdown+JSON report")
    res.add_argument("--offline", action="store_true", help="Use verified caches only; no new network calls")
    args = p.parse_args(argv)

    if args.cmd == "research":
        from .workflow import run_research
        kws = [x.strip() for x in (args.keywords or "").split(",") if x.strip()] or None
        out = args.out or "examples/reports"
        report = run_research(
            args.brand,
            args.ticker.upper(),
            wiki=args.wiki or None,
            keywords=kws,
            out_dir=out,
            offline=bool(args.offline),
        )
        print()
        print(report["markdown"])
        if report.get("written"):
            print("wrote", report["written"]["markdown"])
            print("wrote", report["written"]["json"])
        return 0

    if args.cmd == "street":
        from .street_view import street_profile
        import json as _json
        prof = street_profile(args.ticker.upper())
        v = prof.get("verdict") or {}
        print(f"\n{prof.get('symbol')}  verdict={v.get('label')}  confidence={v.get('confidence')}  points={v.get('priced_in_points')}")
        for r in v.get("reasons") or []:
            print("  -", r)
        print("\n", (prof.get("how_it_feeds_the_tree") or ""), "\n")
        print("Not financial advice.\n")
        if args.out:
            Path(args.out).write_text(_json.dumps(prof, indent=2, default=str), encoding="utf-8")
            print("wrote", args.out)
        return 0

    if args.cmd == "signals":
        from .signals import collect_signals
        import json as _json
        kws = [x.strip() for x in (args.keywords or "").split(",") if x.strip()] or None
        bundle = collect_signals(args.ticker.upper(), keywords=kws, wiki_article=args.wiki or None)
        c = bundle.get("corroboration") or {}
        print(f"\n{bundle.get('symbol')}  corroborated={c.get('corroborated')}  n={c.get('n_confirming')}  z={c.get('weighted_z')}  score={c.get('composite_0_100')}")
        print(" ", c.get("interpretation"))
        for name, res in (bundle.get("platforms") or {}).items():
            print(f"  {name:16} {(res or {}).get('status')}  {(res or {}).get('reason') or ''}")
        print()
        if args.out:
            Path(args.out).write_text(_json.dumps(bundle, indent=2, default=str), encoding="utf-8")
            print("wrote", args.out)
        return 0

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
