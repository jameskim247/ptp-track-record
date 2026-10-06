#!/usr/bin/env python3
"""Publish verified result packages and an honest daily coverage receipt.

This is the publication consumer, not an E24 calculation engine. Its producer
must export four CSVs and proof/anchor.json as a ZIP after the frozen replay.
Missing calculations never become zero-P&L rows. Only retrospective results
are admitted by the current independent verifier.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA = tuple(f'data/series-2/{name}.csv' for name in ('daily', 'weekly', 'monthly', 'summary'))
PAYLOAD = DATA + ('proof/anchor.json',)
LIMIT = 20 * 1024 * 1024
HOSTS = {'storage.googleapis.com', 'github.com', 'raw.githubusercontent.com',
         'objects.githubusercontent.com', 'release-assets.githubusercontent.com'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(root):
    """Reseal tracked publication files, excluding the self-referential anchor."""
    manifest = root / 'proof/records.sha256'
    paths = {line.split('  ', 1)[1] for line in manifest.read_text().splitlines()}
    paths.update(('scripts/publish_daily.py', '.github/workflows/publish-daily.yml',
                  'tests/test_publish_daily.py'))
    if (root / 'proof/publication.json').exists():
        paths.add('proof/publication.json')
    manifest.write_text(''.join(f'{digest(root / rel)}  {rel}\n' for rel in sorted(paths)),
                        encoding='utf-8', newline='\n')
    anchor_path = root / 'proof/anchor.json'
    anchor = json.loads(anchor_path.read_text())
    anchor['records_sha256'] = digest(manifest)
    anchor_path.write_text(json.dumps(anchor, indent=2) + '\n', encoding='utf-8', newline='\n')


def verify(root):
    checked = subprocess.run([sys.executable, str(root / 'scripts/verify.py')],
                             capture_output=True, text=True, check=False)
    if checked.returncode:
        raise ValueError('independent package verification failed: ' + checked.stdout.strip())


def validate_payload(root, files, through):
    if set(files) != set(PAYLOAD):
        raise ValueError('source ZIP must contain exactly the four public CSVs and proof/anchor.json')
    prior = json.loads((root / 'proof/anchor.json').read_text())
    incoming = json.loads(files['proof/anchor.json'])
    if (incoming.get('schema') != prior['schema'] or incoming.get('series_id') != 'series-2'
            or incoming.get('record_start') != prior['record_start']
            or incoming.get('evidence_basis') != 'retrospective_reconstruction'
            or incoming.get('public_cost_per_placed_mwh') != 0.4
            or incoming.get('specification_frozen') != prior['specification_frozen']
            or incoming.get('private_commitments_sha256', {}).get('frozen_specification')
            != prior['private_commitments_sha256']['frozen_specification']):
        raise ValueError('source changed the frozen strategy, costs, start date or evidence class')
    if not prior['record_end'] <= incoming['record_end'] <= through.isoformat():
        raise ValueError('source end date regressed or includes a future/uncompleted day')
    commitments = incoming.get('private_commitments_sha256', {})
    if set(commitments) != set(prior['private_commitments_sha256']):
        raise ValueError('private source commitments are incomplete')
    if any(not isinstance(v, str) or len(v) != 64 or any(c not in '0123456789abcdef' for c in v)
           for v in commitments.values()):
        raise ValueError('private source commitment is not a SHA-256 digest')
    before = list(csv.DictReader(io.StringIO((root / DATA[0]).read_text())))
    after = list(csv.DictReader(io.StringIO(files[DATA[0]].decode('utf-8'))))
    if len(after) < len(before):
        raise ValueError('source removed existing result rows')
    changed = before != after[:len(before)]
    if changed and incoming.get('supersedes_records_sha256') != prior['records_sha256']:
        raise ValueError('historical restatement requires the exact superseded manifest digest')
    if len(after) > len(before) and commitments == prior['private_commitments_sha256']:
        raise ValueError('new result rows require new private book/settlement/input commitments')
    return incoming


def import_package(root, package, through):
    """Verify in isolation before installing any of the candidate results."""
    if len(package) > LIMIT:
        raise ValueError('source package exceeds size limit')
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        members = archive.infolist()
        if (len(members) != len(PAYLOAD) or {m.filename for m in members} != set(PAYLOAD)
                or sum(m.file_size for m in members) > LIMIT
                or any(m.is_dir() for m in members)):
            raise ValueError('source ZIP contains unexpected/duplicate paths or exceeds size limit')
        files = {name: archive.read(name) for name in PAYLOAD}
    anchor = validate_payload(root, files, through)
    with tempfile.TemporaryDirectory(prefix='series2-verify-') as temp:
        stage = Path(temp)
        manifest = (root / 'proof/records.sha256').read_text()
        paths = {line.split('  ', 1)[1] for line in manifest.splitlines()}
        paths.update(PAYLOAD)
        paths.update(('proof/records.sha256', 'scripts/publish_daily.py',
                      '.github/workflows/publish-daily.yml', 'tests/test_publish_daily.py'))
        for rel in paths:
            source = root / rel
            if source.exists():
                target = stage / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        for rel, value in files.items():
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
        # The independent verifier is trusted local code, never supplied by the ZIP.
        seal(stage)
        verify(stage)
        for rel in PAYLOAD:
            (root / rel).write_bytes((stage / rel).read_bytes())
    return anchor


def fetch(url):
    parsed = urlparse(url)
    if (parsed.scheme != 'https' or parsed.hostname not in HOSTS or parsed.username
            or parsed.password or parsed.port not in (None, 443)):
        raise ValueError('source must be an HTTPS public-result ZIP on GitHub or Google Cloud Storage')
    with urlopen(url, timeout=60) as response:
        final = urlparse(response.geturl())
        if final.scheme != 'https' or final.hostname not in HOSTS:
            raise ValueError('source redirected outside the approved public artifact hosts')
        body = response.read(LIMIT + 1)
    if len(body) > LIMIT:
        raise ValueError('source response exceeds size limit')
    return body


def refresh(root, through, source_url='', package=None):
    source_state = 'source_not_configured'
    error_kind = None
    if source_url or package is not None:
        try:
            import_package(root, package if package is not None else fetch(source_url), through)
            source_state = 'verified_package_consumed'
        except (ValueError, KeyError, TypeError, OSError, HTTPError, URLError,
                zipfile.BadZipFile) as exc:
            # The failure is persisted and makes the workflow fail after publishing
            # its coverage receipt. The previous verified economic record survives.
            source_state = 'source_package_rejected'
            error_kind = type(exc).__name__
            print(f'Source package rejected ({error_kind}); existing results retained.', file=sys.stderr)
    anchor = json.loads((root / 'proof/anchor.json').read_text())
    end = date.fromisoformat(anchor['record_end'])
    with (root / DATA[0]).open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    count = max(0, (through - end).days)
    receipt = {
        'schema': 'series-2-publication-status-v1', 'series_id': 'series-2',
        'checked_through_operating_date': through.isoformat(),
        'latest_result_date': end.isoformat(),
        'missing_result_days': count,
        'missing_result_start': (end + timedelta(days=1)).isoformat() if count else None,
        'missing_result_end': through.isoformat() if count else None,
        'partially_settled_days': sum(r['status'] == 'partially_settled' for r in rows),
        'source_state': source_state, 'source_error_kind': error_kind,
        'result_generation_ready': bool(source_url or package is not None)
                                   and source_state == 'verified_package_consumed' and count == 0,
        'status': 'current' if count == 0 and source_state == 'verified_package_consumed'
                  else 'blocked_result_generation',
        'publication_schedule_utc': ['14:17', '22:17'],
        'paper_trading_active': False,
        'reason': None if count == 0 and source_state == 'verified_package_consumed' else
                  'The E24 producer has not supplied current verified results. '
                  'Check the private producer receipt and qualified ERCOT price/load availability. '
                  'No missing date is valued at zero or represented as a prospective decision.'
    }
    (root / 'proof/publication.json').write_text(json.dumps(receipt, indent=2) + '\n',
                                                encoding='utf-8', newline='\n')
    seal(root)
    verify(root)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-url', default=os.environ.get('SERIES2_SOURCE_URL', ''))
    parser.add_argument('--package', type=Path, help='local result ZIP; useful for producer acceptance tests')
    parser.add_argument('--through', type=date.fromisoformat,
                        default=datetime.now(ZoneInfo('America/Chicago')).date() - timedelta(days=1))
    parser.add_argument('--seal-only', action='store_true')
    parser.add_argument('--check-freshness', action='store_true')
    args = parser.parse_args()
    if args.seal_only:
        seal(ROOT)
        verify(ROOT)
        return 0
    if args.check_freshness:
        verify(ROOT)
        receipt = json.loads((ROOT / 'proof/publication.json').read_text())
        current_through = datetime.now(ZoneInfo('America/Chicago')).date() - timedelta(days=1)
        healthy = (receipt['status'] == 'current' and receipt['result_generation_ready']
                   and receipt['checked_through_operating_date'] >= current_through.isoformat())
        print(json.dumps(receipt, indent=2))
        if not healthy:
            print('::error::Series-2 result generation is blocked; see proof/publication.json.')
        return 0 if healthy else 1
    receipt = refresh(ROOT, args.through, args.source_url,
                      args.package.read_bytes() if args.package else None)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
