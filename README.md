# PTP Trader Track Record

A simple public track record for the PTP Trader.

Current public range: **2026-03-01 to 2026-07-10**. Settled rows use basis **model_backfill**; pending rows use basis **prospective**, meaning publicly declared before the realized result was settled (see METHODOLOGY.md for what this label does and does not claim).

## Files

- `data/daily.csv` - one row per delivery date.
- `data/weekly.csv` - calendar-week rollups, clipped to the published range.
- `data/monthly.csv` - monthly rollups, clipped to the published range.
- `data/summary.csv` - one full-record metric row.
- `proof/private_anchor.json` - opaque validation hashes.
- `proof/records.sha256` - hashes for public files.

Weekly, monthly, and summary files are deterministic aggregations of `data/daily.csv`.
