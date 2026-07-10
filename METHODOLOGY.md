# Methodology

The public files publish settled realized dollar PnL and deterministic aggregations only. This record is a pre-settlement declaration ledger: each delivery date receives a public row, and the row's realized PnL is filled in once settled.

Settled historical rows through 2026-07-06 use `model_backfill`. Pending rows use `prospective` until a settled realized result is available.

`prospective` identifies a row publicly declared before its realized result was settled. It does not assert that a trading signal or advisory was generated, archived, or published before the applicable auction deadline.

`source_artifact_sha256` in `proof/private_anchor.json` is a carried-forward validation/source anchor. It is not a per-row signal commitment.

`data/weekly.csv`, `data/monthly.csv`, and `data/summary.csv` are recomputable from `data/daily.csv`. Public proof files expose opaque hashes only.

The public metric set is limited to settled dollar PnL and scale-free ratios that are recomputable from `data/daily.csv`.
