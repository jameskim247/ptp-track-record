# Verify the two-series package

Run from a fresh checkout with Python 3.11 or later:

```bash
python3 scripts/verify.py
```

The verifier checks the two neutral ledgers, their calendars and proof identifiers, aggregate derivations, file hashes, and programme anchor. Unavailable observations and unsettled obligations are explicit.

To also require publication through yesterday after the Central-time SLA:

```bash
python3 scripts/verify.py --require-current --timezone America/Chicago --not-before 08:30
```

Freshness is time-dependent. These checks establish package integrity and publication currency, not executed fills or investment performance. Reconstructed and prospective paper observations remain hypothetical and are distinguished by evidence_basis. The numbered series belong to the programme in the current anchor; they do not continue the retired record.

Reconstructed rows have no pre-gate commitment. Prospective decisions require timely commitments; neutral commitment files may be public while the books remain private. This package establishes that the ledgers are internally consistent and unaltered since their snapshot, and does not by itself establish when each decision was fixed. The verifier still checks any commitment the package does carry, against the programme digest it was sealed with. Git history and privately retained publication acknowledgements are the evidence for timing, and this package alone does not authenticate them.
