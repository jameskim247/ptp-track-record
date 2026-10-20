# Historical storm replay

Retrospective development diagnostics, not executed trades or independent validation.
USD, before costs and without a market-impact model. The original 2024-onward performance record is unchanged.

## Results

Daily strategy books were rebuilt for Uri (February 14-19, 2021) and Elliott
(December 22-25, 2022), rather than applying a recent book to old prices.

| Storm / book | Paper P&L | Event drawdown | Modeled awarded MWh | Price coverage | Award-node evidence |
| --- | ---: | ---: | ---: | ---: | ---: |
| Uri / pairs-100 | -$79,987 | $108,683 | 996 | 100% | 64.2% |
| Uri / pairs-50 | -$68,542 | $97,340 | 900 | 100% | 65.3% |
| Elliott / pairs-100 | -$3,000 | $13,486 | 840 | 100% | 67.5% |
| Elliott / pairs-50 | -$3,000 | $13,486 | 843 | 100% | 67.3% |

Amounts above are rounded; CSVs retain precision. Event drawdown starts from zero.
Worst daily loss: $46,685 in Uri and $13,420 in Elliott for both books.

## Files and coverage

- [stress.csv](../risk/stress.csv): four event/book totals, DA and RT dollar legs,
  drawdown, worst day, volume and coverage.
- [stress_daily.csv](../risk/stress_daily.csv): 20 daily/book rows with order counts,
  volumes, DA/RT attribution and fingerprints of each private decision and settlement record.
- [source_anchor.json](../risk/source_anchor.json): study identity, file hashes,
  source bindings and historical assumptions.
- [publication.json](../risk/publication.json): the fixed study's verification receipt,
  not a claim of current trading-day freshness.

Price coverage is fully priced modeled awarded MWh divided by modeled awarded MWh.
Valuation requires all four paired source/sink 15-minute RT intervals and usable DA prices.
No modeled awarded MWh is unpriced in these two event windows.

Award-node evidence is modeled awarded MWh whose two node/hour endpoints both occur in
actual market PTP awards. It is not actual awards to this strategy. Exact directed-pair/hour
award overlap is 0% in Uri and about 1.1% in Elliott; absence of an identical market pair
does not itself establish that a bid was prohibited. Complete prices do not establish
executable awards.

## Timing and historical assumptions

Selection uses then-observed nodes, earlier price publications, dated load forecasts and
the latest 30 DAM disclosures published before D-1 09:55 America/Chicago. Later storm-day
disclosures evaluate modeled auction outcomes; they are not that day's selection input.
Original DA clearing prices determine modeled awards; later corrections affect settlement,
not earlier decisions. The correction search ends 181 days after each event's first day.

Sizing cold-starts at the frozen risk prior at each event start, then updates using D-2
reference results. It is not a continuous pre-storm sizing history. The grid-score formula
is causally refitted from archives beginning in 2018, without a modern topology peer map;
unavailable node fits retain the existing zero fallback.

Original operating-day de-energized-node lists are unavailable. Modeled awards use bid
limits plus the existing in-money/no-awards restriction reconstructed from market bids
and awards. These assumptions cannot establish actual strategy awards or a tail-loss limit.
Stopping new bids does not cancel already-awarded obligations.

## Sources and verification

ERCOT archived products: NP4-190-CD (DA prices), NP6-905-CD (RT prices),
NP3-565-CD (load forecasts), NP3-966-ER (delayed DAM disclosure), NP4-191-CD and
NP6-86-CD (constraint prices), NP4-196-M and NP4-197-M (price corrections).
The study was run October 19, 2026. All 1,379 order rows were independently revalued
from normalized source prices, reconciling to the daily totals; source normalization
remains shared upstream evidence, not an independent audit of ERCOT files.

Run `python3 scripts/verify.py` to check file/row bindings, calendar completeness,
daily and event arithmetic, coverage denominators and preserved financial-series proofs.
Positions, strategy code, source receipts and the prior fixed-book stress snapshot remain private.
