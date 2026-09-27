"""Synthetic model of three real Jyotish Coach defects. Not real astronomy; not the production app.

Each function has a ``broken`` variant that reproduces a defect Jyotish Coach actually shipped
(see NON_NEGOTIABLES.md in github.com/sakti1977/astro-coach) and a fixed variant.

1. Sync badge: the profile save reported "synced" although nothing was stored.
2. Age behind UTC: a date-only birth date parsed as UTC midnight shifted a day for users
   behind UTC, so ages flipped a day early.
3. Stale coaching: coaching generated while the user corrected their birth time was stored
   against the chart it was no longer about. (A race modelled for this lab.)

Status values resemble HTTP; this is not a web API.
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
        db.execute("CREATE TABLE profiles (user_id TEXT PRIMARY KEY, birth_date TEXT NOT NULL, "
                   "birth_time TEXT NOT NULL, utc_offset_minutes INTEGER NOT NULL, "
                   "chart_version INTEGER NOT NULL)")
        # current_at_write is an audit column: the profile's chart version at the moment the
        # coaching row was inserted. It is how the lab observes a stale write.
        db.execute("CREATE TABLE coaching (id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, "
                   "chart_version INTEGER NOT NULL, current_at_write INTEGER, text TEXT NOT NULL)")


def valid(birth_date, birth_time, utc_offset_minutes):
    try:
        parse_birth_date(birth_date)
        hours, minutes = (int(x) for x in birth_time.split(":"))
    except (AttributeError, TypeError, ValueError):
        return False
    return 0 <= hours < 24 and 0 <= minutes < 60 and -720 <= utc_offset_minutes <= 840


# 1. Sync badge ---------------------------------------------------------------------------
def save_profile(path, user_id, birth_date, birth_time, utc_offset_minutes, *, broken=False,
                 fail_write=False):
    """Create or update the profile. Returns (status, body); body["synced"] drives the badge."""
    if not valid(birth_date, birth_time, utc_offset_minutes):
        return 400, {"synced": False, "error": "invalid birth details"}
    try:
        with connect(path) as db:
            if fail_write:
                raise sqlite3.OperationalError("write rejected")
            db.execute("INSERT INTO profiles VALUES (?, ?, ?, ?, 1) ON CONFLICT(user_id) DO UPDATE SET "
                       "birth_date=excluded.birth_date, birth_time=excluded.birth_time, "
                       "utc_offset_minutes=excluded.utc_offset_minutes, "
                       "chart_version=profiles.chart_version+1",
                       (user_id, birth_date, birth_time, utc_offset_minutes))
            if not broken:
                db.commit()
            # Broken: the connection closes without commit, so the write is discarded,
            # and the error path below is never reached. The badge still says "Synced".
    except sqlite3.Error:
        if broken:
            return 200, {"synced": True}
        return 503, {"synced": False, "error": "profile not saved; try again"}
    return 200, {"synced": True}


def stored_profile(path, user_id):
    with connect(path) as db:
        return db.execute("SELECT birth_date, birth_time, utc_offset_minutes, chart_version "
                          "FROM profiles WHERE user_id=?", (user_id,)).fetchone()


# 2. Age behind UTC -----------------------------------------------------------------------
def parse_birth_date(text):
    year, month, day = (int(part) for part in text.split("-"))
    return date(year, month, day)


def age_on(birth_date, today, utc_offset_minutes, *, broken=False):
    """Whole years since birth on ``today`` (the user's local date)."""
    if broken:
        # Mirrors `new Date("YYYY-MM-DD")` read back with local getters: UTC midnight,
        # shifted into the user's zone. Ahead of UTC (IST) the date survives; behind UTC
        # it becomes the previous day.
        midnight_utc = datetime.fromisoformat(birth_date).replace(tzinfo=timezone.utc)
        born = midnight_utc.astimezone(timezone(timedelta(minutes=utc_offset_minutes))).date()
    else:
        born = parse_birth_date(birth_date)
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# 3. Stale coaching -----------------------------------------------------------------------
def chart_for(birth_date, birth_time):
    """Deterministic stand-in for the ephemeris: same input, same placements."""
    born = parse_birth_date(birth_date)
    hours, minutes = (int(x) for x in birth_time.split(":"))
    seed = born.toordinal() * 1440 + hours * 60 + minutes
    return {graha: SIGNS[(seed // (97 * (i + 1))) % 12] for i, graha in enumerate(GRAHAS)}


def generate_coaching(path, user_id, *, broken=False, checkpoint=None):
    """Read the chart, compose chart-grounded coaching, store it. Returns (status, body).

    ``checkpoint(name)`` is a test hook called between steps so a harness can interleave
    another request at an exact point. Production code would not have it.
    """
    step = checkpoint or (lambda name: None)
    step("start")
    profile = stored_profile(path, user_id)
    if profile is None:
        return 404, {"error": "no profile"}
    birth_date, birth_time, _, version = profile
    step("after_read")
    lines = []
    for graha, sign in chart_for(birth_date, birth_time).items():
        # In production this is the slow part: an LLM call grounded in each placement.
        lines.append(f"{graha} in {sign}: one behavioural practice for this week.")
        step(f"compose:{graha}")
    text = "\n".join(lines)
    step("before_write")
    with connect(path) as db, db:
        if broken:
            db.execute("INSERT INTO coaching(user_id, chart_version, current_at_write, text) VALUES "
                       "(?, ?, (SELECT chart_version FROM profiles WHERE user_id=?), ?)",
                       (user_id, version, user_id, text))
            written = 1
        else:
            # One statement: insert only if the chart is still the one we read.
            written = db.execute(
                "INSERT INTO coaching(user_id, chart_version, current_at_write, text) "
                "SELECT ?, ?, chart_version, ? FROM profiles WHERE user_id=? AND chart_version=?",
                (user_id, version, text, user_id, version)).rowcount
    step("after_write")
    if not written:
        return 409, {"error": "birth details changed while coaching was generated; regenerate"}
    return 201, {"chart_version": version}


def coaching_rows(path, user_id):
    with connect(path) as db:
        return db.execute("SELECT chart_version, current_at_write FROM coaching WHERE user_id=? "
                          "ORDER BY id", (user_id,)).fetchall()


def stale_rows(path, user_id):
    """Coaching rows written against a chart that was no longer current at write time."""
    return [row for row in coaching_rows(path, user_id) if row[0] != row[1]]
