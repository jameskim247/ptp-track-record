# Historical storm replay

Retrospective development diagnostics; not executed trades, independent validation or a tail-loss limit.

| Storm / book | P&L | Event drawdown | Awarded MWh | Price coverage |
| --- | ---: | ---: | ---: | ---: |
| uri / pairs-100 | $0 | $0 | 0.0 | 0.0% |
| uri / pairs-50 | $0 | $0 | 0.0 | 0.0% |
| elliott / pairs-100 | $-132,088 | $174,609 | 2,590.2 | 100.0% |
| elliott / pairs-50 | $-78,428 | $122,776 | 2,249.4 | 100.0% |

## Why Elliott had a different result

Uri was already above the stress thresholds before the February 14 decision. The prior day’s peak day-ahead hub price was $2,052.75/MWh against a $116.62/MWh threshold. For Elliott, the indicators remained below their thresholds at the December 22 and 23, 2022 decisions. Both books submitted bids and received modeled awards on those dates. For the December 24 decision, the prior morning’s absolute gap between real-time and day-ahead hub prices had reached $2,636.35/MWh against a $642.20/MWh threshold. The stress flag fired for December 24 and 25, and both books stood aside.

December 23 drove Elliott’s losses. The real-time leg lost $207,031 for pairs-100 and $148,115 for pairs-50, exceeding their day-ahead gains of $32,422 and $25,339. The net losses that day were $174,609 and $122,776, respectively. December 22 gains reduced the event losses shown above. All modeled Elliott awards had usable settlement prices, yielding 100% coverage.

The strategy is replayed continuously from 2021-01-01 using its declared historical inputs and outcome-only restrictions. Zero exposure in a storm does not establish survival with awarded obligations. Statistical grid estimates are not physical network sensitivities. Historical input publication vintages and complete tradability remain incompletely certified.

[Event totals](stress.csv) · [Daily detail](stress_daily.csv). Award-node evidence identifies both node/hour endpoints in actual market awards; it does not establish an award to this strategy. Stopping new bids does not cancel awarded obligations.

The source-binding hashes identify the original audited storm plan, replay and order records. The derivative study hash binds the doubled rows to the active quantity protocol.
