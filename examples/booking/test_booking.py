"""Outcome checks for both variants; use the demo to exercise the intentional failure."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
import os
import unittest
from examples.booking.booking import initialize, available, book, count


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "appointments.db"
        self.broken = os.environ.get("BOOKING_VARIANT") == "broken"
        initialize(self.path, broken=self.broken)

    def reserve(self, slot="09:00", **kwargs):
        return book(self.path, "doctor-1", slot, broken=self.broken, **kwargs)

    def test_helper_detects_occupied_slot(self):
        # This passes even when the application ignores the helper's answer.
        self.reserve()
        self.assertFalse(available(self.path, "doctor-1", "09:00"))

    def test_valid_booking_persists(self):
        self.assertEqual(self.reserve(), 201)
        self.assertEqual(count(self.path), 1)

    def test_conflicting_booking_changes_no_rows(self):
        self.reserve()
        result = self.reserve()
        self.assertEqual((result, count(self.path)), (409, 1))

    def test_different_slot_succeeds(self):
        self.reserve()
        self.assertEqual(self.reserve("10:00"), 201)
        self.assertEqual(count(self.path), 2)

    def test_invalid_input_changes_no_rows(self):
        result = book(self.path, "", "09:00", broken=self.broken)
        self.assertEqual((result, count(self.path)), (400, 0))

    def test_concurrent_same_slot_has_one_winner(self):
        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.reserve, before_insert=lambda: barrier.wait(timeout=5)) for _ in range(2)]
            results = sorted(f.result(timeout=15) for f in futures)
        self.assertEqual((results, count(self.path)), ([201, 409], 1))


if __name__ == "__main__":
    unittest.main()
