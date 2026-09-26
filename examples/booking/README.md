# Booking outcome lab

From the repository root, run `python3 -m examples.booking.demo`.

Expected sequence: one helper test passes on the broken application; exactly the duplicate and concurrent single-winner outcome tests fail; all six outcome checks pass on the fixed application. `LAB PASSED` and exit 0 mean the demonstration behaved as intended.

Run only the fixed application checks with `python3 -m unittest examples.booking.test_booking -v`.

The deliberately broken variant ignores an availability result and lacks a database uniqueness constraint. The fixed variant uses `UNIQUE(doctor, slot)` and returns status value 409 on the conflicting insert. Every test gets a temporary SQLite file. The concurrent test uses independent connections synchronized before insertion.

This example covers identical doctor/slot keys, not time interval overlap, a deployed API, multi-tenant authorization or distributed databases. Status values are Python integers resembling HTTP codes. See [the full learning note](../../docs/handbook/11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md).
