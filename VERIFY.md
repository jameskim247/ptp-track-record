# Verify

Run:

```bash
python3 scripts/verify.py --public-repo .
```

The verifier checks CSV schemas, `legacy_he24_v1`/`ercot_he24_q4_v2` basis-compatible labeling, daily proof binding to valuation revision, date coverage, daily drawdown, weekly/monthly/summary aggregation, complete append-only valuation provenance, provisional coverage disclosures, the pre-v2 archive hash, public file hashes, the opaque validation anchor, and public-boundary leak guards.
