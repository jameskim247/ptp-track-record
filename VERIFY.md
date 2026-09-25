# Verify

```bash
python3 scripts/verify.py
python3 scripts/verify.py --require-current --timezone America/Chicago --not-before 08:30
```

Checks file hashes, calendars and the programme anchor; the second form also requires data through yesterday. It proves the files are consistent and unaltered, not when decisions were made: pre-cutoff decision timestamps are kept privately.
