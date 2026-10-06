# Status

## Daily publication readiness

The [daily publication workflow](.github/workflows/publish-daily.yml) runs twice daily at 14:17 and 22:17 UTC.
See [the machine-readable coverage receipt](proof/publication.json) for the latest checked date and missing-result range.

The original E24 producer was left in a temporary research workspace. Its first-published decision cube
`/home/claude/ptp/data/cube_pit2.npz`, final-settlement cube `cube_full4.npz`, and replay/sizing state
have not been restored to the production VM. E24 is not running prospective paper trading there.
The production programme's `series-02` is a different strategy.

Once the producer is restored, configure the repository variable `SERIES2_SOURCE_URL` to its HTTPS public-result ZIP.
The ZIP must contain exactly `data/series-2/{daily,weekly,monthly,summary}.csv` and `proof/anchor.json`.
The consumer checks the unchanged frozen-spec digest, costs, evidence class, contiguous dates, row proofs,
and independent arithmetic before installation. New rows require updated private source commitments;
historical restatements require `supersedes_records_sha256` naming the current public manifest.
The source package must contain no strategy code, orders, credentials or private price files.
No source URL is currently configured. Missing calculations remain explicitly missing, never zero-valued results.

## Existing economic record

- series-2: 1,095 rows, 2023-10-01 through 2026-09-29. 1,009 `settled`, 86 `partially_settled`, none blank.
- Every row is `retrospective_reconstruction`. There are no forward rows: no book in this record was committed before its decision cutoff.

## Partially settled

A `partially_settled` row has at least one awarded order whose settlement needs a real-time price that is missing from our data for a resource node or a DC tie. The day-ahead prices for every such order are known, so its award is not in doubt; only its value is.

The row stays `partially_settled` until the missing prices are recovered from ERCOT's archive and the row is restated. A restatement changes the affected rows, their proofs and every derived table, and is recorded here with the superseded manifest digest.

- 2025: 82 days. The volume is mostly DC ties (DC_L, DC_N, DC_R, DC_E).
- 2026: 4 days (01-08, 06-04, 07-09, 08-27). Each is a whole hour missing for almost every resource node.

## Not yet in ERCOT's annual reports

Zone and hub prices for 2026-09-27, 09-28 and 09-29 come from the same source as resource nodes. They will be checked against ERCOT's annual reports once those reports include them.
