"""Named defects for the harness tests. Each takes a Scratch copy of the fixture and breaks one thing.

A defect may first set up a legitimate state (for example, run real transitions to reach
ready_for_verification) and then introduce exactly one fault. Setup uses the real harness
code; only the fault is hand-made.
"""
import json
import shutil

CLAIMS_ROW_1 = "saving a profile reports synced only when the profile is stored"


# setup helpers -------------------------------------------------------------------------
def activate(s):
    s.move("active", "planner", "sakti", "adopt the ledger")


def reach_ready(s, *, actor="copilot-agent"):
    activate(s)
    s.write("src/profile.py", s.read("src/profile.py") + "\n# commit only after the write succeeds\n")
    s.commit()
    s.move("ready_for_verification", "worker", actor, "claims covered")


def record_evidence(s, claims=None, revision=None):
    head = revision or s.head()
    s.write(".harness/evidence.json", json.dumps(
        [{"claim": c, "command": "python3 -m unittest tests.test_profile -v", "result": "pass", "revision": head}
         for c in (s.feature()["claims"] if claims is None else claims)]))


def reach_passing(s, *, commit_log=True):
    reach_ready(s)
    record_evidence(s)
    if commit_log:
        s.commit()
    s.move("passing", "verifier", "sakti", "evidence reviewed")
    if commit_log:
        s.commit()


def append_forged(s, **fields):
    """Append a hand-written entry with a valid hash chain, so only the policy can reject it."""
    lines = s.read(".harness/feature-log.jsonl").splitlines()
    entry = {"seq": len(lines) + 1, "at": "2026-01-01T00:00:00Z", "feature": s.feature()["id"],
             "actor": "copilot-agent", "role": "worker", "revision": s.head(), "reason": "forged",
             "prev": s.check.line_hash(lines[-1])}
    entry.update(fields)
    lines.append(json.dumps(entry, sort_keys=True, separators=(",", ":")))
    s.write(".harness/feature-log.jsonl", "\n".join(lines) + "\n")
    s.set_feature(state=entry["to"])


def matrix_row(s, claim, replacement):
    lines = s.read("docs/proof-matrix.md").splitlines()
    out = [replacement if line.startswith(f"| {claim} |") else line for line in lines]
    out = [line for line in out if line is not None]
    s.write("docs/proof-matrix.md", "\n".join(out) + "\n")


# clean setups (no defect) ----------------------------------------------------------------
def none(s):
    pass


def activated(s):
    activate(s)


def activated_with_in_scope_change(s):
    activate(s)
    s.write("src/profile.py", s.read("src/profile.py") + "\n# in-scope change\n")
    s.commit()


def ready_with_evidence(s):
    reach_ready(s)
    record_evidence(s)
    s.commit()


def verified_passing(s):
    reach_passing(s)


# artifact defects -------------------------------------------------------------------------
def missing_artifact(s):
    s.delete("docs/readiness.md")


def ledger_not_json(s):
    s.write(".harness/feature.json", "{")


def ledger_bad_state(s):
    s.set_feature(state="banana")


def self_attested_passing(s):
    s.set_feature(state="passing")


def ready_without_log(s):
    s.set_feature(state="ready_for_verification")


def proof_no_table(s):
    ready_without_log(s)
    s.write("docs/proof-matrix.md", "# Claim-to-Proof Matrix\n\nWe test the important things.\n")


def proof_claim_missing(s):
    ready_without_log(s)
    lines = [l for l in s.read("docs/proof-matrix.md").splitlines() if not l.startswith(f"| {CLAIMS_ROW_1} |")]
    s.write("docs/proof-matrix.md", "\n".join(lines) + "\n")


def proof_unknown_claim(s):
    ready_without_log(s)
    s.write("docs/proof-matrix.md", s.read("docs/proof-matrix.md") +
            "| profiles sync across devices | badge | entry | `t` | entry | |\n")


def proof_producer_missing(s):
    ready_without_log(s)
    matrix_row(s, CLAIMS_ROW_1, f"| {CLAIMS_ROW_1} | read back | entry, persistence | TBD | entry, persistence | |")


def proof_boundary_unknown(s):
    ready_without_log(s)
    matrix_row(s, CLAIMS_ROW_1, f"| {CLAIMS_ROW_1} | read back | api, database | `t` | api, database | |")


def proof_boundary_gap(s):
    ready_without_log(s)
    matrix_row(s, CLAIMS_ROW_1, f"| {CLAIMS_ROW_1} | read back | entry, persistence | `test_save_reports_synced` | entry | |")


# audit-log defects ------------------------------------------------------------------------
def log_not_json(s):
    s.write(".harness/feature-log.jsonl", "not json\n")


def log_entry_edited(s):
    activate(s)
    s.move("blocked", "worker", "copilot-agent", "waiting on schema review")
    s.write(".harness/feature-log.jsonl", s.read(".harness/feature-log.jsonl").replace('"adopt the ledger"', '"rewritten"'))


def log_feature_renamed(s):
    activate(s)
    s.set_feature(id="profile-sync-v2")


def forged_skip_to_passing(s):
    activate(s)
    append_forged(s, **{"from": "active", "to": "passing", "role": "verifier", "claims": s.feature()["claims"]})


def forged_wrong_role(s):
    activate(s)
    append_forged(s, **{"from": "active", "to": "ready_for_verification", "role": "verifier"})


def forged_self_approval(s):
    reach_ready(s)
    append_forged(s, **{"from": "ready_for_verification", "to": "passing", "role": "verifier",
                        "actor": "copilot-agent", "claims": s.feature()["claims"]})


def state_hand_edited(s):
    activate(s)
    s.set_feature(state="ready_for_verification")


def committed_log_rewritten(s):
    activate(s)
    s.commit()
    entries = [json.loads(line) for line in s.read(".harness/feature-log.jsonl").splitlines()]
    entries[0]["actor"] = "someone-else"
    s.write(".harness/feature-log.jsonl", json.dumps(entries[0], sort_keys=True, separators=(",", ":")) + "\n")


def passing_then_code_changed(s):
    reach_passing(s)
    s.write("src/profile.py", s.read("src/profile.py") + "\n# a later session edits verified code\n")
    s.commit()


def passing_then_claims_changed(s):
    reach_passing(s)
    claim = "a rejected write reports synced false"
    s.set_feature(claims=s.feature()["claims"] + [claim])
    s.write("docs/proof-matrix.md", s.read("docs/proof-matrix.md") +
            f"| {claim} | 503 and synced false | entry | `t` | entry | None |\n")


def passing_revision_unknown(s):
    reach_passing(s, commit_log=False)
    lines = s.read(".harness/feature-log.jsonl").splitlines()
    entries = [json.loads(line) for line in lines]
    entries[-1]["revision"] = "0" * 40
    out = []
    for entry in entries:
        entry["prev"] = s.check.line_hash(out[-1]) if out else ""
        out.append(json.dumps(entry, sort_keys=True, separators=(",", ":")))
    s.write(".harness/feature-log.jsonl", "\n".join(out) + "\n")


# session defects --------------------------------------------------------------------------
def edit_outside_surface(s):
    s.write("src/other.py", "def unrelated():\n    return 'tidied by the agent'\n")


def edit_excluded_path(s):
    s.set_feature(expected_surface=["src/", "tests/test_profile.py"])
    s.commit()
    s.write("src/payments/upi.py", 'UPI_ID = "changed"\n')


def no_git(s):
    shutil.rmtree(s.root / ".git")


def ledger_path_traversal(s):
    s.set_feature(expected_surface=["../outside"])


def evidence_not_a_list(s):
    s.write(".harness/evidence.json", "{}")


def evidence_reworded_claim(s):
    record_evidence(s, claims=["profile sync works"])


def ready_without_evidence(s):
    ready_without_log(s)


# transition defects -----------------------------------------------------------------------
def ready_after_out_of_scope_commit(s):
    activate(s)
    s.write("src/other.py", "def unrelated():\n    return 'refactored'\n")
    s.commit()


def proof_gap_before_activation(s):
    proof_boundary_gap_body(s)
    s.commit()
    activate(s)


def proof_boundary_gap_body(s):
    matrix_row(s, CLAIMS_ROW_1, f"| {CLAIMS_ROW_1} | read back | entry, persistence | `test_save_reports_synced` | entry | |")


def ready_no_evidence(s):
    reach_ready(s)


def ready_stale_evidence(s):
    reach_ready(s)
    record_evidence(s)
    s.commit()
    s.write("src/profile.py", s.read("src/profile.py") + "\n# changed after the evidence\n")
    s.commit()


def missing_ledger(s):
    s.delete(".harness/feature.json")


# handoff and resume -----------------------------------------------------------------------
NEXT_EDIT = "Add the read-back assertion to test_synced_only_when_stored in tests/test_profile.py."


def write_checkpoint(s):
    s.handoff.write(s.root)
    s.write(".harness/checkpoint.md", s.read(".harness/checkpoint.md").replace(
        "## Next bounded edit\n\nTODO", f"## Next bounded edit\n\n{NEXT_EDIT}"))


def checkpoint_with_dirty_work(s):
    s.write("src/profile.py", s.read("src/profile.py") + "\n# work in progress\n")
    write_checkpoint(s)


def checkpoint_with_evidence(s):
    s.write("src/profile.py", s.read("src/profile.py") + "\n# finished\n")
    s.commit()
    record_evidence(s)
    s.commit()
    write_checkpoint(s)


def checkpoint_over_accidental_edit(s):
    s.write("src/other.py", "def unrelated():\n    return 'accidentally edited'\n")
    write_checkpoint(s)


def checkpoint_next_edit_left_blank(s):
    s.handoff.write(s.root)


def checkpoint_overclaims(s):
    write_checkpoint(s)
    text = s.read(".harness/checkpoint.md").replace(
        "Nothing has current evidence.", f"- {CLAIMS_ROW_1}: `python3 -m unittest` passed (from memory)")
    s.write(".harness/checkpoint.md", text)


def checkpoint_hides_unverified(s):
    write_checkpoint(s)
    s.write(".harness/checkpoint.md", s.read(".harness/checkpoint.md").replace(f"- {CLAIMS_ROW_1}\n", ""))


def commit_after_checkpoint(s):
    checkpoint_with_dirty_work(s)
    s.commit()


def edit_after_checkpoint(s):
    checkpoint_with_dirty_work(s)
    s.write("src/other.py", "def unrelated():\n    return 'changed after the handoff'\n")


def state_changed_after_checkpoint(s):
    activate(s)
    write_checkpoint(s)
    s.move("blocked", "worker", "copilot-agent", "waiting on review")


def evidence_outdated_after_checkpoint(s):
    checkpoint_with_evidence(s)
    s.write("src/profile.py", s.read("src/profile.py") + "\n# changed after the handoff\n")
    s.commit()


def checkpoint_deleted(s):
    s.delete(".harness/checkpoint.md")
