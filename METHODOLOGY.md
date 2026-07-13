# Methodology

The canonical record follows `live_lineage_canonical_v3`: it preserves the historical decision-state path that leads into the pinned live fold-9 continuation and applies corrected ERCOT quarter handling where immutable books exist. `data/daily.csv` is intentionally a minimal outcome ledger with no basis, valuation-version, revision, coverage, exposure, or estimation columns. Those dimensions remain in the hash-bound `data/valuation_provenance.csv`.

March 1–July 6 carries the originally published pre-v2 walk-forward values as `settled`. Those values use the disclosed `legacy_he24_v1` convention, under which archive-path midnight-ending intervals could be labeled HE0 and excluded from the HE1–24 merge. Exact corrected-q4 restatement is not claimed because the original per-day books were not retained and official source gaps reach 1/4–2/4 coverage. Revision 3 restores these values to canonical status; revisions 1 and 2 remain immutable in provenance.

`data/retrospective_q4_replay.csv` separately publishes the 128-day corrected-q4 counterfactual for March 1–July 6. It totals $114,559.82 and is excluded from `daily.csv`, headline metrics, and weekly/monthly/summary rollups because resetting replay progress changed the decision path and therefore did not generate the live state. Its missing intervals, exposure, estimates, and artifact lineage remain recorded in provenance revision 2.

July 7–8 retain their immutable declared books under `ercot_he24_q4_v2`: July 7 uses the corrected four-quarter HE24 valuation and July 8 records a zero-impact convention revision. From July 9 onward, live settlement maps midnight-ending RT intervals to HE24, retains quarter identity, and evaluates completeness against held source/sink/hour exposure.

Exactly one missing held quarter may publish as `provisional` using the mean of the three observed quarters. Anything weaker fails. Once official data arrives, immutable positions are revalued and an append-only `observed_complete` revision supersedes the provisional revision. A complete later date may settle even when its decision state records dependency on an earlier provisional valuation; that dependency remains explicit in provenance.

All PnL is hypothetical must-clear model-replay PnL against public DA/RT prices. It is not actual auction-award, bid-execution, settlement-statement, invoice, or cash-account PnL. A public pending row does not by itself prove that a signal or advisory existed before the applicable auction deadline.

`source_artifact_sha256` in `proof/private_anchor.json` is a validation/source anchor, not a per-row signal commitment. `data/weekly.csv`, `data/monthly.csv`, and `data/summary.csv` are recomputable from canonical `data/daily.csv`; provisional values affect the displayed daily path but are excluded from settled rollup PnL.
