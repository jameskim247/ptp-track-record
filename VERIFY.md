# Verify

Run:

```bash
python3 scripts/verify.py
```

The repository enforces canonical LF bytes for hashed text files through
`.gitattributes`. Run verification from a fresh checkout; no manual Git line-ending
configuration is required on Windows or Linux.

The verifier checks every file listed in the proof manifest, binds that manifest to the
private anchor, requires all three neutral daily ledgers, and confirms that each ledger
starts on the anchor's frozen record start. It also rejects a package when the first two
lanes are economically indistinguishable across every common settled date. Historical
rows and prospective shadow rows remain distinguished by the `evidence_basis` column.

This verifier establishes package integrity, not execution, capacity, or realized
performance. Publication currency is reported by the dated rows and repository status;
it is not inferred by silently extending the record.
