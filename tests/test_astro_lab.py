"""The Jyotish Coach lab's own tools must keep telling the truth."""
from pathlib import Path
import re
import unittest
from examples.astro import ablation, sweep
from examples.astro.test_astro import route_failure

ROOT = Path(__file__).resolve().parents[1]


class AstroLabTools(unittest.TestCase):
    def test_sweep_finds_the_window_only_on_the_broken_app(self):
        rows = sweep.sweep()
        points = [row[0] for row in rows]
        self.assertEqual((points[0], points[-1]), ("start", "after_write"))
        self.assertEqual(sum(row[1] for row in rows), len(rows) - 2, "broken app: stale at every point inside the window")
        self.assertFalse(rows[0][1] or rows[-1][1], "sequential points must look fine on the broken app")
        self.assertFalse(any(row[3] for row in rows), "fixed app must never store stale coaching")
        self.assertTrue(all(row[4] == 409 for row in rows[1:-1]))

    def test_ablation_classification(self):
        verdicts = {name: verdict for name, verdict, _ in ablation.results()}
        self.assertEqual(verdicts, ablation.EXPECTED)

    def test_route_messages_point_at_real_routes(self):
        verify = (ROOT / "docs/verify.md").read_text()
        anchors = {"route-" + m for m in re.findall(r"^## Route: ([a-z-]+)$", verify, re.M)}
        source = (ROOT / "examples/astro/test_astro.py").read_text()
        used = {"route-" + name for name in re.findall(r'route_failure\(\s*"[^"]+",\s*"([a-z-]+)"', source)}
        self.assertEqual(len(used), 3, used)
        self.assertLessEqual(used, anchors)
        self.assertIn("ROUTE     docs/verify.md#route-profile-sync", route_failure("c", "profile-sync", "e", "o", "r"))

    def test_every_claim_has_a_route(self):
        verify = (ROOT / "docs/verify.md").read_text()
        import json
        for claim in json.loads((ROOT / ".harness/feature.json").read_text())["claims"]:
            self.assertIn(f"| Claim | {claim} |", verify)


if __name__ == "__main__":
    unittest.main()
