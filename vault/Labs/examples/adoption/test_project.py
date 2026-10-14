"""Verify failure/fix behavior and preservation of existing work."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest
from examples.adoption.project import create, fix

class WalkthroughTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'starter'

    def run_project(self):
        return subprocess.run([sys.executable, '-m', 'unittest', 'test_booking', '-v'],
            cwd=self.path, capture_output=True, text=True, timeout=30)

    def test_negative_control_and_fix(self):
        create(self.path)
        before = {p.name: p.read_bytes() for p in self.path.iterdir() if p.name != 'booking.py'}
        broken = self.run_project()
        self.assertEqual(broken.returncode, 1, broken.stderr)
        self.assertIn('FAILED (failures=2)', broken.stderr)
        for name in ['test_duplicate_changes_no_rows', 'test_concurrent_single_winner']:
            self.assertIn('FAIL: ' + name, broken.stderr)
        self.assertNotIn('ERROR:', broken.stderr)
        fix(self.path)
        fixed = self.run_project()
        self.assertEqual(fixed.returncode, 0, fixed.stderr)
        self.assertIn('Ran 3 tests', fixed.stderr)
        self.assertEqual(before, {name: (self.path / name).read_bytes() for name in before})

    def test_preserves_existing_directory(self):
        self.path.mkdir()
        sentinel = self.path / 'booking.py'
        sentinel.write_text('existing work')
        with self.assertRaises(FileExistsError):
            create(self.path)
        self.assertEqual(sentinel.read_text(), 'existing work')
        self.assertEqual(list(self.path.iterdir()), [sentinel])

    def test_preserves_edited_source(self):
        create(self.path)
        source = self.path / 'booking.py'
        source.write_text('my own fix')
        with self.assertRaises(ValueError):
            fix(self.path)
        self.assertEqual(source.read_text(), 'my own fix')

    def test_preserves_symlink_source(self):
        create(self.path)
        source = self.path / 'booking.py'
        target = self.path / 'other.py'
        source.rename(target)
        original = target.read_bytes()
        try:
            source.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable on this platform")
        with self.assertRaises(ValueError):
            fix(self.path)
        self.assertEqual(target.read_bytes(), original)

if __name__ == '__main__':
    unittest.main()
