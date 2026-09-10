# Verify the four-series package

Run from a fresh checkout with Python 3.11 or later:

```bash
python3 scripts/verify.py
```

The verifier checks the four neutral ledgers, their calendars and proof identifiers, aggregate derivations, file hashes, and programme anchor. Unavailable observations and unsettled obligations are explicit.

To also require publication through yesterday after the Central-time SLA:

```bash
python3 scripts/verify.py --require-current --timezone America/Chicago --not-before 08:30
```

Freshness is time-dependent. These checks establish package integrity and publication currency, not executed fills or investment performance. Reconstructed and prospective paper observations remain hypothetical and are distinguished by evidence_basis. The numbered series belong to the programme in the current anchor; they do not continue the retired record.
