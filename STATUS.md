# Status

## Daily publication readiness

The [daily publication workflow](.github/workflows/publish-daily.yml) runs twice daily at 14:17 and 22:17 UTC.
See [the machine-readable coverage receipt](proof/publication.json) for the latest checked date and missing-result range.

The original price seeds were recovered on 6 October 2026, checked against the public fingerprints,
and backed up privately in GCS. The restored source matches the frozen specification. On the recovered laptop runtime, five days of books,
per-order settlement lines and volatility sizing reconcile against the original record.
The E24 producer supports daily retrospective continuation on GCP; the production programme's `series-02`
remains a different strategy. No E24 prospective paper-trading claim is made.

The original engine contains an unstable sort for equal-scored pairs. Its tie order can differ
between the original AVX-512 environment and the GCP AVX2 environment, even with identical
source and NumPy versions. Original published books and rows are retained exactly, not reselected.
Continuation pins the existing GCP NumPy 2.5 / X86_V3 / single-threaded OpenBLAS Haswell kernels,
records them in the anchor, and verifies restored continuation books against archived orders.
This is a numerical-runtime limitation, not a change to weights or a newly selected historical strategy.

The normal source is `SERIES2_GCS_URI`, read through a GitHub OIDC identity restricted to this repository's
main-branch publication workflow and the GCS public-artifact prefix. It cannot read private seeds or orders.
An HTTPS public-result ZIP configured as `SERIES2_SOURCE_URL` remains an optional alternate.
The ZIP must contain exactly `data/series-2/{daily,weekly,monthly,summary}.csv` and `proof/anchor.json`.
The consumer checks the unchanged frozen-spec digest, costs, evidence class, contiguous dates, row proofs,
and independent arithmetic before installation. New rows require updated private source commitments;
historical restatements require `supersedes_records_sha256` naming the current public manifest.
The source package must contain no strategy code, orders, credentials or private price files.
The producer retains verified observations and retries incomplete continuation settlements hourly.
A narrower or temporarily unavailable current price view cannot erase previously verified observations.
The coverage receipt reports readiness from actual verified artifacts,
not from this setup description. Original-history rows remain unchanged; continuation restatements name the superseded
public manifest. A partially settled row reports only priced P&L and all placed costs, with unknown awarded volume shown separately.

## Original economic record (snapshot before daily continuation)

- series-2: 1,095 rows, 2023-10-01 through 2026-09-29. 1,009 `settled`, 86 `partially_settled`, none blank.
- Every row is `retrospective_reconstruction`. There are no forward rows: no book in this record was committed before its decision cutoff.

## Partially settled

A `partially_settled` row has at least one awarded order whose settlement needs a real-time price that is missing from our data for a resource node or a DC tie. The day-ahead prices for every such order are known, so its award is not in doubt; only its value is.

The row stays `partially_settled` until the missing prices are recovered from ERCOT's archive and the row is restated. A restatement changes the affected rows, their proofs and every derived table, and is recorded here with the superseded manifest digest.

The 86 original-history partial days below are preserved unchanged by the continuation producer;
their historical archive repair is not included in this deployment. New continuation partial days are retried automatically.
The current date range, missing-day count and total partial-day count are always in `proof/publication.json`.

- 2025: 82 days. The volume is mostly DC ties (DC_L, DC_N, DC_R, DC_E).
- 2026: 4 days (01-08, 06-04, 07-09, 08-27). Each is a whole hour missing for almost every resource node.

## Not yet in ERCOT's annual reports

Zone and hub prices for 2026-09-27, 09-28 and 09-29 come from the same source as resource nodes. They will be checked against ERCOT's annual reports once those reports include them.
