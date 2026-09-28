"""Adoption: preview first, never overwrite, and leave a project the other commands can drive."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
spec = importlib.util.spec_from_file_location("harness_adopt", SCRIPTS / "harness_adopt.py")
adopt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adopt)
ENV = dict(os.environ, HARNESS_KIT=str(ROOT), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
           GIT_CONFIG_COUNT="3", GIT_CONFIG_KEY_0="gc.auto", GIT_CONFIG_VALUE_0="0",
           GIT_CONFIG_KEY_1="maintenance.auto", GIT_CONFIG_VALUE_1="false",
           GIT_CONFIG_KEY_2="gc.autoDetach", GIT_CONFIG_VALUE_2="false")


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}


class Adopt(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "my-app"
        (self.root / "src").mkdir(parents=True)
        (self.root / "src/app.ts").write_text("export const save = () => true;\n")

    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), "--root", str(self.root), *args],
                              capture_output=True, text=True, env=ENV, cwd=self.root)

    def test_preview_writes_nothing(self):
        before = snapshot(self.root)
        result = self.run_script("harness_adopt.py", "--agents", "all", "--ci")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preview; nothing written", result.stdout)
        self.assertEqual(snapshot(self.root), before)

    def test_apply_creates_files_the_checker_accepts(self):
        result = self.run_script("harness_adopt.py", "--apply", "--agents", "all", "--ci")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", ".cursor/rules/harness.mdc",
                     ".github/workflows/harness.yml", ".harness/agent-protocol.md", "docs/verify.md"):
            self.assertTrue((self.root / name).is_file(), name)
        check = self.run_script("harness_check.py")
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_agent_lists_create_the_right_instruction_files(self):
        result = self.run_script("harness_adopt.py", "--apply", "--agents", "gemini,cursor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("@./AGENTS.md", (self.root / "GEMINI.md").read_text())
        self.assertIn("imported by GEMINI.md", result.stdout)
        rule = (self.root / ".cursor/rules/harness.mdc").read_text()
        self.assertTrue(rule.startswith("---\n"))
        self.assertIn("alwaysApply: true", rule.split("---")[1])
        self.assertIn(adopt.PROTOCOL_START, rule)
        self.assertIn(adopt.PROTOCOL_START, (self.root / "AGENTS.md").read_text())
        self.assertFalse((self.root / "CLAUDE.md").exists())
        self.assertFalse((self.root / ".github/copilot-instructions.md").exists())

    def test_unknown_agent_is_rejected_before_anything_is_written(self):
        before = snapshot(self.root)
        result = self.run_script("harness_adopt.py", "--apply", "--agents", "claude,vim")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown --agents value vim", result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_existing_importer_needs_no_hint(self):
        (self.root / "GEMINI.md").write_text("# Ours\n\n@AGENTS.md\n")
        (self.root / "CLAUDE.md").write_text("# Ours\n")
        result = self.run_script("harness_adopt.py", "--agents", "claude,gemini")
        self.assertIn("CLAUDE.md already exists", result.stdout)
        self.assertNotIn("GEMINI.md already exists", result.stdout)

    def test_existing_files_are_never_changed_and_rerun_is_a_no_op(self):
        (self.root / "CLAUDE.md").write_text("# House rules\n")
        (self.root / "docs").mkdir()
        (self.root / "docs/authority.md").write_text("# Our policy\n")
        self.run_script("harness_adopt.py", "--apply", "--agents", "all")
        self.assertEqual((self.root / "CLAUDE.md").read_text(), "# House rules\n")
        self.assertEqual((self.root / "docs/authority.md").read_text(), "# Our policy\n")
        after_first = snapshot(self.root)
        second = self.run_script("harness_adopt.py", "--apply", "--agents", "all")
        self.assertIn("Created 0 file(s)", second.stdout)
        self.assertIn("CLAUDE.md already exists", second.stdout)
        self.assertEqual(snapshot(self.root), after_first)

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_printed_commit_step_leaves_a_clean_session_check(self):
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True, env=ENV)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=ENV)
        subprocess.run(["git", "commit", "-q", "-m", "app"], cwd=self.root, check=True, env=ENV)
        result = self.run_script("harness_adopt.py", "--apply", "--agents", "all")
        command = next(line.strip() for line in result.stdout.splitlines() if line.strip().startswith("git add "))
        before = self.run_script("harness_check.py", "--session")
        self.assertIn("SCOPE_OUTSIDE_SURFACE", before.stdout, "uncommitted setup files are reported until committed")
        subprocess.run(command, shell=True, cwd=self.root, check=True, env=ENV)
        after = self.run_script("harness_check.py", "--session")
        self.assertEqual(after.returncode, 0, after.stdout)
        self.assertEqual(subprocess.run(["git", "status", "--porcelain"], cwd=self.root, capture_output=True,
                                        text=True, env=ENV).stdout, "", "the printed command must commit every created file")

    def test_symlink_escaping_the_project_is_refused(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        try:
            (self.root / "docs").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        result = self.run_script("harness_adopt.py", "--apply")
        self.assertEqual(result.returncode, 1)
        self.assertIn("refuse", result.stdout)
        self.assertEqual(list(outside.iterdir()), [])

    def test_bad_roots_are_rejected(self):
        self.assertEqual(subprocess.run([sys.executable, str(SCRIPTS / "harness_adopt.py"), "--root", str(ROOT)],
                                        capture_output=True, text=True).returncode, 2)
        self.assertEqual(subprocess.run([sys.executable, str(SCRIPTS / "harness_adopt.py"), "--root",
                                         str(self.root / "missing")], capture_output=True, text=True).returncode, 2)

    def test_commands_in_project_files_point_at_real_kit_scripts(self):
        self.run_script("harness_adopt.py", "--apply", "--agents", "all", "--ci")
        text = "".join((self.root / name).read_text() for name in
                       ("AGENTS.md", ".harness/agent-protocol.md", ".harness/checkpoint.md", ".github/workflows/harness.yml",
                        ".cursor/rules/harness.mdc", ".github/copilot-instructions.md"))
        self.assertNotIn(str(ROOT), text, "project files must not embed this machine's kit path")
        scripts = set(re.findall(r"\$HARNESS_KIT/scripts/(harness_\w+\.py)", text))
        self.assertTrue(scripts)
        for script in scripts:
            self.assertTrue((SCRIPTS / script).is_file(), script)
        self.assertNotRegex(text, r"python3 scripts/harness_")

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_adopted_project_runs_the_whole_workflow(self):
        self.run_script("harness_adopt.py", "--apply")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True, env=ENV)
        claim = "saving returns true and stores the record"
        ledger = json.loads((self.root / ".harness/feature.json").read_text())
        ledger.update(outcome="Saving stores the record", expected_surface=["src/app.ts"],
                      verification="npm test -- save", claims=[claim])
        (self.root / ".harness/feature.json").write_text(json.dumps(ledger, indent=2))
        matrix = self.root / "docs/proof-matrix.md"
        row = next(line for line in matrix.read_text().splitlines() if line.startswith("| TODO: first claim"))
        matrix.write_text(matrix.read_text().replace(
            row, f"| {claim} | true, then the record read back | entry, persistence | `save.test.ts` | entry, persistence | None |"))
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=ENV)
        subprocess.run(["git", "commit", "-q", "-m", "adopt"], cwd=self.root, check=True, env=ENV)
        for to, role in (("planned", "planner"), ("active", "worker")):
            moved = self.run_script("harness_transition.py", "--to", to, "--actor", "sakti", "--role", role, "--reason", "start")
            self.assertEqual(moved.returncode, 0, moved.stdout)
        (self.root / "src/app.ts").write_text("export const save = () => store();\n")
        self.assertEqual(self.run_script("harness_handoff.py", "--write").returncode, 0)
        checkpoint = self.root / ".harness/checkpoint.md"
        self.assertIn("$HARNESS_KIT/scripts/harness_handoff.py --root . --resume", checkpoint.read_text())
        checkpoint.write_text(checkpoint.read_text().replace("## Next bounded edit\n\nTODO",
                                                             "## Next bounded edit\n\nWrite save.test.ts reading the record back."))
        handoff = self.run_script("harness_handoff.py", "--check")
        self.assertEqual(handoff.returncode, 0, handoff.stdout)
        self.assertEqual(self.run_script("harness_handoff.py", "--resume").returncode, 0)
        self.assertEqual(self.run_script("harness_check.py", "--session").returncode, 0)


if __name__ == "__main__":
    unittest.main()
