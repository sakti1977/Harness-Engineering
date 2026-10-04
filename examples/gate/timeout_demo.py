"""A lost response, with and without the attempt gate.

The work already finished; its response never arrived. A scripted agent stands in for the behavior
seen in a real incident: it reads every error correctly ("timeout", "record locked") and runs the
task again anyway. Run it once with nothing between the agent and the test environment, then once
through the gate. No model, network or project commands; everything runs in a temporary directory.

The counts are exact for this simulation. They are not a measurement of a real agent, and they do
not price the extra executions (wall-clock time, load on the environment, output tokens).
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("harness_attempt", ROOT / "scripts/harness_attempt.py")
attempt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attempt)

REVIEW = "review-17"
RETRY_CAP = 4   # the unguarded loop is unbounded in practice; a person stepped in after four runs


class LockedRecord(Exception):
    pass


class TestEnvironment:
    """The system under test. Every run writes a record and takes a lock, so repeating a run is visible."""

    def __init__(self, can_look_up=True):
        self.records, self.locked, self.executions, self.failed = [], False, 0, 0
        self.can_look_up = can_look_up

    def run_suite(self):
        self.executions += 1
        self.records.append(f"coverage run {len(self.records) + 1} for {REVIEW}")   # the side effect comes first
        if self.locked:
            self.failed += 1
            raise LockedRecord("record is locked by an earlier run")
        self.locked = True                                   # the first run leaves its lock behind...
        raise TimeoutError("the response never arrived")     # ...and finishes, but nobody hears about it

    def has_run(self):
        """What a probe can see: the effect itself, if the environment lets anyone look."""
        return (len(self.records) > 0) if self.can_look_up else None


def without_the_gate(out):
    env = TestEnvironment()
    out("WITHOUT THE GATE: the agent calls the runner directly")
    for number in range(1, RETRY_CAP + 1):
        try:
            env.run_suite()
        except TimeoutError as error:
            out(f"  attempt {number}: suite executed, {error}; agent: 'timeout, retrying'")
        except LockedRecord as error:
            out(f"  attempt {number}: suite executed again, {error}; agent: 'record locked, retrying'")
    out(f"  a person steps in: {len(env.records)} records exist and the task finished at attempt 1")
    return {"executions": env.executions, "records": len(env.records), "failed": env.failed, "confirmed": False}


def with_the_gate(out, root, env, title):
    key = attempt.key_for(REVIEW, "smoke", "staging", "app@abc123", "tests@def456")
    out(title)

    def call_run():
        return attempt.execute(root, key, ["run_suite", REVIEW], env.run_suite, actor="coverage-agent")

    first = call_run()
    out(f"  attempt 1: no response ({first.detail}); the outcome is recorded as unknown, not as a failure")
    try:
        call_run()                                           # the same instinct as before
    except attempt.Refused as error:
        out(f"  attempt 2: REFUSED {error.codes[0]}: the agent is not allowed to run it again")
    settled = attempt.reconcile(root, key, env.has_run, actor="coverage-agent")
    out(f"  reconcile: {settled.state.upper()} ({settled.detail})")
    confirmed = settled.state == "complete"
    if settled.state == "needs_inspection":
        out("  the agent stops and reports; it cannot settle this one")
        done = attempt.resolve(root, key, "complete", actor="sakti", role="operator", reason="saw the run in the dashboard")
        out(f"  operator sakti: {done.state.upper()} ({done.detail})")
        confirmed = True
    replay = attempt.execute(root, key, ["run_suite", REVIEW], env.run_suite, actor="coverage-agent")
    out(f"  next run request: {replay.status.upper()}: the finished run is returned, nothing executes")
    return {"executions": env.executions, "records": len(env.records), "failed": env.failed,
            "confirmed": confirmed and replay.status == "replayed"}


def main():
    lines = []
    out = lambda text="": (print(text), lines.append(text))
    with TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        before = without_the_gate(out)
        out()
        after = with_the_gate(out, Path(temp) / "probe-works", TestEnvironment(), "WITH THE GATE: a probe can see the effect")
        out()
        blind = with_the_gate(out, Path(temp) / "probe-blind", TestEnvironment(can_look_up=False),
                              "WITH THE GATE, nobody can look: the decision goes to a person")
        ledger = (Path(temp) / "probe-works/.harness/attempts.jsonl").read_text(encoding="utf-8").splitlines()
        verified = attempt.load(Path(temp) / "probe-works")[2] == []
    out()
    out(f"{'':<28}{'no gate':>9}{'gate':>9}{'gate, blind':>13}")
    for label, field in (("suite executions", "executions"), ("records created", "records"),
                         ("failed attempts", "failed")):
        out(f"{label:<28}{before[field]:>9}{after[field]:>9}{blind[field]:>13}")
    yes = lambda value: "yes" if value else "no"
    out(f"{'task confirmed finished':<28}{yes(before['confirmed']):>9}{yes(after['confirmed']):>9}{yes(blind['confirmed']):>13}")
    out(f"\nLedger: {len(ledger)} hash-chained entries, verified: {yes(verified)}")
    ok = (before["executions"] == RETRY_CAP and before["records"] == RETRY_CAP and not before["confirmed"]
          and after["executions"] == 1 and after["records"] == 1 and after["failed"] == 0 and after["confirmed"]
          and blind["executions"] == 1 and blind["records"] == 1 and blind["confirmed"] and verified)
    out("\nTIMEOUT DEMO PASSED: the work ran once, left one record, and the unknown outcome was settled, not retried."
        if ok else "\nTIMEOUT DEMO FAILED: unexpected behavior.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
