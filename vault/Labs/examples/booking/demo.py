"""Run one intentionally weak check, then outcome checks, against both variants."""
import os
import unittest
from examples.booking.test_booking import BookingTests


def run(variant, names):
    os.environ["BOOKING_VARIANT"] = variant
    suite = unittest.TestSuite(BookingTests(name) for name in names)
    return unittest.TextTestRunner(verbosity=2).run(suite)


def main():
    previous = os.environ.get("BOOKING_VARIANT")
    try:
        helper = ["test_helper_detects_occupied_slot"]
        outcomes = unittest.defaultTestLoader.getTestCaseNames(BookingTests)
        print("1. Weak helper check on broken application: expected green", flush=True)
        weak = run("broken", helper)
        print("2. Outcome checks on broken application: expected two failures", flush=True)
        broken = run("broken", outcomes)
        print("3. Outcome checks on fixed application: expected green", flush=True)
        fixed = run("fixed", outcomes)
        expected = {"test_conflicting_booking_changes_no_rows", "test_concurrent_same_slot_has_one_winner"}
        failed_names = {case._testMethodName for case, _ in broken.failures}
        ok = weak.wasSuccessful() and fixed.wasSuccessful() and not broken.errors and failed_names == expected
        print("LAB PASSED: the stronger checks detect the seeded defect and accept the fix." if ok else "LAB FAILED: unexpected behavior.")
        return 0 if ok else 1
    finally:
        if previous is None:
            os.environ.pop("BOOKING_VARIANT", None)
        else:
            os.environ["BOOKING_VARIANT"] = previous


if __name__ == "__main__":
    raise SystemExit(main())
