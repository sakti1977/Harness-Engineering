"""Feature ledger as a gate: an agent tries to shortcut the lifecycle and is stopped.

Runs in a throwaway git repository. No model, network or project commands.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("harness_transition", ROOT / "scripts/harness_transition.py")
mover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mover)
check = mover.check
# Background auto-maintenance after commits can outlive a test and race its temp-dir cleanup.
NO_BACKGROUND_GIT = {"GIT_CONFIG_COUNT": "3", "GIT_CONFIG_KEY_0": "gc.auto", "GIT_CONFIG_VALUE_0": "0",
                     "GIT_CONFIG_KEY_1": "maintenance.auto", "GIT_CONFIG_VALUE_1": "false",
                     "GIT_CONFIG_KEY_2": "gc.autoDetach", "GIT_CONFIG_VALUE_2": "false"}
ENV = dict(os.environ, GIT_AUTHOR_NAME="demo", GIT_AUTHOR_EMAIL="demo@example.com",
           GIT_COMMITTER_NAME="demo", GIT_COMMITTER_EMAIL="demo@example.com",
           **NO_BACKGROUND_GIT)


def main():
    if not shutil.which("git"):
        print("This demo needs git on PATH.")
        return 1
    with TemporaryDirectory() as temp:
        root = Path(temp)

        def git(*args):
            return subprocess.run(["git", "-C", temp, *args], check=True, capture_output=True,
                                  text=True, env=ENV).stdout.strip()

        def put(name, text):
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text)

        def commit():
            git("add", "-A")
            git("commit", "-q", "--allow-empty", "-m", "step")

        for name in check.CORE_FILES:
            put(name, (ROOT / name).read_text())
        feature = json.loads((ROOT / ".harness/feature.json").read_text())
        put(".harness/feature.json", json.dumps(dict(feature, state="planned"), indent=2))
        put("examples/astro/astro.py", "# broken: coaching write ignores chart_version\n")
        put("app/support/upi.py", "# voluntary contributions: never touches coaching\n")
        git("init", "-q", "-b", "main")
        commit()

        results = []

        def step(label, to, actor, role, expect_ok):
            ok, messages = mover.transition(root, to, actor, role, label)
            mark = "RECORDED" if ok else "REFUSED "
            print(f"{mark} {label}")
            for message in [m for m in messages if not m.endswith(":")] if not ok else []:
                print(f"         {message}")
            results.append(ok == expect_ok)
            if ok:
                commit()

        step("Planner adopts the ledger", "planned", "sakti", "planner", True)
        step("Agent starts work", "active", "copilot-agent", "worker", True)
        step("Agent marks its own work passing", "passing", "copilot-agent", "worker", False)
        put("examples/astro/astro.py", "# fixed: conditional write on chart_version\n")
        put("app/support/upi.py", "# agent 'tidied' the contributions module\n")
        commit()
        step("Agent asks for verification", "ready_for_verification", "copilot-agent", "worker", False)
        git("revert", "--no-edit", "HEAD")
        put("examples/astro/astro.py", "# fixed: conditional write on chart_version\n")
        commit()
        step("Agent asks again, scope clean", "ready_for_verification", "copilot-agent", "worker", True)
        step("Verifier approves with no evidence", "passing", "sakti", "verifier", False)
        head = git("rev-parse", "HEAD")
        put(".harness/evidence.json", json.dumps(
            [{"claim": c, "command": feature["verification"], "result": "pass", "revision": head}
             for c in feature["claims"]], indent=2))
        commit()
        step("Same agent approves its own request", "passing", "copilot-agent", "verifier", False)
        step("Independent verifier approves with evidence", "passing", "sakti", "verifier", True)

        put("examples/astro/astro.py", "# a later session edits the verified code\n")
        commit()
        stale = [f for f in check.inspect(root)["findings"] if f["code"] == "PASSING_STALE"]
        print(("STALE    " if stale else "MISSED   ") + "Next session changes verified code: passing is flagged stale")
        results.append(bool(stale))

        log = (root / check.LOG_FILE).read_text().splitlines()
        print(f"\nAudit log: {len(log)} hash-chained entries in {check.LOG_FILE}")
        for line in log:
            e = json.loads(line)
            print(f"  {e['seq']}. {e['from']:>22} -> {e['to']:<22} {e['actor']} ({e['role']})")
        ok = all(results)
        print("\nGATE DEMO PASSED: every shortcut was refused and every legitimate step was recorded."
              if ok else "\nGATE DEMO FAILED: unexpected behavior.")
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
