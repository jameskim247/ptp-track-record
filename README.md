# PTP Trader Track Record

A simple public track record for the PTP Trader.

Current public range: **2026-03-01 to 2026-07-12**. `data/daily.csv` is the minimal outcome ledger: delivery date, signal date, status, realized and cumulative PnL, drawdown, duration, and proof ID. Detailed valuation methodology, source coverage, revision evidence, and retrospective research are retained privately and can be supplied for diligence; they are not part of the public performance series.

## Files

- `data/daily.csv` - one row per delivery date.
- `data/weekly.csv` - calendar-week rollups, clipped to the published range.
- `data/monthly.csv` - monthly rollups, clipped to the published range.
- `data/summary.csv` - one full-record metric row.
- `proof/private_anchor.json` - opaque validation hashes.
- `proof/records.sha256` - hashes for public files.

Weekly, monthly, and summary files are deterministic aggregations of `data/daily.csv`.
