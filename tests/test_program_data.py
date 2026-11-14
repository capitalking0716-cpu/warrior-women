"""Tests for Warrior Women — program data correctness."""

from warrior_women import program_data as pd


def test_app_identity_and_price():
    assert pd.APP_NAME == "Warrior Women"
    assert pd.PRICE_MONTHLY_USD == 10
    assert pd.CHECKOUT_URL == "https://buy.stripe.com/00w6oGbGz6dugXU0ve97G0d"
    assert pd.STRIPE_PRICE_ID == "price_1UaH5BCXOGypS7lTcOV4GsQP"
    assert "hourglass" in pd.GOAL_FRAMING.lower()


def test_reentry_week_is_seven_days_starting_at_day_one():
    assert len(pd.REENTRY_WEEK) == 7
    assert [d["day"] for d in pd.REENTRY_WEEK] == [1, 2, 3, 4, 5, 6, 7]
    for d in pd.REENTRY_WEEK:
        assert d["title"] and d["items"]
    # Day 1 is an upper-body check, Day 7 is rest and review
    assert "Upper" in pd.REENTRY_WEEK[0]["title"]
    assert "rest" in pd.REENTRY_WEEK[6]["title"].lower()


def test_weekly_split_is_six_training_days_plus_rest():
    assert len(pd.WEEKLY_SPLIT) == 7
    training = [s for s in pd.WEEKLY_SPLIT if s["exercises"]]
    rest = [s for s in pd.WEEKLY_SPLIT if not s["exercises"]]
    assert len(training) == 6
    assert len(rest) == 1
    assert rest[0]["day"] == "Sunday"
    days = [s["day"] for s in pd.WEEKLY_SPLIT]
    assert days == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # Glute focus is in the program
    tuesday = pd.WEEKLY_SPLIT[1]
    assert "glute" in tuesday["title"].lower()
    assert any("Hip Thrust" in name for name, _, _ in tuesday["exercises"])
    friday = pd.WEEKLY_SPLIT[4]
    assert any("Cable Kickback" in name for name, _, _ in friday["exercises"])


def test_blocks_and_phases():
    assert len(pd.BLOCKS_120) == 4
    assert [b["block"] for b in pd.BLOCKS_120] == [1, 2, 3, 4]
    assert pd.BLOCKS_120[0]["name"].startswith("Awakening")
    assert len(pd.PHASES_24) == 6
    assert pd.PHASES_24[0]["name"] == "Foundation"
    assert pd.PHASES_24[-1]["name"] == "Super Saiyan"


def test_exercise_library_has_40_with_required_fields():
    assert len(pd.EXERCISE_LIBRARY) == 40
    names = pd.library_names()
    assert len(set(names)) == 40  # no duplicates
    for required in ("Hip Thrust", "Glute Bridge", "Hip Abduction (Machine)",
                     "Cable Kickback", "Bulgarian Split Squat"):
        assert required in names
    for ex in pd.EXERCISE_LIBRARY:
        for field in ("name", "target", "setup", "execution", "regression", "progression", "safety"):
            assert ex[field], f"{ex['name']} is missing {field}"


def test_protein_target():
    low, high = pd.protein_target_grams(70)
    assert low == 112 and high == 154
    assert pd.protein_target_grams(0) is None
    assert pd.protein_target_grams(None) is None


def test_readiness_verdicts():
    assert pd.readiness_verdict(7.5, 4, 2, 2, False) == "Green"
    assert pd.readiness_verdict(5.0, 4, 2, 2, False) == "Yellow"  # short sleep
    assert pd.readiness_verdict(7.5, 2, 2, 2, False) == "Yellow"  # low energy
    assert pd.readiness_verdict(7.5, 4, 2, 2, True) == "Red"  # pain
    assert pd.readiness_verdict(5.0, 2, 4, 4, False) == "Red"  # everything bad


def test_safety_rules_present():
    text = " ".join(pd.SAFETY_RULES).lower()
    assert "one-rep-max" in text
    assert "steroid" in text
    assert "never train through pain" in text
    assert "12-18 months" in text


def test_week_for_day_number():
    block, phase, week = pd.week_for_day_number(1)
    assert block["block"] == 1 and week == 1 and phase["name"] == "Foundation"
    block, phase, week = pd.week_for_day_number(45)
    assert block["block"] == 2
    block, phase, week = pd.week_for_day_number(100)
    assert block["block"] == 4
    block, phase, week = pd.week_for_day_number(150)
    assert phase["name"] == "Super Saiyan"
