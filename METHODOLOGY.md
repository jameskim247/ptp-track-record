# Methodology

The public files publish settled realized dollar PnL and deterministic aggregations only.

Settled historical rows through 2026-07-06 use `model_backfill`. Pending prospective rows use `prospective` until a settled realized result is available.

`data/weekly.csv`, `data/monthly.csv`, and `data/summary.csv` are recomputable from `data/daily.csv`. Public proof files expose opaque hashes only.

The public metric set is limited to settled dollar PnL and scale-free ratios that are recomputable from `data/daily.csv`.
