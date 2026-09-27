"""The feature ledger as a gate: transition policy, independent verification, audit log."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load("harness_check")
mover = load("harness_transition")
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
LOG = ".harness/feature-log.jsonl"


@unittest.skipUnless(shutil.which("git"), "git is required for transitions")
class TransitionGate(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in checker.CORE_FILES:
            self.put(name, (ROOT / name).read_text())
        feature = json.loads((ROOT / ".harness/feature.json").read_text())
        feature["state"] = "planned"
        self.put(".harness/feature.json", json.dumps(feature, indent=2))
        self.claims = feature["claims"]
        self.put("examples/astro/astro.py", "v1\n")
        self.put("src/billing.py", "unrelated\n")
        self.git("init", "-q", "-b", "main")
        self.commit()

    # helpers -------------------------------------------------------------
    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True, env=GIT_ENV).stdout.strip()

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "step")

    def move(self, to, actor="copilot-agent", role="worker", reason="test"):
        return mover.transition(self.root, to, actor, role, reason)

    def ok(self, to, **kwargs):
        ok, messages = self.move(to, **kwargs)
        self.assertTrue(ok, messages)
        self.commit()

    def snapshot(self):
        return {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}

    def refused(self, to, expect, **kwargs):
        before = self.snapshot()
        ok, messages = self.move(to, **kwargs)
        self.assertFalse(ok)
        self.assertIn(expect, "\n".join(messages))
        self.assertEqual(before, self.snapshot(), "a refused transition must not change any file")

    def record_evidence(self, claims=None):
        head = self.git("rev-parse", "HEAD")
        self.put(".harness/evidence.json", json.dumps(
            [{"claim": c, "command": "python3 -m unittest", "result": "pass", "revision": head}
             for c in (self.claims if claims is None else claims)]))

    def state(self):
        return json.loads((self.root / ".harness/feature.json").read_text())["state"]

    def codes(self):
        return [f["code"] for f in checker.inspect(self.root)["findings"] if not f["ok"]]

    def to_ready(self):
        self.ok("planned", actor="sakti", role="planner")
        self.ok("active")
        self.put("examples/astro/astro.py", "v2 with transaction\n")
        self.commit()
        self.ok("ready_for_verification")

    # the happy path ------------------------------------------------------
    def test_full_lifecycle_with_independent_verifier(self):
        self.to_ready()
        self.record_evidence()
        self.commit()
        self.ok("passing", actor="sakti", role="verifier", reason="all four claims observed")
        self.assertEqual(self.state(), "passing")
        result = checker.inspect(self.root)
        self.assertTrue(result["ok"], result)
        log = [json.loads(line) for line in (self.root / LOG).read_text().splitlines()]
        self.assertEqual([(e["from"], e["to"], e["role"]) for e in log], [
            ("none", "planned", "planner"), ("planned", "active", "worker"),
            ("active", "ready_for_verification", "worker"),
            ("ready_for_verification", "passing", "verifier")])
        self.assertEqual(log[-1]["claims"], self.claims)
        self.assertTrue(all(e["revision"] and e["at"].endswith("Z") for e in log))

    # policy --------------------------------------------------------------
    def test_self_attested_passing_without_log_is_rejected(self):
        feature = json.loads((self.root / ".harness/feature.json").read_text())
        self.put(".harness/feature.json", json.dumps(dict(feature, state="passing")))
        self.assertIn("PASSING_WITHOUT_LOG", self.codes())

    def test_genesis_must_match_current_state(self):
        self.refused("active", "No transition log yet")

    def test_skipping_states_is_refused(self):
        self.ok("planned", actor="sakti", role="planner")
        self.ok("active")
        self.refused("passing", "TRANSITION_NOT_ALLOWED", actor="sakti", role="verifier")

    def test_worker_cannot_approve_its_own_work(self):
        self.to_ready()
        self.record_evidence()
        self.commit()
        self.refused("passing", "TRANSITION_ROLE_DENIED", role="worker")

    def test_verifier_must_be_independent_of_requester(self):
        self.to_ready()
        self.record_evidence()
        self.commit()
        self.refused("passing", "TRANSITION_NOT_INDEPENDENT", actor="copilot-agent", role="verifier")

    # gates ---------------------------------------------------------------
    def test_scope_gate_names_out_of_scope_work_since_activation(self):
        self.ok("planned", actor="sakti", role="planner")
        self.ok("active")
        self.put("src/billing.py", "agent refactored this too\n")
        self.commit()
        self.refused("ready_for_verification", "src/billing.py")

    def test_verification_request_needs_a_complete_proof_matrix(self):
        self.ok("planned", actor="sakti", role="planner")
        self.ok("active")
        matrix = (self.root / "docs/proof-matrix.md").read_text()
        claim = "coaching started before a birth-time correction is not stored against the old chart"
        # Weaken only the Tested boundary column (the last occurrence on the row).
        gapped = "\n".join("entry |".join(line.rsplit("entry, persistence, concurrency |", 1))
                           if line.startswith(f"| {claim}") else line for line in matrix.splitlines())
        self.put("docs/proof-matrix.md", gapped)
        self.save_scope_and_commit()
        self.refused("ready_for_verification", "PROOF_BOUNDARY_GAP")

    def save_scope_and_commit(self):
        feature = json.loads((self.root / ".harness/feature.json").read_text())
        feature["expected_surface"] = feature["expected_surface"] + ["docs/proof-matrix.md"]
        self.put(".harness/feature.json", json.dumps(feature, indent=2))
        self.commit()

    def test_evidence_gate_requires_every_claim(self):
        self.to_ready()
        self.refused("passing", "CLAIM_UNPROVEN", actor="sakti", role="verifier")
        self.record_evidence(claims=self.claims[:2])
        self.commit()
        self.refused("passing", "CLAIM_UNPROVEN", actor="sakti", role="verifier")

    def test_evidence_gate_rejects_uncommitted_work(self):
        self.to_ready()
        self.record_evidence()
        self.commit()
        self.put("examples/astro/astro.py", "edited after evidence\n")
        self.refused("passing", "uncommitted work", actor="sakti", role="verifier")

    def test_verifier_can_send_work_back(self):
        self.to_ready()
        self.ok("active", actor="sakti", role="verifier", reason="E2E check failed")
        self.assertEqual(self.state(), "active")
        self.assertTrue(checker.inspect(self.root)["ok"])

    # audit log integrity -------------------------------------------------
    def test_hand_edited_state_is_detected(self):
        self.to_ready()
        feature = json.loads((self.root / ".harness/feature.json").read_text())
        self.put(".harness/feature.json", json.dumps(dict(feature, state="passing")))
        self.assertIn("STATE_MISMATCH", self.codes())

    def test_edited_log_entry_breaks_the_chain(self):
        self.to_ready()
        lines = (self.root / LOG).read_text().splitlines()
        lines[0] = lines[0].replace('"reason":"test"', '"reason":"rewritten"')
        self.put(LOG, "\n".join(lines) + "\n")
        self.assertIn("LOG_CHAIN_BROKEN", self.codes())

    def test_forged_entry_with_valid_hash_is_still_checked_against_policy(self):
        self.ok("planned", actor="sakti", role="planner")
        self.ok("active")
        lines = (self.root / LOG).read_text().splitlines()
        forged = {"seq": len(lines) + 1, "at": "2026-01-01T00:00:00Z", "feature": "jyotish-profile-coaching",
                  "from": "active", "to": "passing", "actor": "copilot-agent", "role": "verifier",
                  "revision": self.git("rev-parse", "HEAD"), "reason": "trust me",
                  "prev": checker.line_hash(lines[-1]), "claims": self.claims}
        self.put(LOG, "\n".join(lines + [json.dumps(forged)]) + "\n")
        feature = json.loads((self.root / ".harness/feature.json").read_text())
        self.put(".harness/feature.json", json.dumps(dict(feature, state="passing")))
        self.assertIn("TRANSITION_NOT_ALLOWED", self.codes())

    def test_rewriting_committed_history_is_detected(self):
        self.to_ready()
        # Rebuild a fully consistent but different history (valid hashes) over the committed one.
        entries = [json.loads(line) for line in (self.root / LOG).read_text().splitlines()][:2]
        entries[1]["actor"] = "someone-else"
        lines = []
        for entry in entries:
            entry["prev"] = checker.line_hash(lines[-1]) if lines else ""
            lines.append(json.dumps(entry, sort_keys=True, separators=(",", ":")))
        self.put(LOG, "\n".join(lines) + "\n")
        feature = json.loads((self.root / ".harness/feature.json").read_text())
        self.put(".harness/feature.json", json.dumps(dict(feature, state="active")))
        self.assertIn("LOG_REWRITTEN", self.codes())

    # invalidation across sessions ----------------------------------------
    def test_passing_goes_stale_when_files_change_and_can_be_reopened(self):
        self.to_ready()
        self.record_evidence()
        self.commit()
        self.ok("passing", actor="sakti", role="verifier")
        self.put("examples/astro/astro.py", "a later session changed this\n")
        self.commit()
        self.assertIn("PASSING_STALE", self.codes())
        self.ok("active", actor="sakti", role="verifier", reason="changed after verification")
        self.assertTrue(checker.inspect(self.root)["ok"])

    def test_passing_goes_stale_when_claims_change(self):
        self.to_ready()
        self.record_evidence()
        self.commit()
        self.ok("passing", actor="sakti", role="verifier")
        feature = json.loads((self.root / ".harness/feature.json").read_text())
        feature["claims"].append("every remedy includes a behavioural practice")
        self.put(".harness/feature.json", json.dumps(feature, indent=2))
        self.assertIn("PASSING_STALE", self.codes())

    # CLI -----------------------------------------------------------------
    def test_cli_exit_codes(self):
        script = [sys.executable, str(ROOT / "scripts/harness_transition.py"), "--root", str(self.root)]
        good = subprocess.run(script + ["--to", "planned", "--actor", "sakti", "--role", "planner",
                                        "--reason", "adopt ledger"], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertIn("none -> planned recorded", good.stdout)
        bad = subprocess.run(script + ["--to", "passing", "--actor", "bot", "--role", "worker",
                                       "--reason", "done"], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("TRANSITION_NOT_ALLOWED", bad.stdout)
        blank = subprocess.run(script + ["--to", "active", "--actor", " ", "--role", "worker",
                                         "--reason", "x"], capture_output=True, text=True)
        self.assertEqual(blank.returncode, 2)


if __name__ == "__main__":
    unittest.main()
