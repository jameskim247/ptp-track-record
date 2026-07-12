# Methodology

The public files publish settled realized dollar PnL, explicitly labeled provisional valuations, and deterministic aggregations. This record is a pre-settlement declaration ledger: each delivery date receives a public row, and its valuation advances independently of final settlement.

Settled realized PnL always comes from the pinned walk-forward model replay valued against complete held source/sink/hour DA/RT prices, and settlement lags delivery by at least one day. The `basis` column records each row's lifecycle: `prospective_settled` rows were publicly declared as pending `prospective` rows first and later settled by the live pipeline; `prospective_provisional` rows use a deterministic mean of three observed RT quarters when exactly one held quarter is unavailable; `model_backfill` rows were constructed retroactively at the 2026-07-07 reset without a prior public declaration.

`provisional` is not settled. It advances the valuation frontier without advancing the settled headline statistics. `data/valuation_provenance.csv` is append-only and records coverage, missing interval, affected exposure, exact PnL sensitivity, source artifact hash, and revision lineage. Once the official fourth quarter arrives, the immutable declared positions are revalued and a new `observed_complete` revision supersedes the provisional one; historical positions are never regenerated.

Completeness is exposure-relative for daily valuation: missing cells outside every held source/sink/hour do not block settlement. A held cell with 4/4 observed quarters is exact, 3/4 is provisional, and anything weaker remains a hard error. Missing payoff cells are never coerced to zero.

`prospective` identifies a row publicly declared before its realized result was settled. It does not assert that a trading signal or advisory was generated, archived, or published before the applicable auction deadline.

`source_artifact_sha256` in `proof/private_anchor.json` is a carried-forward validation/source anchor. It is not a per-row signal commitment.

`data/weekly.csv`, `data/monthly.csv`, and `data/summary.csv` are recomputable from `data/daily.csv`. Public proof files expose opaque hashes only.

Headline metrics remain limited to settled dollar PnL and scale-free ratios recomputable from `data/daily.csv`; provisional values affect the displayed valuation path but are excluded from settled weekly/monthly/summary PnL.
