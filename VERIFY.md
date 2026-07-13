# Verify

Run:

```bash
python3 scripts/verify.py --public-repo .
```

The verifier checks the minimal daily and rollup schemas, visible-field daily proofs, contiguous dates, cumulative PnL and drawdown, weekly/monthly/summary aggregation, public-file hashes, the opaque private-validation anchor, and public-boundary leak guards. Detailed valuation, coverage, revision, and retrospective evidence is retained in the private manifest-bound validation package rather than published in this repository.
