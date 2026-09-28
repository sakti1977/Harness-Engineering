"""Would the agent's own tests catch each bug if it came back?

  python3 evals/jyotish/regression.py RUN_DIR       # prints JSON

Builds a correct app, then three copies with exactly one defect put back (sync, age, race), and
runs the agent's tests against each. A test counts only if it passes on the correct app and fails
on the defective one, so tests tied to the agent's own implementation details are not credited.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
FIXES = {
    "sync": ('''                       (user_id, birth_date, birth_time, utc_offset_minutes))
    except sqlite3.Error:
        pass
    return 200, {"synced": True}''', '''                       (user_id, birth_date, birth_time, utc_offset_minutes))
            db.commit()
    except sqlite3.Error:
        return 503, {"synced": False, "error": "not saved"}
    return 200, {"synced": True}'''),
    "age": ('''    born = datetime.fromisoformat(birth_date).replace(tzinfo=timezone.utc)
    born = born.astimezone(timezone(timedelta(minutes=utc_offset_minutes))).date()''',
            '''    born = datetime.strptime(birth_date, "%Y-%m-%d").date()'''),
    "race": ('''        db.execute("INSERT INTO coaching(user_id, chart_version, text) VALUES (?, ?, ?)", (user_id, version, text))
    return 201, {"chart_version": version}''', '''        n = db.execute("INSERT INTO coaching(user_id, chart_version, text) SELECT ?, ?, ? FROM profiles "
                       "WHERE user_id=? AND chart_version=?", (user_id, version, text, user_id, version)).rowcount
    if not n:
        return 409, {"error": "chart changed"}
    return 201, {"chart_version": version}'''),
}
RUNNER = '''import json, unittest
class R(unittest.TestResult):
    def __init__(self):
        super().__init__(); self.status = {}
    def startTest(self, t):
        super().startTest(t); self.status.setdefault(t.id(), "ok")
    def addFailure(self, t, e): super().addFailure(t, e); self.status[t.id()] = "bad"
    def addError(self, t, e): super().addError(t, e); self.status[getattr(t, "id", lambda: str(t))()] = "bad"
    def addSubTest(self, t, s, e):
        super().addSubTest(t, s, e)
        if e is not None: self.status[t.id()] = "bad"
r = R(); unittest.defaultTestLoader.discover("tests").run(r); print(json.dumps(r.status))
'''


def app_with(defect):
    """The task app with every fix applied except ``defect`` ('none' for the fully correct app)."""
    text = (HERE / "task/jyotish/app.py").read_text()
    for name, (broken, fixed) in FIXES.items():
        if name != defect:
            assert broken in text, name
            text = text.replace(broken, fixed)
    return text


def results(tests_dir, defect):
    with TemporaryDirectory() as d:
        d = Path(d)
        (d / "jyotish").mkdir()
        (d / "jyotish/__init__.py").write_text("")
        (d / "jyotish/app.py").write_text(app_with(defect))
        shutil.copytree(tests_dir, d / "tests", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "run_tests.py").write_text(RUNNER)
        r = subprocess.run([sys.executable, "-B", "run_tests.py"], cwd=d, capture_output=True, text=True, timeout=300,
                           env=dict(os.environ, PYTHONPATH=str(d)))
        return json.loads(r.stdout.strip().splitlines()[-1])


def main():
    run = Path(sys.argv[1]).resolve()
    correct = results(run / "tests", "none")
    valid = {t for t, s in correct.items() if s == "ok"}
    report = {"run": run.name, "tests": len(correct), "valid_on_correct_app": len(valid)}
    for defect in FIXES:
        broken = results(run / "tests", defect)
        report[f"catches_{defect}"] = sorted(t.split(".")[-1] for t in valid if broken.get(t) == "bad")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
