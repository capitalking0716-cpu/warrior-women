"""Tests for Warrior Women — per-member data isolation and logging."""

from warrior_women import db


def _member(conn, email="ada@example.com"):
    return db.create_member(conn, email, "salt", "hash", "Ada")


def test_members_data_is_isolated(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    ada = _member(conn, "ada@example.com")
    beth = _member(conn, "beth@example.com")
    db.log_set(conn, ada, "2026-11-10", "Tuesday", "Hip Thrust", 1, reps=10, load_kg=40)
    db.log_set(conn, beth, "2026-11-10", "Tuesday", "Hip Thrust", 1, reps=8, load_kg=20)
    ada_logs = db.all_set_logs(conn, ada)
    beth_logs = db.all_set_logs(conn, beth)
    assert len(ada_logs) == 1 and ada_logs[0]["load_kg"] == 40
    assert len(beth_logs) == 1 and beth_logs[0]["load_kg"] == 20


def test_last_performance_returns_latest_session(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    ada = _member(conn)
    db.log_set(conn, ada, "2026-11-03", "Tuesday", "Hip Thrust", 1, reps=8, load_kg=30)
    db.log_set(conn, ada, "2026-11-03", "Tuesday", "Hip Thrust", 2, reps=8, load_kg=30)
    db.log_set(conn, ada, "2026-11-10", "Tuesday", "Hip Thrust", 1, reps=10, load_kg=40)
    last = db.last_performance(conn, ada, "Hip Thrust")
    assert last["date"] == "2026-11-10"
    assert len(last["sets"]) == 1
    assert last["sets"][0]["load_kg"] == 40
    assert db.last_performance(conn, ada, "Bulgarian Split Squat") is None


def test_sessions_this_week_counts_distinct_days(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    ada = _member(conn)
    db.log_set(conn, ada, "2026-11-09", "Monday", "Machine Chest Press", 1, reps=10)
    db.log_set(conn, ada, "2026-11-09", "Monday", "Lat Pulldown", 1, reps=10)
    db.log_set(conn, ada, "2026-11-10", "Tuesday", "Hip Thrust", 1, reps=10)
    assert db.sessions_this_week(conn, ada, "2026-11-09", "2026-11-15") == 2


def test_profile_roundtrip(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    ada = _member(conn)
    assert db.get_profile(conn, ada) is None
    db.upsert_profile(conn, ada, height_cm=165, weight_kg=70, location="Gym X",
                      days_available=6, injuries="none", health_notes="",
                      sleep_hours=7.5, equipment=["Dumbbells and benches", "Bands"],
                      rest_day="Sunday", waist_cm=72, start_date="2026-11-10",
                      onboarding_done=1)
    profile = db.get_profile(conn, ada)
    assert profile["weight_kg"] == 70
    assert profile["equipment"] == ["Dumbbells and benches", "Bands"]
    assert profile["onboarding_done"] == 1
    # Update keeps the rest
    db.upsert_profile(conn, ada, weight_kg=69.5)
    profile = db.get_profile(conn, ada)
    assert profile["weight_kg"] == 69.5
    assert profile["height_cm"] == 165


def test_readiness_and_progress_and_nutrition(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    ada = _member(conn)
    db.log_readiness(conn, ada, "2026-11-10", 7.0, 4, 2, 2, False, "Green")
    latest = db.latest_readiness(conn, ada)
    assert latest["verdict"] == "Green"
    db.log_progress(conn, ada, "2026-11-10", weight_kg=70, waist_cm=72, pushups=8,
                    confidence_rating=4)
    history = db.progress_history(conn, ada)
    assert len(history) == 1 and history[0]["weight_kg"] == 70
    db.log_nutrition(conn, ada, "2026-11-10", meals=["Eggs", "Chicken salad"],
                     protein_g=120, water_ml=2000, sleep_hours=7.5)
    days = db.nutrition_history(conn, ada)
    assert days[0]["meals"] == ["Eggs", "Chicken salad"]
    assert days[0]["protein_g"] == 120
