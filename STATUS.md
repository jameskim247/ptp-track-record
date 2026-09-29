# Status

- series-01: 271 settled rows

Display through: 2026-09-28.

- series-01: contiguous settled through 2026-09-28; latest settled date 2026-09-28; 0 unsettled or unavailable dates.

All-series contiguous settled through: 2026-09-28.

## Availability

A date records INCONCLUSIVE-SHARED-AVAILABILITY when one shared cause left no series able to commit before the frozen cutoff, and FAIL-SERIES-AVAILABILITY when a series failed while the shared inputs and the other series stayed healthy. Only the second counts against a series. Both leave the date out of every settled statistic.

Recovered after the cutoff and published as `recovered_after_cutoff` rows: 2026-09-26, 2026-09-28. Each missed its decision cutoff, so no commitment exists for it. Its book was rebuilt afterwards by the same frozen rule from inputs published before the cutoff, then paper-settled. These rows count in the daily ledger, cumulative P&L and period statistics, and never in the `prospective_shadow` summary. A recovered row stays pending until every price it settles on is published. The original availability failure is kept in the private record.
