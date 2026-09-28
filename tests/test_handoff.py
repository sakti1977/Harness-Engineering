"""Handoff gate and Resume Protocol: honest checkpoints, no ceremonial commits, stale handoffs fail."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import os
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/harness_handoff.py"
spec = importlib.util.spec_from_file_location("harness_handoff", SCRIPT)
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
               GIT_CONFIG_COUNT="3", GIT_CONFIG_KEY_0="gc.auto", GIT_CONFIG_VALUE_0="0",
               GIT_CONFIG_KEY_1="maintenance.auto", GIT_CONFIG_VALUE_1="false",
               GIT_CONFIG_KEY_2="gc.autoDetach", GIT_CONFIG_VALUE_2="false")


@unittest.skipUnless(shutil.which("git"), "git is required")
class Handoff(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(ROOT / "harness-tests/fixtures/clean-project", self.root)
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "start")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True,
                              text=True, env=GIT_ENV).stdout.strip()

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True)

    def fill_next_edit(self, text="Add the read-back assertion to tests/test_profile.py."):
        path = self.root / ".harness/checkpoint.md"
        path.write_text(path.read_text().replace("## Next bounded edit\n\nTODO", f"## Next bounded edit\n\n{text}"))

    def test_write_records_dirty_work_without_committing(self):
        (self.root / "src/profile.py").write_text("# half-finished change\n")
        head = self.git("rev-parse", "HEAD")
        self.assertEqual(self.cli("--write").returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD"), head, "writing a checkpoint must not commit")
        text = (self.root / ".harness/checkpoint.md").read_text()
        self.assertIn("- Uncommitted files: src/profile.py", text)
        self.assertIn(f"- Revision: {head}", text)
        self.assertIn("## Not verified since the last edit", text)

    def test_hand_written_sections_survive_a_rewrite(self):
        self.cli("--write")
        self.fill_next_edit("Wrap the insert in a transaction in src/profile.py.")
        path = self.root / ".harness/checkpoint.md"
        path.write_text(path.read_text().replace("## Suspected causes (not verified)\n\nNone recorded.",
                                                 "## Suspected causes (not verified)\n\nThe write is never committed."))
        (self.root / "src/profile.py").write_text("# another edit\n")
        self.cli("--write")
        text = path.read_text()
        self.assertIn("The write is never committed.", text)
        self.assertIn("Wrap the insert in a transaction in src/profile.py.", text)

    def test_check_passes_an_honest_handoff_and_fails_a_blank_one(self):
        self.cli("--write")
        blank = self.cli("--check")
        self.assertEqual(blank.returncode, 1)
        self.assertIn("CHECKPOINT_MISSING_FIELD", blank.stdout)
        self.fill_next_edit()
        good = self.cli("--check")
        self.assertEqual(good.returncode, 0, good.stdout)

    def test_resume_answers_eight_questions_with_evidence(self):
        self.cli("--write")
        self.fill_next_edit()
        result = self.cli("--resume")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.count("\nQ  ") + result.stdout.startswith("Q  "), 8)
        self.assertEqual(result.stdout.count("   evidence: "), 8)

    def test_resume_detects_a_change_made_after_the_checkpoint(self):
        self.cli("--write")
        self.fill_next_edit()
        (self.root / "src/profile.py").write_text("# someone kept working after the handoff\n")
        result = self.cli("--resume")
        self.assertEqual(result.returncode, 1)
        self.assertIn("CHECKPOINT_STALE", result.stdout)
        self.assertIn("do not follow its next edit", result.stdout)

    def test_fresh_template_means_no_handoff_yet(self):
        resume = self.cli("--resume")
        self.assertEqual(resume.returncode, 0, resume.stdout)
        self.assertIn("No handoff has been written yet", resume.stdout)
        check = self.cli("--check")
        self.assertEqual(check.returncode, 1, "the handoff gate must still refuse an unwritten checkpoint")

    def test_modes_are_required_and_exclusive(self):
        self.assertEqual(self.cli().returncode, 2)
        self.assertEqual(self.cli("--check", "--resume").returncode, 2)


if __name__ == "__main__":
    unittest.main()
