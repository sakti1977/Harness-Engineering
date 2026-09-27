"""Interleaving sweep: inject a birth-time correction at every step of coaching generation.

A sequential run tests only the first and last points. One concurrent run tests one point.
The sweep tests them all, deterministically, for both variants. Then it shows how often
free-running threads (no synchronization) happen to hit the window.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import argparse
import sys
from examples.astro.astro import generate_coaching, initialize, save_profile, stale_rows

USER, BIRTH, IST = "user-1", ("1977-08-15", "06:30"), 330


def fresh(directory, name):
    path = Path(directory) / f"{name}.db"
    initialize(path)
    save_profile(path, USER, *BIRTH, IST)
    return path


def points():
    names = []
    with TemporaryDirectory() as directory:
        generate_coaching(fresh(directory, "probe"), USER, checkpoint=names.append)
    return names


def inject_at(point, broken):
    """Run coaching once, correcting the birth time at ``point``. True if stale coaching was stored."""
    with TemporaryDirectory() as directory:
        path = fresh(directory, "run")

        def hook(name):
            if name == point:
                save_profile(path, USER, BIRTH[0], "07:10", IST)

        status, _ = generate_coaching(path, USER, broken=broken, checkpoint=hook)
        return bool(stale_rows(path, USER)), status


def free_run(broken):
    with TemporaryDirectory() as directory:
        path = fresh(directory, "free")
        threads = [Thread(target=generate_coaching, args=(path, USER), kwargs={"broken": broken}),
                   Thread(target=save_profile, args=(path, USER, BIRTH[0], "07:10", IST))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)
        return bool(stale_rows(path, USER))


def sweep():
    rows = []
    for point in points():
        broken_stale, broken_status = inject_at(point, True)
        fixed_stale, fixed_status = inject_at(point, False)
        rows.append((point, broken_stale, broken_status, fixed_stale, fixed_status))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--free-runs", type=int, default=50, help="unsynchronized concurrent runs to try")
    args = parser.parse_args(argv)
    rows = sweep()
    print(f"{'injection point':<18} {'broken app':<24} fixed app")
    for point, b_stale, b_status, f_stale, f_status in rows:
        broken = f"{'STALE STORED' if b_stale else 'ok'} ({b_status})"
        fixed = f"{'STALE STORED' if f_stale else 'ok'} ({f_status})"
        print(f"{point:<18} {broken:<24} {fixed}")
    caught = sum(r[1] for r in rows)
    print(f"\nBroken app stored stale coaching at {caught} of {len(rows)} points; "
          f"fixed app at {sum(r[3] for r in rows)}.")
    print(f"A sequential run only tests '{rows[0][0]}' or '{rows[-1][0]}': both are ok on the broken app.")
    if args.free_runs:
        hits = sum(free_run(True) for _ in range(args.free_runs))
        print(f"Free-running threads on the broken app hit the window in {hits} of {args.free_runs} runs "
              "(varies by machine). A green replay is not evidence the race is gone.")
    ok = caught > 0 and not any(r[3] for r in rows) and not rows[0][1] and not rows[-1][1]
    print("SWEEP PASSED: the window was found on the broken app and closed on the fixed app."
          if ok else "SWEEP FAILED: unexpected behavior.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
