#!/usr/bin/env python3
import argparse, csv, hashlib, json, sys
from decimal import Decimal
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DAILY = ['date','signal_date','status','modeled_pnl','cumulative_modeled_pnl','modeled_pnl_drawdown','days_since_equity_high','proof_id']
PERIODS = {
    'weekly': ('data/weekly.csv', ['period_start','period_end','status','settled_days','pending_days','total_days','modeled_pnl','cumulative_modeled_pnl','mean_day_modeled_pnl','median_day_modeled_pnl','win_days','loss_days','win_rate','avg_win_modeled_pnl','avg_loss_modeled_pnl','payoff_ratio','profit_factor','best_day_modeled_pnl','worst_day_modeled_pnl','period_max_modeled_pnl_drawdown','top_day_share','proof_id']),
    'monthly': ('data/monthly.csv', ['period_start','period_end','status','settled_days','pending_days','total_days','modeled_pnl','cumulative_modeled_pnl','mean_day_modeled_pnl','median_day_modeled_pnl','win_days','loss_days','win_rate','avg_win_modeled_pnl','avg_loss_modeled_pnl','payoff_ratio','profit_factor','best_day_modeled_pnl','worst_day_modeled_pnl','period_max_modeled_pnl_drawdown','top_day_share','proof_id']),
}
SUMMARY = ['basis','start_date','end_date','n_days','total_modeled_pnl','mean_day_modeled_pnl','median_day_modeled_pnl','daily_modeled_pnl_stdev','win_days','loss_days','win_rate','avg_win_modeled_pnl','avg_loss_modeled_pnl','payoff_ratio','profit_factor','best_day_modeled_pnl','worst_day_modeled_pnl','modeled_pnl_var_5','modeled_pnl_es_5','worst_to_mean_modeled_pnl_ratio','es5_to_mean_modeled_pnl_ratio','max_modeled_pnl_drawdown','max_drawdown_duration_days','top_1_day_share','top_5_day_share','top_10_day_share','largest_month','largest_month_modeled_pnl','largest_month_share','modeled_pnl_mean_to_stdev','modeled_pnl_mean_to_downside_deviation','proof_id']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def proof(row):
    payload = {'kind':'daily-v5','values':{key:row[key] for key in DAILY if key!='proof_id'}}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def row_proof(kind, row, columns):
    payload={'kind':kind,'values':{key:row[key] for key in columns if key!='proof_id'}}
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
        settled=[row for row in rows if row['status']=='settled']
        cumulative=Decimal('0'); peak=Decimal('0')
        for row in rows:
            cumulative += Decimal(row['modeled_pnl'] or '0')
            peak=max(peak,cumulative)
            if row['cumulative_modeled_pnl'] != f'{cumulative:.2f}': errors.append('daily cumulative mismatch: '+row['date'])
            if row['modeled_pnl_drawdown'] != f'{cumulative-peak:.2f}': errors.append('daily drawdown mismatch: '+row['date'])
        for kind,(name,columns) in PERIODS.items():
            with (ROOT/name).open(newline='',encoding='utf-8') as fh:
                reader=csv.DictReader(fh); aggregate_rows=list(reader)
                if reader.fieldnames!=columns: errors.append(name+' schema mismatch')
            previous_end=None
            for aggregate in aggregate_rows:
                chunk=[row for row in rows if aggregate['period_start']<=row['date']<=aggregate['period_end']]
                measured=[Decimal(row['modeled_pnl']) for row in chunk if row['status']=='settled']
                expected_total=f'{sum(measured):.2f}'
                if aggregate['modeled_pnl']!=expected_total: errors.append(kind+' modeled P&L mismatch: '+aggregate['period_start'])
                if aggregate['settled_days']!=str(len(measured)) or aggregate['total_days']!=str(len(chunk)): errors.append(kind+' day-count mismatch: '+aggregate['period_start'])
                if aggregate['proof_id']!=row_proof(kind,aggregate,columns): errors.append(kind+' proof mismatch: '+aggregate['period_start'])
                if previous_end and date.fromisoformat(aggregate['period_start'])!=date.fromisoformat(previous_end)+timedelta(days=1): errors.append(kind+' periods are not contiguous')
                previous_end=aggregate['period_end']
        with (ROOT/'data/summary.csv').open(newline='',encoding='utf-8') as fh:
            reader=csv.DictReader(fh); summaries=list(reader)
            if reader.fieldnames!=SUMMARY: errors.append('data/summary.csv schema mismatch')
        if len(summaries)!=1: errors.append('summary row count mismatch')
        else:
            summary=summaries[0]
            if summary['total_modeled_pnl']!=f'{sum((Decimal(row["modeled_pnl"]) for row in settled), Decimal(0)):.2f}': errors.append('summary total modeled P&L mismatch')
            if summary['n_days']!=str(len(settled)): errors.append('summary day-count mismatch')
            if summary['proof_id']!=row_proof('summary',summary,SUMMARY): errors.append('summary proof mismatch')
    anchor=json.loads((ROOT/'proof/private_anchor.json').read_text())
    for key,name in (('daily_csv_sha256','data/daily.csv'),('weekly_csv_sha256','data/weekly.csv'),('monthly_csv_sha256','data/monthly.csv'),('summary_csv_sha256','data/summary.csv')):
        if anchor.get(key)!=sha(ROOT/name): errors.append('anchor mismatch: '+name)
    if args.require_current and rows:
        errors.extend(freshness_errors(rows,args.timezone,args.not_before))
    print(json.dumps({'ok':not errors,'errors':errors},indent=2))
    return 1 if errors else 0

if __name__ == '__main__': raise SystemExit(main())
