#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

DAILY_COLUMNS = ['date','signal_date','status','realized_pnl','cumulative_pnl','source','memo']
PERIOD_COLUMNS = ['period_start','period_end','status','settled_days','pending_days','total_days','realized_pnl','cumulative_pnl']
FORBIDDEN_TRACKED_PREFIXES = ('private/', '_private/', 'vault/', 'raw/', 'tmp/')
FORBIDDEN_SUFFIXES = ('.parquet', '.pkl', '.pickle', '.key', '.pem', '.env', '.sqlite', '.db')
FORBIDDEN_TEXT = ('/mnt/c/', '/home/', 'OPENAI_API_KEY', 'GITHUB_TOKEN', 'password=', 'secret=', 'scored_signals', 'positions_', 'model_stack', 'training_dataset')


def read_csv(path: Path, columns: list[str]) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != columns:
            raise ValueError(f'{path}: expected columns {columns}, got {reader.fieldnames}')
        return list(reader)


def parse_money(value: str, *, allow_blank: bool = False) -> float:
    if value == '' and allow_blank:
        return 0.0
    try:
        out = float(value)
    except ValueError as exc:
        raise ValueError(f'invalid numeric value {value!r}') from exc
    if not math.isfinite(out):
        raise ValueError(f'non-finite numeric value {value!r}')
    return out


def date_range(start: date, end: date) -> list[date]:
    out = []
    cur = start
    while cur <= end:
        out.append(cur)
        cur += timedelta(days=1)
    return out


def group_periods(rows: list[dict[str, str]], kind: str) -> list[dict[str, str]]:
    start = date.fromisoformat(rows[0]['date'])
    end = date.fromisoformat(rows[-1]['date'])
    out = []
    idx = 0
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
        settled = [r for r in chunk if r['status'] == 'settled']
        pending = [r for r in chunk if r['status'] == 'pending']
        realized = sum(parse_money(r['realized_pnl']) for r in settled)
        out.append({
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'status': 'pending' if pending else 'settled',
            'settled_days': str(len(settled)),
            'pending_days': str(len(pending)),
            'total_days': str(len(chunk)),
            'realized_pnl': f'{realized:.2f}',
            'cumulative_pnl': chunk[-1]['cumulative_pnl'],
        })
    return out


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hashes(root: Path) -> list[str]:
    errors = []
    path = root / 'proof/records.sha256'
    rows = read_csv(path, ['path','sha256'])
    for row in rows:
        target = root / row['path']
        if not target.is_file():
            errors.append(f'missing hashed file: {row["path"]}')
            continue
        actual = sha256_file(target)
        if actual != row['sha256']:
            errors.append(f'hash mismatch for {row["path"]}: {actual} != {row["sha256"]}')
    return errors


def tracked_files(root: Path) -> list[str]:
    git_dir = root / '.git'
    if not git_dir.exists():
        return []
    result = subprocess.run(['git', '-C', str(root), 'ls-files'], text=True, capture_output=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


def verify_leaks(root: Path) -> list[str]:
    errors = []
    files = tracked_files(root)
    for rel in files:
        low = rel.lower()
        if low.startswith(FORBIDDEN_TRACKED_PREFIXES):
            errors.append(f'forbidden private/raw tracked path: {rel}')
        if low.endswith(FORBIDDEN_SUFFIXES):
            errors.append(f'forbidden tracked raw/source file type: {rel}')
        path = root / rel
        if rel in ('scripts/verify.py', 'scripts/verify_selftest.py'):
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


def verify(root: Path) -> list[str]:
    errors = []
    manifest = json.loads((root / 'proof/source_manifest.json').read_text(encoding='utf-8'))
    daily = read_csv(root / 'data/daily.csv', DAILY_COLUMNS)
    weekly = read_csv(root / 'data/weekly.csv', PERIOD_COLUMNS)
    monthly = read_csv(root / 'data/monthly.csv', PERIOD_COLUMNS)
    expected_dates = [d.isoformat() for d in date_range(date.fromisoformat(manifest['record_start']), date.fromisoformat(manifest['record_end']))]
    actual_dates = [r['date'] for r in daily]
    if actual_dates != expected_dates:
        errors.append('daily.csv does not contain the exact complete date range')
    cumulative = 0.0
    pending_dates = []
    for row in daily:
        status = row['status']
        if status not in ('settled', 'pending'):
            errors.append(f'invalid daily status for {row["date"]}: {status}')
            continue
        if status == 'settled':
            if row['source'] != 'backfill':
                errors.append(f'settled row source must be backfill: {row["date"]}')
            cumulative += parse_money(row['realized_pnl'])
        else:
            pending_dates.append(row['date'])
            if row['realized_pnl'] != '':
                errors.append(f'pending row must not publish realized_pnl: {row["date"]}')
        observed_cum = parse_money(row['cumulative_pnl'])
        if f'{observed_cum:.2f}' != f'{cumulative:.2f}':
            errors.append(f'bad cumulative_pnl for {row["date"]}: {observed_cum:.2f} != {cumulative:.2f}')
    if pending_dates != manifest['pending_dates']:
        errors.append(f'pending dates mismatch: {pending_dates} != {manifest["pending_dates"]}')
    if weekly != group_periods(daily, 'weekly'):
        errors.append('weekly.csv is not derived from daily.csv')
    if monthly != group_periods(daily, 'monthly'):
        errors.append('monthly.csv is not derived from daily.csv')
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
