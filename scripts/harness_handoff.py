"""Session handoff: write the checkpoint from the observed repository, gate the handoff, check it on resume.

  --write    Draft .harness/checkpoint.md from the repository as it is: feature and state from the
             ledger, HEAD, uncommitted files (no ceremonial commit), which claims have current
             evidence and which do not. Hand-written sections (suspected causes, blockers,
             decisions, first command, next edit, grants) are kept from the existing checkpoint.
  --check    The handoff gate, the last action of a session. Fails on accidental edits outside
             the feature's scope, a checkpoint that does not match the repository, a claim
             presented as verified without current evidence, an unverified claim left undeclared,
             or a missing field.
  --resume   The Resume Protocol, the first action of a session. Answers the eight recovery
             questions from files and commands, and treats a stale or incomplete checkpoint as a
             failed check instead of following it.

Never executes project commands. Reads git with the checker's safe, read-only queries.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import importlib.util
import json
import re
import sys

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("harness_check", HERE / "harness_check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

CHECKPOINT = ".harness/checkpoint.md"
SECTIONS = ("Verified at this state", "Not verified since the last edit", "Suspected causes (not verified)",
            "Blockers and commands still to run", "Decisions to preserve", "First command for the next session",
            "Next bounded edit", "Grants used this session")
HAND_WRITTEN = SECTIONS[2:]
REQUIRED_TEXT = ("First command for the next session", "Next bounded edit")
PLACEHOLDER = "TODO"
QUESTIONS = (
    ("What outcome is active, and in what state?", ".harness/feature.json and .harness/feature-log.jsonl"),
    ("Which revision and uncommitted files does the handoff describe, and do they still match?", "git rev-parse HEAD; git status"),
    ("Which claims are verified, by which command, at which revision?", ".harness/evidence.json"),
    ("Which claims are not verified since the last edit?", "python3 scripts/harness_check.py --session"),
    ("What is suspected but not verified?", "checkpoint: Suspected causes (not verified)"),
    ("What is blocked, and which command still needs to run?", "checkpoint: Blockers and commands still to run"),
    ("Which decisions and constraints must be preserved?", "checkpoint: Decisions to preserve; docs/authority.md"),
    ("What is the first command, and the next bounded edit?", "checkpoint: First command; Next bounded edit"),
)


# observed state ---------------------------------------------------------------------------------
def not_bookkeeping(path):
    return not any(path.startswith(prefix) for prefix in check.ALWAYS_IN_SCOPE)


def dirty_files(root):
    out = check.git(root, "status", "--porcelain", "-z", "--no-renames", "--untracked-files=all")
    return sorted({entry[3:] for entry in out.split("\0") if entry and not_bookkeeping(entry[3:])})


def claim_status(root, feature):
    """(proven, unproven) claim lists, judged exactly as the evidence gate judges them."""
    findings = check.session_findings(root, dict(feature, state="ready_for_verification"))
    proven = [f["detail"] for f in findings if f["code"] == "CLAIM_PROVEN"]
    return proven, [c for c in feature["claims"] if c not in proven]


def observe(root):
    feature = json.loads(check.read_artifact(root, ".harness/feature.json"))
    head = check.git(root, "rev-parse", "HEAD").strip()
    proven, unproven = claim_status(root, feature)
    evidence, _ = check.load_evidence(root)
    latest = {}
    for entry in evidence or []:
        latest[entry["claim"]] = entry
    inside_kit = (root / "scripts/harness_handoff.py").is_file()
    command = "python3 scripts/harness_handoff.py" if inside_kit else "python3 $HARNESS_KIT/scripts/harness_handoff.py --root ."
    return {"command": command, "feature": feature, "head": head, "dirty": dirty_files(root), "proven": proven,
            "unproven": unproven, "evidence": latest}


# checkpoint format ------------------------------------------------------------------------------
def placeholder(text):
    """Unfilled: empty, TODO, 'None recorded', or a template hint such as '<one edit ...>'."""
    text = (text or "").strip()
    return not text or text == PLACEHOLDER or "None recorded" in text or text.startswith("<")

def parse(text):
    header, sections, current = {}, {}, None
    for line in text.splitlines():
        heading = re.match(r"^## (.+?)\s*$", line)
        if heading:
            current = heading.group(1)
            sections[current] = []
            continue
        if current is None:
            field = re.match(r"^- (Written|Feature|Revision|Uncommitted files): (.*)$", line)
            if field:
                header[field.group(1)] = field.group(2).strip()
        else:
            sections[current].append(line)
    return header, {name: "\n".join(lines).strip() for name, lines in sections.items()}


def render(observed, kept, now=None):
    feature = observed["feature"]
    written = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%MZ")
    dirty = ", ".join(observed["dirty"]) or "none"
    verified = [f"- {claim}: `{observed['evidence'][claim]['command']}` passed at "
                f"{observed['evidence'][claim]['revision'][:12]}" for claim in observed["proven"]]
    unverified = [f"- {claim}" for claim in observed["unproven"]]
    if unverified:
        unverified.append(f"- Command that would verify them: `{feature['verification']}`")
    defaults = {"Suspected causes (not verified)": "None recorded.",
                "Blockers and commands still to run": "None recorded.",
                "Decisions to preserve": "None recorded.",
                "First command for the next session": f"`{observed['command']} --resume`, then `{feature['verification']}`",
                "Next bounded edit": PLACEHOLDER,
                "Grants used this session": "None."}
    body = [
        "# Checkpoint",
        "",
        f"Written from the observed repository by `{observed['command']} --write`. "
        "Check it with `--check` before ending a session and `--resume` before starting one. "
        "Facts below are observed; anything under Suspected causes is not.",
        "",
        f"- Written: {written}",
        f"- Feature: {feature['id']} (state: {feature['state']})",
        f"- Revision: {observed['head']}",
        f"- Uncommitted files: {dirty}",
        "",
        "## Verified at this state",
        "",
        "\n".join(verified) or "Nothing has current evidence.",
        "",
        "## Not verified since the last edit",
        "",
        "\n".join(unverified) or "None: every claim has current evidence.",
    ]
    for name in HAND_WRITTEN:
        body += ["", f"## {name}", "", kept.get(name) or defaults[name]]
    return "\n".join(body) + "\n"


def write(root, now=None):
    path = root / CHECKPOINT
    kept = parse(path.read_text())[1] if path.is_file() else {}
    kept = {name: text for name, text in kept.items() if not placeholder(text)}
    text = render(observe(root), kept, now)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return text


# checks -----------------------------------------------------------------------------------------
def finding(code, detail):
    return {"code": code, "ok": False, "detail": detail}


def staleness(root, header, observed):
    problems = []
    recorded = header.get("Revision", "")
    if recorded != observed["head"]:
        try:
            check.git(root, "rev-parse", "--verify", "--quiet", f"{recorded}^{{commit}}")
            moved = [p for p in check.git(root, "diff", "--name-only", "--no-renames", "--no-ext-diff",
                                          "--no-textconv", "-z", recorded, "HEAD", "--").split("\0")
                     if p and not_bookkeeping(p)]
        except RuntimeError:
            moved = None
        if moved is None:
            problems.append(finding("CHECKPOINT_STALE", f"recorded revision {recorded or '(none)'} is not a commit here"))
        elif moved:
            problems.append(finding("CHECKPOINT_STALE", f"files committed since the checkpoint: {', '.join(moved[:5])}"))
    recorded_dirty = sorted(p.strip() for p in header.get("Uncommitted files", "").split(",")
                            if p.strip() and p.strip() != "none")
    if recorded_dirty != observed["dirty"]:
        problems.append(finding("CHECKPOINT_STALE", f"uncommitted files are {', '.join(observed['dirty']) or 'none'}, "
                                                    f"checkpoint says {', '.join(recorded_dirty) or 'none'}"))
    feature = observed["feature"]
    if header.get("Feature") != f"{feature['id']} (state: {feature['state']})":
        problems.append(finding("CHECKPOINT_STALE", f"ledger is {feature['id']} ({feature['state']}), "
                                                    f"checkpoint says {header.get('Feature') or '(none)'}"))
    return problems


def completeness(header, sections):
    problems = []
    for name in ("Written", "Feature", "Revision", "Uncommitted files"):
        if not header.get(name):
            problems.append(finding("CHECKPOINT_MISSING_FIELD", f"header line '- {name}:' is missing"))
    for name in SECTIONS:
        if name not in sections:
            problems.append(finding("CHECKPOINT_MISSING_FIELD", f"section '## {name}' is missing"))
    for name in REQUIRED_TEXT:
        if placeholder(sections.get(name)):
            problems.append(finding("CHECKPOINT_MISSING_FIELD", f"'{name}' must say exactly what to do next"))
    if "`" not in sections.get("First command for the next session", ""):
        problems.append(finding("CHECKPOINT_MISSING_FIELD", "the first command must be a runnable command in backticks"))
    return problems


def honesty(sections, observed):
    problems = []
    verified, unverified = sections.get(SECTIONS[0], ""), sections.get(SECTIONS[1], "")
    for claim in observed["feature"]["claims"]:
        if claim in verified and claim not in observed["proven"]:
            problems.append(finding("CHECKPOINT_OVERCLAIM", f"listed as verified without current evidence: {claim}"))
        if claim in observed["unproven"] and claim not in unverified:
            problems.append(finding("CHECKPOINT_UNDECLARED_UNVERIFIED", f"not verified since the last edit but not declared: {claim}"))
    return problems


def load(root):
    text = check.read_artifact(root, CHECKPOINT)
    return parse(text)


def handoff_findings(root):
    """The handoff gate: the last action of a work session."""
    try:
        observed = observe(root)
        header, sections = load(root)
    except (OSError, ValueError, RuntimeError) as error:
        return [finding("HANDOFF_UNREADABLE", f"cannot observe the repository or read the checkpoint: {error}")]
    feature = observed["feature"]
    scope = [f for f in check.session_findings(root, feature)
             if f["code"] in ("SCOPE_OUTSIDE_SURFACE", "SCOPE_EXCLUDED") and f.get("path") in observed["dirty"]]
    for f in scope:
        f["detail"] = "uncommitted and outside the feature's scope: an accidental edit? Revert it or amend the scope."
    return scope + completeness(header, sections) + staleness(root, header, observed) + honesty(sections, observed)


def resume_findings(root):
    """The Resume Protocol: the first action of a work session."""
    try:
        observed = observe(root)
        header, sections = load(root)
    except (OSError, ValueError, RuntimeError) as error:
        return [finding("HANDOFF_UNREADABLE", f"cannot observe the repository or read the checkpoint: {error}")], None
    problems = completeness(header, sections) + staleness(root, header, observed) + honesty(sections, observed)
    feature = observed["feature"]
    answers = [
        f"{feature['outcome']} ({feature['state']})",
        f"checkpoint {header.get('Revision', '(none)')[:12]} with {header.get('Uncommitted files', '(none)')}; "
        f"repository {observed['head'][:12]} with {', '.join(observed['dirty']) or 'none'}",
        "; ".join(observed["proven"]) or "nothing has current evidence",
        "; ".join(observed["unproven"]) or "none",
        sections.get("Suspected causes (not verified)", "(missing)"),
        sections.get("Blockers and commands still to run", "(missing)"),
        sections.get("Decisions to preserve", "(missing)"),
        f"{sections.get('First command for the next session', '(missing)')} / {sections.get('Next bounded edit', '(missing)')}",
    ]
    return problems, answers


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="draft the checkpoint from the observed repository")
    mode.add_argument("--check", action="store_true", help="the handoff gate: run as the last action of a session")
    mode.add_argument("--resume", action="store_true", help="the Resume Protocol: run as the first action of a session")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.write:
        write(root)
        print(f"Wrote {CHECKPOINT}. Fill anything marked {PLACEHOLDER}, then run --check.")
        return 0
    if args.check:
        problems = handoff_findings(root)
    else:
        problems, answers = resume_findings(root)
        for (question, source), answer in zip(QUESTIONS, answers or []):
            print(f"Q  {question}\n   {answer}\n   evidence: {source}")
    for f in problems:
        print(f"FAIL {f['code']} {f.get('path', '')}".rstrip())
        print(f"  {f['detail']}")
    if args.resume and problems:
        print("Checkpoint is stale or incomplete: do not follow its next edit. Re-derive the state from the "
              "repository, then rewrite it with --write.")
    label = "Handoff" if args.check else "Resume"
    print(f"{label} check {'passed' if not problems else 'failed'}.")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
