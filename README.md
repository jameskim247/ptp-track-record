# PTP Trader Track Record

A simple public track record for the PTP Trader.

Current public range: **2026-03-01 to 2026-07-10**. Pending rows use basis **prospective** (publicly declared before the realized result was settled). Settled rows use **prospective_settled** when the pending declaration was later settled by the live pipeline, or **model_backfill** for history constructed retroactively at the 2026-07-07 reset (see METHODOLOGY.md for what these labels do and do not claim).

## Files

- `data/daily.csv` - one row per delivery date.
- `data/weekly.csv` - calendar-week rollups, clipped to the published range.
- `data/monthly.csv` - monthly rollups, clipped to the published range.
- `data/summary.csv` - one full-record metric row.
- `proof/private_anchor.json` - opaque validation hashes.
- `proof/records.sha256` - hashes for public files.

Weekly, monthly, and summary files are deterministic aggregations of `data/daily.csv`.
