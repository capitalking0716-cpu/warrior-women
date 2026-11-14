"""Tests for Warrior Women — the FREE 7-Day Challenge mode.

The challenge is the free front door: a challenge-flagged account gets
the seven-day re-entry week (program days 1-7, anchored to her own
start date) and nothing beyond it. An active subscription converts her
to a full member with start date and logs intact. Plain members are
completely unaffected.
"""

import sqlite3
from datetime import date, timedelta

from warrior_women import challenge, db, paywall, program_data as pd

TODAY = date(2026, 11, 13)


def _start(days_ago):
    return (TODAY - timedelta(days=days_ago)).isoformat()


def _profile(days_ago):
    return {"start_date": _start(days_ago)}


# --- the account flag ------------------------------------------------------

def test_challenge_flag_persists_and_defaults_to_member(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    plain = db.create_member(conn, "ada@example.com", "s", "h", "Ada")
    challenger = db.create_member(conn, "beth@example.com", "s", "h", "Beth",
                                  account_type=challenge.ACCOUNT_CHALLENGE)
    assert db.get_member(conn, plain)["account_type"] == "member"
    beth = db.get_member(conn, challenger)
    assert beth["account_type"] == "challenge"
    assert challenge.is_challenge_member(beth)
    assert not challenge.is_challenge_member(db.get_member(conn, plain))


def test_set_account_type_flips_flag(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    mid = db.create_member(conn, "ada@example.com", "s", "h", "Ada",
                           account_type=challenge.ACCOUNT_CHALLENGE)
    db.set_account_type(conn, mid, challenge.ACCOUNT_MEMBER)
    assert db.get_member(conn, mid)["account_type"] == "member"


def test_old_database_gains_flag_as_member(tmp_path):
    """Databases created before the challenge existed must keep working:
    connect() adds account_type and old accounts read as plain members."""
    path = str(tmp_path / "old.db")
    raw = sqlite3.connect(path)
    raw.execute(
        "CREATE TABLE members (id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " email TEXT UNIQUE NOT NULL, password_salt TEXT NOT NULL,"
        " password_hash TEXT NOT NULL, name TEXT NOT NULL,"
        " stripe_customer_id TEXT, created_at REAL NOT NULL)"
    )
    raw.execute(
        "INSERT INTO members (email, password_salt, password_hash, name, created_at)"
        " VALUES ('ada@example.com', 's', 'h', 'Ada', 1.0)"
    )
    raw.commit()
    raw.close()

    conn = db.connect(path)
    member = db.get_member_by_email(conn, "ada@example.com")
    assert member["account_type"] == "member"
    assert not challenge.is_challenge_member(member)


# --- access resolution -----------------------------------------------------

def _result(unlocked, reason=None):
    return paywall.PaywallResult(
        unlocked, reason or ("active" if unlocked else "no_subscription")
    )


def test_access_matrix():
    challenger = {"account_type": "challenge"}
    plain = {"account_type": "member"}
    legacy = {}  # no flag at all reads as a plain member
    active = _result(True)
    none = _result(False, "no_subscription")
    unconfigured = _result(False, "not_configured")
    broken = _result(False, "error")

    # Challenge account: the free week is open even with no subscription,
    # and even before Stripe verification is configured at all.
    assert challenge.resolve_access(challenger, none) == challenge.CHALLENGE
    assert challenge.resolve_access(challenger, unconfigured) == challenge.CHALLENGE
    assert challenge.resolve_access(challenger, broken) == challenge.CHALLENGE
    # ...but an active subscription converts her to a full member.
    assert challenge.resolve_access(challenger, active) == challenge.FULL

    # Plain members: exactly the old behaviour — paywall or full access.
    assert challenge.resolve_access(plain, none) == challenge.LOCKED
    assert challenge.resolve_access(plain, unconfigured) == challenge.LOCKED
    assert challenge.resolve_access(plain, active) == challenge.FULL
    assert challenge.resolve_access(legacy, none) == challenge.LOCKED
    assert challenge.resolve_access(legacy, active) == challenge.FULL


# --- day anchoring and gating ----------------------------------------------

def test_challenge_days_anchor_to_own_start_date():
    assert challenge.challenge_day_number(_profile(0), today=TODAY) == 1
    assert challenge.challenge_day_number(_profile(3), today=TODAY) == 4
    assert challenge.challenge_day_number(_profile(6), today=TODAY) == 7
    assert challenge.challenge_day_number(None, today=TODAY) == 1
    assert challenge.challenge_day_number({}, today=TODAY) == 1
    assert challenge.challenge_day_number({"start_date": "not-a-date"}, today=TODAY) == 1


def test_challenge_covers_all_seven_reentry_days_and_nothing_beyond():
    # The challenge content is exactly the re-entry week: 7 days.
    assert len(pd.REENTRY_WEEK) == 7
    assert [d["day"] for d in pd.REENTRY_WEEK] == [1, 2, 3, 4, 5, 6, 7]
    for days_ago in range(0, 7):
        day_no = challenge.challenge_day_number(_profile(days_ago), today=TODAY)
        assert day_no == days_ago + 1
        assert challenge.within_challenge(day_no)
        assert not challenge.challenge_finished(day_no)
    # Day 8: the free week is over.
    day_no = challenge.challenge_day_number(_profile(7), today=TODAY)
    assert day_no == 8
    assert not challenge.within_challenge(day_no)
    assert challenge.challenge_finished(day_no)


def test_membership_offer_timing():
    # No offer before day 7, offer on day 7, and it stays after the finish.
    for day_no in range(1, 7):
        assert not challenge.show_membership_offer(day_no)
        assert not challenge.is_final_day(day_no)
    assert challenge.is_final_day(7)
    assert challenge.show_membership_offer(7)
    assert challenge.show_membership_offer(8)
    assert challenge.show_membership_offer(30)


# --- the conversion path ----------------------------------------------------

def test_conversion_keeps_start_date_and_logs(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    mid = db.create_member(conn, "ada@example.com", "s", "h", "Ada",
                           account_type=challenge.ACCOUNT_CHALLENGE)
    start = _start(2)  # she is on challenge day 3
    db.upsert_profile(conn, mid, height_cm=165, weight_kg=70,
                      start_date=start, onboarding_done=1)
    db.log_set(conn, mid, start, "Re-entry Day 1", "Re-entry session", 1,
               notes="Upper-body movement check")

    member = db.get_member(conn, mid)
    assert challenge.resolve_access(member, _result(False)) == challenge.CHALLENGE

    # She pays: the app's subscription check now says active.
    assert challenge.resolve_access(member, _result(True)) == challenge.FULL

    # The app flips the flag on conversion; nothing else about her changes.
    db.set_account_type(conn, mid, challenge.ACCOUNT_MEMBER)
    member = db.get_member(conn, mid)
    assert challenge.resolve_access(member, _result(True)) == challenge.FULL
    profile = db.get_profile(conn, mid)
    assert profile["start_date"] == start
    assert challenge.challenge_day_number(profile, today=TODAY) == 3
    logs = db.all_set_logs(conn, mid)
    assert len(logs) == 1 and logs[0]["exercise"] == "Re-entry session"
