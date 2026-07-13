# PTP Trader Track Record

A simple public track record for the PTP Trader.

Current public range: **2026-03-01 to 2026-07-12**. `data/daily.csv` is the minimal outcome ledger: delivery date, signal date, status, realized and cumulative PnL, drawdown, duration, and proof ID. Valuation method, source coverage, estimation, and revision history remain in the separately hash-bound `data/valuation_provenance.csv`. The pre-migration snapshot remains in `data/archive/daily_pre_valuation_v2.csv`; the corrected-q4 counterfactual remains separate in `data/retrospective_q4_replay.csv` (see METHODOLOGY.md).

## Files

- `data/daily.csv` - one row per delivery date.
- `data/archive/daily_pre_valuation_v2.csv` - immutable pre-v2 public record snapshot.
- `data/retrospective_q4_replay.csv` - research-only corrected-q4 counterfactual; excluded from headline metrics.
- `data/valuation_provenance.csv` - append-only valuation quality and revision history.
- `data/weekly.csv` - calendar-week rollups, clipped to the published range.
- `data/monthly.csv` - monthly rollups, clipped to the published range.
- `data/summary.csv` - one full-record metric row.
- `proof/private_anchor.json` - opaque validation hashes.
- `proof/records.sha256` - hashes for public files.

Weekly, monthly, and summary files are deterministic aggregations of `data/daily.csv`.
