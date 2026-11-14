"""Warrior Women — member data storage (SQLite).

One database file, one row per member, each member's data keyed by her
own member id. The database file lives in ``data/`` and is gitignored —
it is never committed to the repo.

Tables:
  members       — account (email, password hash, name, account_type, created_at)
  profiles      — onboarding answers (one row per member)
  readiness     — daily readiness checks
  set_logs      — per-set workout logs
  progress      — body measurements / baseline reassessments
  nutrition     — daily food / water / sleep logs
"""

import json
import os
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    stripe_customer_id TEXT,
    account_type TEXT NOT NULL DEFAULT 'member',
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS profiles (
    member_id INTEGER PRIMARY KEY,
    height_cm REAL,
    weight_kg REAL,
    location TEXT,
    days_available INTEGER,
    injuries TEXT,
    health_notes TEXT,
    sleep_hours REAL,
    equipment TEXT,
    rest_day TEXT,
    waist_cm REAL,
    start_date TEXT,
    onboarding_done INTEGER DEFAULT 0,
    FOREIGN KEY (member_id) REFERENCES members (id)
);
CREATE TABLE IF NOT EXISTS readiness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    sleep_hours REAL,
    energy INTEGER,
    soreness INTEGER,
    stress INTEGER,
    pain INTEGER,
    verdict TEXT,
    FOREIGN KEY (member_id) REFERENCES members (id)
);
CREATE TABLE IF NOT EXISTS set_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    session_label TEXT,
    exercise TEXT NOT NULL,
    set_number INTEGER NOT NULL,
    reps INTEGER,
    load_kg REAL,
    duration_sec INTEGER,
    rpe REAL,
    rir INTEGER,
    notes TEXT,
    FOREIGN KEY (member_id) REFERENCES members (id)
);
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    weight_kg REAL,
    waist_cm REAL,
    balance_left_sec REAL,
    balance_right_sec REAL,
    pushups INTEGER,
    walk_m REAL,
    sleep_rating INTEGER,
    energy_rating INTEGER,
    soreness_rating INTEGER,
    confidence_rating INTEGER,
    notes TEXT,
    FOREIGN KEY (member_id) REFERENCES members (id)
);
CREATE TABLE IF NOT EXISTS nutrition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    meals TEXT,
    protein_g REAL,
    water_ml REAL,
    sleep_hours REAL,
    notes TEXT,
    FOREIGN KEY (member_id) REFERENCES members (id)
);
"""


def default_db_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "data", "warrior_women.db")


def connect(db_path=None):
    path = db_path or os.environ.get("WARRIOR_WOMEN_DB") or default_db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    _migrate(conn)
    conn.commit()
    return conn


def _migrate(conn):
    """Add columns introduced after a database was first created.

    CREATE TABLE IF NOT EXISTS never alters an existing table, so new
    columns are added here, once, guarded by the live table shape.
    Existing rows take the column default ('member'), so accounts made
    before the challenge existed are plain members, untouched.
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(members)")}
    if "account_type" not in cols:
        conn.execute(
            "ALTER TABLE members ADD COLUMN account_type TEXT NOT NULL DEFAULT 'member'"
        )


# --- members ---------------------------------------------------------------

def create_member(conn, email, password_salt, password_hash, name,
                  account_type="member"):
    """Insert a member. Returns the new member id, or None if email taken.

    ``account_type`` is 'member' (default) or 'challenge' for accounts
    created through the free 7-Day Challenge sign-up.
    """
    try:
        cur = conn.execute(
            "INSERT INTO members (email, password_salt, password_hash, name, account_type, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (email.strip().lower(), password_salt, password_hash, name.strip(),
             account_type, time.time()),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def set_account_type(conn, member_id, account_type):
    conn.execute(
        "UPDATE members SET account_type = ? WHERE id = ?",
        (account_type, member_id),
    )
    conn.commit()


def get_member_by_email(conn, email):
    cur = conn.execute(
        "SELECT * FROM members WHERE email = ?", (email.strip().lower(),)
    )
    return cur.fetchone()


def get_member(conn, member_id):
    cur = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    return cur.fetchone()


def set_stripe_customer_id(conn, member_id, customer_id):
    conn.execute(
        "UPDATE members SET stripe_customer_id = ? WHERE id = ?",
        (customer_id, member_id),
    )
    conn.commit()


# --- profiles --------------------------------------------------------------

def upsert_profile(conn, member_id, **fields):
    """Insert or update the onboarding profile for a member."""
    allowed = {
        "height_cm", "weight_kg", "location", "days_available", "injuries",
        "health_notes", "sleep_hours", "equipment", "rest_day", "waist_cm",
        "start_date", "onboarding_done",
    }
    data = {k: v for k, v in fields.items() if k in allowed}
    if "equipment" in data and isinstance(data["equipment"], (list, tuple)):
        data["equipment"] = json.dumps(list(data["equipment"]))
    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" * len(data))
    updates = ", ".join(f"{c} = excluded.{c}" for c in data.keys())
    conn.execute(
        f"INSERT INTO profiles (member_id, {cols}) VALUES (?, {placeholders}) "
        f"ON CONFLICT(member_id) DO UPDATE SET {updates}",
        (member_id, *data.values()),
    )
    conn.commit()


def get_profile(conn, member_id):
    cur = conn.execute(
        "SELECT * FROM profiles WHERE member_id = ?", (member_id,)
    )
    row = cur.fetchone()
    if row is None:
        return None
    d = dict(row)
    if d.get("equipment"):
        try:
            d["equipment"] = json.loads(d["equipment"])
        except (ValueError, TypeError):
            d["equipment"] = []
    return d


# --- readiness -------------------------------------------------------------

def log_readiness(conn, member_id, date, sleep_hours, energy, soreness, stress, pain, verdict):
    conn.execute(
        "INSERT INTO readiness (member_id, date, sleep_hours, energy, soreness, stress, pain, verdict)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (member_id, date, sleep_hours, energy, soreness, stress, int(bool(pain)), verdict),
    )
    conn.commit()


def latest_readiness(conn, member_id):
    cur = conn.execute(
        "SELECT * FROM readiness WHERE member_id = ? ORDER BY date DESC, id DESC LIMIT 1",
        (member_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


# --- set logs ---------------------------------------------------------------

def log_set(conn, member_id, date, session_label, exercise, set_number,
            reps=None, load_kg=None, duration_sec=None, rpe=None, rir=None, notes=None):
    conn.execute(
        "INSERT INTO set_logs (member_id, date, session_label, exercise, set_number,"
        " reps, load_kg, duration_sec, rpe, rir, notes)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (member_id, date, session_label, exercise, set_number,
         reps, load_kg, duration_sec, rpe, rir, notes),
    )
    conn.commit()


def last_performance(conn, member_id, exercise):
    """The most recent logged sets for one exercise (for prior-performance hints)."""
    cur = conn.execute(
        "SELECT date, set_number, reps, load_kg, rpe, rir FROM set_logs"
        " WHERE member_id = ? AND exercise = ? ORDER BY date DESC, id DESC LIMIT 10",
        (member_id, exercise),
    )
    rows = [dict(r) for r in cur.fetchall()]
    if not rows:
        return None
    latest_date = rows[0]["date"]
    return {"date": latest_date, "sets": [r for r in rows if r["date"] == latest_date]}


def sessions_this_week(conn, member_id, week_start, week_end):
    """Count of distinct training days logged in a date range (YYYY-MM-DD)."""
    cur = conn.execute(
        "SELECT COUNT(DISTINCT date) FROM set_logs"
        " WHERE member_id = ? AND date >= ? AND date <= ?",
        (member_id, week_start, week_end),
    )
    return cur.fetchone()[0]


def all_set_logs(conn, member_id):
    cur = conn.execute(
        "SELECT * FROM set_logs WHERE member_id = ? ORDER BY date, id",
        (member_id,),
    )
    return [dict(r) for r in cur.fetchall()]


# --- progress ---------------------------------------------------------------

def log_progress(conn, member_id, date, **fields):
    allowed = {
        "weight_kg", "waist_cm", "balance_left_sec", "balance_right_sec",
        "pushups", "walk_m", "sleep_rating", "energy_rating",
        "soreness_rating", "confidence_rating", "notes",
    }
    data = {k: v for k, v in fields.items() if k in allowed}
    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" * len(data))
    conn.execute(
        f"INSERT INTO progress (member_id, date, {cols}) VALUES (?, ?, {placeholders})",
        (member_id, date, *data.values()),
    )
    conn.commit()


def progress_history(conn, member_id, limit=50):
    cur = conn.execute(
        "SELECT * FROM progress WHERE member_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (member_id, limit),
    )
    return [dict(r) for r in cur.fetchall()]


# --- nutrition ---------------------------------------------------------------

def log_nutrition(conn, member_id, date, meals=None, protein_g=None,
                  water_ml=None, sleep_hours=None, notes=None):
    meals_json = json.dumps(meals) if isinstance(meals, (list, tuple, dict)) else meals
    conn.execute(
        "INSERT INTO nutrition (member_id, date, meals, protein_g, water_ml, sleep_hours, notes)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (member_id, date, meals_json, protein_g, water_ml, sleep_hours, notes),
    )
    conn.commit()


def nutrition_history(conn, member_id, limit=30):
    cur = conn.execute(
        "SELECT * FROM nutrition WHERE member_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (member_id, limit),
    )
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        if d.get("meals"):
            try:
                d["meals"] = json.loads(d["meals"])
            except (ValueError, TypeError):
                pass
        rows.append(d)
    return rows
