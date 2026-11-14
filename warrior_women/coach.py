"""Warrior Women — rule-based AI coach.

Answers from the program data and the member's own logs. No live model,
no invented content. Guardrails:

- Never recommend steroids, hormones, or training through pain.
- Never promise a body, a weight, or a date.
- Never increase multiple training variables at once.
- Pain / red-flag symptoms -> stop the workout, seek medical care.
- Medical questions -> point to a clinician / dietitian.
"""

from . import program_data

COACH_IDENTITY = (
    "You are the Warrior Women training coach. Follow the approved "
    "gym-based program and the member's logged performance. Coach with "
    "direct, encouraging, practical language. Prioritize technique, "
    "consistency, gradual progression and recovery. Do not claim fictional "
    "abilities or guarantee outcomes. Never recommend steroids or training "
    "through pain. Explain why a change is being made. Do not increase "
    "multiple training variables at once. Ask about health changes or "
    "restrictions when relevant."
)

RED_FLAG_WORDS = (
    "sharp pain", "chest pain", "dizzy", "dizziness", "numb", "numbness",
    "short of breath", "can't breathe", "faint", "blacked out",
)


def _protein_answer(weight_kg):
    target = program_data.protein_target_grams(weight_kg)
    if not target:
        return (
            "Your protein target depends on your bodyweight. Add your weight "
            "in your profile and I can work it out — the guide is about "
            "1.6-2.2 g of protein per kg of bodyweight per day, spread over "
            "3-5 meals."
        )
    low, high = target
    return (
        f"At {weight_kg:.0f} kg, your protein target is about {low}-{high} g "
        f"per day (1.6-2.2 g per kg). Spread it over 3-5 meals. That is the "
        "program's guide — I do not prescribe supplements or diets, and if "
        "you have a medical condition, check with a clinician or dietitian."
    )


def _substitute_answer(exercise_name):
    ex = program_data.get_exercise(exercise_name)
    if ex is None:
        return (
            "Tell me the exercise name as it appears in the Movement Library "
            "and I can suggest its listed regression or a same-pattern "
            "substitution from your gym's equipment."
        )
    return (
        f"For **{ex['name']}** ({ex['target']}): if it is too hard or your "
        f"gym does not have it, use the regression — {ex['regression']}. "
        f"When it gets easy, step up with: {ex['progression']}. "
        f"Safety: {ex['safety']}"
    )


def answer(question, member_weight_kg=None, last_logs=None, readiness=None):
    """Return a coach reply for a free-text question.

    ``last_logs`` and ``readiness`` are optional context dicts from the
    member's own data; they are only ever used to quote back what she did.
    """
    q = (question or "").strip().lower()
    if not q:
        return "Ask me about an exercise, your protein target, a missed workout, or how to progress."

    if any(word in q for word in RED_FLAG_WORDS):
        return (
            "Stop the workout now. Sharp pain, chest pain, dizziness, "
            "numbness, or unusual shortness of breath are not things to push "
            "through — seek appropriate medical care. You can come back to "
            "training when you have been checked and you are pain-free. "
            "I am a training coach, not a clinician, and I cannot clear you "
            "to train."
        )

    if "protein" in q:
        return _protein_answer(member_weight_kg)

    if "substitut" in q or "instead of" in q or "replace" in q:
        # try to find an exercise name in the question
        for name in program_data.library_names():
            if name.lower() in q:
                return _substitute_answer(name)
        return (
            "Tell me which exercise you want to swap — for example "
            "'substitute for hip thrust' — and I will give you its listed "
            "regression or a same-pattern option from your gym."
        )

    if "missed" in q or "skip" in q or "couldn't train" in q or "couldnt train" in q:
        return (
            "Do not make it up and never double the next session — just "
            "reschedule or continue from where you are. One missed session "
            "does not change the plan; consistency over weeks is what counts."
        )

    if "deload" in q:
        return (
            "Every fourth week is a deload: reduce hard sets by about "
            "25-40%, keep movement practice easy, no max testing. The app "
            "never increases weight automatically — you add load only when "
            "all sets reach the top of the rep range with good form on two "
            "sessions."
        )

    if "progress" in q or "stronger" in q or "increase" in q or "heavier" in q:
        return (
            "Use double progression: start at the low end of the rep range "
            "with 2-3 reps in reserve. Add reps across sessions while "
            "technique stays clean. When all sets hit the top of the range "
            "with good form on two sessions, increase load by the smallest "
            "practical increment. Never increase load, speed, range and "
            "complexity at the same time."
        )

    if "hip thrust" in q:
        return _substitute_answer("Hip Thrust")

    if "hourglass" in q or "glute" in q:
        return (
            "The hourglass shape in this program comes from three things: "
            "strong glutes and hips (hip thrusts, Romanian deadlifts, "
            "abductions), a strong toned waist (trunk work, not endless "
            "crunches), and balanced shoulders and back (rows, pulldowns, "
            "lateral raises). It is built over months — substantial change "
            "commonly takes 12-18 months — not promised by a date."
        )

    if "sore" in q or "pain" in q:
        return (
            "Mild muscle soreness after training is common; sharp pain is "
            "not. If it is sharp, in a joint, or it stops you moving "
            "normally, stop that exercise and get it checked. Never train "
            "through pain. If you are just sore, the readiness check will "
            "tell you whether to train, ease off (Yellow), or rest (Red)."
        )

    if "steroid" in q or "hormone" in q:
        return (
            "No. This program never recommends steroids, hormones, or drug "
            "protocols. Progress comes from training, food, sleep and "
            "consistency."
        )

    if readiness:
        verdict = readiness.get("verdict")
        if verdict == "Yellow":
            return (
                "Your last readiness check was Yellow: reduce sets by "
                "20-30%, avoid new high-impact skills, keep effort moderate. "
                "Ask me about a specific exercise if you want a lighter "
                "version today."
            )
        if verdict == "Red":
            return (
                "Your last readiness check was Red: no strenuous workout "
                "today. Rest or gentle pain-free mobility only. Ask me "
                "again tomorrow after a fresh readiness check."
            )

    return (
        "Good question. I coach from the program: start with the seven-day "
        "re-entry week, follow the six-day split, log every set, and use the "
        "readiness check each morning. Ask me about a specific exercise "
        "(for example 'how do I hip thrust?'), your protein target, or what "
        "to do after a missed workout."
    )
