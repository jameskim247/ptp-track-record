# Historical storm replay

Retrospective development diagnostics; not executed trades, independent validation or a tail-loss limit.

| Storm / book | P&L | Event drawdown | Awarded MWh | Price coverage |
| --- | ---: | ---: | ---: | ---: |
| uri / pairs-100 | $0 | $0 | 0.0 | 0.0% |
| uri / pairs-50 | $0 | $0 | 0.0 | 0.0% |
| elliott / pairs-100 | $-66,044 | $87,304 | 1,295.1 | 100.0% |
| elliott / pairs-50 | $-39,214 | $61,388 | 1,124.7 | 100.0% |

## Why both S1 books stood aside during Uri

The system-stress flag fired on all six days, February 14–19, 2021. Each decision had only 3–8 prior flagged days available, below the minimum of 10. The regular and alternate books also had negative cumulative paper P&L on the prior stress days used by their respective rules. The regular books stood aside and the alternate books did not qualify, so neither book submitted orders.

Price coverage is priced awarded MWh divided by awarded MWh. Both Uri books had zero awarded MWh, so the ratio is undefined. The tables display 0.0% by convention for this zero denominator.

The strategy is replayed continuously from 2021-01-01 using its declared historical inputs and outcome-only restrictions. Zero exposure in a storm does not establish survival with awarded obligations. Statistical grid estimates are not physical network sensitivities. Historical input publication vintages and complete tradability remain incompletely certified.

[Event totals](../risk/stress.csv) · [Daily detail](../risk/stress_daily.csv). Award-node evidence identifies both node/hour endpoints in actual market awards; it does not establish an award to this strategy. Stopping new bids does not cancel awarded obligations.
