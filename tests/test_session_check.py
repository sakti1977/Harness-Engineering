"""Session mode: changed files against the feature scope, claims against recorded evidence."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("harness_check", ROOT / "scripts/harness_check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

# Background auto-maintenance after commits can outlive a test and race its temp-dir cleanup.
NO_BACKGROUND_GIT = {"GIT_CONFIG_COUNT": "3", "GIT_CONFIG_KEY_0": "gc.auto", "GIT_CONFIG_VALUE_0": "0",
                     "GIT_CONFIG_KEY_1": "maintenance.auto", "GIT_CONFIG_VALUE_1": "false",
                     "GIT_CONFIG_KEY_2": "gc.autoDetach", "GIT_CONFIG_VALUE_2": "false"}
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
               **NO_BACKGROUND_GIT)


@unittest.skipUnless(shutil.which("git"), "git is required for session checks")
class SessionChecks(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in checker.CORE_FILES:
            self.put(name, (ROOT / name).read_text())
        self.feature = json.loads((ROOT / ".harness/feature.json").read_text())
        self.feature["excluded_paths"] = ["examples/astro/migrations/"]
        self.save_feature()
        self.put("examples/astro/astro.py", "print('v1')\n")
        self.put("examples/astro/test_astro.py", "# tests\n")
        self.put("examples/astro/migrations/001.sql", "-- schema\n")
        self.put("src/billing.py", "# unrelated\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "start")

    # helpers -------------------------------------------------------------
    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True, env=GIT_ENV).stdout.strip()

    def save_feature(self, **changes):
        self.feature.update(changes)
        self.put(".harness/feature.json", json.dumps(self.feature, indent=2))

    def record(self, claims=None, result="pass", revision=None):
        revision = revision or self.git("rev-parse", "HEAD")
        entries = [{"claim": c, "command": "python3 -m unittest", "result": result,
                    "revision": revision, "observed": "ok"}
                   for c in (claims if claims is not None else self.feature["claims"])]
        self.put(".harness/evidence.json", json.dumps(entries))

    def check(self, base=None):
        return checker.inspect(self.root, session=True, base=base)

    def codes(self, result, ok=None):
        return [f["code"] for f in result["findings"] if ok is None or f["ok"] == ok]

    def commit_all(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "work")

    # scope ---------------------------------------------------------------
    def test_clean_session_passes(self):
        result = self.check()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["scope"], "session-scope-and-evidence")

    def test_edit_inside_surface_passes(self):
        self.put("examples/astro/astro.py", "print('v2')\n")
        self.assertTrue(self.check()["ok"])

    def test_edit_outside_surface_fails_and_names_the_file(self):
        self.put("src/billing.py", "# agent 'tidied' this\n")
        result = self.check()
        self.assertFalse(result["ok"])
        outside = [f["path"] for f in result["findings"] if f["code"] == "SCOPE_OUTSIDE_SURFACE"]
        self.assertEqual(outside, ["src/billing.py"])

    def test_untracked_new_file_outside_surface_fails(self):
        self.put("scratch/notes.py", "x = 1\n")
        self.assertIn("SCOPE_OUTSIDE_SURFACE", self.codes(self.check(), ok=False))

    def test_staged_and_deleted_files_count(self):
        (self.root / "src/billing.py").unlink()
        self.assertIn("SCOPE_OUTSIDE_SURFACE", self.codes(self.check(), ok=False))
        self.git("checkout", "--", "src/billing.py")
        self.put("src/billing.py", "# staged change\n")
        self.git("add", "src/billing.py")
        self.assertIn("SCOPE_OUTSIDE_SURFACE", self.codes(self.check(), ok=False))

    def test_excluded_path_fails_even_inside_a_directory_surface(self):
        self.save_feature(expected_surface=["examples/astro/"])
        self.commit_all()
        self.put("examples/astro/migrations/002.sql", "DROP TABLE coaching;\n")
        result = self.check()
        self.assertEqual(self.codes(result, ok=False), ["SCOPE_EXCLUDED"])

    def test_harness_bookkeeping_is_always_in_scope(self):
        self.put(".harness/checkpoint.md", "# Updated checkpoint\n\nNext: rerun tests.\n")
        self.record()
        self.assertTrue(self.check()["ok"])

    def test_glob_and_directory_surface_patterns(self):
        for pattern in ("examples/astro", "examples/astro/", "examples/*/astro.py", "examples/astro/*.py"):
            with self.subTest(pattern=pattern):
                self.save_feature(expected_surface=[pattern])
                self.put("examples/astro/astro.py", "print('v3')\n")
                self.assertTrue(self.check()["ok"], pattern)
        self.save_feature(expected_surface=["examples/ast"])
        self.assertIn("SCOPE_OUTSIDE_SURFACE", self.codes(self.check(), ok=False))

    def test_paths_with_spaces(self):
        self.put("odd dir/file name.py", "x\n")
        outside = [f["path"] for f in self.check()["findings"] if f["code"] == "SCOPE_OUTSIDE_SURFACE"]
        self.assertEqual(outside, ["odd dir/file name.py"])

    def test_base_revision_includes_committed_session_work(self):
        start = self.git("rev-parse", "HEAD")
        self.put("src/billing.py", "# committed outside scope\n")
        self.commit_all()
        self.assertTrue(self.check()["ok"], "HEAD-only view should not see committed work")
        self.assertIn("SCOPE_OUTSIDE_SURFACE", self.codes(self.check(base=start), ok=False))

    # evidence ------------------------------------------------------------
    def test_active_feature_reports_pending_claims_without_failing(self):
        result = self.check()
        self.assertTrue(result["ok"])
        self.assertEqual(self.codes(result).count("CLAIM_PENDING"), len(self.feature["claims"]))

    def test_ready_feature_without_evidence_fails(self):
        self.save_feature(state="ready_for_verification")
        self.commit_all()
        result = self.check()
        self.assertFalse(result["ok"])
        self.assertEqual(self.codes(result, ok=False).count("CLAIM_UNPROVEN"), len(self.feature["claims"]))

    def test_ready_feature_with_passing_evidence_at_head_passes(self):
        self.save_feature(state="ready_for_verification")
        self.commit_all()
        self.record()
        result = self.check()
        self.assertTrue(result["ok"], result)
        self.assertEqual(self.codes(result).count("CLAIM_PROVEN"), len(self.feature["claims"]))

    def test_one_missing_or_failing_claim_blocks_completion(self):
        self.save_feature(state="ready_for_verification")
        self.commit_all()
        self.record(claims=self.feature["claims"][:-1])
        self.assertEqual(self.codes(self.check(), ok=False), ["CLAIM_UNPROVEN"])
        self.record(result="fail")
        self.assertFalse(self.check()["ok"])

    def test_latest_entry_per_claim_wins(self):
        self.save_feature(state="ready_for_verification")
        self.commit_all()
        head = self.git("rev-parse", "HEAD")
        claim = self.feature["claims"][0]
        entries = [{"claim": c, "command": "t", "result": "pass", "revision": head} for c in self.feature["claims"]]
        entries.append({"claim": claim, "command": "t", "result": "fail", "revision": head})
        self.put(".harness/evidence.json", json.dumps(entries))
        self.assertEqual(self.codes(self.check(), ok=False), ["CLAIM_UNPROVEN"])

    def test_stale_evidence_from_older_revision_fails(self):
        self.save_feature(state="ready_for_verification")
        self.commit_all()
        old = self.git("rev-parse", "HEAD")
        self.put("examples/astro/astro.py", "print('changed after tests')\n")
        self.commit_all()
        self.record(revision=old)
        result = self.check()
        self.assertFalse(result["ok"])
        self.assertIn("project files changed since: examples/astro/astro.py", json.dumps(result))

    def test_abbreviated_revision_is_accepted_but_not_too_short(self):
        self.save_feature(state="ready_for_verification")
        self.commit_all()
        head = self.git("rev-parse", "HEAD")
        self.record(revision=head[:7])
        self.assertTrue(self.check()["ok"])
        self.record(revision=head[:4])
        self.assertFalse(self.check()["ok"])

    def test_uncommitted_edits_after_evidence_make_it_stale(self):
        self.save_feature(state="ready_for_verification")
        self.commit_all()
        self.record()
        self.put("examples/astro/astro.py", "print('edited after evidence')\n")
        result = self.check()
        self.assertFalse(result["ok"])
        self.assertIn("uncommitted work", json.dumps(result))

    def test_paraphrased_claim_is_rejected(self):
        self.record(claims=["conflicts return 409"])
        self.assertIn("EVIDENCE_UNKNOWN_CLAIM", self.codes(self.check(), ok=False))

    def test_malformed_evidence_fails(self):
        for raw in ("{", "{}", '[{"claim": "x"}]', '[{"claim": "x", "command": "c", "result": "maybe", "revision": "abc1234"}]'):
            with self.subTest(raw=raw):
                self.put(".harness/evidence.json", raw)
                self.assertIn("EVIDENCE_INVALID", self.codes(self.check(), ok=False))

    # safety and CLI ------------------------------------------------------
    def test_not_a_git_repository_fails_clearly(self):
        shutil.rmtree(self.root / ".git")
        self.assertEqual(self.codes(self.check(), ok=False), ["SESSION_GIT_UNAVAILABLE"])

    def test_invalid_ledger_skips_session_checks(self):
        self.save_feature(expected_surface=["../outside"])
        self.assertIn("SESSION_SKIPPED", self.codes(self.check(), ok=False))

    def test_verification_string_is_never_executed(self):
        self.save_feature(verification="rm -rf / --do-not-run")
        real = subprocess.run

        def only_git(command, *args, **kwargs):
            if command[0] != "git":
                raise AssertionError(f"executed {command}")
            return real(command, *args, **kwargs)

        with patch("subprocess.run", side_effect=only_git):
            self.check()

    def test_repository_fsmonitor_hook_is_not_run(self):
        marker = self.root.parent / f"{self.root.name}-fsmonitor-ran"
        hook = self.root / "hook.sh"
        hook.write_text(f"#!/bin/sh\ntouch '{marker}'\n")
        hook.chmod(0o755)
        self.git("add", "hook.sh")
        self.git("config", "core.fsmonitor", str(hook))
        self.check()
        self.assertFalse(marker.exists(), "session check must not run repository-configured hooks")

    def test_cli_exit_codes_summary_and_no_mutation(self):
        script = str(ROOT / "scripts/harness_check.py")
        self.put("src/billing.py", "# outside\n")
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}
        text = subprocess.run([sys.executable, script, "--root", str(self.root), "--session"],
                              capture_output=True, text=True)
        self.assertEqual(text.returncode, 1, text.stderr)
        self.assertIn("FAIL SCOPE_OUTSIDE_SURFACE src/billing.py", text.stdout)
        self.assertIn("Session: 1 file(s) outside scope", text.stdout)
        as_json = subprocess.run([sys.executable, script, "--root", str(self.root), "--session", "--format", "json"],
                                 capture_output=True, text=True)
        self.assertFalse(json.loads(as_json.stdout)["ok"])
        after = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before, after)
        self.git("checkout", "--", "src/billing.py")
        clean = subprocess.run([sys.executable, script, "--root", str(self.root), "--session"],
                               capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0, clean.stdout)

    def test_cli_rejects_base_without_session_and_option_like_base(self):
        script = str(ROOT / "scripts/harness_check.py")
        for extra in (["--base", "main"], ["--session", "--base=--output=/tmp/x"]):
            with self.subTest(extra=extra):
                result = subprocess.run([sys.executable, script, "--root", str(self.root), *extra],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
