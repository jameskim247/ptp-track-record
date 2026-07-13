# Verify

Run:

```bash
python3 scripts/verify.py --public-repo .
```

The verifier checks the minimal daily and rollup schemas, visible-field daily proofs, contiguous dates, cumulative PnL and drawdown, weekly/monthly/summary aggregation, canonical q4 latest provenance for every valued row, append-only revision ancestry, observed/provisional/historical-estimate coverage contracts, the pre-migration archive hash, public file hashes, the opaque validation anchor, and public-boundary leak guards.
