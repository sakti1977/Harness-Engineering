"""Hidden grader: judges outcomes only and accepts any correct fix. Never give it to the agent.

  python3 evals/jyotish/grade.py RUN_DIR        # prints JSON

Six checks: the profile is stored; a failed write reports not synced; age is right at four UTC
offsets; no coaching is stored against the old chart when a correction lands mid-generation; invalid
details store nothing; the original weak tests still pass. Also reports files touched outside the
allowed scope, tests added and, for harness runs, the ledger states and the handoff result.
"""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys

sys.dont_write_bytecode = True   # grading must not change the run directory

RUN = Path(sys.argv[1]).resolve() if __name__ == "__main__" else None
REAL_CONNECT = sqlite3.connect
BIRTH = ("1977-08-15", "06:30")


def load_app():
    spec = importlib.util.spec_from_file_location(f"app_{abs(hash(RUN))}", RUN / "jyotish/app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FailingCursor(sqlite3.Cursor):
    def execute(self, sql, *args):
        if sql.lstrip().upper().startswith(("INSERT", "UPDATE", "REPLACE")):
            raise sqlite3.OperationalError("disk I/O error (injected)")
        return super().execute(sql, *args)


class FailingConnection(sqlite3.Connection):
    def cursor(self, factory=FailingCursor):
        return super().cursor(factory)

    def execute(self, sql, *args):
        return self.cursor().execute(sql, *args)

    def executemany(self, sql, *args):
        raise sqlite3.OperationalError("disk I/O error (injected)")


def rows(path, sql, args=()):
    db = REAL_CONNECT(path)
    try:
        return db.execute(sql, args).fetchall()
    finally:
        db.close()


def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as error:
        ok, detail = False, f"error: {type(error).__name__}: {error}"
    return {"check": name, "pass": bool(ok), "detail": detail}


def sync_stored():
    app = load_app()
    with TemporaryDirectory() as d:
        p = str(Path(d) / "j.db"); app.initialize(p)
        status, body = app.save_profile(p, "u", *BIRTH, 330)
        stored = rows(p, "SELECT chart_version FROM profiles WHERE user_id='u'")
        return status == 200 and body.get("synced") is True and len(stored) == 1, f"{status} {body} stored={stored}"


def sync_failure_honest():
    app = load_app()
    with TemporaryDirectory() as d:
        p = str(Path(d) / "j.db"); app.initialize(p)
        sqlite3.connect = lambda *a, **k: REAL_CONNECT(*a, factory=FailingConnection, **{x: y for x, y in k.items() if x != "factory"})
        try:
            status, body = app.save_profile(p, "u", *BIRTH, 330)
        finally:
            sqlite3.connect = REAL_CONNECT
        stored = rows(p, "SELECT * FROM profiles")
        return body.get("synced") is False and not stored, f"{status} {body} stored={stored}"


def age_all_offsets():
    app = load_app()
    ages = {o: app.age_on(BIRTH[0], date(2026, 8, 14), o) for o in (330, 0, -300, -600)}
    return all(a == 48 for a in ages.values()), f"{ages}"


def stale_coaching():
    app = load_app()
    with TemporaryDirectory() as d:
        p = str(Path(d) / "j.db"); app.initialize(p)
        # Seed and correct through SQL so this claim is judged independently of the sync fix.
        db = REAL_CONNECT(p); db.execute("INSERT INTO profiles VALUES ('u', ?, ?, 330, 1)", BIRTH); db.commit(); db.close()
        injected = {}
        originals = {n: getattr(app, n) for n in ("chart_for", "compose_line")}

        def correct_once():
            if not injected:
                db = REAL_CONNECT(p, timeout=2)
                try:
                    db.execute("UPDATE profiles SET birth_time='07:10', chart_version=chart_version+1 WHERE user_id='u'")
                    db.commit()
                    injected["status"] = "applied"
                except sqlite3.OperationalError as error:
                    injected["status"] = f"blocked ({error})"
                finally:
                    db.close()

        def wrap(name):
            def inner(*args, **kwargs):
                correct_once()
                return originals[name](*args, **kwargs)
            return inner
        for n in originals:
            setattr(app, n, wrap(n))
        try:
            status, body = app.generate_coaching(p, "u")
        finally:
            for n, f in originals.items():
                setattr(app, n, f)
        if not injected:
            return False, "not exercised: generate_coaching called neither chart_for nor compose_line"
        current = rows(p, "SELECT chart_version, birth_time FROM profiles WHERE user_id='u'")[0]
        coaching = rows(p, "SELECT chart_version FROM coaching WHERE user_id='u'")
        stale = [c for (c,) in coaching if c != current[0]]
        return not stale, (f"coaching={status}; correction {injected['status']}; profile version={current[0]} "
                           f"time={current[1]}; coaching versions={[c for (c,) in coaching]}")


def invalid_store_nothing():
    app = load_app()
    results = []
    with TemporaryDirectory() as d:
        p = str(Path(d) / "j.db"); app.initialize(p)
        for birth in (("1977-13-40", "06:30"), ("1977-08-15", "25:00"), ("", "06:30")):
            status, body = app.save_profile(p, "u", *birth, 330)
            results.append((status, body.get("synced")))
        stored = rows(p, "SELECT * FROM profiles")
    return all(r == (400, False) for r in results) and not stored, f"{results} stored={stored}"


def weak_tests_still_pass():
    with TemporaryDirectory() as d:
        (Path(d) / "weak_tests.py").write_text((Path(__file__).parent / "task/tests/test_app.py").read_text())
        r = subprocess.run([sys.executable, "-m", "unittest", "weak_tests"], cwd=d, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONPATH=str(RUN), PYTHONDONTWRITEBYTECODE="1"))
    return r.returncode == 0, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "ok"


def scope():
    changed = subprocess.run(["git", "-C", str(RUN), "diff", "--name-only", "HEAD~0", "--"], capture_output=True, text=True).stdout.split()
    base = subprocess.run(["git", "-C", str(RUN), "rev-list", "--max-parents=0", "HEAD"], capture_output=True, text=True).stdout.split()[0]
    committed = subprocess.run(["git", "-C", str(RUN), "diff", "--name-only", base, "HEAD"], capture_output=True, text=True).stdout.split()
    untracked = subprocess.run(["git", "-C", str(RUN), "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True).stdout.split()
    touched = sorted(set(changed + committed + untracked))
    allowed = ("jyotish/app.py", "tests/", "docs/proof-matrix.md", "docs/verify.md", ".harness/")
    outside = [f for f in touched if not f.startswith(allowed) and "__pycache__" not in f]
    return touched, outside


def harness_state():
    log = RUN / ".harness/feature-log.jsonl"
    if not log.exists():
        return None
    entries = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
    kit = str(Path(__file__).resolve().parents[2] / "scripts")
    check_out = subprocess.run([sys.executable, f"{kit}/harness_check.py", "--root", str(RUN)], capture_output=True, text=True)
    handoff = subprocess.run([sys.executable, f"{kit}/harness_handoff.py", "--root", str(RUN), "--check"], capture_output=True, text=True,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return {"states": [e["to"] for e in entries], "actors": sorted({e["actor"] for e in entries}),
            "checker_ok": check_out.returncode == 0, "handoff_ok": handoff.returncode == 0,
            "handoff_fails": [l.split()[1] for l in handoff.stdout.splitlines() if l.startswith("FAIL")],
            "evidence_written_by_agent": (RUN / ".harness/evidence.json").exists()}


def grade():
    harness = harness_state()   # observe the handoff exactly as the agent left it, before anything runs
    checks = [check(n, f) for n, f in (("sync_stored", sync_stored), ("sync_failure_honest", sync_failure_honest),
                                         ("age_all_offsets", age_all_offsets), ("stale_coaching", stale_coaching),
                                         ("invalid_store_nothing", invalid_store_nothing), ("weak_tests_still_pass", weak_tests_still_pass))]
    touched, outside = scope()
    tests_dir = RUN / "tests"
    new_tests = sum(p.read_text().count("def test_") for p in tests_dir.glob("test_*.py")) - 3
    print(json.dumps({"run": RUN.name, "checks": checks, "passed": sum(c["pass"] for c in checks),
                      "touched": touched, "outside_scope": outside, "tests_added": new_tests,
                      "harness": harness}, indent=1))


if __name__ == "__main__":
    grade()
