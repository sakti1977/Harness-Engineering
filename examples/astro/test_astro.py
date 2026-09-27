"""Weak checks and outcome checks for the Jyotish Coach lab. Run the demo to see both variants.

Outcome checks fail with a route message (claim, route, expected, observed, repair boundary),
so the next session does not have to rediscover what broke.
"""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread
import os
import unittest
from examples.astro.astro import (age_on, coaching_rows, generate_coaching, initialize,
                                  save_profile, stale_rows, stored_profile)

USER = "user-1"
BIRTH = ("1977-08-15", "06:30")      # the eve-of-birthday case below uses 2026-08-14
IST, NEW_YORK = 330, -300            # minutes from UTC


def route_failure(claim, route, expected, observed, repair):
    return (f"\nCLAIM     {claim}\nROUTE     docs/verify.md#route-{route}\n"
            f"EXPECTED  {expected}\nOBSERVED  {observed}\nREPAIR AT {repair}")


class AstroTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "jyotish.db"
        self.broken = os.environ.get("ASTRO_VARIANT") == "broken"
        initialize(self.path)

    def save(self, *birth, offset=IST, **kwargs):
        return save_profile(self.path, USER, *(birth or BIRTH), offset, broken=self.broken, **kwargs)

    # Weak checks: each passes on the broken app ------------------------------------------
    def test_save_reports_synced(self):
        # Checks the badge, not the store. This is how the real "Synced" bug shipped.
        status, body = self.save()
        self.assertEqual((status, body["synced"]), (200, True))

    def test_age_in_ist(self):
        # Developer machine and fixtures in IST: UTC midnight never changes the date here.
        self.assertEqual(age_on(BIRTH[0], date(2026, 8, 14), IST, broken=self.broken), 48)

    def test_coaching_is_generated(self):
        # Sequential: nothing changes the chart while coaching is written.
        self._seed()
        status, _ = generate_coaching(self.path, USER, broken=self.broken)
        self.assertEqual(status, 201)

    # Outcome checks -------------------------------------------------------------------------
    def test_synced_only_when_stored(self):
        status, body = self.save()
        self.assertEqual((status, body["synced"], stored_profile(self.path, USER) is not None),
                         (200, True, True), route_failure(
            "saving a profile reports synced only when the profile is stored", "profile-sync",
            "status 200, synced true, one stored profile",
            f"status {status}, synced {body['synced']}, stored profile: {stored_profile(self.path, USER)}",
            "save_profile commit path (examples/astro/astro.py)"))
        status, body = self.save(fail_write=True)
        self.assertEqual((status, body["synced"]), (503, False), route_failure(
            "saving a profile reports synced only when the profile is stored", "profile-sync",
            "a rejected write returns 503 and synced false",
            f"status {status}, synced {body['synced']}", "save_profile error path"))

    def test_age_correct_behind_and_ahead_of_utc(self):
        for offset in (IST, 0, NEW_YORK, -600):
            with self.subTest(offset=offset):
                age = age_on(BIRTH[0], date(2026, 8, 14), offset, broken=self.broken)
                self.assertEqual(age, 48, route_failure(
                    "age is correct for users behind and ahead of UTC", "age-by-timezone",
                    "age 48 on 2026-08-14 at every offset",
                    f"age {age} at UTC{offset / 60:+.1f}", "birth-date parsing (no UTC conversion of date-only strings)"))

    def test_invalid_birth_details_store_nothing(self):
        for birth in (("1977-13-40", "06:30"), ("1977-08-15", "25:00"), ("", "06:30")):
            with self.subTest(birth=birth):
                status, body = self.save(*birth)
                self.assertEqual((status, body["synced"], stored_profile(self.path, USER)), (400, False, None))

    def test_coaching_not_stored_against_superseded_chart(self):
        self._seed()
        read_done, update_done = Event(), Event()
        result = {}

        def pause_after_read(name):
            if name == "after_read":
                read_done.set()
                update_done.wait(timeout=10)

        def coach():
            result["coach"] = generate_coaching(self.path, USER, broken=self.broken, checkpoint=pause_after_read)

        def correct_birth_time():
            read_done.wait(timeout=10)
            result["update"] = save_profile(self.path, USER, BIRTH[0], "07:10", IST, broken=False)
            update_done.set()

        threads = [Thread(target=coach), Thread(target=correct_birth_time)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)
        observed = (result["coach"][0], len(stale_rows(self.path, USER)))
        self.assertEqual(observed, (409, 0), route_failure(
            "coaching started before a birth-time correction is not stored against the old chart",
            "stale-coaching",
            "coaching returns 409 and no coaching row was written against a superseded chart",
            f"coaching returned {observed[0]}; rows (chart_version, current_at_write): {coaching_rows(self.path, USER)}",
            "coaching write must check chart_version in the same statement (examples/astro/astro.py)"))

    def _seed(self):
        # Seed with the fixed save so the broken variant still has a profile to coach.
        save_profile(self.path, USER, *BIRTH, IST, broken=False)


if __name__ == "__main__":
    unittest.main()
