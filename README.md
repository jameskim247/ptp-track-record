# PTP Paper Record

[Daily](data/ptp-paper/daily.csv) · [Weekly](data/ptp-paper/weekly.csv) · [Monthly](data/ptp-paper/monthly.csv) · [Summary](data/ptp-paper/summary.csv)

Daily paper results from 2024-01-01. Historical reconstruction, not executed trades. USD P&L includes $0.40/placed MWh; `_mw` volumes are MWh; `path_count` counts submitted source-sink-hour orders, not MW. Paper valuations can use incomplete prices; unvalued payouts are excluded. No market-impact or collateral model.

Check hashes/arithmetic: `python3 scripts/verify.py` (not private-order verification). [Status](STATUS.md) · [Valuation and quantity basis](data/ptp-paper/source_anchor.json). Prior Git history is preserved privately.
