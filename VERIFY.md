# Verify

```bash
python3 scripts/verify.py
```

The script checks five things:
- every file listed in `proof/records.sha256` is unaltered, and the manifest matches `proof/anchor.json`;
- the daily ledger covers every calendar date from `record_start` to `record_end` once;
- each row's P&L equals gross minus $0.40 per placed MWh, and its cumulative P&L and drawdown follow from the rows before it;
- the weekly, monthly and summary tables recompute from the daily ledger;
- every row's `proof_id` matches its contents.

It proves the files are consistent and unaltered. It cannot prove when the rule was frozen relative to the data: every row is a retrospective reconstruction.

`proof/anchor.json` also commits to four private objects by SHA-256:
- the frozen specification;
- the order books and per-order settlement lines;
- the two price sets used;
- the program that built this record.

Those objects are available on request and can be checked against these digests.
