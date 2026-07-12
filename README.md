# PTP Trader Track Record

A simple public track record for the PTP Trader.

Current public range: **2026-03-01 to 2026-07-12**. Pending rows use basis **prospective** (publicly declared before the realized result was settled). Settled rows use **prospective_settled** when the pending declaration was later settled by the live pipeline, or **model_backfill** for history constructed retroactively at the 2026-07-07 reset. Model-backfill rows retain explicit **legacy_he24_v1** labeling because severe historical ERCOT interval gaps prevent exact restatement; prospective rows use **ercot_he24_q4_v2**. Provisional rows use **prospective_provisional** and carry explicit interval/exposure evidence in `data/valuation_provenance.csv`. Superseded pre-fix values remain in `data/archive/daily_pre_valuation_v2.csv` (see METHODOLOGY.md).

## Files

- `data/daily.csv` - one row per delivery date.
- `data/archive/daily_pre_valuation_v2.csv` - immutable pre-v2 public record snapshot.
- `data/valuation_provenance.csv` - append-only valuation quality and revision history.
- `data/weekly.csv` - calendar-week rollups, clipped to the published range.
- `data/monthly.csv` - monthly rollups, clipped to the published range.
- `data/summary.csv` - one full-record metric row.
- `proof/private_anchor.json` - opaque validation hashes.
- `proof/records.sha256` - hashes for public files.

Weekly, monthly, and summary files are deterministic aggregations of `data/daily.csv`.
