# S4R-v2 retrospective causal replay

Public range: **2026-02-01 through 2026-08-13**. This is a retrospective causal replay and is not prospective evidence of a modeled
S4R-v2 shadow book at 800-MW gross, a 40-MW
variable replacement ceiling, and LOAD scale 0.20.
It is **not a live or realized trading track record** and is not promotion evidence.

The published arm was selected after outcomes were inspected from **15 candidate arms**
across 2025-H1, 2025-H2, and 2026-H1. Its Sharpe ranks were 2/15, 5/15,
1/15, and 2/15 pooled; on the original 2026-02-01 through 2026-06-30
publication window it ranks 4/15. No cross-arm rank is claimed for later replay dates.
All evidence is permanently **retrospective diagnostic / development-only**.
Hash proofs establish byte integrity and reproducibility, not out-of-sample or
prospective validity.

## What the S4R mechanism contributed

The whole S4R book includes a matched native book that does not use the S4R
overlay. On the 181 settled dates published here:

- S4R whole-book modeled PnL: $204268.69
- Matched native control modeled PnL: $194648.99
- Incremental S4R modeled PnL: $9619.70
  (0.049421 of matched-control PnL)
- Paired daily t statistic: 1.502351 with
  180 degrees of freedom

The paired statistic is descriptive, unadjusted, and development-only. It is
not a confirmatory test. Full outcome-inspected window comparisons are:

| Window | Paired exact days | Incremental modeled PnL | Increment/control | Paired t |
|---|---:|---:|---:|---:|
| 2025h1 | 114 | $30330.92 | 0.116415 | 2.638527 |
| 2025h2 | 182 | $94854.46 | 0.206870 | 4.029128 |
| 2026h1 | 169 | $-342.78 | -0.000945 | -0.037813 |

Sharpe and Sortino use a 365-day factor for the calendar-day cadence. They are
computed on settled days only; 12 unavailable days
are excluded rather than treated as zero returns.

`data/daily.csv` is the minimal public outcome ledger. `weekly.csv`,
`monthly.csv`, and `summary.csv` are deterministic derivatives. Detailed books,
positions, source data, and immutable evidence remain in the private hash-bound
canonical ledger.

Current rows: 181 settled, 12 unavailable, 0
provisional, 1 pending. Unavailable dates are explicit and excluded from
performance metrics; no zero is presented as a settled result.

This GitHub repository identity was created on 2026-08-13. The predecessor is
preserved at `jameskim247/ptp-track-record-archive-2026-08-13`.
