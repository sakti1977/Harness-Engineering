"""Create a new disposable project, or apply its reviewed teaching fix.

Run from Labs: python3 -m examples.adoption.project create /tmp/booking-starter
No existing directory is reused. No model, network, or dependencies are needed.
"""
import argparse
from pathlib import Path
from examples.adoption import booking

TESTS = """import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from booking import initialize, book, count

class OutcomeTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / 'bookings.db'
        initialize(self.path)

    def test_valid_booking(self):
        self.assertEqual(book(self.path, 'doctor-1', '09:00'), 201)
        self.assertEqual(count(self.path), 1)

    def test_duplicate_changes_no_rows(self):
        book(self.path, 'doctor-1', '09:00')
        self.assertEqual((book(self.path, 'doctor-1', '09:00'), count(self.path)), (409, 1))

    def test_concurrent_single_winner(self):
        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(book, self.path, 'doctor-1', '09:00',
                    before_insert=lambda: barrier.wait(timeout=5)) for _ in range(2)]
            results = sorted(job.result(timeout=15) for job in jobs)
        self.assertEqual((results, count(self.path)), ([201, 409], 1))

if __name__ == '__main__':
    unittest.main()
"""
TASK = """# One-feature task contract

Outcome: two requests for the same doctor and slot produce one stored booking.
Allowed edits: booking.py, test_booking.py, checkpoint.md.
Excluded: task.md, proof.md, dependencies, services, shared databases.
Verification: python3 -m unittest test_booking -v
Acceptance: all three tests pass; duplicate and simultaneous requests return
one 201 and one 409, with exactly one persisted row.
Negative control: the seeded implementation must fail duplicate and concurrency
checks. Keep these assertions intact during the fix.
Authority: local temporary databases only; no credentials or network needed.
Owner: the developer reviews the diff and test output before accepting work.
These rules are instructions. No sandbox or independent verifier is configured.
"""
PROOF = """# Claims and proof routes

1. A valid request persists: test_valid_booking checks status 201 and row count 1.
2. A duplicate is rejected without mutation: test_duplicate_changes_no_rows
   checks status 409 and row count 1 after the second request.
3. Simultaneous requests have one winner: test_concurrent_single_winner uses
   separate connections and a barrier, then checks [201, 409] and row count 1.

Run: python3 -m unittest test_booking -v
Producer: local unittest runner. Review the actual output and test source.
Boundary: Python function and temporary SQLite database, not an HTTP service.
Limits: exact text slots only; no timezone, interval, authorization or deployment
claim. A worker can edit tests here; review is needed to catch weakened assertions.
"""
CHECKPOINT = """# Checkpoint

State: seeded defect; verification has not run in this new project.
Known defect: initialization omits the doctor/slot uniqueness constraint;
booking ignores the availability helper's answer.
Next command: python3 -m unittest test_booking -v
Expected: duplicate and concurrency checks fail; valid-booking check passes.
After running: replace this text with actual results, changed files, limits,
and the next command. Never copy expected results into verified facts.
"""

def sources():
    fixed = Path(booking.__file__).read_text()
    broken = fixed.replace('broken=False', 'broken=True')
    if broken == fixed:
        raise RuntimeError('Teaching source changed; update the seeded variant.')
    return broken, fixed


def create(path):
    broken, _ = sources()
    # mkdir without exist_ok prevents overwriting existing work, including symlinks.
    path.mkdir(parents=True)
    for name, content in {'booking.py': broken, 'test_booking.py': TESTS,
            'task.md': TASK, 'proof.md': PROOF, 'checkpoint.md': CHECKPOINT}.items():
        (path / name).write_text(content)
    print(f'Created {path}. Read task.md and proof.md, then run the tests.')


def fix(path):
    broken, fixed = sources()
    source = path / 'booking.py'
    if source.is_symlink() or source.read_text() != broken:
        raise ValueError('Refusing fix: booking.py differs from the seeded source.')
    source.write_text(fixed)
    print('Applied teaching fix to booking.py. Verification has not run.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'fix'])
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    try:
        (create if args.action == 'create' else fix)(args.path.absolute())
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f'Refused: {exc}\n')

if __name__ == '__main__':
    main()
