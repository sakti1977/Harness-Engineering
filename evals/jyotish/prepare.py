"""Prepare one evaluation run: a fresh git repository with the task, optionally with the harness.

  python3 evals/jyotish/prepare.py --out ~/eval-runs --condition bare --name run1
  python3 evals/jyotish/prepare.py --out ~/eval-runs --condition harness --name run1

Creates <out>/<condition>-<name>/ (the agent's working directory) and, for the harness condition,
<out>/kit/ with only the harness scripts and schemas, so the agent cannot read the lab, the
handbook or this grader. Prints the prompt to give the agent. Keep <out> outside this repository.
"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1]
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="eval", GIT_AUTHOR_EMAIL="eval@example.com",
               GIT_COMMITTER_NAME="eval", GIT_COMMITTER_EMAIL="eval@example.com", PYTHONDONTWRITEBYTECODE="1")

BARE_PROMPT = """You are working on a small Python codebase at {run}. Work only inside that directory: do not read, list or search any other location on this machine (no parent directories, no home directory, no other repositories). Python 3.10+ standard library only; no package installs, no network.

Read README.md and ISSUES.md. Fix the three user reports in ISSUES.md in jyotish/app.py. Keep the public function names and signatures and the table and column names. You may add or change tests under tests/. Run the tests. You may commit or leave your changes uncommitted.

When you are finished, reply with a short summary of what you changed and how you know it works. Make the very last line of your reply a single JSON object, exactly in this shape: {{"fixed": [<issue numbers you are confident are fixed>], "tests_added": <int>, "done": <true|false>}}"""

HARNESS_PROMPT = """You are working on a small Python codebase at {run}. Work only inside that directory: do not read, list or search any other location on this machine (no parent directories, no home directory, no other repositories). The one exception is the harness kit at {kit}, which you may read and run (export HARNESS_KIT={kit}). Python 3.10+ standard library only; no package installs, no network.

This repository uses an agent harness. Before anything else, read AGENTS.md and follow it, including the Resume Protocol at the start and the handoff gate at the end. Use the actor name "{actor}" wherever the harness asks for an actor.

Read README.md and ISSUES.md. Fix the three user reports in ISSUES.md in jyotish/app.py. Keep the public function names and signatures and the table and column names. You may add or change tests under tests/. Run the tests. You may commit or leave your changes uncommitted.

When you are finished, reply with a short summary of what you changed and how you know it works. Make the very last line of your reply a single JSON object, exactly in this shape: {{"fixed": [<issue numbers you are confident are fixed>], "tests_added": <int>, "done": <true|false>}}"""


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=GIT_ENV)


def prepare(out, condition, name):
    out = out.resolve()
    if out == KIT or KIT in out.parents:
        raise SystemExit("--out must be outside this repository, so the agent cannot find the grader")
    run = out / f"{condition}-{name}"
    if run.exists():
        raise SystemExit(f"{run} already exists")
    shutil.copytree(HERE / "task", run)
    kit = out / "kit"
    if condition == "harness":
        shutil.copytree(HERE / "harness", run, dirs_exist_ok=True)
        if not kit.exists():
            (kit / "scripts").mkdir(parents=True)
            for script in ("harness_check.py", "harness_transition.py", "harness_handoff.py"):
                shutil.copy(KIT / "scripts" / script, kit / "scripts" / script)
            shutil.copytree(KIT / "schemas", kit / "schemas")
    git(run, "init", "-q", "-b", "main")
    git(run, "add", "-A")
    git(run, "commit", "-q", "-m", "task")
    if condition == "harness":
        subprocess.run([sys.executable, str(kit / "scripts/harness_transition.py"), "--root", str(run), "--to", "planned",
                        "--actor", "planner", "--role", "planner", "--reason", "user reports scoped"],
                       check=True, capture_output=True, env=GIT_ENV)
        git(run, "add", "-A")
        git(run, "commit", "-q", "-m", "scoped")
        return run, HARNESS_PROMPT.format(run=run, kit=kit, actor=f"agent-{name}")
    return run, BARE_PROMPT.format(run=run)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--condition", choices=("bare", "harness"), required=True)
    parser.add_argument("--name", required=True, help="run label, e.g. sonnet-1")
    args = parser.parse_args(argv)
    run, prompt = prepare(args.out, args.condition, args.name)
    print(f"Prepared {run}\n\nPrompt for the agent:\n\n{prompt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
