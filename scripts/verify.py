#!/usr/bin/env python3
import csv, hashlib, json, sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY = ['date','signal_date','status','realized_pnl','cumulative_pnl','drawdown','days_since_equity_high','proof_id']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def proof(row):
    payload = {'kind':'daily-v3','values':{key:row[key] for key in ('date','signal_date','status','realized_pnl')}}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
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
            if row['status'] not in ('settled','pending','provisional'): errors.append('bad status: '+row['date'])
            if row['proof_id']!=proof(row): errors.append('daily proof mismatch: '+row['date'])
    anchor=json.loads((ROOT/'proof/private_anchor.json').read_text())
    for key,name in (('daily_csv_sha256','data/daily.csv'),('weekly_csv_sha256','data/weekly.csv'),('monthly_csv_sha256','data/monthly.csv'),('summary_csv_sha256','data/summary.csv')):
        if anchor.get(key)!=sha(ROOT/name): errors.append('anchor mismatch: '+name)
    print(json.dumps({'ok':not errors,'errors':errors},indent=2))
    return 1 if errors else 0

if __name__ == '__main__': raise SystemExit(main())
