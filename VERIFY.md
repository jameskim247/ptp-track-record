# Verify

Run:

```bash
python3 scripts/verify.py
```

The repository enforces canonical LF bytes for hashed text files through
`.gitattributes`. Run verification from a fresh checkout; no manual Git line-ending
configuration is required on Windows or Linux.

The verifier checks file hashes, the private anchor, calendar continuity, statuses,
daily proof identifiers, and aggregate derivations. The optional currency check is:

```bash
python3 scripts/verify.py --require-current --timezone America/Chicago --not-before 08:30
```

The currency check is intentionally time-dependent. It verifies publication freshness,
not historical integrity.
