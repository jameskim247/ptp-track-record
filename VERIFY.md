# Verify

Run:

```bash
python3 scripts/verify.py
```

The verifier checks the public allowlist hashes, the opaque private anchor,
selection disclosure, declared publication mode, calendar continuity, statuses,
matched-control arithmetic, and visible-field daily proof identifiers. Every PnL field is modeled shadow PnL.
Weekly, monthly, and summary derivation is also checked before every publication
by the private canonical publisher.
