"""Synthetic booking example. Status values resemble HTTP; this is not a web API."""
import sqlite3
from contextlib import closing


def initialize(path, *, broken=False):
    with closing(sqlite3.connect(path)) as db, db:
        constraint = "" if broken else ", UNIQUE(doctor, slot)"
        db.execute(f"CREATE TABLE bookings (id INTEGER PRIMARY KEY, doctor TEXT NOT NULL, slot TEXT NOT NULL{constraint})")


def available(path, doctor, slot):
    with closing(sqlite3.connect(path)) as db, db:
        return db.execute("SELECT COUNT(*) FROM bookings WHERE doctor=? AND slot=?", (doctor, slot)).fetchone()[0] == 0


def book(path, doctor, slot, *, broken=False, before_insert=None):
    if not isinstance(doctor, str) or not doctor.strip() or not isinstance(slot, str) or not slot.strip():
        return 400
    # Deliberately broken: ignores the helper's result and has no uniqueness boundary.
    if broken:
        available(path, doctor, slot)
    if before_insert:
        before_insert()
    try:
        with closing(sqlite3.connect(path, timeout=10)) as db, db:
            db.execute("INSERT INTO bookings(doctor, slot) VALUES (?, ?)", (doctor, slot))
        return 201
    except sqlite3.IntegrityError:
        return 409


def count(path):
    with closing(sqlite3.connect(path)) as db, db:
        return db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
