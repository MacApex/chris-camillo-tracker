# Chris Camillo Tracker

A researched, cited archive of Chris Camillo's **social-arbitrage** investing — the independently reviewed track record, a distilled playbook, a map of tools that approximate the inputs he uses, a counter-analysis of why Wall Street can lag consumer culture, and a working Python **divergence scanner** that contrasts sell-side consensus with search and social momentum.

**[Open the site](https://macapex.github.io/chris-camillo-tracker/)** · Research notes live in [`research/`](research/) · Scanner in [`toolkit/`](toolkit/)

This project is **not affiliated with** Chris Camillo, Dumb Money, TickerTags, M Science, Jack Schwager, or Business Insider. **It is not financial advice.** You can lose money, especially with options and concentration. Read [DISCLAIMER.md](DISCLAIMER.md) before anything else.

## The audited core, in brief

The only numbers we treat as independently reviewed are from Jack Schwager's audit of monthly brokerage statements, reported and partly re-examined by *Business Insider* (Laila Maidan, 18 August 2021), with a second reading by Prof. Biljana Adebambo:

- Statements from **August 2006**, starting balance **$84,000**.
- **77%** average annual compounded return, 2006–2020, against **7.6%** for the S&P 500 in the same window.
- More than **$21 million** by May 2020, including withdrawals; **$42 million** cumulative profits by May 2021.
- Portfolio volatility almost **five times** an S&P 500 ETF; options were a likely ingredient.
- Later headline totals ($70 million, $80 million) and single-trade P&Ls are **self-reported** unless we say otherwise. The popular "$20,000 to $2 million" origin is a sleeve (or at least not Schwager's starting balance). Details: [`research/01-track-record.md`](research/01-track-record.md).

## Strategy essence

Social arbitrage is **information-gap investing**. Observe a real change in culture, consumption, technology, or policy — often on the ground or in unpolished social conversation — connect it to a public company large enough for the change to *matter* and early enough that the Street has not priced it, and exit as the fact reaches earnings, notes, and the tape. Camillo ignores charts and traditional fundamentals (except size), does not use stop-losses, sizes by conviction (he has said 2–30%), often uses **options** for leverage inside a separate "big money" account, and scales out as information reaches parity. The edge is **being early**, not being clever on the same model as everyone else. Full playbook: [`research/02-methodology-and-playbook.md`](research/02-methodology-and-playbook.md).

## Repository map

```
research/     Cited notes: track record, playbook, resources, Wall Street lag, sources
toolkit/      Divergence scanner (analyst vs. social), with a real example run
docs/         Static site for GitHub Pages
DISCLAIMER.md Not financial advice; verification policy
```

## Divergence scanner

```bash
cd toolkit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m camillo_tracker scan CROX LULU ELF NWL TPR --out examples/sample_run.json
```

The scanner (a) pulls Yahoo Finance recommendations, price targets, upgrades/downgrades and headlines via yfinance; (b) scores the text with VADER (optional FinBERT); (c) pulls Google Trends via pytrends and Reddit via public JSON (optional X); (d) emits a divergence score that flags names where **niche momentum is rising while analyst sentiment is flat or negative**. That flag is a prompt for human work, not a trade. See [`toolkit/README.md`](toolkit/README.md) and [`research/04-wall-street-lag.md`](research/04-wall-street-lag.md).

## What we could not verify

Pabst Blue Ribbon and Vegas Golden Knights stories: **no source** linking them to Camillo. GameStop as a documented personal trade: **not found**. The 2014 accountant's PDF: cited by Wikipedia, **not retrieved**. Lifetime totals beyond the May 2021 Schwager update: **self-reported**. See the [sources and gaps log](research/05-sources.md).

## License and use

Research and education only. Quoted passages are brief and attributed. Please do not treat this archive as a product, a signal service, or a substitute for *Laughing at Wall Street* or *Unknown Market Wizards*.
