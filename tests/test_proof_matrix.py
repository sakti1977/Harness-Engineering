"""Proof-matrix coverage: every claim has a producer tested at the boundary it needs."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("harness_check", ROOT / "scripts/harness_check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
HEADER = ("| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |\n"
          "| --- | --- | --- | --- | --- | --- |\n")


class ProofMatrix(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in checker.CORE_FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / name).read_text(encoding="utf-8"), encoding="utf-8")
        self.feature = json.loads((ROOT / ".harness/feature.json").read_text(encoding="utf-8"))
        self.claims = self.feature["claims"]

    def matrix(self, rows, state="ready_for_verification"):
        body = "".join(f"| {c} | obs | {req} | {prod} | {tested} | |\n" for c, req, prod, tested in rows)
        (self.root / "docs/proof-matrix.md").write_text("# Proof\n\n" + HEADER + body + "\nTrailing text.\n", encoding="utf-8")
        (self.root / ".harness/feature.json").write_text(json.dumps(dict(self.feature, state=state)), encoding="utf-8")
        return checker.inspect(self.root)

    def full(self, **override):
        rows = [[c, "entry, persistence", "`test_x`", "entry, persistence"] for c in self.claims]
        for index, row in override.items():
            rows[int(index[1:])] = row
        return rows

    def failing(self, result):
        return [f["code"] for f in result["findings"] if not f["ok"]]

    def test_repository_matrix_covers_the_sample_feature(self):
        findings = checker.proof_findings(ROOT, dict(self.feature, state="ready_for_verification"))
        self.assertEqual([f["code"] for f in findings], ["PROOF_COVERED"] * len(self.claims))

    def test_complete_matrix_passes(self):
        self.assertTrue(self.matrix(self.full())["ok"])

    def test_helper_only_evidence_is_a_boundary_gap(self):
        result = self.matrix(self.full(r1=[self.claims[1], "entry, persistence", "`test_helper`", "unit"]))
        self.assertEqual(self.failing(result), ["PROOF_BOUNDARY_GAP"])
        self.assertIn("missing entry, persistence", json.dumps(result))

    def test_partial_boundary_coverage_is_a_gap(self):
        result = self.matrix(self.full(r3=[self.claims[3], "entry, persistence, concurrency", "`t`", "entry; persistence"]))
        self.assertIn("missing concurrency", json.dumps(result))

    def test_missing_claim_row_and_reworded_claim(self):
        rows = self.full()
        rows[0][0] = "conflicts return 409"
        codes = self.failing(self.matrix(rows))
        self.assertIn("PROOF_CLAIM_MISSING", codes)
        self.assertIn("PROOF_UNKNOWN_CLAIM", codes)

    def test_missing_producer(self):
        for producer in ("", "TBD", "-", "n/a"):
            with self.subTest(producer=producer):
                result = self.matrix(self.full(r0=[self.claims[0], "entry", producer, "entry"]))
                self.assertEqual(self.failing(result), ["PROOF_PRODUCER_MISSING"])

    def test_unknown_or_missing_required_boundary(self):
        self.assertEqual(self.failing(self.matrix(self.full(r0=[self.claims[0], "api", "`t`", "api"]))),
                         ["PROOF_BOUNDARY_UNKNOWN"])
        self.assertEqual(self.failing(self.matrix(self.full(r0=[self.claims[0], "", "`t`", "entry"]))),
                         ["PROOF_BOUNDARY_GAP"])

    def test_matrix_without_table(self):
        (self.root / "docs/proof-matrix.md").write_text("# Proof\n\nWe test things.\n", encoding="utf-8")
        (self.root / ".harness/feature.json").write_text(json.dumps(dict(self.feature, state="ready_for_verification")), encoding="utf-8")
        self.assertEqual(self.failing(checker.inspect(self.root)), ["PROOF_MATRIX_NO_TABLE"])

    def test_gaps_are_advisory_before_verification_is_requested(self):
        for state in ("planned", "active", "blocked"):
            with self.subTest(state=state):
                result = self.matrix(self.full(r1=[self.claims[1], "persistence", "`t`", "unit"]), state=state)
                self.assertTrue(result["ok"])
                gap = [f for f in result["findings"] if f["code"] == "PROOF_BOUNDARY_GAP"]
                self.assertEqual(gap[0]["severity"], "info")

    def test_claim_markup_and_case_in_boundaries_are_tolerated(self):
        rows = [[f"**{c}**", "`Entry`", "`t`", "ENTRY, persistence"] for c in self.claims]
        self.assertTrue(self.matrix(rows)["ok"])


if __name__ == "__main__":
    unittest.main()
