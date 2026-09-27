"""Read-only harness checks. Never executes commands from the inspected project.

Default mode validates the harness artifacts. ``--session`` also compares the
session's changed files with the feature contract and, when the feature is
``ready_for_verification``, requires recorded passing evidence for every claim.
"""
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE_FILES = (
    "docs/authority.md", "docs/scope-contract.md", "docs/proof-matrix.md",
    "docs/readiness.md", ".harness/checkpoint.md", ".harness/feature.json",
)
EVIDENCE_FILE = ".harness/evidence.json"
LOG_FILE = ".harness/feature-log.jsonl"

# Transition policy: (from, to) -> roles allowed, gate to pass, independence rule.
# "none" is the genesis state before the log exists.
POLICY = {
    ("none", "planned"): {"roles": {"planner"}},
    ("none", "active"): {"roles": {"planner"}},
    ("planned", "active"): {"roles": {"planner", "worker"}},
    ("active", "blocked"): {"roles": {"planner", "worker"}},
    ("blocked", "active"): {"roles": {"planner", "worker"}},
    ("active", "ready_for_verification"): {"roles": {"worker"}, "gate": "scope"},
    ("ready_for_verification", "active"): {"roles": {"worker", "verifier"}},
    ("ready_for_verification", "passing"): {"roles": {"verifier"}, "gate": "evidence",
                                            "independent": True},
    ("passing", "active"): {"roles": {"planner", "verifier"}},
}
# Harness bookkeeping the agent is expected to update during any session.
ALWAYS_IN_SCOPE = (".harness/",)


def schema_errors(value, schema, location="feature"):
    """Validate the small schema subset used by our versioned feature contract."""
    errors = []
    expected = schema.get("type")
    valid = {"object": isinstance(value, dict), "array": isinstance(value, list),
             "string": isinstance(value, str),
             "integer": isinstance(value, int) and not isinstance(value, bool)}.get(expected, False)
    if not valid:
        return [f"{location}: expected {expected}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: expected one of {schema['enum']}")
    if expected == "string" and len(value.strip()) < schema.get("minLength", 0):
        errors.append(f"{location}: must not be blank")
    if expected == "object":
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{location}.{key}: required")
        props = schema.get("properties", {})
        for key, item in value.items():
            if key in props:
                errors.extend(schema_errors(item, props[key], f"{location}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}.{key}: unknown field")
    if expected == "array":
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: needs at least {schema['minItems']} item(s)")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(x, sort_keys=True) for x in value]
            if len(set(serialized)) != len(serialized):
                errors.append(f"{location}: duplicate items")
        for i, item in enumerate(value):
            errors.extend(schema_errors(item, schema['items'], f"{location}[{i}]"))
    return errors


def path_errors(field, items):
    errors = []
    for item in items if isinstance(items, list) else []:
        if isinstance(item, str):
            parts = PurePosixPath(item).parts
            if (not parts or item.startswith("/") or ".." in parts
                    or "\\" in item or ":" in item):
                errors.append(f"feature.{field}: use project-relative paths without parent traversal")
    return errors


def read_artifact(root, name):
    path = root / name
    # Refuse symlinks outside the inspected project; do not print file contents.
    if not path.resolve().is_relative_to(root):
        raise ValueError("artifact resolves outside project")
    if not path.is_file():
        raise ValueError("required regular file is missing")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("artifact is empty")
    return text


def inspect(root, adapter=None, session=False, base=None):
    root = root.resolve()
    findings = []
    feature_text = None
    names = CORE_FILES + ((".github/copilot-instructions.md",) if adapter == "copilot" else ())
    for name in names:
        try:
            content = read_artifact(root, name)
            findings.append({"code": "ARTIFACT_PRESENT", "path": name, "ok": True})
            if name == ".harness/feature.json":
                feature_text = content
        except (OSError, ValueError, RuntimeError) as error:
            findings.append({"code": "ARTIFACT_INVALID", "path": name, "ok": False,
                             "detail": str(error)})
    if feature_text is not None:
        try:
            data = json.loads(feature_text)
        except (ValueError, RecursionError):
            findings.append({"code": "FEATURE_JSON_INVALID", "ok": False,
                             "detail": "Use a UTF-8 JSON object with the documented fields."})
        else:
            schema = json.loads((ROOT / "schemas/feature.schema.json").read_text())
            errors = schema_errors(data, schema)
            if isinstance(data, dict):
                errors += path_errors("expected_surface", data.get("expected_surface"))
                errors += path_errors("excluded_paths", data.get("excluded_paths"))
            findings.append({"code": "FEATURE_SCHEMA", "ok": not errors, "errors": errors})
            if not errors:
                findings.extend(log_findings(root, data, base))
            if session:
                if errors:
                    findings.append({"code": "SESSION_SKIPPED", "ok": False,
                                     "detail": "Fix the feature ledger before checking a session."})
                else:
                    findings.extend(session_findings(root, data, base))
    limitations = ["No project commands executed", "No readiness or task outcome verified",
                   "No sandbox or authority policy enforced"]
    if session:
        limitations.append("Evidence entries are recorded observations; commands are not re-run")
    return {"schema_version": 1, "root": str(root),
            "scope": "session-scope-and-evidence" if session else "artifact-and-ledger-validation",
            "ok": all(item["ok"] for item in findings), "findings": findings,
            "limitations": limitations}


def git(root, *args):
    """Run a read-only git query. Hooks, fsmonitor, external diff and textconv are disabled."""
    command = ["git", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
               "-c", "diff.external=", "-C", str(root), *args]
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_EXTERNAL_DIFF", "GIT_DIR", "GIT_WORK_TREE")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(command, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "git failed")
    return result.stdout


def changed_files(root, base):
    """Files changed since ``base`` (committed, staged, unstaged) plus untracked files."""
    tracked = git(root, "diff", "--name-only", "--no-renames", "--no-ext-diff", "--no-textconv",
                  "-z", base or "HEAD", "--")
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted({p for p in (tracked + untracked).split("\0") if p})


def matches(path, pattern):
    """Exact file, directory prefix (``dir`` or ``dir/``) or glob (``*``, ``?``, ``[``)."""
    if any(ch in pattern for ch in "*?["):
        return fnmatchcase(path, pattern)
    pattern = pattern.rstrip("/")
    return path == pattern or path.startswith(pattern + "/")


def load_evidence(root):
    path = root / EVIDENCE_FILE
    if not path.exists():
        return None, []
    try:
        data = json.loads(read_artifact(root, EVIDENCE_FILE))
    except (OSError, ValueError, RuntimeError) as error:
        return None, [f"evidence: {error}"]
    schema = json.loads((ROOT / "schemas/evidence.schema.json").read_text())
    return data, schema_errors(data, schema, "evidence")


def session_findings(root, feature, base=None):
    findings = []
    try:
        git(root, "rev-parse", "--verify", "HEAD")
        changed = changed_files(root, base)
    except (OSError, RuntimeError) as error:
        return [{"code": "SESSION_GIT_UNAVAILABLE", "ok": False,
                 "detail": f"Session checks need a git repository with a commit: {error}"}]

    surface = feature["expected_surface"]
    excluded = feature.get("excluded_paths", [])
    work = [p for p in changed if not any(p.startswith(a) for a in ALWAYS_IN_SCOPE)]
    outside = [p for p in work if not any(matches(p, s) for s in surface)]
    touched_exclusions = [p for p in work if any(matches(p, e) for e in excluded)]
    findings.append({"code": "SESSION_CHANGES", "ok": True, "path": base or "HEAD",
                     "detail": f"{len(changed)} changed file(s), {len(work)} outside harness bookkeeping"})
    for path in outside:
        findings.append({"code": "SCOPE_OUTSIDE_SURFACE", "ok": False, "path": path,
                         "detail": "Not in expected_surface: amend the scope with a reason, or revert."})
    for path in touched_exclusions:
        findings.append({"code": "SCOPE_EXCLUDED", "ok": False, "path": path,
                         "detail": "Matches excluded_paths: this work is not funded by the task."})
    if feature["exclusions"]:
        findings.append({"code": "EXCLUSIONS_REMINDER", "ok": True,
                         "detail": "Review manually: " + "; ".join(feature["exclusions"])})

    evidence, errors = load_evidence(root)
    ready = feature["state"] == "ready_for_verification"
    if errors:
        findings.append({"code": "EVIDENCE_INVALID", "ok": False, "errors": errors})
        return findings
    entries = evidence or []
    claims = feature["claims"]
    for entry in entries:
        if entry["claim"] not in claims:
            findings.append({"code": "EVIDENCE_UNKNOWN_CLAIM", "ok": False, "detail": entry["claim"],
                             "errors": ["Quote the claim exactly as written in feature.json."]})
    dirty_work = [p for p in git(root, "status", "--porcelain", "-z", "--no-renames", "--untracked-files=all").split("\0")
                  if p and not any(p[3:].startswith(a) for a in ALWAYS_IN_SCOPE)]
    since_cache = {}

    def changed_since(revision):
        """Project files changed after ``revision``; None if it is not a commit here."""
        if revision not in since_cache:
            try:
                git(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
                since_cache[revision] = [p for p in changed_files(root, revision)
                                         if not any(p.startswith(a) for a in ALWAYS_IN_SCOPE)]
            except RuntimeError:
                since_cache[revision] = None
        return since_cache[revision]

    for claim in claims:
        recorded = [e for e in entries if e["claim"] == claim]
        latest = recorded[-1] if recorded else None
        if latest is None:
            problem = "no evidence recorded"
        elif latest["result"] != "pass":
            problem = "latest evidence did not pass"
        elif len(latest["revision"]) < 7 or latest["revision"].startswith("-"):
            problem = "evidence revision must be a commit id of at least 7 characters"
        elif changed_since(latest["revision"]) is None:
            problem = f"evidence revision {latest['revision']} is not a commit in this repository"
        elif dirty_work:
            problem = "files changed after the evidence was recorded (uncommitted work)"
        elif changed_since(latest["revision"]):
            files = ", ".join(changed_since(latest["revision"])[:5])
            problem = f"evidence recorded at {latest['revision'][:12]}; project files changed since: {files}"
        else:
            findings.append({"code": "CLAIM_PROVEN", "ok": True, "detail": claim})
            continue
        findings.append({"code": "CLAIM_UNPROVEN" if ready else "CLAIM_PENDING", "ok": not ready,
                         "detail": claim, "errors": [problem]})
    return findings


def line_hash(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def read_log(root):
    """Return (raw lines, entries, errors). Missing log -> (None, None, [])."""
    if not (root / LOG_FILE).exists():
        return None, None, []
    try:
        text = read_artifact(root, LOG_FILE)
    except (OSError, ValueError, RuntimeError) as error:
        return None, None, [f"log: {error}"]
    lines = text.rstrip("\n").split("\n")
    schema = json.loads((ROOT / "schemas/feature-log.schema.json").read_text())
    entries, errors = [], []
    for number, line in enumerate(lines, 1):
        try:
            entry = json.loads(line)
        except ValueError:
            errors.append(f"log line {number}: not JSON")
            continue
        errors += schema_errors(entry, schema, f"log line {number}")
        entries.append(entry)
    return lines, entries, errors


def replay(lines, entries, feature):
    """Check the hash chain and every transition against POLICY. Returns (findings, state)."""
    findings, state, requester = [], "none", None
    for i, (line, entry) in enumerate(zip(lines, entries)):
        where = f"log line {i + 1}"
        expected_prev = line_hash(lines[i - 1]) if i else ""
        if entry["seq"] != i + 1 or entry["prev"] != expected_prev:
            findings.append({"code": "LOG_CHAIN_BROKEN", "ok": False, "path": where,
                             "detail": "Sequence or hash chain broken: an entry was edited, removed or reordered."})
            return findings, None
        if entry["feature"] != feature["id"]:
            findings.append({"code": "LOG_FEATURE_MISMATCH", "ok": False, "path": where,
                             "detail": f"Entry is for {entry['feature']!r}, ledger is {feature['id']!r}."})
        if entry["from"] != state:
            findings.append({"code": "TRANSITION_NOT_ALLOWED", "ok": False, "path": where,
                             "detail": f"Entry starts from {entry['from']!r} but the state was {state!r}."})
        rule = POLICY.get((entry["from"], entry["to"]))
        if rule is None:
            findings.append({"code": "TRANSITION_NOT_ALLOWED", "ok": False, "path": where,
                             "detail": f"{entry['from']} -> {entry['to']} is not in the transition policy."})
        else:
            if entry["role"] not in rule["roles"]:
                findings.append({"code": "TRANSITION_ROLE_DENIED", "ok": False, "path": where,
                                 "detail": f"{entry['role']} may not move {entry['from']} -> {entry['to']}."})
            if rule.get("independent") and requester and entry["actor"] == requester:
                findings.append({"code": "TRANSITION_NOT_INDEPENDENT", "ok": False, "path": where,
                                 "detail": f"{entry['actor']} requested verification and cannot also approve it."})
            if entry["to"] == "passing" and sorted(entry.get("claims", [])) != sorted(feature["claims"]):
                findings.append({"code": "PASSING_STALE", "ok": False, "path": where,
                                 "detail": "Claims changed after they were verified; reopen and verify again."})
        if entry["to"] == "ready_for_verification":
            requester = entry["actor"]
        state = entry["to"]
    return findings, state


def log_findings(root, feature, base=None):
    lines, entries, errors = read_log(root)
    if lines is None and not errors:
        if feature["state"] == "passing":
            return [{"code": "PASSING_WITHOUT_LOG", "ok": False,
                     "detail": "passing is only accepted through a verified transition log; "
                               "use scripts/harness_transition.py."}]
        return []
    if errors:
        return [{"code": "LOG_INVALID", "ok": False, "path": LOG_FILE, "errors": errors}]
    findings, state = replay(lines, entries, feature)
    if state is not None and state != feature["state"]:
        findings.append({"code": "STATE_MISMATCH", "ok": False, "path": ".harness/feature.json",
                         "detail": f"feature.json says {feature['state']!r} but the log ends at {state!r}; "
                                   "change state only through scripts/harness_transition.py."})
    # Append-only: the committed log (and the session base's log) must be a prefix of this one.
    current = "\n".join(lines)
    for revision in dict.fromkeys(r for r in ("HEAD", base) if r):
        try:
            earlier = git(root, "show", f"{revision}:{LOG_FILE}").rstrip("\n")
        except (OSError, RuntimeError):
            continue  # not committed there yet, or no git: nothing to compare
        if earlier and not (current == earlier or current.startswith(earlier + "\n")):
            findings.append({"code": "LOG_REWRITTEN", "ok": False, "path": LOG_FILE,
                             "detail": f"The log at {revision} is not a prefix of the current log."})
    # Invalidation: passing proof goes stale when project files change after it.
    if state == "passing" and not findings:
        passed_at = entries[-1]["revision"]
        try:
            changed = [p for p in changed_files(root, passed_at)
                       if not any(p.startswith(a) for a in ALWAYS_IN_SCOPE)]
        except (OSError, RuntimeError) as error:
            findings.append({"code": "PASSING_UNVERIFIABLE", "ok": False,
                             "detail": f"Cannot compare with the verified revision: {error}"})
        else:
            if changed:
                findings.append({"code": "PASSING_STALE", "ok": False, "path": ", ".join(changed[:5]),
                                 "detail": "Files changed after verification; reopen (passing -> active) and verify again."})
    if not any(not f["ok"] for f in findings):
        findings.append({"code": "LOG_VERIFIED", "ok": True, "path": LOG_FILE,
                         "detail": f"{len(entries)} transition(s), chain intact, state {state}"})
    return findings


def summary(result):
    codes = [item["code"] for item in result["findings"]]
    proven = codes.count("CLAIM_PROVEN")
    claims = proven + codes.count("CLAIM_UNPROVEN") + codes.count("CLAIM_PENDING")
    return (f"Session: {codes.count('SCOPE_OUTSIDE_SURFACE')} file(s) outside scope, "
            f"{codes.count('SCOPE_EXCLUDED')} in excluded paths, {proven} of {claims} claim(s) proven.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project to inspect (read-only)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--adapter", choices=("copilot",), help="Also require this adapter's instruction file")
    parser.add_argument("--session", action="store_true",
                        help="Also check changed files against the feature scope and claims against recorded evidence")
    parser.add_argument("--base", help="Git revision the session started from (default: HEAD, i.e. uncommitted work)")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error("--root must be an existing directory")
    if args.base and not args.session:
        parser.error("--base requires --session")
    if args.base and args.base.startswith("-"):
        parser.error("--base must be a revision, not an option")
    result = inspect(args.root, args.adapter, args.session, args.base)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        for item in result["findings"]:
            label = "PASS" if item["ok"] else "FAIL"
            if item["code"] in ("CLAIM_PENDING", "EXCLUSIONS_REMINDER", "SESSION_CHANGES"):
                label = "INFO"
            print(f"{label} {item['code']} {item.get('path', '')}".rstrip())
            for error in item.get("errors", []):
                print(f"  {error}")
            if "detail" in item:
                print(f"  {item['detail']}")
        if args.session:
            print(summary(result))
            print("Harness session checks passed." if result["ok"] else "Harness session checks failed.")
            print("Scope: read-only git queries and recorded evidence; no project commands were executed.")
        else:
            print("Harness artifact checks passed." if result["ok"] else "Harness artifact checks failed.")
            print("Scope: artifact and ledger validation only; no project commands were executed.")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
