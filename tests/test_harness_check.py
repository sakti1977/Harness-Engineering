from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import importlib.util
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("harness_check", ROOT / "scripts/harness_check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ArtifactChecks(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in checker.CORE_FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / name).read_text())
        self.feature = self.root / ".harness/feature.json"
        self.data = json.loads(self.feature.read_text())

    def write(self, data):
        self.feature.write_text(json.dumps(data))

    def test_valid_core_does_not_require_vendor_file(self):
        self.assertTrue(checker.inspect(self.root)["ok"])
        self.assertFalse(checker.inspect(self.root, "copilot")["ok"])

    def test_malformed_and_nonobject_json(self):
        for raw in ("{", "[]", "null", '"text"', "42"):
            with self.subTest(raw=raw):
                self.feature.write_text(raw)
                self.assertFalse(checker.inspect(self.root)["ok"])

    def test_state_is_enum_and_not_self_attested_passing(self):
        for state in ("passing", "banana", "", None, 7):
            with self.subTest(state=state):
                self.write(dict(self.data, state=state))
                self.assertFalse(checker.inspect(self.root)["ok"])
        for state in ("planned", "active", "blocked", "ready_for_verification"):
            self.write(dict(self.data, state=state))
            self.assertTrue(checker.inspect(self.root)["ok"])

    def test_missing_blank_wrong_type_and_unknown_fields(self):
        variants = [dict(self.data, outcome="  "), dict(self.data, claims=[]),
                    dict(self.data, claims=[7]), dict(self.data, claims=["x", "x"]),
                    dict(self.data, exclusions="none"), dict(self.data, surprise=True),
                    dict(self.data, verification="")]
        missing = dict(self.data)
        del missing["id"]
        variants.append(missing)
        for data in variants:
            with self.subTest(data=data):
                self.write(data)
                self.assertFalse(checker.inspect(self.root)["ok"])

    def test_expected_surface_is_relative(self):
        for path in ("../outside", "/etc/passwd", "C:\\data", "", "."):
            self.write(dict(self.data, expected_surface=[path]))
            self.assertFalse(checker.inspect(self.root)["ok"])

    def test_missing_empty_directory_and_non_utf8_artifacts(self):
        path = self.root / "docs/readiness.md"
        path.unlink()
        self.assertFalse(checker.inspect(self.root)["ok"])
        path.mkdir()
        self.assertFalse(checker.inspect(self.root)["ok"])
        path.rmdir()
        path.write_text("")
        self.assertFalse(checker.inspect(self.root)["ok"])
        path.write_bytes(b"\xff")
        self.assertFalse(checker.inspect(self.root)["ok"])

    def test_verification_string_is_never_executed(self):
        self.write(dict(self.data, verification="do-not-execute-this"))
        with patch("subprocess.run", side_effect=AssertionError("executed")):
            self.assertTrue(checker.inspect(self.root)["ok"])

    def test_cli_json_exit_code_and_no_mutation(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = subprocess.run([sys.executable, str(ROOT / "scripts/harness_check.py"), "--root", str(self.root), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.feature.write_text("{")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/harness_check.py"), "--root", str(self.root), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_external_symlink_is_rejected(self):
        path = self.root / "docs/readiness.md"
        path.unlink()
        try:
            path.symlink_to(ROOT / "README.md")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        self.assertFalse(checker.inspect(self.root)["ok"])


if __name__ == "__main__":
    unittest.main()
