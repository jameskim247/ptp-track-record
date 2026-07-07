# Methodology

The public files publish daily, weekly, and monthly PnL records only. They intentionally exclude raw model inputs, positions, signals, checkpoints, and lake data.

`settled` rows come from a backfilled PTP Trader financial artifact identified by the SHA-256 hash in `proof/source_manifest.json`. `pending` rows reserve the delivery dates that are in range but not yet settlement/model complete.

When the model, backtest window, or live publication process changes, new public rows should keep the same simple schema and identify the new methodology in `proof/source_manifest.json`.
