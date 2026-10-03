#!/usr/bin/env python3
"""Verify the series-2 package: file hashes, anchor, daily calendar, and that every derived number (cumulative P&L,
drawdown, weekly, monthly and summary tables, row proof ids) recomputes from the daily ledger.
It proves the files are consistent and unaltered. It cannot prove when the rule was frozen relative to the data:
every row is a retrospective reconstruction (see README.md)."""
import csv, hashlib, json, math, statistics as st
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SID = 'series-2'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def rid(row):
    """proof_id = sha256 of the row's other fields, JSON with sorted keys and typed values as published"""
    body = {k: v for k, v in row.items() if k != 'proof_id'}
    return hashlib.sha256(json.dumps(body, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def typed(row, ints=(), strs=()):
    out = {}
    for k, v in row.items():
        if k in strs or v == '' or k.endswith('_id') or k in ('date', 'signal_date', 'status', 'evidence_basis', 'basis',
                                                           'start_date', 'end_date', 'period_start', 'period_end', 'latest_settled_date'):
            out[k] = v
        elif k in ints:
            out[k] = int(v)
        else:
            out[k] = float(v)
    return out


def close(a, b):
    """USD amounts: published values are rounded to 4 decimals, so sums may drift by a few cents over 1,095 rows"""
    return abs(a - b) <= 0.10


def close_ratio(a, b):
    return abs(a - b) <= 1e-5 * max(1.0, abs(b))


def main():
    errors = []
    manifest = ROOT / 'proof' / 'records.sha256'
    for line in manifest.read_text(encoding='utf-8').splitlines():
        expected, rel = line.split('  ', 1)
        p = ROOT / rel
        if not p.is_file() or digest(p) != expected:
            errors.append('hash mismatch: ' + rel)
    anchor = json.loads((ROOT / 'proof' / 'anchor.json').read_text())
    if digest(manifest) != anchor.get('records_sha256'):
        errors.append('records manifest hash mismatch')
    rows = list(csv.DictReader((ROOT / 'data' / SID / 'daily.csv').open(newline='', encoding='utf-8')))
    start, end = date.fromisoformat(anchor['record_start']), date.fromisoformat(anchor['record_end'])
    cal = [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]
    if [r['date'] for r in rows] != cal:
        errors.append('daily calendar mismatch')
    ints = ()
    cum = peak = 0.0
    for r in rows:
        t = typed(r)
        if r['evidence_basis'] != 'retrospective_reconstruction':
            errors.append('unexpected evidence basis ' + r['date'])
        if rid(t) != r['proof_id']:
            errors.append('row proof mismatch ' + r['date'])
        cum += t['pnl']; peak = max(peak, cum)
        if not close(cum, t['cumulative_pnl']) or not close(cum - peak, t['pnl_drawdown']):
            errors.append('cumulative/drawdown mismatch ' + r['date'])
        if not close(t['gross_pnl'] - 0.40 * t['placed_mw'], t['pnl']):
            errors.append('cost arithmetic mismatch ' + r['date'])
        if t['placed_mw'] > 800 + 1e-6:
            errors.append('daily budget exceeded ' + r['date'])
        if (r['status'] == 'settled') != (t['pending_awarded_mw'] == 0):
            errors.append('status/pending mismatch ' + r['date'])
    by = {r['date']: typed(r) for r in rows}
    for name in ('weekly', 'monthly'):
        for r in csv.DictReader((ROOT / 'data' / SID / f'{name}.csv').open(newline='', encoding='utf-8')):
            t = typed(r, ints=('calendar_days', 'settled_days', 'partially_settled_days'))
            if rid(t) != r['proof_id']:
                errors.append(f'{name} proof mismatch ' + r['period_start'])
            ds = [d for d in cal if r['period_start'] <= d <= r['period_end']]
            if len(ds) != t['calendar_days'] or not close(sum(by[d]['pnl'] for d in ds), t['pnl']) \
                    or not close(sum(by[d]['placed_mw'] for d in ds), t['placed_mw']):
                errors.append(f'{name} totals mismatch ' + r['period_start'])
    for r in csv.DictReader((ROOT / 'data' / SID / 'summary.csv').open(newline='', encoding='utf-8')):
        t = typed(r, ints=('calendar_days', 'settled_days', 'ex_top_five_days_count', 'partially_settled_days'))
        if rid(t) != r['proof_id']:
            errors.append('summary proof mismatch ' + r['basis'])
        p = [by[d]['pnl'] for d in cal if r['start_date'] <= d <= r['end_date']]
        sh = st.mean(p) / st.stdev(p) * math.sqrt(365)
        c = 0.0; pk = 0.0; mdd = 0.0
        for x in p:
            c += x; pk = max(pk, c); mdd = min(mdd, c - pk)
        if not (close(sum(p), t['total_pnl']) and close_ratio(sh, t['annualized_pnl_mean_to_stdev']) and close(mdd, t['max_pnl_drawdown'])
                and close(min(p), t['worst_day_pnl'])):
            errors.append('summary statistics mismatch ' + r['basis'])
    print(json.dumps({'ok': not errors, 'errors': errors, 'rows': len(rows), 'record_start': anchor['record_start'],
                      'record_end': anchor['record_end']}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
