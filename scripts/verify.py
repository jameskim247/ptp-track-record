#!/usr/bin/env python3
import csv, hashlib, json, sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY = ['date','signal_date','status','s4r_book_modeled_net_pnl','matched_native_control_modeled_net_pnl','s4r_incremental_modeled_net_pnl','cumulative_s4r_book_modeled_net_pnl','cumulative_matched_native_control_modeled_net_pnl','cumulative_s4r_incremental_modeled_net_pnl','s4r_book_modeled_drawdown','days_since_equity_high','proof_id']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def proof(row):
    payload = {'kind':'daily-v5-attribution','values':{key:row[key] for key in ('date','signal_date','status','s4r_book_modeled_net_pnl','matched_native_control_modeled_net_pnl','s4r_incremental_modeled_net_pnl')}}
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
            if row['status'] not in ('settled','pending','provisional','unavailable'): errors.append('bad status: '+row['date'])
            if row['proof_id']!=proof(row): errors.append('daily proof mismatch: '+row['date'])
            if row['status']=='settled' and round(float(row['s4r_book_modeled_net_pnl'])-float(row['matched_native_control_modeled_net_pnl']),2)!=round(float(row['s4r_incremental_modeled_net_pnl']),2): errors.append('daily attribution mismatch: '+row['date'])
    anchor=json.loads((ROOT/'proof/private_anchor.json').read_text())
    if anchor.get('publication_mode') not in ('frozen_development_study','prospective_shadow_cohort','retrospective_development_study'): errors.append('unsupported publication mode')
    if anchor.get('selection',{}).get('candidate_arm_count')!=15: errors.append('selection disclosure missing')
    for key,name in (('daily_csv_sha256','data/daily.csv'),('weekly_csv_sha256','data/weekly.csv'),('monthly_csv_sha256','data/monthly.csv'),('summary_csv_sha256','data/summary.csv')):
        if anchor.get(key)!=sha(ROOT/name): errors.append('anchor mismatch: '+name)
    print(json.dumps({'ok':not errors,'errors':errors},indent=2))
    return 1 if errors else 0

if __name__ == '__main__': raise SystemExit(main())
