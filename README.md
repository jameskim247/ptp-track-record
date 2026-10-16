# PTP Paper Record

[Daily](data/ptp-paper/daily.csv) · [Weekly](data/ptp-paper/weekly.csv) · [Monthly](data/ptp-paper/monthly.csv) · [Summary](data/ptp-paper/summary.csv)

Daily paper results from 2024-01-01. Historical reconstruction, not executed trades. `pnl` is the ERCOT day-ahead and real-time settlement of awarded orders with no fees or cost assumptions (ERCOT charges no PTP Obligation bid fee), so it equals `gross_pnl`; until 2026-10-16 this record deducted an assumed $0.40 per placed MWh. `_mw` volumes are MWh; `pairs` counts distinct submitted source-sink pairs (bid IDs) and `pair_hours` submitted source-sink-hour orders, not MW. Paper valuations can use incomplete prices; unvalued payouts are excluded. This record does not apply ERCOT's de-energized award restriction (the v2 variants below do). No market-impact, credit or collateral model.

## Biddable-node pair-capped variants (v2)

[pairs-500](data/pairs-500/daily.csv) · [pairs-100](data/pairs-100/daily.csv) · [pairs-50](data/pairs-50/daily.csv)

The same frozen sleeves and sizing rule, rebuilt so every order uses settlement points that other participants were bidding in ERCOT's public 60-day DAM disclosures published before the bid deadline, excluding combined-cycle logical nodes and points ERCOT listed as de-energized in the latest DAM before the deadline. As in ERCOT's market, an order whose point is de-energized in that DAM hour is not awarded. `pairs-N` submits at most N distinct source-sink pairs (bid IDs) a day. pairs-100 is the primary series; pairs-500 and pairs-50 are shown for comparison. Same x3 quantity basis and no costs. v2 replaces the v1 variants first published on 2026-10-16. Rules written after earlier results were known: development evidence, not validation. [Rule and sources](data/pairs-100/source_anchor.json).

Check hashes/arithmetic: `python3 scripts/verify.py` (not private-order verification). [Status](STATUS.md) · [Valuation and quantity basis](data/ptp-paper/source_anchor.json). Prior Git history is preserved privately.
