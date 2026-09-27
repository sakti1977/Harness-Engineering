"""The harness tests must fail when a gate is broken, uncovered or its fixture drifts."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("harness_tests_run", ROOT / "harness-tests/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
MANIFEST = json.loads((ROOT / "harness-tests/manifest.json").read_text())["entries"]


def entries(*ids):
    return [e for e in MANIFEST if e["id"] in ids]


class HarnessTests(unittest.TestCase):
    def run_main(self, manifest=None):
        out = StringIO()
        with redirect_stdout(out):
            code = runner.main(manifest)
        return code, out.getvalue()

    def test_full_manifest_passes(self):
        code, out = self.run_main()
        self.assertEqual(code, 0, out)

    def test_disabled_independence_check_is_caught(self):
        with patch.object(runner.mover, "gate_failures", return_value=[]):
            received = runner.run_entry(entries("transition-self-approval")[0])
        self.assertEqual(received, [], "sabotaged gate lets self-approval through")
        # ...and the runner reports it as a failure with the id and both codes.
        with patch.object(runner.mover, "gate_failures", return_value=[]):
            code, out = self.run_main(entries("transition-self-approval", "clean-artifacts",
                                              "clean-session", "clean-transition-genesis"))
        self.assertEqual(code, 1)
        self.assertIn("FAIL transition-self-approval: expected ['TRANSITION_NOT_INDEPENDENT'] received PASS", out)

    def test_disabled_proof_gate_is_caught(self):
        with patch.object(runner.check, "proof_findings", return_value=[]):
            self.assertEqual(runner.run_entry(entries("proof-boundary-gap")[0]), [])

    def test_new_code_without_fixture_is_uncovered(self):
        with patch.object(runner, "gate_codes", return_value=runner.gate_codes() | {"NEW_GATE_DENIED"}):
            problems = runner.coverage_problems(MANIFEST)
        self.assertEqual(problems, ["UNCOVERED NEW_GATE_DENIED: add a defect fixture that makes a gate emit it"])

    def test_every_gate_needs_a_clean_fixture(self):
        without_clean_session = [e for e in MANIFEST if not (e["gate"] == "session" and not e["expect"])]
        self.assertIn("NO_CLEAN_FIXTURE session: add a clean entry that this gate passes",
                      runner.coverage_problems(without_clean_session))

    def test_unknown_defect_and_duplicate_ids(self):
        broken = MANIFEST + [dict(MANIFEST[0], defect="does_not_exist")]
        problems = runner.coverage_problems(broken)
        self.assertIn(f"DUPLICATE_ID {MANIFEST[0]['id']}", problems)
        self.assertTrue(any(p.startswith("UNKNOWN_DEFECT") for p in problems))

    def test_fixture_drift_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            fixtures = Path(directory) / "fixtures"
            shutil.copytree(ROOT / "harness-tests/fixtures", fixtures)
            (fixtures / "clean-project/docs/readiness.md").unlink()
            matrix = fixtures / "clean-project/docs/proof-matrix.md"
            matrix.write_text(matrix.read_text().replace("Tested boundary", "Coverage"))
            with patch.object(runner, "HERE", Path(directory)):
                problems = runner.drift_problems()
        self.assertIn("FIXTURE_DRIFT clean-project: missing docs/readiness.md", problems)
        self.assertTrue(any("proof matrix lacks the columns" in p for p in problems))

    def test_every_manifest_code_is_a_real_gate_code(self):
        known = runner.gate_codes()
        for entry in MANIFEST:
            for code in entry["expect"]:
                self.assertIn(code, known, f"{entry['id']} expects {code}, which no gate emits")


if __name__ == "__main__":
    unittest.main()
