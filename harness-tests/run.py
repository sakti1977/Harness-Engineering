"""Harness tests: prove each gate catches the defect it promises to catch, and passes clean work.

For each manifest entry: copy the fixture to a scratch directory, commit it to a fresh git
repository, apply the named defect, call the real gate function, and compare the receipt (the
sorted failure codes; empty means pass) with the expected one. Output is only what failed:
the entry id, the expected codes and the received codes.

Also enforced:
  coverage  every failure code the gates can emit has a defect entry, and every gate has a
            clean entry. A new gate without both does not pass.
  drift     the fixture still has the shape the harness expects (core files, schema, matrix
            columns). Run on a schedule too, because fixtures rot as the repository moves.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CODE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
# Codes that report success or information, and environment variable names, are not gates.
NOT_FAILURES = {"ARTIFACT_PRESENT", "CLAIM_PENDING", "CLAIM_PROVEN", "EXCLUSIONS_REMINDER",
                "LOG_VERIFIED", "PROOF_COVERED", "SESSION_CHANGES"}
GATES = ("artifacts", "session", "transition")
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="harness", GIT_AUTHOR_EMAIL="harness@example.com",
               GIT_COMMITTER_NAME="harness", GIT_COMMITTER_EMAIL="harness@example.com",
               GIT_CONFIG_COUNT="3", GIT_CONFIG_KEY_0="gc.auto", GIT_CONFIG_VALUE_0="0",
               GIT_CONFIG_KEY_1="maintenance.auto", GIT_CONFIG_VALUE_1="false",
               GIT_CONFIG_KEY_2="gc.autoDetach", GIT_CONFIG_VALUE_2="false")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = load("harness_check", ROOT / "scripts/harness_check.py")
mover = load("harness_transition", ROOT / "scripts/harness_transition.py")
defects = load("harness_defects", HERE / "defects.py")


class Scratch:
    """A disposable git-backed copy of a fixture, with helpers the defects use."""

    check = check

    def __init__(self, root):
        self.root = root

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True,
                              text=True, env=GIT_ENV).stdout.strip()

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "step")

    def head(self):
        return self.git("rev-parse", "HEAD")

    def read(self, name):
        return (self.root / name).read_text()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def delete(self, name):
        (self.root / name).unlink()

    def feature(self):
        return json.loads(self.read(".harness/feature.json"))

    def set_feature(self, **changes):
        self.write(".harness/feature.json", json.dumps(dict(self.feature(), **changes), indent=2))

    def move(self, to, role, actor, reason):
        ok, messages = mover.transition(self.root, to, actor, role, reason)
        if not ok:
            raise RuntimeError(f"fixture setup refused {to}: {messages}")


def receipt(gate, root, entry):
    """Call the real gate and return its sorted failure codes; [] means it passed."""
    if gate in ("artifacts", "session"):
        result = check.inspect(root, session=gate == "session")
        return sorted({f["code"] for f in result["findings"] if not f["ok"]})
    if gate == "transition":
        args = entry["transition"]
        ok, messages = mover.transition(root, args["to"], args["actor"], args["role"], "harness test")
        return [] if ok else sorted({code for message in messages for code in CODE.findall(message)})
    raise ValueError(f"unknown gate {gate!r}")


def run_entry(entry):
    with TemporaryDirectory(ignore_cleanup_errors=True) as directory:
        root = Path(directory) / "project"
        shutil.copytree(HERE / "fixtures" / entry.get("fixture", "clean-project"), root)
        scratch = Scratch(root)
        scratch.git("init", "-q", "-b", "main")
        scratch.commit()
        getattr(defects, entry["defect"])(scratch)
        return receipt(entry["gate"], root, entry)


def gate_codes():
    """Every failure code the gates can emit, read from their source."""
    source = "".join((ROOT / f"scripts/{name}.py").read_text() for name in ("harness_check", "harness_transition"))
    literals = set(re.findall(r'"([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)', source))
    return {code for code in literals if code not in NOT_FAILURES and not code.startswith("GIT_")}


def coverage_problems(manifest):
    problems = []
    expected = {code for entry in manifest for code in entry["expect"]}
    for code in sorted(gate_codes() - expected):
        problems.append(f"UNCOVERED {code}: add a defect fixture that makes a gate emit it")
    for gate in GATES:
        if not any(e["gate"] == gate and not e["expect"] for e in manifest):
            problems.append(f"NO_CLEAN_FIXTURE {gate}: add a clean entry that this gate passes")
    ids = [e["id"] for e in manifest]
    for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"DUPLICATE_ID {duplicate}")
    for entry in manifest:
        if not hasattr(defects, entry["defect"]):
            problems.append(f"UNKNOWN_DEFECT {entry['id']}: {entry['defect']} is not in defects.py")
    return problems


def drift_problems():
    problems = []
    for fixture in sorted(p for p in (HERE / "fixtures").iterdir() if p.is_dir()):
        for name in check.CORE_FILES:
            if not (fixture / name).is_file():
                problems.append(f"FIXTURE_DRIFT {fixture.name}: missing {name}")
        try:
            feature = json.loads((fixture / ".harness/feature.json").read_text())
            schema = json.loads((ROOT / "schemas/feature.schema.json").read_text())
            for error in check.schema_errors(feature, schema):
                problems.append(f"FIXTURE_DRIFT {fixture.name}: {error}")
        except (OSError, ValueError) as error:
            problems.append(f"FIXTURE_DRIFT {fixture.name}: feature ledger unreadable ({error})")
        matrix = fixture / "docs/proof-matrix.md"
        if matrix.is_file() and check.proof_table(matrix.read_text()) is None:
            problems.append(f"FIXTURE_DRIFT {fixture.name}: proof matrix lacks the columns {check.PROOF_COLUMNS}")
    return problems


def main(manifest=None):
    if manifest is None:
        manifest = json.loads((HERE / "manifest.json").read_text())["entries"]
    failures = coverage_problems(manifest) + drift_problems()
    for entry in manifest:
        try:
            received = run_entry(entry)
        except Exception as error:  # a broken fixture setup is a failure, not a crash
            received = [f"SETUP_ERROR: {error}"]
        if received != sorted(entry["expect"]):
            failures.append(f"FAIL {entry['id']}: expected {sorted(entry['expect']) or 'PASS'} "
                            f"received {received or 'PASS'}")
    for line in failures:
        print(line)
    print(f"Harness tests: {len(manifest)} entries, {len(failures)} problem(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
