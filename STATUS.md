# Status

- series-01: 249 settled rows
- series-02: 257 settled rows
- series-03: 257 settled rows
- series-04: 257 settled rows

Display through: 2026-09-16.

- series-01: contiguous settled through 2026-01-07; latest settled date 2026-09-16; 10 unsettled or unavailable dates.
- series-02: contiguous settled through 2026-09-13; latest settled date 2026-09-16; 2 unsettled or unavailable dates.
- series-03: contiguous settled through 2026-09-13; latest settled date 2026-09-16; 2 unsettled or unavailable dates.
- series-04: contiguous settled through 2026-09-13; latest settled date 2026-09-16; 2 unsettled or unavailable dates.

All-series contiguous settled through: 2026-01-07.

## Availability

A date records INCONCLUSIVE-SHARED-AVAILABILITY when one shared cause left no series able to commit before the frozen cutoff, and FAIL-SERIES-AVAILABILITY when a series failed while the shared inputs and the other series stayed healthy. Only the second counts against a series. Both leave the date out of every settled statistic.

- Shared, counting against no series: 2026-09-14, 2026-09-15.
- series-01, counting against that series: 2026-01-10, 2026-03-08, 2026-03-10, 2026-06-06, 2026-07-11, 2026-08-29.

Status corrected after publication:
- 2026-09-14: FAIL-SERIES-AVAILABILITY to INCONCLUSIVE-SHARED-AVAILABILITY on 2026-09-17T18:13:32.506964+00:00; superseded decision e39628cdd98c; rule: docs/reports/2026-09-01_three-series-limit-paper-record-goal.md section 7.
- 2026-09-15: FAIL-SERIES-AVAILABILITY to INCONCLUSIVE-SHARED-AVAILABILITY on 2026-09-17T18:13:32.631410+00:00; superseded decision 7f3214f4c52a; rule: docs/reports/2026-09-01_three-series-limit-paper-record-goal.md section 7.
