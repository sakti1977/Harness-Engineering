"""The attempt gate: work with side effects runs at most once per intent, and an unknown outcome stops it."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/harness_attempt.py"
spec = importlib.util.spec_from_file_location("harness_attempt", SCRIPT)
attempt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attempt)

OP = {"actor": "sakti", "role": "operator"}


class Died(BaseException):
    """The caller was killed mid-run; not an Exception, so nothing records an outcome."""


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runs = 0

    def work(self, outcome="ok"):
        """A runner whose side effect is counted. 'lost' does the work, then the response never arrives."""
        def fn():
            self.runs += 1
            if outcome == "lost":
                raise TimeoutError("no response")
            if outcome == "fail":
                raise RuntimeError("test environment refused")
            if outcome == "die":
                raise Died()
            return {"records": 1}
        return fn

    def run_it(self, key="k", payload="suite-a", outcome="ok", actor="agent", **options):
        return attempt.execute(self.root, key, payload, self.work(outcome), actor=actor, **options)

    def refused(self, call, *codes):
        with self.assertRaises(attempt.Refused) as caught:
            call()
        self.assertEqual(caught.exception.codes, sorted(codes))
        return caught.exception

    def state(self, key="k"):
        return attempt.state_of(attempt.load(self.root)[1], key)


class Identity(unittest.TestCase):
    def test_key_is_stable_and_depends_on_what_the_work_is(self):
        a = attempt.key_for("review-17", "smoke", "staging", "abc123")
        self.assertEqual(a, attempt.key_for("review-17", "smoke", "staging", "abc123"))
        self.assertNotEqual(a, attempt.key_for("review-17", "smoke", "staging", "abc124"))
        self.assertNotEqual(attempt.key_for("ab", "c"), attempt.key_for("a", "bc"))

    def test_blank_key_parts_and_unsafe_keys_are_rejected(self):
        for parts in ((), ("",), ("a", "  ")):
            with self.assertRaises(ValueError):
                attempt.key_for(*parts)
        for key in ("", "../x", "a/b", "a b", "-lead", "x" * 129):
            with self.assertRaises(ValueError):
                attempt.check_key(key)


class RunOnce(Base):
    def test_completed_work_is_replayed_not_run_again(self):
        first = self.run_it()
        self.assertEqual((first.status, first.state, self.runs), ("ran", "complete", 1))
        for _ in range(3):
            again = self.run_it()
            self.assertEqual(again.status, "replayed")
            self.assertEqual(again.result["records"], 1)
        self.assertEqual(self.runs, 1)

    def test_a_lost_response_runs_the_work_once_however_often_the_agent_retries(self):
        """The incident: the task finished, the response was lost, and every retry repeated it."""
        self.assertEqual(self.run_it(outcome="lost").status, "unknown")
        for _ in range(5):
            self.refused(lambda: self.run_it(outcome="lost"), "ATTEMPT_OUTCOME_UNKNOWN")
        self.assertEqual(self.runs, 1)

    def test_a_caller_that_dies_mid_run_leaves_the_intent_unresolved(self):
        with self.assertRaises(Died):
            self.run_it(outcome="die")
        self.assertEqual(self.state(), "submitting")
        self.refused(self.run_it, "ATTEMPT_OUTCOME_UNKNOWN")
        self.assertEqual(self.runs, 1)

    def test_a_definite_failure_may_retry_within_a_budget(self):
        for _ in range(3):
            self.assertEqual(self.run_it(outcome="fail").status, "failed")
        self.assertEqual(self.runs, 3)
        self.refused(lambda: self.run_it(outcome="fail"), "ATTEMPT_BUDGET_EXHAUSTED")
        self.assertEqual(self.runs, 3)
        attempt.resolve(self.root, "k", "rerun", reason="environment repaired", **OP)
        self.assertEqual(self.run_it().status, "ran")

    def test_a_key_cannot_be_reused_for_different_work(self):
        self.run_it(outcome="fail")
        self.refused(lambda: self.run_it(payload="suite-b"), "ATTEMPT_KEY_PAYLOAD_MISMATCH")
        self.run_it()
        self.refused(lambda: self.run_it(payload="suite-b"), "ATTEMPT_ALREADY_COMPLETE", "ATTEMPT_KEY_PAYLOAD_MISMATCH")

    def test_a_refused_start_writes_nothing(self):
        self.run_it(outcome="lost")
        before = (self.root / attempt.LEDGER).read_text(encoding="utf-8")
        self.refused(self.run_it, "ATTEMPT_OUTCOME_UNKNOWN")
        self.assertEqual((self.root / attempt.LEDGER).read_text(encoding="utf-8"), before)

    def test_concurrent_starts_run_the_work_once(self):
        """Look up then start races; the ledger lock makes it one atomic step."""
        def fn():
            self.runs += 1
            time.sleep(0.05)
            return {}

        def go(_):
            try:
                return attempt.execute(self.root, "k", "suite-a", fn, actor="agent").status
            except attempt.Refused as error:
                return error.codes[0]

        with ThreadPoolExecutor(8) as pool:
            outcomes = list(pool.map(go, range(8)))
        self.assertEqual(self.runs, 1)
        self.assertEqual(outcomes.count("ran"), 1)
        self.assertTrue(all(o in ("ran", "replayed", "ATTEMPT_OUTCOME_UNKNOWN") for o in outcomes), outcomes)
        self.assertEqual(attempt.load(self.root)[2], [])


class Preconditions(Base):
    def test_a_missing_prerequisite_refuses_before_any_work_or_intent(self):
        error = self.refused(lambda: self.run_it(preconditions={"vpn": False, "lock-clear": True}),
                             "ATTEMPT_PRECONDITION_FAILED")
        self.assertIn("vpn", str(error))
        self.assertNotIn("lock-clear", str(error))
        self.assertEqual((self.runs, self.state()), (0, None))

    def test_a_probe_that_raises_counts_as_not_met(self):
        def broken():
            raise OSError("no route to host")
        error = self.refused(lambda: self.run_it(preconditions={"vpn": broken}), "ATTEMPT_PRECONDITION_FAILED")
        self.assertIn("no route to host", str(error))

    def test_prerequisites_are_not_probed_when_the_ledger_already_decides(self):
        probes = []
        self.run_it()
        again = self.run_it(preconditions={"vpn": lambda: probes.append(1) or False})
        self.assertEqual(again.status, "replayed")
        self.run_it(key="u", outcome="lost")
        self.refused(lambda: self.run_it(key="u", preconditions={"vpn": lambda: probes.append(1) or False}),
                     "ATTEMPT_OUTCOME_UNKNOWN")
        self.assertEqual(probes, [])


class KillSwitch(Base):
    def test_stop_refuses_new_work_but_replays_finished_work(self):
        self.run_it(key="done")
        attempt.stop(self.root, actor="sakti", reason="pause")
        self.refused(lambda: self.run_it(key="new"), "ATTEMPT_KILL_SWITCH")
        self.assertEqual(self.run_it(key="done").status, "replayed")
        self.assertEqual(self.runs, 1)

    def test_only_an_operator_lifts_it(self):
        attempt.stop(self.root, actor="agent", reason="unsure")
        self.refused(lambda: attempt.go(self.root, actor="agent", role="worker", reason="resume"), "ATTEMPT_ROLE_DENIED")
        self.refused(lambda: self.run_it(), "ATTEMPT_KILL_SWITCH")
        self.assertTrue(attempt.go(self.root, reason="checked", **OP))
        self.assertEqual(self.run_it().status, "ran")
        self.assertFalse(attempt.go(self.root, reason="again", **OP))

    def test_an_unreadable_stop_file_still_stops(self):
        (self.root / ".harness").mkdir()
        (self.root / attempt.STOP_FILE).write_text("{not json", encoding="utf-8")
        self.refused(self.run_it, "ATTEMPT_KILL_SWITCH")

    def test_stop_and_go_are_in_the_ledger(self):
        attempt.stop(self.root, actor="agent", reason="unsure")
        attempt.go(self.root, reason="checked", **OP)
        events = [e["event"] for e in attempt.load(self.root)[1]]
        self.assertEqual(events, ["stop", "go"])


class Reconcile(Base):
    def lost(self):
        self.run_it(outcome="lost")

    def test_a_probe_that_finds_the_effect_completes_the_attempt(self):
        self.lost()
        self.assertEqual(attempt.reconcile(self.root, "k", lambda: True, actor="agent").state, "complete")
        self.assertEqual(self.run_it().status, "replayed")
        self.assertEqual(self.runs, 1)

    def test_a_probe_that_finds_nothing_releases_the_intent(self):
        self.lost()
        self.assertEqual(attempt.reconcile(self.root, "k", lambda: False, actor="agent").state, "released")
        self.assertEqual(self.run_it().status, "ran")
        self.assertEqual(self.runs, 2)

    def test_a_probe_that_cannot_tell_hands_the_decision_to_a_person(self):
        self.lost()
        for probe in (lambda: None, lambda: 1 / 0):
            self.assertEqual(attempt.reconcile(self.root, "k", probe, actor="agent").state, "needs_inspection")
            self.refused(self.run_it, "ATTEMPT_OUTCOME_UNKNOWN")
        self.assertEqual(self.runs, 1)

    def test_only_an_unresolved_attempt_can_be_reconciled(self):
        self.refused(lambda: attempt.reconcile(self.root, "k", lambda: True, actor="agent"), "ATTEMPT_RESOLVE_NOT_PENDING")
        self.run_it()
        self.refused(lambda: attempt.reconcile(self.root, "k", lambda: True, actor="agent"), "ATTEMPT_RESOLVE_NOT_PENDING")


class Resolve(Base):
    def test_an_independent_operator_settles_an_uncertain_attempt(self):
        self.run_it(outcome="lost")
        self.assertEqual(attempt.resolve(self.root, "k", "complete", reason="saw the records", **OP).state, "complete")
        self.run_it(key="u", outcome="lost")
        self.assertEqual(attempt.resolve(self.root, "u", "rerun", reason="nothing there", **OP).state, "released")

    def test_refusals(self):
        self.run_it(outcome="lost")
        self.refused(lambda: attempt.resolve(self.root, "k", "complete", actor="other", role="worker", reason="x"),
                     "ATTEMPT_ROLE_DENIED")
        self.refused(lambda: attempt.resolve(self.root, "k", "complete", actor="agent", role="operator", reason="x"),
                     "ATTEMPT_RESOLVE_NOT_INDEPENDENT")
        self.refused(lambda: attempt.resolve(self.root, "missing", "complete", reason="x", **OP),
                     "ATTEMPT_RESOLVE_NOT_PENDING")
        self.run_it(key="f", outcome="fail")
        self.refused(lambda: attempt.resolve(self.root, "f", "complete", reason="x", **OP), "ATTEMPT_RESOLVE_NOT_PENDING")
        with self.assertRaises(ValueError):
            attempt.resolve(self.root, "k", "maybe", reason="x", **OP)


class Ledger(Base):
    def test_every_entry_chains_to_the_one_before(self):
        self.run_it(outcome="lost")
        attempt.reconcile(self.root, "k", lambda: True, actor="agent")
        self.run_it(key="u")
        lines, entries, errors = attempt.load(self.root)
        self.assertEqual(errors, [])
        self.assertEqual([e["seq"] for e in entries], list(range(1, len(lines) + 1)))
        self.assertEqual(entries[0]["prev"], "")

    def test_an_edited_ledger_blocks_every_gate(self):
        self.run_it(key="a")
        self.run_it(key="b")
        path = self.root / attempt.LEDGER
        path.write_text(path.read_text(encoding="utf-8").replace('"actor":"agent"', '"actor":"nobody"', 1), encoding="utf-8")
        self.refused(lambda: self.run_it(key="c"), "ATTEMPT_LEDGER_INVALID")
        self.assertEqual([f.code for f in attempt.permission(self.root, "c")], ["ATTEMPT_LEDGER_INVALID"])
        self.refused(lambda: attempt.reconcile(self.root, "a", lambda: True, actor="x"), "ATTEMPT_LEDGER_INVALID")
        self.assertEqual(self.runs, 2)

    def test_garbage_in_the_ledger_is_invalid_not_a_crash(self):
        (self.root / ".harness").mkdir()
        (self.root / attempt.LEDGER).write_text("not json\n[]\n", encoding="utf-8")
        self.assertTrue(attempt.load(self.root)[2])
        self.refused(self.run_it, "ATTEMPT_LEDGER_INVALID")

    def test_a_missing_ledger_is_empty(self):
        self.assertEqual(attempt.load(self.root), ([], [], []))
        self.assertEqual(attempt.permission(self.root, "k"), [])

    def test_a_busy_ledger_fails_closed(self):
        (self.root / ".harness").mkdir()
        (self.root / attempt.LOCK_FILE).write_text("held\n", encoding="utf-8")
        with self.assertRaises(attempt.LedgerBusy):
            attempt.execute(self.root, "k", "p", self.work(), actor="agent", wait=0.05)
        self.assertEqual(self.runs, 0)

    def test_a_stale_lock_from_a_crashed_holder_is_broken(self):
        (self.root / ".harness").mkdir()
        lock = self.root / attempt.LOCK_FILE
        lock.write_text("123\n", encoding="utf-8")
        old = time.time() - attempt.STALE_LOCK_SECONDS - 5
        os.utime(lock, (old, old))
        self.assertEqual(self.run_it().status, "ran")


class CommandLine(Base):
    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def script(self, name, code):
        path = self.root / name
        path.write_text(code, encoding="utf-8")
        return [sys.executable, str(path)]

    def counted(self, tail=""):
        """A command whose side effect appends one line to a file, so reruns are visible."""
        return self.script("work.py", "import pathlib\nopen(pathlib.Path(__file__).with_name('effects.txt'), 'a').write('x\\n')\n"
                                      "print('suite ran')\n" + tail)

    def effects(self):
        path = self.root / "effects.txt"
        return len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0

    def quoted(self, command):
        return " ".join(f'"{part}"' for part in command)

    def test_run_saves_output_and_replays_instead_of_rerunning(self):
        command = self.counted()
        first = self.cli("run", "--key", "k", "--actor", "agent", "--", *command)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertIn("OK key=k exit=0", first.stdout)
        self.assertIn("suite ran", first.stdout)
        self.assertEqual((self.root / ".harness/attempts/k.out").read_text(encoding="utf-8").strip(), "suite ran")
        again = self.cli("run", "--key", "k", "--actor", "agent", "--", *command)
        self.assertEqual(again.returncode, 0)
        self.assertIn("ALREADY DONE", again.stdout)
        self.assertNotIn("suite ran", again.stdout)
        self.assertEqual(self.effects(), 1)

    def test_a_failing_command_exits_1_and_is_retryable_within_budget(self):
        command = self.counted("raise SystemExit(7)\n")
        result = self.cli("run", "--key", "k", "--actor", "agent", "--", *command)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAILED key=k exit=7", result.stdout)
        self.cli("run", "--key", "k", "--actor", "agent", "--", *command)
        self.assertEqual(self.effects(), 2)

    def test_a_timeout_is_unknown_and_blocks_the_retry_until_reconciled(self):
        command = self.counted("import time\ntime.sleep(30)\n")
        lost = self.cli("run", "--key", "k", "--actor", "agent", "--timeout", "2", "--", *command)
        self.assertEqual(lost.returncode, 3, lost.stdout + lost.stderr)
        self.assertIn("Do NOT run it again", lost.stdout)
        retry = self.cli("run", "--key", "k", "--actor", "agent", "--timeout", "2", "--", *command)
        self.assertEqual(retry.returncode, 1)
        self.assertIn("REFUSED ATTEMPT_OUTCOME_UNKNOWN", retry.stdout)
        self.assertEqual(self.effects(), 1)
        self.assertIn("decide before running again", self.cli("status").stdout)
        probe = self.script("probe.py", "import pathlib, sys\n"
                                        "sys.exit(0 if pathlib.Path(__file__).with_name('effects.txt').exists() else 1)\n")
        done = self.cli("reconcile", "--key", "k", "--actor", "agent", "--probe", self.quoted(probe))
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("COMPLETE", done.stdout)
        self.assertIn("ALREADY DONE", self.cli("run", "--key", "k", "--actor", "agent", "--timeout", "2", "--", *command).stdout)
        self.assertEqual(self.effects(), 1)

    def test_reconcile_without_a_probe_asks_for_a_person(self):
        self.cli("run", "--key", "k", "--actor", "agent", "--timeout", "1", "--", *self.script("slow.py", "import time\ntime.sleep(30)\n"))
        result = self.cli("reconcile", "--key", "k", "--actor", "agent")
        self.assertEqual(result.returncode, 3)
        self.assertIn("NEEDS_INSPECTION", result.stdout)
        refused = self.cli("resolve", "--key", "k", "--verdict", "rerun", "--actor", "agent", "--role", "operator", "--reason", "x")
        self.assertIn("ATTEMPT_RESOLVE_NOT_INDEPENDENT", refused.stdout)
        settled = self.cli("resolve", "--key", "k", "--verdict", "rerun", "--actor", "sakti", "--role", "operator", "--reason", "checked")
        self.assertEqual(settled.returncode, 0, settled.stdout)

    def test_a_failing_precondition_refuses_and_runs_nothing(self):
        command = self.counted()
        failing = self.quoted(self.script("no.py", "raise SystemExit(1)\n"))
        result = self.cli("run", "--key", "k", "--actor", "agent", "--precondition", f"vpn={failing}", "--", *command)
        self.assertEqual(result.returncode, 1)
        self.assertIn("ATTEMPT_PRECONDITION_FAILED: vpn", result.stdout)
        self.assertEqual(self.effects(), 0)

    def test_kill_switch_from_the_command_line(self):
        command = self.counted()
        self.assertEqual(self.cli("stop", "--actor", "agent", "--reason", "unsure").returncode, 0)
        self.assertIn("ATTEMPT_KILL_SWITCH", self.cli("run", "--key", "k", "--actor", "agent", "--", *command).stdout)
        self.assertEqual(self.cli("go", "--actor", "agent", "--role", "worker", "--reason", "x").returncode, 1)
        self.assertEqual(self.cli("go", "--actor", "sakti", "--role", "operator", "--reason", "ok").returncode, 0)
        self.assertEqual(self.cli("run", "--key", "k", "--actor", "agent", "--", *command).returncode, 0)

    def test_usage_errors_exit_2_and_run_nothing(self):
        for args in (("run", "--key", "../x", "--actor", "a", "--", "echo"), ("run", "--key", "k", "--actor", " ", "--", "echo"),
                     ("stop", "--actor", "a", "--reason", ""), ("run", "--key", "k", "--actor", "a")):
            self.assertEqual(self.cli(*args).returncode, 2, args)
        self.assertFalse((self.root / attempt.LEDGER).exists())

    def test_key_command_is_stable(self):
        first = self.cli("key", "review-17", "smoke").stdout.strip()
        self.assertEqual(first, attempt.key_for("review-17", "smoke"))
        self.assertEqual(first, self.cli("key", "review-17", "smoke").stdout.strip())

    def test_status_of_an_empty_project(self):
        out = self.cli("status")
        self.assertEqual(out.returncode, 0)
        self.assertIn("kill switch: off", out.stdout)
        self.assertIn("verified, 0 intent(s)", out.stdout)


class Demo(unittest.TestCase):
    def test_the_timeout_demo_passes(self):
        done = subprocess.run([sys.executable, "-m", "examples.gate.timeout_demo"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("TIMEOUT DEMO PASSED", done.stdout)


class RecordedFacts(Base):
    def test_the_ledger_records_who_what_and_when_without_the_command_text(self):
        self.run_it(payload=["python3", "-c", "secret-token-123"])
        text = (self.root / attempt.LEDGER).read_text(encoding="utf-8")
        self.assertNotIn("secret-token-123", text)
        entry = json.loads(text.splitlines()[0])
        self.assertEqual((entry["event"], entry["state"], entry["actor"]), ("submit", "submitting", "agent"))
        self.assertEqual(len(entry["payload"]), 64)


if __name__ == "__main__":
    unittest.main()
