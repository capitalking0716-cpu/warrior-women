"""Tests for Warrior Women — rule-based coach guardrails."""

from warrior_women import coach


def test_protein_answer_uses_bodyweight():
    reply = coach.answer("what is my protein target?", member_weight_kg=70)
    assert "112" in reply and "154" in reply
    reply = coach.answer("protein?", member_weight_kg=None)
    assert "bodyweight" in reply.lower()


def test_red_flags_stop_the_workout():
    reply = coach.answer("I have sharp pain in my knee")
    assert "Stop" in reply
    assert "medical" in reply.lower()
    reply = coach.answer("I feel dizzy")
    assert "Stop" in reply


def test_steroids_always_refused():
    reply = coach.answer("should I take steroids?")
    assert "No" in reply


def test_missed_workout_rule():
    reply = coach.answer("I missed yesterday's workout")
    assert "never double" in reply.lower()


def test_progression_rule():
    reply = coach.answer("how do I get stronger?")
    assert "double progression" in reply.lower()
    assert "smallest practical increment" in reply.lower()


def test_substitution_uses_library():
    reply = coach.answer("substitute for hip thrust")
    assert "Glute Bridge" in reply or "hip thrust" in reply.lower()
    assert "Safety" in reply


def test_deload_answer():
    reply = coach.answer("when is the deload?")
    assert "fourth week" in reply.lower()


def test_hourglass_answer_no_promises():
    reply = coach.answer("how do I get an hourglass figure?")
    assert "12-18 months" in reply
    assert "not promised" in reply.lower()


def test_readiness_context_is_used():
    reply = coach.answer("what should I do today?", readiness={"verdict": "Red"})
    assert "no strenuous workout" in reply.lower()
    reply = coach.answer("what should I do today?", readiness={"verdict": "Yellow"})
    assert "20-30%" in reply


def test_empty_question():
    assert coach.answer("") != ""
    assert coach.answer("   ") != ""
