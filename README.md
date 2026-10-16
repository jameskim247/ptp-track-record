# PTP Paper Record

[Daily](data/ptp-paper/daily.csv) · [Weekly](data/ptp-paper/weekly.csv) · [Monthly](data/ptp-paper/monthly.csv) · [Summary](data/ptp-paper/summary.csv)

Daily paper results from 2024-01-01. Historical reconstruction, not executed trades. USD P&L includes $0.40/placed MWh; `_mw` volumes are MWh; `pairs` counts distinct submitted source-sink pairs (bid IDs) and `pair_hours` submitted source-sink-hour orders, not MW. Paper valuations can use incomplete prices; unvalued payouts are excluded. No market-impact or collateral model.

## Biddable-node pair-capped variants

[pairs-500](data/pairs-500/daily.csv) · [pairs-100](data/pairs-100/daily.csv) · [pairs-50](data/pairs-50/daily.csv)

The same frozen sleeves and sizing, rebuilt so every order uses settlement points that other participants were bidding in ERCOT's public 60-day DAM disclosures published before the bid deadline, with no combined-cycle logical nodes; `pairs-N` submits at most N distinct source-sink pairs (bid IDs) a day. Same $0.40/placed MWh cost and x3 quantity basis. Rule written on 2026-10-16 after earlier results were known: development evidence, not validation. [Rule and sources](data/pairs-500/source_anchor.json).

Check hashes/arithmetic: `python3 scripts/verify.py` (not private-order verification). [Status](STATUS.md) · [Valuation and quantity basis](data/ptp-paper/source_anchor.json). Prior Git history is preserved privately.
