"""The Jyotish evaluation must judge honestly: fail the defects, accept any correct fix, change nothing."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evals/jyotish"
spec = importlib.util.spec_from_file_location("jyotish_regression", EVAL / "regression.py")
regression = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regression)
spec = importlib.util.spec_from_file_location("jyotish_prepare", EVAL / "prepare.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)

REGENERATE = regression.FIXES["race"][1].replace('''    if not n:
        return 409, {"error": "chart changed"}''', '''    if not n:
        return generate_coaching(path, user_id)''')


@unittest.skipUnless(shutil.which("git"), "git is required")
class JyotishEval(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)

    def grade(self, run):
        result = subprocess.run([sys.executable, str(EVAL / "grade.py"), str(run)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def failing(self, graded):
        return sorted(c["check"] for c in graded["checks"] if not c["pass"])

    def test_broken_task_fails_exactly_the_three_defects(self):
        run, _ = prepare.prepare(self.out, "bare", "t")
        self.assertEqual(self.failing(self.grade(run)),
                         ["age_all_offsets", "stale_coaching", "sync_failure_honest", "sync_stored"])

    def test_two_different_correct_fixes_both_score_six(self):
        for style in ("refuse", "regenerate"):
            with self.subTest(style=style):
                run, _ = prepare.prepare(self.out, "bare", style)
                text = regression.app_with("none")
                if style == "regenerate":
                    text = text.replace(regression.FIXES["race"][1], REGENERATE)
                (run / "jyotish/app.py").write_text(text, encoding="utf-8")
                self.assertEqual(self.grade(run)["passed"], 6)

    def test_grading_does_not_change_the_run(self):
        run, _ = prepare.prepare(self.out, "harness", "t")
        before = subprocess.run(["git", "-C", str(run), "status", "--porcelain"], capture_output=True, text=True).stdout
        graded = self.grade(run)
        after = subprocess.run(["git", "-C", str(run), "status", "--porcelain"], capture_output=True, text=True).stdout
        self.assertEqual(before, after)
        self.assertEqual(graded["harness"]["states"], ["planned"])

    def test_single_defect_variants_each_carry_one_defect(self):
        for defect in ("sync", "age", "race"):
            with self.subTest(defect=defect):
                run, _ = prepare.prepare(self.out, "bare", defect)
                (run / "jyotish/app.py").write_text(regression.app_with(defect), encoding="utf-8")
                expected = {"sync": ["sync_failure_honest", "sync_stored"], "age": ["age_all_offsets"],
                            "race": ["stale_coaching"]}[defect]
                self.assertEqual(self.failing(self.grade(run)), expected)

    def test_prepare_refuses_to_put_runs_inside_the_kit(self):
        with self.assertRaises(SystemExit):
            prepare.prepare(ROOT / "evals-out", "bare", "x")

    def test_harness_run_gets_a_stripped_kit_and_no_grader(self):
        run, prompt = prepare.prepare(self.out, "harness", "t")
        kit = self.out / "kit"
        self.assertEqual(sorted(p.name for p in (kit / "scripts").iterdir()),
                         ["harness_check.py", "harness_handoff.py", "harness_transition.py"])
        self.assertFalse(any(kit.rglob("grade.py")) or any(run.rglob("grade.py")))
        self.assertIn(str(kit), prompt)
        self.assertNotIn(str(ROOT), prompt)


if __name__ == "__main__":
    unittest.main()
