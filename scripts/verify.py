#!/usr/bin/env python3
import argparse, csv, hashlib, json, sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DAILY = ['date','signal_date','status','realized_pnl','cumulative_pnl','drawdown','days_since_equity_high','proof_id']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def proof(row):
    payload = {'kind':'daily-v5','values':{key:row[key] for key in DAILY if key!='proof_id'}}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def freshness_errors(rows, timezone, not_before):
    """Opt-in currency check.  Off by default so historical clones stay verifiable."""
    now = datetime.now(ZoneInfo(timezone))
    hour, minute = (int(part) for part in not_before.split(':'))
    expected_as_of = now.date() if now.time() >= time(hour, minute) else now.date()-timedelta(days=1)
    expected_settled = expected_as_of - timedelta(days=1)
    errors=[]
    latest = max(row['date'] for row in rows)
    if latest < expected_as_of.isoformat():
        errors.append('record ends %s, expected through %s' % (latest, expected_as_of))
    settled = [row['date'] for row in rows if row['status']=='settled']
    last_settled = max(settled) if settled else None
    if not last_settled or last_settled < expected_settled.isoformat():
        errors.append('settled through %s, expected through %s' % (last_settled, expected_settled))
    return errors

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--require-current',action='store_true')
    parser.add_argument('--timezone',default='America/Chicago')
    parser.add_argument('--not-before',default='08:30')
    args=parser.parse_args(argv)
    errors=[]
    expected={}
    for line in (ROOT/'proof/records.sha256').read_text().splitlines():
        digest, name=line.split('  ',1); expected[name]=digest
    for name,digest in expected.items():
        path=ROOT/name
        if not path.is_file() or sha(path)!=digest: errors.append('hash mismatch: '+name)
    with (ROOT/'data/daily.csv').open(newline='',encoding='utf-8') as fh:
        reader=csv.DictReader(fh); rows=list(reader)
        if reader.fieldnames!=DAILY: errors.append('daily.csv schema mismatch')
    if not rows: errors.append('daily.csv is empty')
    else:
        start=date.fromisoformat(rows[0]['date']); end=date.fromisoformat(rows[-1]['date'])
        expected_dates=[]; current=start
        while current<=end: expected_dates.append(current.isoformat()); current+=timedelta(days=1)
        if [row['date'] for row in rows]!=expected_dates: errors.append('daily.csv is not calendar-contiguous')
        for row in rows:
            if row['status'] not in ('settled','pending','provisional','unavailable'): errors.append('bad status: '+row['date'])
            if row['proof_id']!=proof(row): errors.append('daily proof mismatch: '+row['date'])
    anchor=json.loads((ROOT/'proof/private_anchor.json').read_text())
    for key,name in (('daily_csv_sha256','data/daily.csv'),('weekly_csv_sha256','data/weekly.csv'),('monthly_csv_sha256','data/monthly.csv'),('summary_csv_sha256','data/summary.csv')):
        if anchor.get(key)!=sha(ROOT/name): errors.append('anchor mismatch: '+name)
    if args.require_current and rows:
        errors.extend(freshness_errors(rows,args.timezone,args.not_before))
    print(json.dumps({'ok':not errors,'errors':errors},indent=2))
    return 1 if errors else 0

if __name__ == '__main__': raise SystemExit(main())
