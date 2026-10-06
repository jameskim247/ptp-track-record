# Verify

```bash
python3 scripts/verify.py
python3 -m unittest discover -s tests -v
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

Daily publication is separate from result generation. `python3 scripts/publish_daily.py`
consumes the optional `SERIES2_SOURCE_URL` public result ZIP, verifies it in isolation, and seals a
coverage receipt even when the producer is unavailable. `--check-freshness` fails until the producer
has supplied verified results through yesterday in America/Chicago. The workflow commits the
honest coverage receipt before that check, so blocked generation is visible in both the repo and Actions.
The scheduler requests write access only to this repository through its per-run `GITHUB_TOKEN`;
the production VM's existing two-repository GitHub App scope is unchanged.
