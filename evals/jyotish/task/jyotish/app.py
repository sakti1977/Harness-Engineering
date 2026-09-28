"""Jyotish Coach core: birth profiles, age, and chart-grounded weekly coaching.

Storage is SQLite. Status values follow HTTP conventions (200, 201, 400, 404, 409, 503).
The chart is computed by a deterministic stand-in for the ephemeris service.
"""
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
import sqlite3

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces")
GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")


def connect(path):
    return closing(sqlite3.connect(path, timeout=10))


def initialize(path):
    with connect(path) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS profiles (user_id TEXT PRIMARY KEY, birth_date TEXT NOT NULL, "
                   "birth_time TEXT NOT NULL, utc_offset_minutes INTEGER NOT NULL, chart_version INTEGER NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS coaching (id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, "
                   "chart_version INTEGER NOT NULL, text TEXT NOT NULL)")


def valid(birth_date, birth_time, utc_offset_minutes):
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
        hours, minutes = (int(x) for x in birth_time.split(":"))
    except (AttributeError, TypeError, ValueError):
        return False
    return 0 <= hours < 24 and 0 <= minutes < 60 and -720 <= utc_offset_minutes <= 840


def save_profile(path, user_id, birth_date, birth_time, utc_offset_minutes):
    """Create or update a user's birth profile. The body's "synced" flag drives the Synced badge."""
    if not valid(birth_date, birth_time, utc_offset_minutes):
        return 400, {"synced": False, "error": "invalid birth details"}
    try:
        with connect(path) as db:
            db.execute("INSERT INTO profiles VALUES (?, ?, ?, ?, 1) ON CONFLICT(user_id) DO UPDATE SET "
                       "birth_date=excluded.birth_date, birth_time=excluded.birth_time, "
                       "utc_offset_minutes=excluded.utc_offset_minutes, "
                       "chart_version=profiles.chart_version+1",
                       (user_id, birth_date, birth_time, utc_offset_minutes))
    except sqlite3.Error:
        pass
    return 200, {"synced": True}


def stored_profile(path, user_id):
    """(birth_date, birth_time, utc_offset_minutes, chart_version) or None."""
    with connect(path) as db:
        return db.execute("SELECT birth_date, birth_time, utc_offset_minutes, chart_version "
                          "FROM profiles WHERE user_id=?", (user_id,)).fetchone()


def age_on(birth_date, today, utc_offset_minutes):
    """Whole years since birth on ``today``, the user's local date."""
    born = datetime.fromisoformat(birth_date).replace(tzinfo=timezone.utc)
    born = born.astimezone(timezone(timedelta(minutes=utc_offset_minutes))).date()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def chart_for(birth_date, birth_time):
    """Placements for each graha; a deterministic stand-in for the ephemeris service."""
    born = datetime.strptime(birth_date, "%Y-%m-%d").date()
    hours, minutes = (int(x) for x in birth_time.split(":"))
    seed = born.toordinal() * 1440 + hours * 60 + minutes
    return {graha: SIGNS[(seed // (97 * (i + 1))) % 12] for i, graha in enumerate(GRAHAS)}


def compose_line(graha, sign):
    """In production this calls the LLM, grounded in one placement. It takes several seconds."""
    return f"{graha} in {sign}: one behavioural practice for this week."


def generate_coaching(path, user_id):
    """Build this week's coaching from the user's chart and store it. Returns (status, body)."""
    profile = stored_profile(path, user_id)
    if profile is None:
        return 404, {"error": "no profile"}
    birth_date, birth_time, _, version = profile
    lines = [compose_line(graha, sign) for graha, sign in chart_for(birth_date, birth_time).items()]
    text = "\n".join(lines)
    with connect(path) as db, db:
        db.execute("INSERT INTO coaching(user_id, chart_version, text) VALUES (?, ?, ?)", (user_id, version, text))
    return 201, {"chart_version": version}


def latest_coaching(path, user_id):
    """(chart_version, text) of the newest coaching for the user, or None."""
    with connect(path) as db:
        return db.execute("SELECT chart_version, text FROM coaching WHERE user_id=? ORDER BY id DESC LIMIT 1",
                          (user_id,)).fetchone()
