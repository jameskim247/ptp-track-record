# Methodology

The public file makes its valuation seam explicit. Prospective rows from 2026-07-07 onward use `ercot_he24_q4_v2`: midnight-ending ERCOT RT intervals map to HE24, quarter identity is retained, and completeness is evaluated against held source/sink/hour exposure. Model-backfill rows through 2026-07-06 retain `legacy_he24_v1` because official ERCOT source gaps as weak as 1/4 held quarters make exact restatement impossible. The immutable pre-migration snapshot remains in `data/archive/daily_pre_valuation_v2.csv`.

`basis` records how a row entered the record. `prospective_settled` rows were publicly declared as pending `prospective` rows and later valued by the live pipeline. `model_backfill` rows are the retained retroactive two-lake reset history; they are not represented as corrected-HE24 values.

`provisional` is not settled. Exactly one missing held quarter uses the deterministic mean of the three observed quarters and records the missing interval, affected exposure, and PnL sensitivity. Anything weaker fails. Once official data arrives, immutable prospective positions are revalued and an append-only `observed_complete` revision supersedes the provisional revision.

`data/valuation_provenance.csv` records old/new PnL, valuation version, revision reason, decision lineage, state dependency, source artifact hash, and revision ancestry. July 7-8 retain their originally declared books: July 7 is revalued to the corrected four-quarter HE24 price, while July 8 records a zero-impact convention revision. Decision lineage is disclosed separately because corrected valuation does not regenerate historical books.

`prospective` identifies a row publicly declared before its realized result was settled. It does not assert that a trading signal or advisory was generated, archived, or published before the applicable auction deadline.

All PnL is hypothetical must-clear model-replay PnL against public DA/RT prices. It is not actual auction-award, bid-execution, settlement-statement, invoice, or cash-account PnL.

`source_artifact_sha256` in `proof/private_anchor.json` is a carried-forward validation/source anchor. It is not a per-row signal commitment.

`data/weekly.csv`, `data/monthly.csv`, and `data/summary.csv` are recomputable from `data/daily.csv`. Public proof files expose opaque hashes only.

Headline metrics remain limited to settled dollar PnL and scale-free ratios recomputable from `data/daily.csv`; they span the explicitly labeled legacy/backfill and corrected/prospective segments and must not be read as a single-convention series. Provisional values affect the displayed valuation path but are excluded from settled weekly/monthly/summary PnL.
