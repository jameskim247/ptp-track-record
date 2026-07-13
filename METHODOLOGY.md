# Methodology

All valued rows use `ercot_he24_q4_v2`: midnight-ending ERCOT RT intervals map to HE24, quarter identity is retained, and completeness is evaluated against held source/sink/hour exposure. The immutable pre-migration ledger remains in `data/archive/daily_pre_valuation_v2.csv`.

`data/daily.csv` is intentionally a minimal outcome ledger. It contains no basis, valuation-version, revision, coverage, exposure, or estimation columns. `settled` is the final public track-record outcome under this methodology; `provisional` remains open to automatic reconciliation; `pending` has no realized outcome.

The March 1–July 6 history was rerun through the corrected q4 model lineage. Four observed quarters produce `observed_complete` provenance. When the official ERCOT sources retain only one, two, or three held-cell quarters, the historical replay uses the arithmetic mean of the observed quarters. At 0/4, where that mean is undefined, it first uses the held node-hour DA price as a neutral RT proxy; if DA is also absent, it uses the nearest observed same-day payoff for the exact pair (lower hour wins ties), then the nearest prior delivery's same-pair/same-hour payoff. It never uses a future delivery or another estimate as an anchor. Both cases record `historical_estimate`, coverage, missing intervals, affected positions/MW, sensitivity, lineage, artifact hash, and revision ancestry in `data/valuation_provenance.csv`. These historical estimates are published as `settled` by policy; they are not represented as fully observed inputs.

Live settlement remains stricter. Exactly one missing held quarter may publish as `provisional` using the mean of the three observed quarters. Anything weaker fails. Once official data arrives, immutable positions are revalued and an append-only `observed_complete` revision supersedes the provisional revision.

July 7–8 retain their originally declared books: July 7 is revalued to the corrected four-quarter HE24 price, while July 8 records a zero-impact convention revision. Corrected valuation does not regenerate these historical books.

All PnL is hypothetical must-clear model-replay PnL against public DA/RT prices. It is not actual auction-award, bid-execution, settlement-statement, invoice, or cash-account PnL. A public pending row does not by itself prove that a signal or advisory existed before the applicable auction deadline.

`source_artifact_sha256` in `proof/private_anchor.json` is a validation/source anchor, not a per-row signal commitment. `data/weekly.csv`, `data/monthly.csv`, and `data/summary.csv` are recomputable from `data/daily.csv`; provisional values affect the displayed daily path but are excluded from settled rollup PnL.
