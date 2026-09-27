"""Fidelity ablation: weaken the stale-coaching route one dimension at a time.

This tests the verification route, not the product. Each variant runs against the BROKEN app.
A variant that passes is a false pass: that weakening would have let the defect ship.
"""
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from threading import Event, Thread
import sys
from examples.astro.astro import generate_coaching, initialize, save_profile, stale_rows

USER, BIRTH, IST = "user-1", ("1977-08-15", "06:30"), 330


def run_route(broken, *, concurrent=True, shared_store=True, expect="409", check_persistence=True):
    """Run the stale-coaching route with the given fidelity. Returns (route_passed, observed)."""
    with TemporaryDirectory() as directory:
        coach_db = Path(directory) / "coach.db"
        initialize(coach_db)
        save_profile(coach_db, USER, *BIRTH, IST)
        correction_db = coach_db
        if not shared_store:
            correction_db = Path(directory) / "correction.db"
            copyfile(coach_db, correction_db)   # each actor gets its own store, as a per-test mock would
        result = {}
        if concurrent:
            read_done, update_done = Event(), Event()

            def pause(name):
                if name == "after_read":
                    read_done.set()
                    update_done.wait(timeout=10)

            def coach():
                result["status"] = generate_coaching(coach_db, USER, broken=broken, checkpoint=pause)[0]

            def correct():
                read_done.wait(timeout=10)
                save_profile(correction_db, USER, BIRTH[0], "07:10", IST)
                update_done.set()

            threads = [Thread(target=coach), Thread(target=correct)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=15)
        else:
            result["status"] = generate_coaching(coach_db, USER, broken=broken)[0]
            save_profile(correction_db, USER, BIRTH[0], "07:10", IST)
        stale = len(stale_rows(coach_db, USER))
        response_ok = {"409": result["status"] == 409, "201": result["status"] == 201,
                       "<500": result["status"] < 500}[expect]
        persistence_ok = stale == 0 if check_persistence else True
        return response_ok and persistence_ok, f"status {result['status']}, stale rows {stale}"


VARIANTS = [
    ("faithful route", {}),
    ("run sequentially", {"concurrent": False}),
    ("run sequentially, test edited to expect 201", {"concurrent": False, "expect": "201"}),
    ("separate store per actor, any status < 500", {"shared_store": False, "expect": "<500"}),
    ("accept any status < 500", {"expect": "<500"}),
    ("drop the stored-state check", {"check_persistence": False}),
    ("status < 500 and no state check", {"expect": "<500", "check_persistence": False}),
]


def classify(broken_passed, fixed_passed):
    if broken_passed:
        return "FALSE PASS"      # the defect would ship
    if not fixed_passed:
        return "always red"      # rejects the fix too: someone will be tempted to edit it
    return "discriminates"


EXPECTED = {
    "faithful route": "discriminates",
    "run sequentially": "always red",
    "run sequentially, test edited to expect 201": "FALSE PASS",
    "separate store per actor, any status < 500": "FALSE PASS",
    "accept any status < 500": "discriminates",
    "drop the stored-state check": "discriminates",
    "status < 500 and no state check": "FALSE PASS",
}


def results():
    rows = []
    for name, options in VARIANTS:
        broken_passed, broken_observed = run_route(True, **options)
        fixed_passed, _ = run_route(False, **options)
        rows.append((name, classify(broken_passed, fixed_passed), broken_observed))
    return rows


def main():
    rows = results()
    print(f"{'route variant':<46} {'verdict':<15} observed on the broken app")
    for name, verdict, observed in rows:
        print(f"{name:<46} {verdict:<15} {observed}")
    print("\ndiscriminates = fails on the broken app, passes on the fixed app.")
    print("The response and stored-state checks cover for each other: weaken one and the other still catches it.")
    print("Sequential runs and per-actor stores remove the race itself; they only look green after the test is bent to fit.")
    ok = {name: verdict for name, verdict, _ in rows} == EXPECTED
    print("ABLATION PASSED: every weakening behaved as expected. Removing the race, or both checks, lets the defect ship."
          if ok else "ABLATION FAILED: unexpected behavior.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
