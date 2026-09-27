"""Run weak checks, then outcome checks, against both variants of the Jyotish Coach lab."""
import os
import unittest
from examples.astro.test_astro import AstroTests

WEAK = ["test_save_reports_synced", "test_age_in_ist", "test_coaching_is_generated"]
OUTCOME = ["test_synced_only_when_stored", "test_age_correct_behind_and_ahead_of_utc",
           "test_coaching_not_stored_against_superseded_chart", "test_invalid_birth_details_store_nothing"]
EXPECTED_FAILURES = set(OUTCOME[:3])


def run(variant, names):
    os.environ["ASTRO_VARIANT"] = variant
    suite = unittest.TestSuite(AstroTests(name) for name in names)
    return unittest.TextTestRunner(verbosity=2).run(suite)


def main():
    previous = os.environ.get("ASTRO_VARIANT")
    try:
        print("1. Weak checks on the broken app: expected green", flush=True)
        weak = run("broken", WEAK)
        print("2. Outcome checks on the broken app: expected three failed claims", flush=True)
        broken = run("broken", OUTCOME)
        print("3. Outcome checks on the fixed app: expected green", flush=True)
        fixed = run("fixed", OUTCOME)
        failed = {getattr(case, "test_case", case)._testMethodName for case, _ in broken.failures}
        ok = weak.wasSuccessful() and fixed.wasSuccessful() and not broken.errors and failed == EXPECTED_FAILURES
        print("LAB PASSED: the outcome checks catch all three defects and accept the fix."
              if ok else "LAB FAILED: unexpected behavior.")
        return 0 if ok else 1
    finally:
        if previous is None:
            os.environ.pop("ASTRO_VARIANT", None)
        else:
            os.environ["ASTRO_VARIANT"] = previous


if __name__ == "__main__":
    raise SystemExit(main())
