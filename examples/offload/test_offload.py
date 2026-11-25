"""Tests for large-output offloading. Failure first: naive truncation hides the verdict."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from examples.offload.offload import naive_head_truncate, offload_large_output

VERDICT = "FAILED (failures=1)"


def noisy_test_run(lines: int = 3000) -> str:
    body = [f"test_case_{i} ... ok" for i in range(lines)]
    return "\n".join(["Running suite", *body, VERDICT])


class OffloadTests(unittest.TestCase):
    def test_small_output_passes_through_unchanged(self):
        with TemporaryDirectory() as tmp:
            result = offload_large_output("Ran 3 tests\nOK", Path(tmp))
            self.assertEqual(result.text, "Ran 3 tests\nOK")
            self.assertIsNone(result.path)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_naive_head_truncation_loses_the_verdict(self):
        # The failure this control exists for.
        output = noisy_test_run()
        self.assertGreater(len(output), 4000)
        self.assertNotIn(VERDICT, naive_head_truncate(output))

    def test_offloaded_preview_keeps_the_verdict_visible(self):
        with TemporaryDirectory() as tmp:
            result = offload_large_output(noisy_test_run(), Path(tmp))
            self.assertIn(VERDICT, result.text)
            self.assertLess(len(result.text), 4000)
            self.assertIn("lines omitted", result.text)

    def test_full_output_is_recoverable_byte_for_byte(self):
        output = noisy_test_run()
        with TemporaryDirectory() as tmp:
            result = offload_large_output(output, Path(tmp))
            self.assertIsNotNone(result.path)
            self.assertEqual(result.path.read_text(encoding="utf-8"), output)
            self.assertIn(str(result.path), result.text)

    def test_same_content_maps_to_the_same_file(self):
        output = noisy_test_run()
        with TemporaryDirectory() as tmp:
            first = offload_large_output(output, Path(tmp))
            second = offload_large_output(output, Path(tmp))
            self.assertEqual(first.path, second.path)
            self.assertEqual(len(list(Path(tmp).iterdir())), 1)

    def test_few_long_lines_are_cut_by_characters_and_saved_in_full(self):
        output = "x" * 10_000  # one line: a line preview would not shrink it
        with TemporaryDirectory() as tmp:
            result = offload_large_output(output, Path(tmp), max_chars=4000)
            self.assertLess(len(result.text), 4200)
            self.assertIn("output cut at 4000 characters", result.text)
            self.assertEqual(result.path.read_text(encoding="utf-8"), output)

    def test_zero_tail_lines_still_offloads_instead_of_returning_everything(self):
        output = noisy_test_run()
        with TemporaryDirectory() as tmp:
            result = offload_large_output(output, Path(tmp), tail_lines=0)
            self.assertIsNotNone(result.path)
            self.assertLess(len(result.text), 4000)
            self.assertIn("lines omitted", result.text)

    def test_few_long_lines_keep_the_verdict_at_the_end(self):
        output = "x" * 4001 + "\nFAILED (failures=1)"
        with TemporaryDirectory() as tmp:
            result = offload_large_output(output, Path(tmp), max_chars=4000)
            self.assertIn("FAILED (failures=1)", result.text)
            self.assertEqual(result.path.read_text(encoding="utf-8"), output)


if __name__ == "__main__":
    unittest.main()
