# Verify

Run:

```bash
python3 scripts/verify.py --public-repo .
```

The verifier checks the minimal daily and rollup schemas, visible-field daily proofs, contiguous dates, cumulative PnL and drawdown, weekly/monthly/summary aggregation, the live-lineage canonical provenance split, append-only revision ancestry, observed/provisional/historical-estimate coverage contracts, the exact 128-day/$114,559.82 retrospective q4 series against retained revision 2, archive and public-file hashes, the opaque validation anchor, and public-boundary leak guards.
