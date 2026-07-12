# Verify

Run:

```bash
python3 scripts/verify.py --public-repo .
```

The verifier checks CSV schemas, canonical `ercot_he24_interval_v2` labeling, daily proof binding to valuation revision, date coverage, daily drawdown, weekly/monthly/summary aggregation, complete append-only valuation provenance, provisional coverage disclosures, the archived legacy-file hash, public file hashes, the opaque validation anchor, and public-boundary leak guards.
