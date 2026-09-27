"""Move a feature through its lifecycle under the transition policy, with an audit entry.

This is the only supported way to change ``state`` in ``.harness/feature.json``.
Each accepted transition appends one hash-chained line to
``.harness/feature-log.jsonl``; a rejected transition changes no file.

Gates (never executes project commands; reads git and recorded evidence only):
  active -> ready_for_verification   no changed file outside expected_surface or
                                     inside excluded_paths since work started; every
                                     claim has a proof-matrix row with no boundary gap
  ready_for_verification -> passing  a verifier who did not request verification;
                                     every claim has passing evidence at HEAD; clean tree
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import importlib.util
import json
import os
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("harness_check", HERE / "harness_check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

FEATURE_FILE = ".harness/feature.json"


def atomic_write(path, text):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(tmp, path)


def gate_failures(root, feature, entries, rule, target, actor):
    """Return a list of human-readable reasons the transition must be refused."""
    problems = []
    gate = rule.get("gate")
    if gate == "scope":
        starts = [e for e in entries if e["to"] == "active"]
        base = starts[-1]["revision"] if starts else None
        for f in check.session_findings(root, feature, base):
            if f["code"] in ("SCOPE_OUTSIDE_SURFACE", "SCOPE_EXCLUDED", "SESSION_GIT_UNAVAILABLE"):
                problems.append(f"{f['code']} {f.get('path', '')}: {f['detail']}".strip())
        # Asking for verification means saying how each claim will be proven.
        strict = dict(feature, state="ready_for_verification")
        for f in check.proof_findings(root, strict):
            if not f["ok"]:
                problems.append(f"{f['code']}: {f['detail']}")
    if gate == "evidence":
        pending = dict(feature, state="ready_for_verification")
        for f in check.session_findings(root, pending, None):
            if not f["ok"]:
                detail = "; ".join(f.get("errors", [])) or f.get("detail", "")
                problems.append(f"{f['code']} {f.get('path', '') or f.get('detail', '')}: {detail}".strip())
    if rule.get("independent"):
        requested = [e for e in entries if e["to"] == "ready_for_verification"]
        if requested and requested[-1]["actor"] == actor:
            problems.append(f"TRANSITION_NOT_INDEPENDENT: {actor} requested verification and cannot approve it")
    return problems


def transition(root, target, actor, role, reason, now=None):
    """Apply one transition. Returns (ok, messages). Writes nothing when refused."""
    root = root.resolve()
    feature_path = root / FEATURE_FILE
    try:
        text = check.read_artifact(root, FEATURE_FILE)
    except (OSError, ValueError, RuntimeError) as error:
        return False, [f"ARTIFACT_INVALID: cannot read {FEATURE_FILE}: {error}"]
    try:
        feature = json.loads(text)
    except ValueError:
        return False, [f"FEATURE_JSON_INVALID: {FEATURE_FILE} is not valid JSON."]
    if not isinstance(feature, dict):
        return False, [f"FEATURE_JSON_INVALID: {FEATURE_FILE} must be a JSON object."]
    schema = json.loads((check.ROOT / "schemas/feature.schema.json").read_text())
    errors = check.schema_errors(feature, schema)
    if errors:
        return False, ["FEATURE_SCHEMA: fix the feature ledger first:"] + errors

    lines, entries, errors = check.read_log(root)
    if errors:
        return False, ["LOG_INVALID: the transition log is invalid:"] + errors
    lines, entries = lines or [], entries or []
    if entries:
        replay_findings, state = check.replay(lines, entries, feature)
        broken = [f for f in replay_findings if not f["ok"]]
        if broken:
            return False, ["The transition log failed verification:"] + [f"{f['code']}: {f['detail']}" for f in broken]
        if state != feature["state"]:
            return False, [f"STATE_MISMATCH: feature.json says {feature['state']!r}, log says {state!r}."]
        current = state
    else:
        current = "none"
        if feature["state"] not in ("planned", "active") or target != feature["state"]:
            return False, ["LOG_GENESIS_REQUIRED: no transition log yet. Adopt the ledger first with "
                           f"--to {feature['state'] if feature['state'] in ('planned', 'active') else 'planned'} "
                           "--role planner (genesis entry)."]

    rule = check.POLICY.get((current, target))
    if rule is None:
        allowed = sorted(to for (frm, to) in check.POLICY if frm == current)
        return False, [f"TRANSITION_NOT_ALLOWED: {current} -> {target}. Allowed from {current}: {', '.join(allowed) or 'none'}."]
    if role not in rule["roles"]:
        return False, [f"TRANSITION_ROLE_DENIED: {role} may not move {current} -> {target} "
                       f"(allowed: {', '.join(sorted(rule['roles']))})."]
    problems = gate_failures(root, feature, entries, rule, target, actor)
    if problems:
        return False, [f"Gate refused {current} -> {target}:"] + problems

    try:
        revision = check.git(root, "rev-parse", "HEAD").strip()
    except (OSError, RuntimeError) as error:
        return False, [f"SESSION_GIT_UNAVAILABLE: a git repository with a commit is required: {error}"]
    entry = {"seq": len(entries) + 1,
             "at": (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "feature": feature["id"], "from": current, "to": target, "actor": actor,
             "role": role, "revision": revision, "reason": reason,
             "prev": check.line_hash(lines[-1]) if lines else ""}
    if target == "passing":
        entry["claims"] = list(feature["claims"])
    line = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    log_path = root / check.LOG_FILE
    atomic_write(log_path, "\n".join(lines + [line]) + "\n")
    if feature["state"] != target:
        feature["state"] = target
        atomic_write(feature_path, json.dumps(feature, indent=2) + "\n")
    return True, [f"{current} -> {target} recorded as entry {entry['seq']} by {actor} ({role})."]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root (default: current directory)")
    parser.add_argument("--to", required=True, choices=("planned", "active", "blocked", "ready_for_verification", "passing"))
    parser.add_argument("--actor", required=True, help="Who is making the change, e.g. copilot-agent or a GitHub handle")
    parser.add_argument("--role", required=True, choices=("planner", "worker", "verifier"))
    parser.add_argument("--reason", required=True, help="Why; recorded in the audit log")
    args = parser.parse_args(argv)
    if not args.reason.strip() or not args.actor.strip():
        parser.error("--actor and --reason must not be blank")
    ok, messages = transition(args.root, args.to, args.actor.strip(), args.role, args.reason.strip())
    print(messages[0])
    for message in messages[1:]:
        print(f"  {message}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
