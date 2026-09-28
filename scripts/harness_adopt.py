"""Adopt Harness Engineering in an existing project: preview first, never overwrite.

  python3 scripts/harness_adopt.py --root /path/to/project            # preview; writes nothing
  python3 scripts/harness_adopt.py --root /path/to/project --apply    # create the missing files

Creates the six core artifacts plus a verification-route file, agent instructions carrying the
Resume Protocol, and optionally a GitHub Actions workflow. A file that already exists is never
changed: it is reported, and where it matters the output says what to add to it by hand.

Run it from this kit's checkout; the other scripts are run from here too, pointed at your
project with --root. Nothing in your project is executed.
"""
from pathlib import Path
import argparse
import json
import re
import sys

KIT = Path(__file__).resolve().parents[1]
PROTOCOL_START = "## Resume Protocol: the first action of every session"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "project"


def portable(text):
    """Point kit commands at $HARNESS_KIT so project files work on every machine and in CI."""
    text = re.sub(r"python3 scripts/(harness_\w+\.py)", r"python3 $HARNESS_KIT/scripts/\1 --root .", text)
    return re.sub(r"`scripts/(harness_\w+\.py)`", r"`$HARNESS_KIT/scripts/\1`", text)


def resume_protocol():
    text = (KIT / "AGENTS.md").read_text(encoding="utf-8")
    return portable(text[text.index(PROTOCOL_START):].strip() + "\n")


def kit_command(script):
    return f"python3 {KIT / 'scripts' / script}"


def feature_ledger(project):
    return json.dumps({
        "id": f"{slug(project)}-first-feature",
        "outcome": "TODO: one externally observable outcome, e.g. a saved profile is really stored",
        "state": "planned",
        "expected_surface": ["TODO/path/to/the/file/this/feature/changes"],
        "exclusions": [],
        "verification": "TODO: the one command that proves the claims, e.g. npm test -- profile",
        "claims": ["TODO: first claim: one observable behavior, a specific value, a named boundary"],
    }, indent=2) + "\n"


PROOF_MATRIX = """# Claim-to-Proof Matrix

One row per claim in `.harness/feature.json`, with the claim text copied exactly. A claim is covered only when a check observes it at the boundary it is about. How to write claims and find gaps: {kit}/docs/proof-gaps.md

| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |
| --- | --- | --- | --- | --- | --- |
| TODO: first claim: one observable behavior, a specific value, a named boundary | TODO: what a check must see | TODO | TODO | TODO | TODO |

Boundaries: `unit`, `entry`, `persistence`, `concurrency`, `environment`, `external`, `ui`.

## Evidence that does not count

| Check | What it observes | Why it is not proof |
| --- | --- | --- |
| An agent's summary saying "all tests pass" | Nothing | Not an observation. Evidence is a named check run at a recorded revision. |
"""

AUTHORITY = """# Authority Policy

Default: deny. Anything not allowed below is refused. The agent may request an action; the harness decides. Where this file and your agent instructions disagree, the stricter rule wins. Annotated example: {kit}/docs/authority.md

## Read

- allowed: TODO source, test and doc folders the task needs
- denied: `.env`, `.env.*`, `**/*.pem`, `**/*.key`, `secrets/**`

> Deny beats allow: list secret locations even inside allowed folders.

## Write

- allowed: the paths in `expected_surface` of `.harness/feature.json`, plus `.harness/checkpoint.md`
- denied: `.harness/feature.json`, `.harness/feature-log.jsonl`, `.harness/evidence.json`, this file, agent instruction files, CI workflows, test runner configuration

> An agent that can edit its own policy, ledger or CI can widen its authority or mark itself done.

## Commands

- allowed (exact strings): TODO the verification command, `git status`, `git diff`
- denied by default: everything else, including dependency installs, pushes, history rewrites and database resets

## Secrets

- injected as: TODO variable names only, never values; sandbox or test credentials only
- never printed: every injected variable, plus `*_TOKEN`, `*_KEY`, `*_SECRET`
- redact on: trace, checkpoint, failure packet, exit report

## Requires approval

- schema change, destructive store operation, history rewrite, dependency install, publish, outbound message to a person

## Grants

- one action, one resource, one session, recorded in `.harness/checkpoint.md`

## Enforced by

- read: TODO (for example your agent tool's permission deny rules)
- write: `harness_check.py --session` after the fact; TODO tool permission rules during the session
- protected files: TODO (for example CODEOWNERS on `.harness/` and branch protection)
"""

VERIFY = """# Verification routes

A test run proves only what it exercised. Write one route per claim that crosses a storage, network, time-zone or timing boundary, so a fresh session reruns the real journey. Worked example: {kit}/docs/verify.md

## Route: TODO-short-name

| Field | Value |
| --- | --- |
| Claim | TODO: exact claim text from .harness/feature.json |
| Entry | TODO: the public entry point real callers use |
| Boundaries | TODO: what must stay real (store, network, time zone, queue) |
| Setup | TODO: seed data and environment, including the values that matter |
| Actions | TODO: steps, with the ordering or concurrency that can change the result |
| Observations | TODO: exact responses and the lasting state read back |
| Cleanup | TODO: what is removed or stopped |

Command: `TODO: one command a fresh session can run`
"""

AGENTS = """# Agent instructions

Read `docs/authority.md` (what you may read, write and run) and `.harness/feature.json` (the active outcome, scope and claims) before editing. Verify claims through the routes in `docs/verify.md`. Change feature state only through the harness transition command, never by editing `.harness/feature.json`.

The harness commands live in the Harness Engineering kit. Set `HARNESS_KIT` to your checkout of it (for example `export HARNESS_KIT=~/Harness-Engineering`) and run them from this project with `--root .`.

"""

CLAUDE = "# Claude Code instructions\n\nFollow the agent instructions, including the Resume Protocol and the handoff gate:\n\n@AGENTS.md\n"
GEMINI = "# Gemini CLI instructions\n\nFollow the agent instructions in AGENTS.md, including the Resume Protocol and the handoff gate:\n\n@./AGENTS.md\n"
CURSOR = "---\ndescription: Harness Engineering Resume Protocol and handoff gate\nalwaysApply: true\n---\n\n"

# Instruction files per agent tool: (path, content builder, note). Tools that import AGENTS.md also get AGENTS.md.
TARGETS = ("agents", "claude", "copilot", "gemini", "cursor")
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", ".cursor/rules/harness.mdc")
IMPORTS_AGENTS = {"CLAUDE.md", "GEMINI.md"}


def parse_agents(value):
    """'all', 'none', or a comma-separated list of TARGETS. Returns a set."""
    if value == "all":
        return set(TARGETS)
    if value == "none":
        return set()
    chosen = {part.strip() for part in value.split(",") if part.strip()}
    unknown = chosen - set(TARGETS)
    if not chosen or unknown:
        named = ", ".join(sorted(unknown)) if unknown else repr(value)
        raise ValueError(f"unknown --agents value {named}; "
                         f"use all, none or a comma-separated list of {', '.join(TARGETS)}")
    return chosen

WORKFLOW = """name: Harness
on: [push, pull_request]
permissions:
  contents: read
jobs:
  harness:
    runs-on: ubuntu-latest
    env:
      HARNESS_KIT: .harness-kit
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/checkout@v4
        with:
          repository: sakti1977/Harness-Engineering
          ref: main   # pin to a release tag or commit you have reviewed
          path: .harness-kit
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Harness artifacts, proof plan and transition log
        run: python "$HARNESS_KIT/scripts/harness_check.py" --root .
      - name: Changed files against the feature's scope
        if: github.event_name == 'pull_request'
        run: python "$HARNESS_KIT/scripts/harness_check.py" --root . --session --base "origin/${{ github.base_ref }}"
"""


def plan(root, agents, ci):
    """[(relative path, content, note)] for everything adoption would create."""
    kit = str(KIT)
    files = [
        (".harness/feature.json", feature_ledger(root.name), "the first feature: fill outcome, surface, verification and claims"),
        (".harness/checkpoint.md", portable((KIT / "templates/core/.harness/checkpoint.md").read_text(encoding="utf-8")), "written by harness_handoff.py --write"),
        ("docs/authority.md", AUTHORITY.format(kit=kit), "fill the TODOs for this project"),
        ("docs/scope-contract.md", (KIT / "templates/core/docs/scope-contract.md").read_text(encoding="utf-8"), "reference; no edits needed"),
        ("docs/proof-matrix.md", PROOF_MATRIX.format(kit=kit), "one row per claim"),
        ("docs/readiness.md", (KIT / "templates/core/docs/readiness.md").read_text(encoding="utf-8"), "reference; add your readiness probes"),
        ("docs/verify.md", VERIFY.format(kit=kit), "one route per claim that crosses a boundary"),
    ]
    protocol = resume_protocol()
    files.append((".harness/agent-protocol.md", "# Resume Protocol and handoff gate\n\nKeep this in your agent "
                  "instructions (for example AGENTS.md, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md "
                  "or a Cursor rule).\n\n" + protocol,
                  "the protocol to keep in your agent instructions"))
    agents = parse_agents(agents) if isinstance(agents, str) else set(agents)
    instructions = AGENTS.format(kit=kit) + protocol
    if agents & {"agents", "claude", "gemini"}:
        importers = sorted({"claude": "CLAUDE.md", "gemini": "GEMINI.md"}[a] for a in agents & {"claude", "gemini"})
        note = ("Resume Protocol and handoff gate for any agent (Codex, Cursor and others read it natively)"
                if "agents" in agents else f"imported by {' and '.join(importers)}")
        files.append(("AGENTS.md", instructions, note))
    if "claude" in agents:
        files.append(("CLAUDE.md", CLAUDE, "Claude Code; imports AGENTS.md"))
    if "gemini" in agents:
        files.append(("GEMINI.md", GEMINI, "Gemini CLI; imports AGENTS.md"))
    if "copilot" in agents:
        files.append((".github/copilot-instructions.md", instructions, "Copilot reads this on every request"))
    if "cursor" in agents:
        files.append((".cursor/rules/harness.mdc", CURSOR + instructions, "Cursor project rule, always applied"))
    if ci:
        files.append((".github/workflows/harness.yml", WORKFLOW, "runs the checker on every push and PR"))
    return files


def safe_target(root, relative):
    """Resolve a target inside root; refuse anything that escapes it through a symlink."""
    target = root / relative
    parent = target.parent
    while not parent.exists():
        parent = parent.parent
    if not parent.resolve().is_relative_to(root) or (target.is_symlink() and not target.resolve().is_relative_to(root)):
        raise ValueError(f"{relative} resolves outside the project")
    return target


def adopt(root, *, apply=False, agents="agents", ci=False):
    """Returns (actions, hints). Each action is (verb, path, note); verb is create, skip or refuse."""
    root = root.resolve()
    actions, hints = [], []
    for relative, content, note in plan(root, agents, ci):
        try:
            target = safe_target(root, relative)
        except ValueError as error:
            actions.append(("refuse", relative, str(error)))
            continue
        if target.exists() or target.is_symlink():
            actions.append(("skip", relative, "exists; left unchanged"))
            existing = target.read_text(errors="replace", encoding="utf-8") if target.is_file() else ""
            if relative in INSTRUCTION_FILES and PROTOCOL_START not in existing and \
                    not (relative in IMPORTS_AGENTS and "@AGENTS.md" in existing.replace("@./AGENTS.md", "@AGENTS.md")):
                hints.append(f"{relative} already exists: add the Resume Protocol and handoff gate to it by hand, "
                             "copying them from .harness/agent-protocol.md"
                             + (" (or add the line @AGENTS.md)." if relative in IMPORTS_AGENTS else "."))
            continue
        actions.append(("create", relative, note))
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "x", encoding="utf-8") as handle:   # "x" never overwrites
                handle.write(content)
    return actions, hints


def next_steps(root, created):
    check, move, hand = (kit_command(s) for s in ("harness_check.py", "harness_transition.py", "harness_handoff.py"))
    files = " ".join(f"'{path}'" if " " in path else path for path in created)
    commit = (f"""  0. Commit the new files first, so the scope check measures your work and not the setup:
       git add {files} && git commit -m "Adopt Harness Engineering"

""" if created else "")
    return f"""Set HARNESS_KIT once so the commands in your project files work (add it to your shell profile):
  export HARNESS_KIT={KIT}

Next steps (from {root}):
{commit}  1. Pick one real failure your agent caused. Describe it in .harness/feature.json: outcome, the files it
     may touch, the verification command, and 2-4 claims (checklist: {KIT / 'docs/proof-gaps.md'}).
  2. Give each claim a row in docs/proof-matrix.md and a route in docs/verify.md. Seed a broken version
     and confirm at least one check fails on it.
  3. Fill the TODOs in docs/authority.md, then check the artifacts:
       {check} --root .
  4. Adopt the ledger and start work:
       {move} --root . --to planned --actor <you> --role planner --reason "first feature scoped"
       {move} --root . --to active --actor <agent> --role worker --reason "start"
  5. End every session with the handoff gate:
       {hand} --root . --write   (then fill the next edit)
       {hand} --root . --check
     and start the next one with {hand} --root . --resume
  6. Protect .harness/feature-log.jsonl and .harness/evidence.json with CODEOWNERS so only a person or CI
     records passing."""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, required=True, help="the project to adopt the harness in")
    parser.add_argument("--apply", action="store_true", help="write the files (default: preview only)")
    parser.add_argument("--agents", default="agents", metavar="LIST",
                        help="instruction files to create: all, none, or a comma-separated list of "
                             f"{', '.join(TARGETS)} (default: agents, which creates AGENTS.md)")
    parser.add_argument("--ci", action="store_true", help="also create .github/workflows/harness.yml")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error("--root must be an existing directory")
    try:
        parse_agents(args.agents)
    except ValueError as error:
        parser.error(str(error))
    root = args.root.resolve()
    if root == KIT:
        parser.error("--root is this kit; point it at your own project")
    actions, hints = adopt(root, apply=args.apply, agents=args.agents, ci=args.ci)
    mode = "applied" if args.apply else "preview; nothing written"
    print(f"Adopting Harness Engineering in {root} ({mode})")
    for verb, relative, note in actions:
        print(f"  {verb:<7} {relative:<34} {note}")
    for hint in hints:
        print(f"  note    {hint}")
    created = sum(verb == "create" for verb, _, _ in actions)
    if not args.apply:
        print(f"Run again with --apply to create {created} file(s). Existing files are never changed.")
    else:
        print(f"Created {created} file(s). Existing files were not changed.")
        print(next_steps(root, [relative for verb, relative, _ in actions if verb == "create"]))
    return 1 if any(verb == "refuse" for verb, _, _ in actions) else 0


if __name__ == "__main__":
    sys.exit(main())
