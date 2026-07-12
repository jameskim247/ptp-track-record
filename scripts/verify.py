#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DAILY_COLUMNS = ['date','signal_date','status','basis','realized_pnl','cumulative_pnl','drawdown','days_since_equity_high','proof_id']
VALUATION_COLUMNS = ['date','revision','valuation_status','rt_coverage_min','missing_intervals','affected_positions','affected_mw','estimate_method','pnl_sensitivity_per_rt_spread_dollar','depends_on_provisional_date','source_artifact_sha256','supersedes_revision']
PERIOD_COLUMNS = ['period_start','period_end','status','basis_mix','settled_days','pending_days','total_days','realized_pnl','cumulative_pnl','mean_day_pnl','median_day_pnl','win_days','loss_days','win_rate','avg_win','avg_loss','payoff_ratio','profit_factor','best_day_pnl','worst_day_pnl','period_max_drawdown','top_day_share','proof_id']
SUMMARY_COLUMNS = ['basis','start_date','end_date','n_days','total_pnl','mean_day_pnl','median_day_pnl','daily_stdev','win_days','loss_days','win_rate','avg_win','avg_loss','payoff_ratio','profit_factor','best_day_pnl','worst_day_pnl','var_5','es_5','tail_ratio_worst_to_mean','tail_ratio_es5_to_mean','max_drawdown','max_drawdown_duration_days','top_1_day_share','top_5_day_share','top_10_day_share','largest_month','largest_month_pnl','largest_month_share','sharpe_daily','sortino_daily','proof_id']
BACKFILL_BASIS = 'model_backfill'
PROSPECTIVE_BASIS = 'prospective'
PROSPECTIVE_SETTLED_BASIS = 'prospective_settled'
PROSPECTIVE_PROVISIONAL_BASIS = 'prospective_provisional'
ANCHOR_KEYS_V1 = ['daily_csv_sha256','monthly_csv_sha256','pending_days','private_manifest_sha256','record_end','record_start','schema','settled_days','source_artifact_sha256','summary_csv_sha256','weekly_csv_sha256']
ANCHOR_KEYS_V2 = sorted(ANCHOR_KEYS_V1 + ['provisional_days','valuation_provenance_csv_sha256'])
FORBIDDEN_TRACKED_PREFIXES = ('private/', '_private/', 'vault/', 'raw/', 'tmp/')
FORBIDDEN_SUFFIXES = ('.parquet', '.pkl', '.pickle', '.key', '.pem', '.env', '.sqlite', '.db')
FORBIDDEN_TEXT = tuple(
    ''.join(parts)
    for parts in (
        ('/', 'mnt', '/c/'),
        ('/', 'home', '/'),
        ('OPENAI', '_API', '_KEY'),
        ('GITHUB', '_TOKEN'),
        ('password', '='),
        ('secret', '='),
        ('scored', '_signals'),
        ('positions', '_'),
        ('model', '_stack'),
        ('training', '_dataset'),
    )
)


def read_csv(path: Path, columns: list[str]) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != columns:
            raise ValueError(f'{path}: expected columns {columns}, got {reader.fieldnames}')
        return list(reader)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def parse_money(value: str) -> float:
    try:
        out = float(value)
    except ValueError as exc:
        raise ValueError(f'invalid numeric value {value!r}') from exc
    if not math.isfinite(out):
        raise ValueError(f'non-finite numeric value {value!r}')
    return out


def money(value: float) -> str:
    return f'{float(value):.2f}'


def ratio(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return ''
    return f'{float(value):.4f}'


def row_hash(prefix: str, payload: dict[str, Any]) -> str:
    return sha256_json({'kind': prefix, 'values': payload})


def date_range(start: date, end: date) -> list[str]:
    out = []
    cur = start
    while cur <= end:
        out.append(cur.isoformat())
        cur += timedelta(days=1)
    return out


def metrics(values: list[float]) -> dict[str, Any]:
    wins = [x for x in values if x > 0]
    losses = [x for x in values if x < 0]
    gross_win = sum(wins)
    gross_loss = sum(losses)
    avg_win = statistics.mean(wins) if wins else None
    avg_loss = statistics.mean(losses) if losses else None
    mean = statistics.mean(values) if values else 0.0
    median = statistics.median(values) if values else 0.0
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    payoff = (avg_win / abs(avg_loss)) if avg_win is not None and avg_loss not in (None, 0) else None
    pf = (gross_win / abs(gross_loss)) if gross_loss < 0 else None
    return {
        'mean': mean,
        'median': median,
        'stdev': stdev,
        'win_days': len(wins),
        'loss_days': len(losses),
        'win_rate': len(wins) / len(values) if values else 0.0,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'payoff_ratio': payoff,
        'profit_factor': pf,
        'best_day_pnl': max(values) if values else 0.0,
        'worst_day_pnl': min(values) if values else 0.0,
    }


def drawdown(values: list[float]) -> tuple[list[float], list[int], float, int]:
    cumulative = 0.0
    high = 0.0
    days_since_high = 0
    dds = []
    durations = []
    max_dd = 0.0
    max_duration = 0
    for pnl in values:
        cumulative += pnl
        if cumulative >= high:
            high = cumulative
            days_since_high = 0
        else:
            days_since_high += 1
        dd = cumulative - high
        dds.append(dd)
        durations.append(days_since_high)
        max_dd = min(max_dd, dd)
        max_duration = max(max_duration, days_since_high)
    return dds, durations, max_dd, max_duration


def expected_periods(rows: list[dict[str, str]], kind: str) -> list[dict[str, str]]:
    out = []
    idx = 0
    end = date.fromisoformat(rows[-1]['date'])
    while idx < len(rows):
        cur = date.fromisoformat(rows[idx]['date'])
        if kind == 'weekly':
            period_start = cur
            period_end = min(end, cur + timedelta(days=(6 - cur.weekday())))
        else:
            first_next = date(cur.year + (1 if cur.month == 12 else 0), 1 if cur.month == 12 else cur.month + 1, 1)
            period_start = cur
            period_end = min(end, first_next - timedelta(days=1))
        chunk = []
        while idx < len(rows) and date.fromisoformat(rows[idx]['date']) <= period_end:
            chunk.append(rows[idx])
            idx += 1
        pnl = [parse_money(r['realized_pnl']) for r in chunk if r['status'] == 'settled']
        m = metrics(pnl)
        total = sum(pnl)
        bases = Counter(r['basis'] for r in chunk)
        basis_mix = '|'.join(f'{k}:{bases[k]}' for k in sorted(bases))
        proof_payload = {
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'total_days': len(chunk),
            'settled_days': len(pnl),
            'realized_pnl': money(total),
            'basis_mix': basis_mix,
        }
        out.append({
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'status': 'pending' if any(r['status'] != 'settled' for r in chunk) else 'settled',
            'basis_mix': basis_mix,
            'settled_days': str(len(pnl)),
            'pending_days': str(sum(1 for r in chunk if r['status'] != 'settled')),
            'total_days': str(len(chunk)),
            'realized_pnl': money(total),
            'cumulative_pnl': chunk[-1]['cumulative_pnl'],
            'mean_day_pnl': money(m['mean']),
            'median_day_pnl': money(m['median']),
            'win_days': str(m['win_days']),
            'loss_days': str(m['loss_days']),
            'win_rate': ratio(m['win_rate']),
            'avg_win': money(m['avg_win']) if m['avg_win'] is not None else '',
            'avg_loss': money(m['avg_loss']) if m['avg_loss'] is not None else '',
            'payoff_ratio': ratio(m['payoff_ratio']),
            'profit_factor': ratio(m['profit_factor']),
            'best_day_pnl': money(m['best_day_pnl']),
            'worst_day_pnl': money(m['worst_day_pnl']),
            'period_max_drawdown': money(drawdown(pnl)[2]),
            'top_day_share': ratio(m['best_day_pnl'] / total if total > 0 else None),
            'proof_id': row_hash(kind, proof_payload),
        })
    return out


def expected_summary(rows: list[dict[str, str]]) -> dict[str, str]:
    values = [parse_money(r['realized_pnl']) for r in rows if r['status'] == 'settled']
    basis_counts = Counter(r['basis'] for r in rows if r['status'] == 'settled')
    summary_basis = '|'.join(k for k in sorted(basis_counts)) if len(basis_counts) > 1 else next(iter(basis_counts), BACKFILL_BASIS)
    m = metrics(values)
    total = sum(values)
    _dds, _durations, max_dd, max_duration = drawdown(values)
    sorted_values = sorted(values)
    var_count = max(1, math.ceil(0.05 * len(sorted_values)))
    var5 = sorted_values[var_count - 1]
    es5 = statistics.mean(sorted_values[:var_count])
    month_totals: dict[str, float] = defaultdict(float)
    for row in rows:
        if row['status'] == 'settled':
            month_totals[row['date'][:7]] += parse_money(row['realized_pnl'])
    largest_month, largest_month_pnl = max(month_totals.items(), key=lambda kv: kv[1])
    downside = math.sqrt(sum(min(0.0, x) ** 2 for x in values) / len(values)) if values else 0.0
    payload = {'basis': summary_basis, 'start_date': rows[0]['date'], 'end_date': rows[-1]['date'], 'n_days': len(values), 'total_pnl': money(total)}
    return {
        'basis': summary_basis,
        'start_date': rows[0]['date'],
        'end_date': rows[-1]['date'],
        'n_days': str(len(values)),
        'total_pnl': money(total),
        'mean_day_pnl': money(m['mean']),
        'median_day_pnl': money(m['median']),
        'daily_stdev': money(m['stdev']),
        'win_days': str(m['win_days']),
        'loss_days': str(m['loss_days']),
        'win_rate': ratio(m['win_rate']),
        'avg_win': money(m['avg_win']) if m['avg_win'] is not None else '',
        'avg_loss': money(m['avg_loss']) if m['avg_loss'] is not None else '',
        'payoff_ratio': ratio(m['payoff_ratio']),
        'profit_factor': ratio(m['profit_factor']),
        'best_day_pnl': money(m['best_day_pnl']),
        'worst_day_pnl': money(m['worst_day_pnl']),
        'var_5': money(var5),
        'es_5': money(es5),
        'tail_ratio_worst_to_mean': ratio(abs(m['worst_day_pnl']) / m['mean'] if m['mean'] else None),
        'tail_ratio_es5_to_mean': ratio(abs(es5) / m['mean'] if m['mean'] else None),
        'max_drawdown': money(max_dd),
        'max_drawdown_duration_days': str(max_duration),
        'top_1_day_share': ratio(sum(sorted(values, reverse=True)[:1]) / total),
        'top_5_day_share': ratio(sum(sorted(values, reverse=True)[:5]) / total),
        'top_10_day_share': ratio(sum(sorted(values, reverse=True)[:10]) / total),
        'largest_month': largest_month,
        'largest_month_pnl': money(largest_month_pnl),
        'largest_month_share': ratio(largest_month_pnl / total),
        'sharpe_daily': ratio(m['mean'] / m['stdev'] if m['stdev'] else None),
        'sortino_daily': ratio(m['mean'] / downside if downside else None),
        'proof_id': row_hash('summary', payload),
    }


def verify_hashes(root: Path) -> list[str]:
    errors = []
    rows = read_csv(root / 'proof/records.sha256', ['path','sha256'])
    seen = set()
    for row in rows:
        seen.add(row['path'])
        target = root / row['path']
        if not target.is_file():
            errors.append(f'missing hashed file: {row["path"]}')
            continue
        actual = sha256_file(target)
        if actual != row['sha256']:
            errors.append(f'hash mismatch for {row["path"]}: {actual} != {row["sha256"]}')
    required = {'data/daily.csv','data/weekly.csv','data/monthly.csv','data/summary.csv','proof/private_anchor.json','README.md','STATUS.md','METHODOLOGY.md','VERIFY.md','scripts/verify.py'}
    missing = sorted(required - seen)
    if missing:
        errors.append(f'records.sha256 missing required paths: {missing}')
    return errors


def tracked_files(root: Path) -> list[str]:
    if not (root / '.git').exists():
        return []
    result = subprocess.run(['git', '-C', str(root), 'ls-files'], text=True, capture_output=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


def verify_leaks(root: Path) -> list[str]:
    errors = []
    for rel in tracked_files(root):
        low = rel.lower()
        if low.startswith(FORBIDDEN_TRACKED_PREFIXES):
            errors.append(f'forbidden private/raw tracked path: {rel}')
        if low.endswith(FORBIDDEN_SUFFIXES):
            errors.append(f'forbidden tracked raw/source file type: {rel}')
        path = root / rel
        if rel == 'scripts/verify.py':
            continue
        if path.is_file() and path.stat().st_size <= 1_000_000:
            try:
                text = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            for needle in FORBIDDEN_TEXT:
                if needle in text:
                    errors.append(f'forbidden private/source text marker {needle!r} in {rel}')
    return errors


def verify_valuation_provenance(daily: list[dict[str, str]], rows: list[dict[str, str]]) -> list[str]:
    errors = []
    daily_by_date = {row['date']: row for row in daily}
    by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row['date'] not in daily_by_date:
            errors.append(f'valuation provenance date outside daily.csv: {row["date"]}')
            continue
        by_date[row['date']].append(row)
        if row['valuation_status'] not in ('provisional', 'observed_complete'):
            errors.append(f'invalid valuation status for {row["date"]}: {row["valuation_status"]}')
        sha = row['source_artifact_sha256']
        if len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
            errors.append(f'valuation source artifact is not sha256 for {row["date"]} revision {row["revision"]}')
        if row['valuation_status'] == 'provisional':
            if row['missing_intervals']:
                if row['rt_coverage_min'] != '3/4' or row['estimate_method'] != 'mean_observed_rt_intervals':
                    errors.append(f'provisional missing-input valuation contract mismatch for {row["date"]}')
            elif not (
                row['rt_coverage_min'] == '4/4'
                and row['estimate_method'] == 'none'
                and row['depends_on_provisional_date']
            ):
                errors.append(f'provisional dependency valuation contract mismatch for {row["date"]}')
    for delivery, revisions in by_date.items():
        revisions.sort(key=lambda row: int(row['revision']))
        expected = list(range(1, len(revisions) + 1))
        actual = [int(row['revision']) for row in revisions]
        if actual != expected:
            errors.append(f'non-contiguous valuation revisions for {delivery}: {actual}')
        for idx, row in enumerate(revisions):
            expected_parent = '' if idx == 0 else str(idx)
            if row['supersedes_revision'] != expected_parent:
                errors.append(f'bad supersedes_revision for {delivery} revision {row["revision"]}')
        latest = revisions[-1]['valuation_status']
        public_status = daily_by_date[delivery]['status']
        if public_status == 'provisional' and latest != 'provisional':
            errors.append(f'provisional daily row lacks latest provisional provenance: {delivery}')
        if public_status == 'settled' and latest != 'observed_complete':
            errors.append(f'settled revised row lacks latest observed provenance: {delivery}')
    return errors


def verify_anchor(root: Path, daily: list[dict[str, str]], weekly: list[dict[str, str]], monthly: list[dict[str, str]], summary: list[dict[str, str]]) -> list[str]:
    errors = []
    anchor_path = root / 'proof/private_anchor.json'
    try:
        anchor = json.loads(anchor_path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'could not read proof/private_anchor.json: {exc}']
    schema = anchor.get('schema')
    expected_keys = ANCHOR_KEYS_V2 if schema == 'ptp-public-private-anchor-v2' else ANCHOR_KEYS_V1
    if sorted(anchor.keys()) != expected_keys:
        errors.append(f'private anchor keys mismatch: {sorted(anchor.keys())}')
    if schema not in ('ptp-public-private-anchor-v1', 'ptp-public-private-anchor-v2'):
        errors.append('private anchor schema mismatch')
    if anchor.get('record_start') != daily[0]['date'] or anchor.get('record_end') != daily[-1]['date']:
        errors.append('private anchor record range mismatch')
    settled = sum(1 for r in daily if r['status'] == 'settled')
    pending = sum(1 for r in daily if r['status'] == 'pending')
    if anchor.get('settled_days') != settled or anchor.get('pending_days') != pending:
        errors.append('private anchor settled/pending counts mismatch')
    if schema == 'ptp-public-private-anchor-v2':
        provisional = sum(1 for r in daily if r['status'] == 'provisional')
        if anchor.get('provisional_days') != provisional:
            errors.append('private anchor provisional count mismatch')
    expected_hashes = {
        'daily_csv_sha256': sha256_file(root / 'data/daily.csv'),
        'weekly_csv_sha256': sha256_file(root / 'data/weekly.csv'),
        'monthly_csv_sha256': sha256_file(root / 'data/monthly.csv'),
        'summary_csv_sha256': sha256_file(root / 'data/summary.csv'),
    }
    if schema == 'ptp-public-private-anchor-v2':
        expected_hashes['valuation_provenance_csv_sha256'] = sha256_file(root / 'data/valuation_provenance.csv')
    for key, expected in expected_hashes.items():
        if anchor.get(key) != expected:
            errors.append(f'private anchor {key} mismatch')
    for key in ('private_manifest_sha256', 'source_artifact_sha256'):
        value = str(anchor.get(key) or '')
        if len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            errors.append(f'private anchor {key} is not a sha256 hex')
    return errors


def verify(root: Path) -> list[str]:
    errors = []
    daily = read_csv(root / 'data/daily.csv', DAILY_COLUMNS)
    valuation_path = root / 'data/valuation_provenance.csv'
    valuation = read_csv(valuation_path, VALUATION_COLUMNS) if valuation_path.is_file() else []
    weekly = read_csv(root / 'data/weekly.csv', PERIOD_COLUMNS)
    monthly = read_csv(root / 'data/monthly.csv', PERIOD_COLUMNS)
    summary = read_csv(root / 'data/summary.csv', SUMMARY_COLUMNS)
    if len(summary) != 1:
        errors.append('summary.csv must contain exactly one row')
    if not daily:
        return ['daily.csv is empty']
    if [r['date'] for r in daily] != date_range(date.fromisoformat(daily[0]['date']), date.fromisoformat(daily[-1]['date'])):
        errors.append('daily.csv does not contain a complete contiguous date range')
    values = []
    cumulative = 0.0
    expected_dds = []
    expected_durations = []
    for idx, row in enumerate(daily):
        if row['status'] not in ('settled', 'pending', 'provisional'):
            errors.append(f'invalid daily status for {row["date"]}: {row["status"]}')
        if row['basis'] not in (BACKFILL_BASIS, PROSPECTIVE_BASIS, PROSPECTIVE_SETTLED_BASIS, PROSPECTIVE_PROVISIONAL_BASIS):
            errors.append(f'invalid daily basis for {row["date"]}: {row["basis"]}')
        if row['status'] == 'pending' and row['basis'] != PROSPECTIVE_BASIS:
            errors.append(f'pending row must use prospective basis: {row["date"]}')
        if row['status'] == 'settled' and row['basis'] == PROSPECTIVE_BASIS:
            errors.append(f'settled row must use a settled basis: {row["date"]}')
        if row['status'] == 'provisional' and row['basis'] != PROSPECTIVE_PROVISIONAL_BASIS:
            errors.append(f'provisional row must use provisional basis: {row["date"]}')
        pnl = parse_money(row['realized_pnl'])
        values.append(pnl)
        cumulative += pnl
        if row['cumulative_pnl'] != money(cumulative):
            errors.append(f'bad cumulative_pnl for {row["date"]}: {row["cumulative_pnl"]} != {money(cumulative)}')
    expected_dds, expected_durations, _max_dd, _max_duration = drawdown(values)
    for idx, row in enumerate(daily):
        if row['drawdown'] != money(expected_dds[idx]):
            errors.append(f'bad drawdown for {row["date"]}: {row["drawdown"]} != {money(expected_dds[idx])}')
        if row['days_since_equity_high'] != str(expected_durations[idx]):
            errors.append(f'bad days_since_equity_high for {row["date"]}')
    if weekly != expected_periods(daily, 'weekly'):
        errors.append('weekly.csv is not derived from daily.csv')
    if monthly != expected_periods(daily, 'monthly'):
        errors.append('monthly.csv is not derived from daily.csv')
    if summary and summary[0] != expected_summary(daily):
        errors.append('summary.csv is not derived from daily.csv')
    errors.extend(verify_valuation_provenance(daily, valuation))
    errors.extend(verify_anchor(root, daily, weekly, monthly, summary))
    errors.extend(verify_hashes(root))
    errors.extend(verify_leaks(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--public-repo', type=Path, default=Path('.'))
    args = parser.parse_args()
    errors = verify(args.public_repo.resolve())
    if errors:
        json.dump({'ok': False, 'errors': errors}, sys.stdout, indent=2)
        sys.stdout.write('\n')
        return 1
    json.dump({'ok': True, 'errors': []}, sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
