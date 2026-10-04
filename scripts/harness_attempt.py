"""Run work with side effects at most once per intent, and stop when its outcome is unknown.

A timeout is an observation, not an outcome. "The work never ran" and "the work finished but its
response was lost" look identical to an agent, and only the first justifies running it again. An
agent that understands the error text still repeats the work, because understanding does not
constrain the next action. This gate keeps the difference outside the model: the executor writes
the intent to a hash-chained ledger (``.harness/attempts.jsonl``) before it acts, and refuses to
start the same intent again until its outcome is known.

States of one intent (identified by a key derived from what the work is, never from when it ran):
  submitting         intent written, no outcome recorded (still running, or its caller died)
  complete           finished; running it again would repeat its side effects
  failed             the work reported a definite failure; a bounded retry is allowed
  unknown            timed out; the work may have finished. Never run again until reconciled
  needs_inspection   reconciliation could not tell; a person decides
  released           reconciled or resolved as safe to run again

Commands (python3 scripts/harness_attempt.py [--root DIR] COMMAND ...):
  run        run one command under an intent key (the only command that executes anything)
  status     show every intent, the kill switch and whether the ledger verifies
  reconcile  ask a probe whether the effect exists: complete, safe to rerun, or needs inspection
  resolve    an operator, who did not start the attempt, settles an uncertain one
  stop / go  kill switch: refuse all new work / let it resume (operator only)
  key        derive a stable key from the parts that identify the work

The roles are labels. What enforces them is the authority policy: keep the ledger and the stop
file out of the agent's write permissions (docs/attempts.md).
"""
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time

LEDGER = ".harness/attempts.jsonl"
STOP_FILE = ".harness/STOP"
LOCK_FILE = ".harness/attempts.lock"
OUTPUT_DIR = ".harness/attempts"
KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
EVENTS = {"submit", "finish", "fail", "lose", "reconcile", "resolve", "stop", "go"}
STATES = {"submitting", "complete", "failed", "unknown", "needs_inspection", "released"}
NEEDS_DECISION = ("submitting", "unknown", "needs_inspection")
DEFAULT_MAX_FAILURES = 3
STALE_LOCK_SECONDS = 60
OPERATOR = "operator"


class Finding(NamedTuple):
    code: str
    detail: str


class Refused(Exception):
    """The gate refused. ``findings`` says why; nothing was written."""

    def __init__(self, findings):
        self.findings = list(findings)
        super().__init__("; ".join(f"{f.code}: {f.detail}" for f in self.findings))

    @property
    def codes(self):
        return sorted({f.code for f in self.findings})


class LedgerBusy(RuntimeError):
    """Another process holds the ledger lock. Fail closed: do not run the work unrecorded."""


@dataclass
class Result:
    status: str           # go | ran | replayed | failed | unknown
    key: str
    state: str
    result: dict = field(default_factory=dict)
    detail: str = ""


# ---- identity -----------------------------------------------------------------------------
def digest(*parts):
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()


def key_for(*parts):
    """A stable key from what the work is (review, suite, environment, commit), not when it ran.

    A new key on every retry defeats the purpose: the same intended work must keep its key.
    """
    parts = [str(p) for p in parts]
    if not parts or any(not p.strip() for p in parts):
        raise ValueError("a key needs one or more non-blank parts")
    return digest(*parts)[:24]


def payload_digest(payload):
    """Bind a key to the work it was first used for. Accepts a string or a list of strings (an argv)."""
    if payload is None:
        return None
    parts = payload if isinstance(payload, (list, tuple)) else [payload]
    return digest(*[str(p) for p in parts])


def check_key(key):
    if not isinstance(key, str) or not KEY_PATTERN.match(key):
        raise ValueError("key must be 1-128 characters: letters, digits, dot, underscore, hyphen")
    return key


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- the ledger ---------------------------------------------------------------------------
def _line(entry):
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))


def _hash(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def _read_text(path):
    for attempt in range(5):  # Windows can refuse a read while another process replaces the file
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.02)


def _atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", text=True)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.replace(tmp, path)


def load(root):
    """Return (lines, entries, errors). A missing ledger is empty; a damaged one reports errors."""
    root = Path(root).resolve()
    path = root / LEDGER
    if path.exists() and not path.resolve().is_relative_to(root):
        return [], [], ["ledger resolves outside the project"]
    text = _read_text(path)
    lines = text.rstrip("\n").split("\n") if text.strip() else []
    entries, errors = [], []
    previous = ""
    for number, line in enumerate(lines, 1):
        try:
            entry = json.loads(line)
        except ValueError:
            errors.append(f"ledger line {number}: not JSON")
            continue
        if not isinstance(entry, dict):
            errors.append(f"ledger line {number}: not an object")
            continue
        entries.append(entry)
        for name in ("seq", "at", "event", "key", "state", "actor", "prev"):
            if name not in entry:
                errors.append(f"ledger line {number}: missing {name}")
        if entry.get("seq") != number:
            errors.append(f"ledger line {number}: seq is {entry.get('seq')!r}")
        if entry.get("event") not in EVENTS:
            errors.append(f"ledger line {number}: unknown event {entry.get('event')!r}")
        if entry.get("state") not in STATES | {""}:
            errors.append(f"ledger line {number}: unknown state {entry.get('state')!r}")
        if entry.get("prev") != previous:
            errors.append(f"ledger line {number}: hash chain broken (the ledger was edited)")
        previous = _hash(line)
    return lines, entries, errors


def _append(root, lines, event, key, state, actor, role, **extra):
    entry = {"seq": len(lines) + 1, "at": _now(), "event": event, "key": key, "state": state,
             "actor": actor, "role": role, "prev": _hash(lines[-1]) if lines else ""}
    entry.update({name: value for name, value in extra.items() if value not in (None, "", {})})
    _atomic_write(root / LEDGER, "\n".join(lines + [_line(entry)]) + "\n")
    return entry


@contextmanager
def _locked(root, wait=10.0):
    """One writer at a time. Creating the lock file is atomic, so look-up-then-start cannot race."""
    path = root / LOCK_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + wait
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except (FileExistsError, PermissionError):
            try:
                if time.time() - path.stat().st_mtime > STALE_LOCK_SECONDS:
                    path.unlink()  # a crashed holder; the lock is only held for a few milliseconds
                    continue
            except OSError:
                pass
            if time.monotonic() >= deadline:
                raise LedgerBusy("the attempt ledger is locked by another process")
            time.sleep(0.01)
    try:
        os.write(fd, f"{os.getpid()}\n".encode("ascii"))
        os.close(fd)
        yield
    finally:
        try:
            path.unlink()
        except OSError:
            pass


def state_of(entries, key):
    states = [e["state"] for e in entries if e.get("key") == key and e.get("state")]
    return states[-1] if states else None


def stop_info(root):
    """The kill switch. A stop file that exists stops everything, even one that cannot be parsed."""
    path = Path(root).resolve() / STOP_FILE
    if not path.exists():
        return None
    try:
        info = json.loads(path.read_text(encoding="utf-8"))
        return info if isinstance(info, dict) else {"reason": "unreadable stop file"}
    except (OSError, ValueError):
        return {"reason": "unreadable stop file"}


# ---- the gate -----------------------------------------------------------------------------
def _check_preconditions(preconditions):
    """name -> (ok, detail). A precondition is a boolean or a callable; an exception counts as not met."""
    results = {}
    for name, probe in (preconditions or {}).items():
        try:
            ok = bool(probe() if callable(probe) else probe)
            results[name] = (ok, "" if ok else "not met")
        except Exception as error:  # a probe that cannot answer is not a yes
            results[name] = (False, f"{type(error).__name__}: {error}")
    return results


def _failures_since_release(mine):
    count = 0
    for entry in mine:
        if entry["state"] == "released":
            count = 0
        elif entry["event"] == "fail":
            count += 1
    return count


def _decide(entries, stopped, key, payload, preconditions, max_failures):
    """Every reason this intent may not start now. Empty means go."""
    mine = [e for e in entries if e.get("key") == key]
    state = state_of(entries, key)
    findings = []
    if payload is not None and any(e.get("payload") not in (None, payload) for e in mine):
        findings.append(Finding("ATTEMPT_KEY_PAYLOAD_MISMATCH",
                                f"key {key} belongs to different work; new work needs a new key"))
    if state == "complete":
        done = [e for e in mine if e["event"] in ("finish", "resolve", "reconcile")][-1]
        findings.append(Finding("ATTEMPT_ALREADY_COMPLETE", f"key {key} completed at {done['at']}"))
    if stopped is not None:
        who = stopped.get("actor", "an operator")
        findings.append(Finding("ATTEMPT_KILL_SWITCH", f"execution stopped by {who}: {stopped.get('reason', 'no reason')}"))
    if state in NEEDS_DECISION:
        last = [e for e in mine if e["state"]][-1]
        how = {"submitting": "was started and has no recorded outcome (still running, or its caller died)",
               "unknown": "timed out and may have finished",
               "needs_inspection": "could not be reconciled"}[state]
        findings.append(Finding("ATTEMPT_OUTCOME_UNKNOWN", f"the earlier attempt of {key} {how} (since {last['at']})"))
    if state == "failed" and _failures_since_release(mine) >= max_failures:
        findings.append(Finding("ATTEMPT_BUDGET_EXHAUSTED",
                                f"{key} failed {_failures_since_release(mine)} times; more attempts need an operator"))
    for name, (ok, detail) in sorted((preconditions or {}).items()):
        if not ok:
            findings.append(Finding("ATTEMPT_PRECONDITION_FAILED", f"{name}: {detail}"))
    return findings


def permission(root, key, payload=None, preconditions=None, max_failures=DEFAULT_MAX_FAILURES):
    """Findings that forbid starting this intent now; [] means the gate would let it through."""
    root = Path(root).resolve()
    check_key(key)
    _, entries, errors = load(root)
    if errors:
        return [Finding("ATTEMPT_LEDGER_INVALID", errors[0])]
    # Prerequisites are only worth probing when nothing else already forbids the work.
    state = state_of(entries, key)
    probed = _check_preconditions(preconditions) if state in (None, "failed", "released") else {}
    return _decide(entries, stop_info(root), key, payload_digest(payload), probed, max_failures)


def begin(root, key, payload, *, actor, role="worker", preconditions=None,
          max_failures=DEFAULT_MAX_FAILURES, wait=10.0):
    """Write the intent before any side effect.

    Returns status "go" (you may start) or "replayed" (the work already completed: do not run it).
    Raises Refused when the work must not start.
    """
    root = Path(root).resolve()
    check_key(key)
    payload = payload_digest(payload)
    if payload is None:
        raise ValueError("begin needs the payload: the work this key stands for")
    _, entries, errors = load(root)
    if errors:
        raise Refused([Finding("ATTEMPT_LEDGER_INVALID", errors[0])])
    state = state_of(entries, key)
    # Probe prerequisites outside the lock, and only if the ledger does not already settle the question.
    probed = _check_preconditions(preconditions) if state in (None, "failed", "released") else {}
    with _locked(root, wait):
        lines, entries, errors = load(root)
        if errors:
            raise Refused([Finding("ATTEMPT_LEDGER_INVALID", errors[0])])
        findings = _decide(entries, stop_info(root), key, payload, probed, max_failures)
        codes = {f.code for f in findings}
        # Replaying a finished result runs nothing, so a stop does not block it. Anything else does.
        if "ATTEMPT_ALREADY_COMPLETE" in codes and codes <= {"ATTEMPT_ALREADY_COMPLETE", "ATTEMPT_KILL_SWITCH"}:
            return _replay(entries, key)
        if findings:
            raise Refused(findings)
        _append(root, lines, "submit", key, "submitting", actor, role, payload=payload)
    return Result("go", key, "submitting")


def _replay(entries, key):
    finished = [e for e in entries if e.get("key") == key and e["state"] == "complete"][-1]
    return Result("replayed", key, "complete", finished.get("result", {}), finished["at"])


def record(root, key, outcome, *, actor, role="worker", result=None, detail="", wait=10.0):
    """Record how an attempt ended: complete, failed or unknown. Only a submitted attempt can end."""
    root = Path(root).resolve()
    check_key(key)
    event, state = {"complete": ("finish", "complete"), "failed": ("fail", "failed"),
                    "unknown": ("lose", "unknown")}[outcome]
    with _locked(root, wait):
        lines, entries, errors = load(root)
        if errors:
            raise Refused([Finding("ATTEMPT_LEDGER_INVALID", errors[0])])
        if state_of(entries, key) != "submitting":
            raise ValueError(f"no submitted attempt for {key} is waiting for an outcome")
        _append(root, lines, event, key, state, actor, role, result=result, detail=detail)
    return Result(outcome if outcome != "complete" else "ran", key, state, result or {}, detail)


def execute(root, key, payload, fn, *, actor, role="worker", preconditions=None,
            max_failures=DEFAULT_MAX_FAILURES, wait=10.0):
    """begin, call fn, record. fn returns a result dict; TimeoutError means the outcome is unknown.

    Any other exception is a definite failure. The caller dying leaves the attempt submitting,
    which the gate treats like unknown.
    """
    begun = begin(root, key, payload, actor=actor, role=role, preconditions=preconditions,
                  max_failures=max_failures, wait=wait)
    if begun.status == "replayed":
        return begun
    started = time.monotonic()
    try:
        result = dict(fn() or {})
    except TimeoutError as error:
        return record(root, key, "unknown", actor=actor, role=role, result=getattr(error, "result", None),
                      detail=str(error) or "timed out", wait=wait)
    except Exception as error:  # noqa: BLE001 - every other exception is a definite failure
        return record(root, key, "failed", actor=actor, role=role, result=getattr(error, "result", None),
                      detail=f"{type(error).__name__}: {error}", wait=wait)
    result.setdefault("seconds", round(time.monotonic() - started, 2))
    return record(root, key, "complete", actor=actor, role=role, result=result, wait=wait)


# ---- reconciling and resolving -------------------------------------------------------------
def reconcile(root, key, probe, *, actor, role="worker", wait=10.0):
    """Ask a probe whether the effect exists. True: complete. False: absent, safe to run again.
    None, or a probe that raises: nobody can tell, so a person decides."""
    root = Path(root).resolve()
    check_key(key)
    with _locked(root, wait):
        lines, entries, errors = load(root)
        if errors:
            raise Refused([Finding("ATTEMPT_LEDGER_INVALID", errors[0])])
        state = state_of(entries, key)
        if state not in NEEDS_DECISION:
            raise Refused([Finding("ATTEMPT_RESOLVE_NOT_PENDING",
                                   f"{key} is {state or 'unknown to the ledger'}; there is nothing to reconcile")])
        detail = ""
        try:
            verdict = probe()
        except Exception as error:  # a probe that cannot answer is not an answer
            verdict, detail = None, f"probe failed: {type(error).__name__}: {error}"
        state = {True: "complete", False: "released"}.get(verdict, "needs_inspection")
        detail = detail or {"complete": "probe found the effect", "released": "probe found no effect",
                            "needs_inspection": "probe could not tell"}[state]
        _append(root, lines, "reconcile", key, state, actor, role, detail=detail)
    return Result(state, key, state, {}, detail)


def resolution_findings(root, key, verdict, actor, role):
    """Why an operator may not settle this attempt. [] means the resolution would be accepted."""
    root = Path(root).resolve()
    check_key(key)
    _, entries, errors = load(root)
    if errors:
        return [Finding("ATTEMPT_LEDGER_INVALID", errors[0])]
    findings = []
    if role != OPERATOR:
        findings.append(Finding("ATTEMPT_ROLE_DENIED", f"{role} may not resolve an attempt; only an {OPERATOR} may"))
    state = state_of(entries, key)
    # An operator may also grant a fresh budget to an intent that keeps failing definitely.
    if state not in NEEDS_DECISION and not (state == "failed" and verdict == "rerun"):
        findings.append(Finding("ATTEMPT_RESOLVE_NOT_PENDING",
                                f"{key} is {state or 'unknown to the ledger'}; there is nothing to resolve"))
    else:
        starters = [e for e in entries if e.get("key") == key and e["event"] == "submit"]
        if starters and starters[-1]["actor"] == actor:
            findings.append(Finding("ATTEMPT_RESOLVE_NOT_INDEPENDENT",
                                    f"{actor} started this attempt and cannot settle it"))
    return findings


def resolve(root, key, verdict, *, actor, role, reason, wait=10.0):
    """An operator who did not start the attempt settles it: complete (it did run) or rerun (it did not)."""
    if verdict not in ("complete", "rerun"):
        raise ValueError("verdict must be complete or rerun")
    root = Path(root).resolve()
    with _locked(root, wait):
        findings = resolution_findings(root, key, verdict, actor, role)
        if findings:
            raise Refused(findings)
        lines, _, _ = load(root)
        state = "complete" if verdict == "complete" else "released"
        _append(root, lines, "resolve", key, state, actor, role, detail=reason)
    return Result(state, key, state, {}, reason)


# ---- the kill switch -----------------------------------------------------------------------
def stop(root, *, actor, reason, role="worker", wait=10.0):
    """Anyone may stop. New work is refused until an operator runs go."""
    root = Path(root).resolve()
    with _locked(root, wait):
        lines, _, errors = load(root)
        if errors:
            raise Refused([Finding("ATTEMPT_LEDGER_INVALID", errors[0])])
        _atomic_write(root / STOP_FILE, json.dumps({"actor": actor, "reason": reason, "at": _now()}) + "\n")
        _append(root, lines, "stop", "", "", actor, role, detail=reason)


def go_findings(root, role):
    return [] if role == OPERATOR else [Finding("ATTEMPT_ROLE_DENIED", f"{role} may not lift the kill switch; only an {OPERATOR} may")]


def go(root, *, actor, role, reason, wait=10.0):
    root = Path(root).resolve()
    findings = go_findings(root, role)
    if findings:
        raise Refused(findings)
    with _locked(root, wait):
        lines, _, errors = load(root)
        if errors:
            raise Refused([Finding("ATTEMPT_LEDGER_INVALID", errors[0])])
        try:
            (root / STOP_FILE).unlink()
        except FileNotFoundError:
            return False
        _append(root, lines, "go", "", "", actor, role, detail=reason)
    return True


def summary(root):
    """{key: (state, last entry)} for every intent, in first-seen order."""
    _, entries, errors = load(root)
    if errors:
        return {}, errors
    keys = list(dict.fromkeys(e["key"] for e in entries if e["key"]))
    return {key: (state_of(entries, key), [e for e in entries if e["key"] == key][-1]) for key in keys}, errors


# ---- command line -------------------------------------------------------------------------
HINTS = {
    "ATTEMPT_OUTCOME_UNKNOWN": "Do not run it again. Find out what happened: python3 scripts/harness_attempt.py reconcile --key {key} "
                               "--actor NAME --probe \"COMMAND\" (COMMAND exits 0 if the effect exists, 1 if it does not). "
                               "If you cannot probe, report it: an operator settles it with resolve.",
    "ATTEMPT_KILL_SWITCH": "An operator stopped execution. Do not retry or work around it; report and wait.",
    "ATTEMPT_PRECONDITION_FAILED": "Fix the named prerequisite. Running the work again will not.",
    "ATTEMPT_BUDGET_EXHAUSTED": "Stop and report the failure. An operator can grant a fresh budget with "
                                "python3 scripts/harness_attempt.py resolve --key {key} --verdict rerun --role operator.",
    "ATTEMPT_KEY_PAYLOAD_MISMATCH": "That key is bound to different work. Derive a new key for new work.",
    "ATTEMPT_LEDGER_INVALID": "The ledger was edited or damaged. Execution stays blocked until an operator inspects it.",
}


def refusal(error, key=None):
    lines = []
    for finding in error.findings:
        lines.append(f"REFUSED {finding.code}: {finding.detail}")
        hint = HINTS.get(finding.code)
        if hint:
            lines.append("  next: " + hint.format(key=key or "KEY"))
    return "\n".join(lines)


def _split(command):
    """Split a command string. POSIX rules would eat the backslashes in a Windows path."""
    if os.name != "nt":
        return shlex.split(command)
    tokens = shlex.split(command, posix=False)
    return [t[1:-1] if len(t) > 1 and t[0] == t[-1] and t[0] in "\"'" else t for t in tokens]


def _run_probe(command, timeout):
    try:
        return subprocess.run(_split(command), stdin=subprocess.DEVNULL, capture_output=True,
                              timeout=timeout).returncode
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


class CommandFailed(Exception):
    def __init__(self, message, result):
        super().__init__(message)
        self.result = result


def _run_command(root, key, argv, timeout):
    """Run the command, saving its full output where an agent can read it instead of rerunning."""
    output = root / OUTPUT_DIR / f"{key}.out"
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timed_out, code, text = False, None, ""
    try:
        done = subprocess.run(argv, cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout or None)
        code, text = done.returncode, done.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as expired:
        timed_out, text = True, (expired.stdout or b"").decode("utf-8", "replace")
    output.write_text(text, encoding="utf-8")
    result = {"exit": code, "seconds": round(time.monotonic() - started, 2), "lines": len(text.splitlines()),
              "output": f"{OUTPUT_DIR}/{key}.out", "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
    if timed_out:
        error = TimeoutError(f"no result after {timeout}s")
        error.result = result
        raise error
    if code != 0:
        raise CommandFailed(f"exit {code}", result)
    return result


def _print_tail(root, result, count):
    if count and result.get("output"):
        print("\n".join((root / result["output"]).read_text(encoding="utf-8").splitlines()[-count:]))


def _describe(result):
    shown = [f"{name}={result[name]}" for name in ("exit", "seconds", "lines", "output") if result.get(name) is not None]
    return " ".join(shown) or "(settled by reconcile or an operator: no output recorded)"


def cmd_run(args):
    root = args.root.resolve()
    argv = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not argv:
        print("run needs a command after --", file=sys.stderr)
        return 2
    preconditions = {}
    for item in args.precondition:
        name, _, command = item.partition("=")
        if not name or not command:
            print("--precondition takes NAME=COMMAND", file=sys.stderr)
            return 2
        preconditions[name] = (lambda command=command: _run_probe(command, 30) == 0)
    try:
        outcome = execute(root, args.key, argv, lambda: _run_command(root, args.key, argv, args.timeout),
                          actor=args.actor, preconditions=preconditions, max_failures=args.max_failures)
    except Refused as error:
        print(refusal(error, args.key))
        return 1
    except LedgerBusy as error:
        print(f"REFUSED ledger busy: {error}. Nothing was run.")
        return 1
    if outcome.status == "replayed":
        print(f"ALREADY DONE key={args.key} completed at {outcome.detail}; not run again. {_describe(outcome.result)}")
        return 0
    if outcome.status == "ran":
        print(f"OK key={args.key} {_describe(outcome.result)}")
        _print_tail(root, outcome.result, args.tail)
        return 0
    if outcome.status == "failed":
        print(f"FAILED key={args.key} " + (_describe(outcome.result) if outcome.result else outcome.detail))
        _print_tail(root, outcome.result, args.tail)
        return 1
    print(f"UNKNOWN key={args.key}: {outcome.detail}. The work may have finished. Do NOT run it again.")
    print(f"  next: python3 scripts/harness_attempt.py reconcile --key {args.key} --actor NAME --probe \"COMMAND\"")
    return 3


def cmd_status(args):
    root = args.root.resolve()
    intents, errors = summary(root)
    stopped = stop_info(root)
    print("kill switch: " + (f"ON ({stopped.get('actor', '?')}: {stopped.get('reason', '')})" if stopped else "off"))
    print("ledger: " + ("INVALID, " + errors[0] if errors else f"verified, {len(intents)} intent(s)"))
    for key, (state, last) in intents.items():
        if args.key and key != args.key:
            continue
        flag = "  <- decide before running again" if state in NEEDS_DECISION else ""
        print(f"{key}: {state} (last {last['event']} by {last['actor']} at {last['at']}){flag}")
    return 1 if errors else 0


def cmd_reconcile(args):
    root = args.root.resolve()
    probe = (lambda: {0: True, 1: False}.get(_run_probe(args.probe, args.timeout))) if args.probe else (lambda: None)
    try:
        outcome = reconcile(root, args.key, probe, actor=args.actor)
    except Refused as error:
        print(refusal(error, args.key))
        return 1
    print(f"{outcome.state.upper()} key={args.key}: {outcome.detail}")
    if outcome.state == "needs_inspection":
        print("  next: report it. An operator who did not start the attempt runs resolve --verdict complete|rerun.")
    return 0 if outcome.state != "needs_inspection" else 3


def cmd_resolve(args):
    try:
        outcome = resolve(args.root.resolve(), args.key, args.verdict, actor=args.actor, role=args.role, reason=args.reason)
    except Refused as error:
        print(refusal(error, args.key))
        return 1
    print(f"{outcome.state.upper()} key={args.key}: recorded by {args.actor}")
    return 0


def cmd_stop(args):
    try:
        stop(args.root.resolve(), actor=args.actor, reason=args.reason, role=args.role)
    except Refused as error:
        print(refusal(error))
        return 1
    print("STOPPED: new work is refused until an operator runs go.")
    return 0


def cmd_go(args):
    try:
        lifted = go(args.root.resolve(), actor=args.actor, role=args.role, reason=args.reason)
    except Refused as error:
        print(refusal(error))
        return 1
    print("RESUMED: the kill switch is off." if lifted else "The kill switch was already off.")
    return 0


def cmd_key(args):
    print(key_for(*args.parts))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root (default: current directory)")
    sub = parser.add_subparsers(dest="command_name", required=True)

    def add(name, handler, help_text):
        p = sub.add_parser(name, help=help_text)
        p.set_defaults(handler=handler)
        return p

    def key_arg(p):
        p.add_argument("--key", required=True, type=check_key, help="Identifies the intent; derive it with the key command")

    run = add("run", cmd_run, "Run a command at most once per key: harness_attempt.py run --key K -- COMMAND ...")
    key_arg(run)
    run.add_argument("--actor", required=True, help="Who is running it, e.g. copilot-agent")
    run.add_argument("--timeout", type=float, default=0, help="Seconds before the outcome is recorded as unknown (0 = none)")
    run.add_argument("--precondition", action="append", default=[], metavar="NAME=COMMAND",
                     help="Command that must exit 0 first, for example vpn=./check_vpn.sh; repeatable")
    run.add_argument("--max-failures", type=int, default=DEFAULT_MAX_FAILURES, help="Definite failures allowed per intent")
    run.add_argument("--tail", type=int, default=40, help="Output lines to print; the full output is saved (0 prints none)")
    run.add_argument("command", nargs=argparse.REMAINDER)

    status = add("status", cmd_status, "Show intents, the kill switch and ledger integrity")
    status.add_argument("--key", type=check_key)

    rec = add("reconcile", cmd_reconcile, "Ask a probe whether the effect exists")
    key_arg(rec)
    rec.add_argument("--actor", required=True)
    rec.add_argument("--probe", help="Command: exit 0 = the effect exists, exit 1 = it does not, anything else = cannot tell")
    rec.add_argument("--timeout", type=float, default=30)

    res = add("resolve", cmd_resolve, "An operator settles an uncertain attempt")
    key_arg(res)
    res.add_argument("--verdict", required=True, choices=("complete", "rerun"))
    res.add_argument("--actor", required=True)
    res.add_argument("--role", required=True, choices=("worker", OPERATOR))
    res.add_argument("--reason", required=True)

    stp = add("stop", cmd_stop, "Kill switch on: refuse all new work")
    stp.add_argument("--actor", required=True)
    stp.add_argument("--role", choices=("worker", OPERATOR), default="worker")
    stp.add_argument("--reason", required=True)

    lift = add("go", cmd_go, "Kill switch off (operator only)")
    lift.add_argument("--actor", required=True)
    lift.add_argument("--role", required=True, choices=("worker", OPERATOR))
    lift.add_argument("--reason", required=True)

    keyer = add("key", cmd_key, "Print a stable key for the parts that identify the work")
    keyer.add_argument("parts", nargs="+")

    args = parser.parse_args(argv)
    for name in ("actor", "reason"):
        if hasattr(args, name) and not str(getattr(args, name)).strip():
            parser.error(f"--{name} must not be blank")
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
