# PTP Trader Track Record

A simple public track record for the PTP Trader.

Current public range: **2026-03-01 to 2026-07-06**. Settled rows are published through **2026-07-06**; there are **0** pending rows.

## Files

- `data/daily.csv` - one row per delivery date.
- `data/weekly.csv` - calendar-week rollups, clipped to the published range.
- `data/monthly.csv` - monthly rollups, clipped to the published range.
- `proof/source_manifest.json` - public-safe source hash and coverage metadata.
- `proof/records.sha256` - hashes for the public data files.

Raw source files are not stored in this public repo.
