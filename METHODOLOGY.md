# Methodology

The public files publish settled realized dollar PnL and deterministic aggregations only.

The current record basis is `model_backfill`. Public rows must not imply live trading.

`data/weekly.csv`, `data/monthly.csv`, and `data/summary.csv` are recomputable from `data/daily.csv`. Public proof files expose opaque hashes only.

The public metric set is limited to settled dollar PnL and scale-free ratios that are recomputable from `data/daily.csv`.
