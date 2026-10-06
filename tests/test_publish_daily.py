import importlib.util
import io
import json
import shutil
import tempfile
import unittest
import warnings
import zipfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publisher', ROOT / 'scripts/publish_daily.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='series2-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel in ('README.md', 'STATUS.md', 'VERIFY.md', '.gitattributes', '.gitignore',
                    '.github/workflows/verify.yml', '.github/workflows/publish-daily.yml',
                    'scripts/verify.py', 'scripts/publish_daily.py', 'tests/test_publish_daily.py',
                    'proof/anchor.json', 'proof/records.sha256') + publisher.DATA:
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        if (ROOT / 'proof/publication.json').exists():
            shutil.copyfile(ROOT / 'proof/publication.json', self.root / 'proof/publication.json')
        publisher.seal(self.root)
        self.anchor = json.loads((self.root / 'proof/anchor.json').read_text())
        self.end = date.fromisoformat(self.anchor['record_end'])

    def package(self, changes=None):
        files = {name: (self.root / name).read_bytes() for name in publisher.PAYLOAD}
        files.update(changes or {})
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as archive:
            for name, body in files.items():
                archive.writestr(name, body)
        return output.getvalue()

    def test_valid_package_verifies(self):
        publisher.import_package(self.root, self.package(), self.end)
        publisher.seal(self.root)
        publisher.verify(self.root)

    def test_no_source_reports_missing_dates_without_changing_economics(self):
        before = {name: (self.root / name).read_bytes() for name in publisher.DATA}
        receipt = publisher.refresh(self.root, self.end + timedelta(days=6))
        self.assertEqual(receipt['missing_result_days'], 6)
        self.assertEqual(receipt['status'], 'blocked_result_generation')
        self.assertFalse(receipt['paper_trading_active'])
        self.assertFalse(receipt['result_generation_ready'])
        for name, contents in before.items():
            self.assertEqual(contents, (self.root / name).read_bytes())
        publisher.verify(self.root)

    def test_no_source_is_not_ready_even_when_dates_are_current(self):
        receipt = publisher.refresh(self.root, self.end)
        self.assertFalse(receipt['result_generation_ready'])

    def test_changed_strategy_rejected(self):
        incoming = dict(self.anchor)
        incoming['private_commitments_sha256'] = dict(incoming['private_commitments_sha256'])
        incoming['private_commitments_sha256']['frozen_specification'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'frozen strategy'):
            publisher.import_package(self.root, self.package({'proof/anchor.json': json.dumps(incoming).encode()}), self.end)

    def test_future_end_rejected(self):
        incoming = dict(self.anchor, record_end=(self.end + timedelta(days=1)).isoformat())
        with self.assertRaisesRegex(ValueError, 'future'):
            publisher.import_package(self.root, self.package({'proof/anchor.json': json.dumps(incoming).encode()}), self.end)

    def test_undeclared_restatement_rejected(self):
        data = (self.root / publisher.DATA[0]).read_bytes().replace(b'retrospective_reconstruction', b'prospective_shadow', 1)
        with self.assertRaisesRegex(ValueError, 'restatement'):
            publisher.import_package(self.root, self.package({publisher.DATA[0]: data}), self.end)

    def test_invalid_math_retains_verified_record(self):
        incoming = dict(self.anchor, supersedes_records_sha256=self.anchor['records_sha256'])
        original = (self.root / publisher.DATA[0]).read_bytes()
        bad = original.replace(b',-499.828,', b',999.828,', 1)
        self.assertNotEqual(bad, original)
        receipt = publisher.refresh(self.root, self.end, package=self.package({
            publisher.DATA[0]: bad, 'proof/anchor.json': json.dumps(incoming).encode()}))
        self.assertEqual(receipt['source_state'], 'source_package_rejected')
        self.assertEqual(original, (self.root / publisher.DATA[0]).read_bytes())

    def test_archive_cannot_supply_executable_files(self):
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            publisher.import_package(self.root, self.package({'scripts/verify.py': b'raise SystemExit(0)'}), self.end)

    def test_duplicate_zip_members_rejected(self):
        output = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(output, 'w') as archive:
                archive.writestr(publisher.DATA[0], b'first')
                archive.writestr(publisher.DATA[0], b'second')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            publisher.import_package(self.root, output.getvalue(), self.end)

    def test_current_consumed_package_is_ready(self):
        receipt = publisher.refresh(self.root, self.end, package=self.package())
        self.assertTrue(receipt['result_generation_ready'])
        self.assertEqual(receipt['status'], 'current')


if __name__ == '__main__':
    unittest.main()
