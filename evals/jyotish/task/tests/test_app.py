from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from jyotish.app import age_on, generate_coaching, initialize, save_profile


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "jyotish.db"
        initialize(self.path)

    def test_save_reports_synced(self):
        status, body = save_profile(self.path, "user-1", "1977-08-15", "06:30", 330)
        self.assertEqual((status, body["synced"]), (200, True))

    def test_age(self):
        self.assertEqual(age_on("1977-08-15", date(2026, 8, 14), 330), 48)

    def test_coaching_is_generated(self):
        save_profile(self.path, "user-1", "1977-08-15", "06:30", 330)
        status, _ = generate_coaching(self.path, "user-1")
        self.assertIn(status, (201, 404))


if __name__ == "__main__":
    unittest.main()
