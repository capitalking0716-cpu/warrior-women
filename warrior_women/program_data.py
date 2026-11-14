"""Warrior Women — program data.

The full women's training program: a strong, athletic hourglass figure
built through glute and hip development, a strong toned waist, and
balanced shoulders and back. Gym-based, six training days + one rest day,
seven-day re-entry week first, 120-day foundation, 24-week progression.

This module is pure data + small helpers. No Streamlit, no database,
no network — so it is easy to test.
"""

APP_NAME = "Warrior Women"
TAGLINE = "Build the body. Master the movement."
GOAL_FRAMING = (
    "A strong, athletic hourglass built through glute and hip development, "
    "a strong toned waist, and balanced shoulders and back — measured in "
    "strength, mobility and conditioning, not a single bodyweight number."
)
PRICE_MONTHLY_USD = 10
CHECKOUT_URL = "https://buy.stripe.com/00w6oGbGz6dugXU0ve97G0d"
STRIPE_PRICE_ID = "price_1UaH5BCXOGypS7lTcOV4GsQP"

# ---------------------------------------------------------------------------
# Safety — shown in the app and enforced by the coach guardrails.
# ---------------------------------------------------------------------------
SAFETY_RULES = [
    "No one-rep-max testing, ever.",
    "No steroids, hormones or drug protocols.",
    "Never train through pain.",
    "Stop exercise for sharp pain, dizziness, chest pain, unusual "
    "shortness of breath, numbness or loss of coordination, and seek "
    "appropriate medical care.",
    "Aim for 7-9 hours of sleep and one full rest day every week.",
    "Substantial all-around transformation commonly takes 12-18 months; "
    "meaningful early changes may appear in 8-12 weeks.",
    "No promised body, no fixed final bodyweight, no guaranteed date.",
]

# ---------------------------------------------------------------------------
# Progression rules (double progression) and deloads.
# ---------------------------------------------------------------------------
PROGRESSION_RULES = [
    "Start at the lower end of a rep range with 2-3 reps in reserve (RIR 2-3).",
    "Add reps across sessions while technique stays clean.",
    "When all sets reach the top of the range with good form on two sessions, "
    "increase load by the smallest practical increment.",
    "If the load jump is too large, add reps or use a safe variation.",
    "If performance drops for two sessions, soreness persists, sleep is poor "
    "or energy is low, reduce volume and recover.",
    "Never increase load, speed, range and complexity at the same time.",
]

DELOAD_RULES = [
    "Every fourth week is a deload.",
    "Reduce hard sets by about 25-40%, keep movement practice easy.",
    "No max testing during a deload.",
    "The app never automatically increases weight each week.",
]

# ---------------------------------------------------------------------------
# Readiness traffic lights.
# ---------------------------------------------------------------------------
READINESS_RULES = {
    "Green": (
        "Perform the planned session if the warm-up feels normal."
    ),
    "Yellow": (
        "Reduce sets by 20-30%, avoid new high-impact skills, keep effort "
        "moderate."
    ),
    "Red": (
        "No strenuous workout. Rest or gentle pain-free mobility only, and "
        "seek professional advice where appropriate."
    ),
}


def readiness_verdict(sleep_hours, energy, soreness, stress, pain):
    """Verdict from a 1-5 self-rating (sleep is hours).

    pain: True/False — any current pain.
    Returns one of 'Green', 'Yellow', 'Red'.
    """
    if pain:
        return "Red"
    score = 0
    if sleep_hours is not None and sleep_hours < 6:
        score += 2
    if energy is not None and energy <= 2:
        score += 2
    if soreness is not None and soreness >= 4:
        score += 1
    if stress is not None and stress >= 4:
        score += 1
    if score >= 3:
        return "Red"
    if score >= 1:
        return "Yellow"
    return "Green"


# ---------------------------------------------------------------------------
# Seven-day gym re-entry and baseline week. Low-fatigue orientation,
# not a challenge. Nothing is assumed complete.
# ---------------------------------------------------------------------------
REENTRY_WEEK = [
    {
        "day": 1,
        "title": "Upper-body movement check",
        "focus": "Learn the patterns, record comfortable loads",
        "items": [
            "Easy cardio 5-8 min",
            "Chest-supported machine row 2x10, easy",
            "Machine chest press 2x10, easy",
            "Lat pulldown 2x10, easy",
            "Seated dumbbell shoulder press or machine press 1-2x10, light",
            "Cable face pull 2x12, light",
            "Dead bug 2x6 each side",
        ],
        "note": "Record comfortable loads and technique notes. No maxes.",
    },
    {
        "day": 2,
        "title": "Lower-body movement check — glute focus",
        "focus": "Glute activation and comfortable ranges",
        "items": [
            "Easy bike or treadmill 5-8 min",
            "Bodyweight glute bridge 2x10",
            "Goblet squat to comfortable depth 2x8",
            "Leg press 2x10, light",
            "Dumbbell Romanian deadlift 2x8, light",
            "Seated leg curl 2x10",
            "Banded or machine hip abduction 2x12, light",
            "Supported single-leg balance 2x20 sec each side",
        ],
        "note": "Record any discomfort or range limits.",
    },
    {
        "day": 3,
        "title": "Mobility and movement",
        "focus": "Move well before you move heavy",
        "items": [
            "Easy walk 5 min",
            "Cat-cow 2x8",
            "90/90 hip switches 2x6",
            "Ankle rocks 2x10 each side",
            "Wall slides 2x10",
            "Supported squat hold 2x20 sec",
            "Tandem walk 3x10 steps",
            "Forward/backward and lateral steps 3x20 sec each",
            "Gentle shadow movement 3x45 sec, easy",
        ],
        "note": "Easy effort throughout. This is practice, not a workout.",
    },
    {
        "day": 4,
        "title": "Upper-body repeat — technique",
        "focus": "Second pass, clean technique",
        "items": [
            "Easy cardio 5-8 min",
            "Incline machine press 2x10",
            "Seated cable row 2x10",
            "Assisted pull-up or pulldown 2x8-10",
            "Dumbbell lateral raise 1-2x12",
            "Cable curl 1-2x12",
            "Rope triceps pressdown 1-2x12",
            "Pallof press 2x8 each side",
        ],
        "note": "Light-to-moderate loads, clean technique.",
    },
    {
        "day": 5,
        "title": "Lower-body repeat — glute focus",
        "focus": "Second pass, glute patterns",
        "items": [
            "Easy cardio 5-8 min",
            "Leg press or goblet squat 2x10",
            "Hip thrust, light weight or bodyweight 2x10",
            "Dumbbell Romanian deadlift 2x10, light",
            "Split squat holding support 1-2x6 each side",
            "Leg curl 2x10",
            "Calf raise 2x12",
            "Side plank 2x15-25 sec each side",
        ],
        "note": "Comfort first. Note what felt strong and what felt shaky.",
    },
    {
        "day": 6,
        "title": "Functional movement and easy conditioning",
        "focus": "Carry, step, balance, breathe",
        "items": [
            "Farmer carry 3x20 sec, moderate and controlled",
            "Glute bridge 2x10",
            "Low step-up 2x6 each side",
            "Incline push-up 2x8",
            "Cable row 2x10",
            "Bird dog 2x6 each side",
            "Balance near support 2x20 sec each side",
            "Easy conversational cardio 10-15 min",
            "Gentle full-body mobility 5 min",
        ],
        "note": "Conversational pace — you should be able to talk the whole time.",
    },
    {
        "day": 7,
        "title": "Full rest and review",
        "focus": "Look back before Week 2",
        "items": [
            "Rest — no training today",
            "Review: energy, soreness, sleep, technique, loads, confidence",
            "Do not make up missed sessions — just start Week 2 from where you are",
        ],
        "note": "Use the review to set your starting loads for Week 2.",
    },
]

# ---------------------------------------------------------------------------
# Main weekly split. Six training days + one rest day.
# exercises: (name, sets x reps, note)
# ---------------------------------------------------------------------------
WEEKLY_SPLIT = [
    {
        "day": "Monday",
        "title": "Upper-body strength",
        "focus": "Push and pull strength",
        "duration_min": "60-85",
        "exercises": [
            ("Machine or Barbell Chest Press", "3x6-10", "Main push"),
            ("Assisted Pull-Up or Lat Pulldown", "3x8-12", "Main pull"),
            ("Chest-Supported Machine Row", "3x8-12", "Back thickness"),
            ("Dumbbell Overhead Press", "2x8-10", "Shoulders"),
            ("Cable Face Pull", "2x12-15", "Rear shoulders, posture"),
            ("Dumbbell Curl", "2x10-15", "Arms"),
            ("Dead Bug", "3x8 each side", "Trunk control"),
        ],
    },
    {
        "day": "Tuesday",
        "title": "Lower-body strength — glute / hip dominant",
        "focus": "Glutes and hips first",
        "duration_min": "60-85",
        "exercises": [
            ("Hip Thrust", "3x8-10", "Main glute lift"),
            ("Squat Pattern (Goblet / Hack / Barbell)", "3x6-10", "Pick by skill"),
            ("Romanian Deadlift (Dumbbell)", "3x8-10", "Hinge, hamstrings"),
            ("Leg Press", "2x10-12", "Volume"),
            ("Seated Leg Curl", "2x10-12", "Hamstrings"),
            ("Hip Abduction (Machine)", "2x12-15", "Glute medius"),
            ("Calf Raise", "3x12-15", "Calves"),
            ("Side Plank", "2x20-40 sec each side", "Trunk"),
        ],
        "note": (
            "Power is earned — no jumps during re-entry. Later, low-amplitude "
            "jumps 3x3-5 with full rest only when landing skill and "
            "conditioning are adequate. Stop if technique degrades."
        ),
    },
    {
        "day": "Wednesday",
        "title": "Monkey King movement day",
        "focus": "Mobility, balance, footwork",
        "duration_min": "45-70",
        "exercises": [
            ("90/90 Hip Switch", "2x8", "Hip mobility"),
            ("Hip Flexor Stretch", "2x30 sec each side", "Comfortable hold"),
            ("Adductor Rock-Back", "2x8", "Inner thigh"),
            ("Ankle Rocks", "2x10", "Ankle mobility"),
            ("Thoracic Rotation", "2x8 each side", "Upper back"),
            ("Wall Slide", "2x10", "Shoulders"),
            ("Supported Single-Leg Balance", "3x20-30 sec each side", "Balance"),
            ("Tandem Walk", "3x10 steps", "Balance"),
            ("Forward/Backward Stance Steps", "3x30 sec", "Footwork"),
            ("Lateral Steps", "3x30 sec", "Footwork"),
            ("Controlled Pivots", "2x8 each direction", "Footwork"),
            ("Shadow Movement", "3x60 sec, easy", "Flow"),
            ("Incline Push-Up", "2x8-12, optional", "Light calisthenics"),
            ("Assisted Pull-Up", "2x5-8, optional", "Light calisthenics"),
        ],
        "note": "No maximal speed, no sparring, no blindfolded drills.",
    },
    {
        "day": "Thursday",
        "title": "Upper-body hypertrophy — shoulders / back emphasis",
        "focus": "A balanced silhouette",
        "duration_min": "60-85",
        "exercises": [
            ("Incline Dumbbell Press", "3x8-12", "Upper chest"),
            ("Seated Cable Row", "3x10-12", "Back"),
            ("Machine Chest Press or Cable Fly", "2x10-15", "Chest"),
            ("Neutral-Grip Pulldown", "2x10-12", "Lats"),
            ("Dumbbell Lateral Raise", "3x12-15", "Shoulder width"),
            ("Hammer Curl", "2x10-15", "Arms"),
            ("Rope Triceps Pressdown", "2x10-15", "Arms"),
        ],
    },
    {
        "day": "Friday",
        "title": "Lower-body hypertrophy + trunk — glute focus",
        "focus": "Glute volume and a strong waist",
        "duration_min": "60-85",
        "exercises": [
            ("Hip Thrust", "3x8-12", "Main glute lift"),
            ("Dumbbell or Machine Romanian Deadlift", "3x8-12", "Hinge"),
            ("Bulgarian Split Squat or Reverse Lunge", "2x8 each side", "Single leg"),
            ("Hip Abduction (Machine)", "2x12-15", "Glute medius"),
            ("Cable Kickback", "2x12 each side", "Glute isolation"),
            ("Seated Leg Curl", "2x10-15", "Hamstrings"),
            ("Calf Raise", "3x12-20", "Calves"),
            ("Cable Anti-Rotation Press", "2x10 each side", "Trunk"),
            ("Reverse Crunch", "2x10-15", "Trunk"),
        ],
    },
    {
        "day": "Saturday",
        "title": "Functional strength, conditioning + movement",
        "focus": "Carry, step, move, breathe",
        "duration_min": "45-70",
        "exercises": [
            ("Farmer Carry", "4x20-40 sec", "Grip and trunk"),
            ("Step-Up", "2x8 each side", "Single leg"),
            ("Cable or Chest-Supported Row", "2x10", "Pull"),
            ("Push-Up Variation", "2x8-12", "Push"),
            ("Glute Bridge", "2x10", "Glutes"),
            ("Bird Dog", "2x8 each side", "Trunk"),
            ("Weight Shifts", "3x30 sec", "Balance"),
            ("Step-and-Pivot to Visual Cue", "3x30 sec", "Footwork"),
            ("Shadow Movement", "3x60 sec, easy", "Flow"),
            ("Conversational Cardio", "10-15 min, build toward 20-25", "Aerobic base"),
        ],
        "note": (
            "No hard intervals until a basic aerobic base and good recovery "
            "are established."
        ),
    },
    {
        "day": "Sunday",
        "title": "Full rest",
        "focus": "Recover",
        "duration_min": "-",
        "exercises": [],
        "note": "A different rest day can be chosen in Settings.",
    },
]

# ---------------------------------------------------------------------------
# 120-day Warrior Foundation (runs alongside the strength split).
# ---------------------------------------------------------------------------
BLOCKS_120 = [
    {
        "block": 1,
        "days": "Days 1-30",
        "name": "Awakening / Re-entry",
        "focus": (
            "Routine and gym technique. Joint tolerance, basic strength, easy "
            "conditioning. Learn squat, hinge, push, pull, carry, step, pivot "
            "and balance patterns. No maximal tests, forced flexibility, "
            "advanced acrobatics or hard sparring."
        ),
    },
    {
        "block": 2,
        "days": "Days 31-60",
        "name": "Earth / Build",
        "focus": (
            "Progress main lifts gradually. Static balance to controlled "
            "reaches and slow direction changes. Low-impact conditioning once "
            "or twice weekly as recovery allows. Low-amplitude jumps only "
            "when landing mechanics are reliable."
        ),
    },
    {
        "block": 3,
        "days": "Days 61-90",
        "name": "Fire / Warrior",
        "focus": (
            "Controlled speed, power and coordination. Small jump/skip sets "
            "if pain-free and conditioned. Multi-direction footwork and "
            "visual-cue response. Keep skill crisp — stop before fatigue "
            "degrades technique."
        ),
    },
    {
        "block": 4,
        "days": "Days 91-120",
        "name": "Water / Integration",
        "focus": (
            "Combine strength, mobility, balance, footwork and redirection. "
            "Progress carries, unilateral strength and bodyweight control. "
            "Cooperative partner drills only with qualified instruction. "
            "Reassess baseline tests and plan the next cycle."
        ),
    },
]

# ---------------------------------------------------------------------------
# 24-week physique and strength progression.
# ---------------------------------------------------------------------------
PHASES_24 = [
    {"weeks": "1-4", "name": "Foundation", "focus": "Technique, routine, work capacity."},
    {"weeks": "5-8", "name": "Build", "focus": "Progressive strength and muscle."},
    {"weeks": "9-12", "name": "Warrior", "focus": "Strength and athletic coordination."},
    {"weeks": "13-16", "name": "Beast", "focus": "Training capacity and controlled power."},
    {"weeks": "17-20", "name": "Ascension", "focus": "Advanced bodyweight and mobility progressions."},
    {"weeks": "21-24", "name": "Super Saiyan", "focus": "Integration and reassessment."},
]

# ---------------------------------------------------------------------------
# Movement library — 40 exercises.
# Each entry: name, target, setup, execution, regression, progression, safety.
# ---------------------------------------------------------------------------
def _ex(name, target, setup, execution, regression, progression, safety):
    return {
        "name": name,
        "target": target,
        "setup": setup,
        "execution": execution,
        "regression": regression,
        "progression": progression,
        "safety": safety,
    }


EXERCISE_LIBRARY = [
    _ex("Hip Thrust", "Glutes",
        "Upper back on a bench, feet flat, bar or dumbbell across hips, chin tucked.",
        "Drive through heels, squeeze glutes at the top, ribs down. Lower with control.",
        "Bodyweight glute bridge.", "Barbell hip thrust, pause at top, single-leg.",
        "Keep ribs down — do not arch the lower back. Stop if the lower back takes over."),
    _ex("Glute Bridge", "Glutes",
        "Lie on your back, knees bent, feet flat near hips, arms by sides.",
        "Press through heels, lift hips until knees-hips-shoulders line up, squeeze. Lower slowly.",
        "Shorter range, feet closer.", "Single-leg bridge, band around knees, weighted bridge.",
        "Do not over-extend the lower back at the top."),
    _ex("Hip Abduction (Machine)", "Glute medius",
        "Sit tall, pads against outer knees, feet on platforms.",
        "Push knees outward with control, pause, return slowly — do not let the stack slam.",
        "Band abduction seated.", "Slower tempo, pause at end range.",
        "Keep the pelvis still — do not rock side to side."),
    _ex("Cable Kickback", "Glutes",
        "Ankle strap on cable, hinge slightly, hands on the machine for balance.",
        "Kick the leg back and slightly out, squeeze the glute, return slowly.",
        "Bodyweight standing kickback.", "Slower tempo, pause at the squeeze.",
        "Keep the lower back still — the leg moves, the torso does not."),
    _ex("Bulgarian Split Squat", "Glutes, quads, single leg",
        "Rear foot on a bench behind you, front foot far enough forward to keep the knee over the ankle.",
        "Lower until the front thigh is near parallel, drive through the front heel.",
        "Split squat with rear foot on the floor, holding support.", "Dumbbells, goblet load, deficit.",
        "Hold support if balance is shaky. Stop if the front knee caves inward."),
    _ex("Goblet Squat", "Quads, glutes",
        "Hold a dumbbell at the chest, feet shoulder-width, toes slightly out.",
        "Sit between the heels, chest up, knees tracking over toes. Drive up.",
        "Bodyweight squat to a box.", "Heavier dumbbell, tempo squat.",
        "Do not let the heels lift or the knees collapse inward."),
    _ex("Barbell Back Squat", "Quads, glutes",
        "Bar across the upper back, hands gripping wide, feet shoulder-width.",
        "Brace, sit down and back, keep the chest up, drive through the mid-foot.",
        "Goblet squat, box squat.", "Pause squat, tempo squat.",
        "Use a rack with safety bars. Never max out. Stop if depth forces the back to round."),
    _ex("Romanian Deadlift (Dumbbell)", "Hamstrings, glutes",
        "Dumbbells in front of thighs, feet hip-width, soft knees.",
        "Push hips back, dumbbells slide down the thighs, slight knee bend. Feel the hamstrings stretch, then drive hips forward.",
        "Bodyweight hinge to a wall, single dumbbell.", "Barbell RDL, single-leg RDL.",
        "Keep the back flat — hinge at the hips, not the waist."),
    _ex("Leg Press", "Quads, glutes",
        "Back flat on the pad, feet shoulder-width on the platform.",
        "Lower with control until knees are near 90 degrees, press without locking knees.",
        "Lighter load, shorter range.", "Single-leg press, slow tempo.",
        "Do not let the lower back lift off the pad. Never lock the knees hard."),
    _ex("Seated Leg Curl", "Hamstrings",
        "Pad behind the lower calves, knees lined up with the machine pivot.",
        "Curl the pad down with control, squeeze, return slowly.",
        "Lighter load, partial range.", "Single-leg curl, slow negatives.",
        "Do not jerk the weight or lift the hips off the seat."),
    _ex("Calf Raise", "Calves",
        "Ball of the foot on a step or platform, heels hanging off.",
        "Rise high onto the toes, pause, lower slowly below level.",
        "Flat-floor calf raise, holding support.", "Single-leg, weighted, slow tempo.",
        "Hold support if balance is shaky."),
    _ex("Reverse Lunge", "Glutes, quads, single leg",
        "Stand tall, step one foot back.",
        "Lower until both knees are near 90 degrees, push through the front heel to return.",
        "Split squat in place, holding support.", "Dumbbells, deficit reverse lunge.",
        "Keep the front knee tracking over the toes."),
    _ex("Step-Up", "Glutes, quads, single leg",
        "One foot on a low step or box, chest tall.",
        "Drive through the step foot to stand, lower with control. Do not push off the trailing leg.",
        "Lower step, holding support.", "Higher box, dumbbells.",
        "Hold support if balance is shaky. Keep the knee tracking over the toes."),
    _ex("Machine Chest Press", "Chest",
        "Seat set so handles are at mid-chest, back flat on the pad.",
        "Press forward until arms are nearly straight, return with control.",
        "Lighter load, shorter range.", "Slower tempo, single-arm.",
        "Do not let the shoulders roll forward off the pad."),
    _ex("Incline Dumbbell Press", "Upper chest",
        "Bench at a low incline, dumbbells at the shoulders.",
        "Press up and slightly together, elbows at about 45 degrees. Lower with control.",
        "Machine incline press.", "Heavier dumbbells, tempo press.",
        "Do not flare the elbows wide or bounce the weights."),
    _ex("Cable Fly", "Chest",
        "Cables at shoulder height, slight forward lean, soft elbows.",
        "Bring hands together in front of the chest, squeeze, return slowly.",
        "Machine fly, lighter load.", "Low-to-high or high-to-low angles.",
        "Keep the elbows soft and the movement in the chest, not the shoulders."),
    _ex("Chest-Supported Machine Row", "Back",
        "Chest on the pad, handles in reach, feet braced.",
        "Pull elbows back, squeeze shoulder blades, lower with control.",
        "Lighter load, shorter range.", "Slower tempo, single-arm.",
        "Do not swing the torso — the chest stays on the pad."),
    _ex("Seated Cable Row", "Back",
        "Feet on the platform, knees soft, handle in both hands, chest tall.",
        "Pull the handle to the lower ribs, elbows close, squeeze, return slowly.",
        "Lighter load, chest-supported row.", "Single-arm row, slow tempo.",
        "Do not rock the torso back and forth."),
    _ex("Lat Pulldown", "Lats",
        "Knees under the pad, grip just wider than shoulders.",
        "Pull the bar to the upper chest, elbows driving down, return with control.",
        "Lighter load, neutral grip.", "Slower tempo, single-arm pulldown.",
        "Do not lean far back or jerk the bar."),
    _ex("Assisted Pull-Up", "Lats, biceps",
        "Knees or feet on the assisted platform, grip shoulder-width or wider.",
        "Pull the chest to the bar, control the lowering. Use less assistance over time.",
        "Lat pulldown.", "Less assistance, negative-only reps.",
        "Use a full controlled range — do not drop at the bottom."),
    _ex("Neutral-Grip Pulldown", "Lats",
        "Knees under the pad, neutral (palms facing) grip on the handles.",
        "Pull handles to the chest, elbows close to the body, return with control.",
        "Standard lat pulldown.", "Slower tempo, single-arm.",
        "Do not lean far back or jerk."),
    _ex("Dumbbell Overhead Press", "Shoulders",
        "Dumbbells at shoulder height, elbows slightly forward, core braced.",
        "Press overhead until arms are straight, lower with control.",
        "Machine shoulder press.", "Seated press, tempo press.",
        "Do not arch the lower back to press the weight up."),
    _ex("Seated Dumbbell Shoulder Press", "Shoulders",
        "Seated with back support, dumbbells at shoulder height.",
        "Press overhead, lower with control. Keep the ribs down.",
        "Machine shoulder press.", "Standing press, tempo press.",
        "Stop if the shoulders pinch or the back arches."),
    _ex("Dumbbell Lateral Raise", "Side shoulders",
        "Dumbbells at the sides, slight elbow bend, chest tall.",
        "Raise arms to shoulder height, slight pause, lower slowly.",
        "Cable lateral raise, lighter load.", "Slower tempo, partial top range.",
        "Do not swing the weights or shrug the traps up."),
    _ex("Cable Face Pull", "Rear shoulders, posture",
        "Rope at face height, grip with thumbs toward you.",
        "Pull the rope to the face, elbows high and wide, squeeze, return slowly.",
        "Lighter load, shorter range.", "Slower tempo, split stance.",
        "Keep the chest tall — do not lean back."),
    _ex("Cable Curl", "Biceps",
        "Stand tall, bar or rope at the cable, elbows pinned to the sides.",
        "Curl to the shoulders, squeeze, lower with control.",
        "Dumbbell curl.", "Single-arm curl, slow negatives.",
        "Do not swing the torso to lift the weight."),
    _ex("Hammer Curl", "Biceps, forearms",
        "Dumbbells at the sides, palms facing each other.",
        "Curl with palms still facing, squeeze, lower slowly.",
        "Cable curl.", "Slower tempo, cross-body curl.",
        "Keep the elbows pinned to the sides."),
    _ex("Rope Triceps Pressdown", "Triceps",
        "Rope at the cable, elbows pinned to the sides, slight lean.",
        "Press the rope down, split the ends at the bottom, return with control.",
        "Dumbbell kickback.", "Single-arm pressdown, slow tempo.",
        "Do not let the elbows drift forward."),
    _ex("Dead Bug", "Trunk control",
        "Lie on your back, arms up, hips and knees at 90 degrees, lower back pressed to the floor.",
        "Extend one arm and the opposite leg, return, switch sides. Keep the back on the floor.",
        "Arms only or legs only.", "Slower tempo, straight legs.",
        "If the lower back lifts off the floor, shorten the range."),
    _ex("Pallof Press", "Trunk, anti-rotation",
        "Cable at chest height at your side, hands together at the chest.",
        "Press the handle straight out, resist the pull to the side, hold, return.",
        "Shorter hold, closer stance.", "Longer holds, half-kneeling.",
        "Keep the hips square — do not let the cable twist you."),
    _ex("Side Plank", "Trunk, obliques",
        "Elbow under the shoulder, body in one straight line, feet stacked.",
        "Hold the line from head to heels, breathe normally.",
        "Knees on the floor.", "Longer holds, top leg lift.",
        "Do not let the hips sag or rotate. Stop if the shoulder hurts."),
    _ex("Reverse Crunch", "Lower abs",
        "Lie on your back, knees bent 90 degrees, hands by the sides.",
        "Lift the hips a few inches off the floor, lower with control. Small, controlled range.",
        "Knee raises, partial range.", "Slower tempo, straight legs.",
        "Do not swing the legs for momentum."),
    _ex("Bird Dog", "Trunk, balance",
        "On hands and knees, back flat, core braced.",
        "Extend the opposite arm and leg, hold, return, switch. Keep the hips level.",
        "Arm only or leg only.", "Longer holds, draw a square with the foot.",
        "If the hips tip, shorten the reach."),
    _ex("Farmer Carry", "Grip, trunk, legs",
        "Dumbbells or handles at the sides, tall posture, shoulders down.",
        "Walk with short, controlled steps, ribs down, steady breathing.",
        "Lighter load, shorter distance.", "Heavier load, longer distance.",
        "Stop if the posture collapses or the load pulls you sideways."),
    _ex("Push-Up (Incline)", "Chest, shoulders, triceps",
        "Hands on a bench or bar, body in one straight line, hands under the shoulders.",
        "Lower the chest to the bar, press back up. Keep the body straight.",
        "Wall push-up, higher incline.", "Lower surface, floor push-up.",
        "Do not let the hips sag — shorten the range before breaking form."),
    _ex("Hack Squat", "Quads, glutes",
        "Back and shoulders on the pads, feet shoulder-width on the platform.",
        "Lower with control, drive through the mid-foot. Keep the lower back on the pad.",
        "Goblet squat, leg press.", "Slower tempo, narrow stance.",
        "Do not let the knees collapse inward."),
    _ex("Cable Anti-Rotation Press", "Trunk",
        "Cable at chest height at your side, hands at the chest.",
        "Press out and hold against the pull, return. Same pattern as the Pallof press.",
        "Shorter hold.", "Half-kneeling, longer holds.",
        "Keep the hips square."),
    _ex("90/90 Hip Switch", "Hip mobility",
        "Sit with one leg forward and one leg back, both knees at 90 degrees.",
        "Switch sides smoothly, keeping the chest tall.",
        "Hold each side longer, hands on the floor for support.", "Hands-free switch.",
        "Work within a comfortable range — do not force the knees."),
    _ex("Wall Slide", "Shoulder mobility",
        "Back and arms against a wall, elbows at 90 degrees.",
        "Slide arms up as high as comfortable, then back down, keeping contact.",
        "Smaller range.", "Longer holds at the top.",
        "Stop if the shoulders pinch."),
    _ex("Cat-Cow", "Spine mobility",
        "On hands and knees, back flat.",
        "Round the spine up (cat), then arch gently (cow). Move slowly with the breath.",
        "Smaller ranges.", "Segmental cat-cow, slow breathing.",
        "Move only within a comfortable range."),
]

# ---------------------------------------------------------------------------
# Baseline + four-week reassessment (submaximal, repeatable, no 1RM).
# ---------------------------------------------------------------------------
BASELINE_TESTS = [
    "Bodyweight (and optional waist measurement)",
    "Comfortable push-up variation — clean reps",
    "Assisted pull-up / pulldown benchmark, or supported hang time",
    "Controlled squat quality and comfortable range",
    "Single-leg balance time, each side, near support",
    "Comfortable ankle mobility and overhead reach",
    "Six-minute walk or conversational-pace cardio benchmark",
    "Sleep, energy, soreness and confidence ratings (1-5)",
]

NUTRITION_GUIDANCE = [
    "Establish maintenance intake with a 1-2 week food log before setting a calorie target.",
    "If fat loss is appropriate, a modest deficit of about 250-400 kcal/day, "
    "while monitoring strength, energy and waist.",
    "Protein around 1.6-2.2 g/kg/day of goal or reference bodyweight, "
    "adjusted for preference and tolerance.",
    "Fruit, vegetables, fiber-rich carbohydrates, healthy fats, sufficient fluids.",
    "Spread protein over 3-5 meals.",
    "Avoid crash dieting, forced food volume, or a 5,000-calorie bulk.",
    "Reassess after 3-4 weeks.",
    "Do not prescribe supplements, diagnose conditions, or replace a clinician or dietitian.",
]


def protein_target_grams(weight_kg):
    """Protein target range in grams/day from bodyweight (1.6-2.2 g/kg)."""
    if not weight_kg or weight_kg <= 0:
        return None
    return (round(weight_kg * 1.6), round(weight_kg * 2.2))


def library_names():
    return [e["name"] for e in EXERCISE_LIBRARY]


def get_exercise(name):
    for e in EXERCISE_LIBRARY:
        if e["name"].lower() == name.lower():
            return e
    return None


def week_for_day_number(day_number):
    """Map a program day number (1-based, from onboarding start) to a block.

    Returns (foundation_block, phase) for the given day.
    """
    if day_number <= 30:
        block = BLOCKS_120[0]
    elif day_number <= 60:
        block = BLOCKS_120[1]
    elif day_number <= 90:
        block = BLOCKS_120[2]
    else:
        block = BLOCKS_120[3]
    week = (day_number - 1) // 7 + 1
    phase = PHASES_24[min((week - 1) // 4, len(PHASES_24) - 1)]
    return block, phase, week
