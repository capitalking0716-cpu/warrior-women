"""Warrior Women — standalone membership app.

Public landing + member sign-up/login + REAL Stripe paywall ($10/month)
+ the full women's training program with per-member saved data.

Run locally:  streamlit run app.py
Deploy: see DEPLOY.md (Streamlit Community Cloud, free).

The Stripe secret key comes from Streamlit Secrets (st.secrets) or the
STRIPE_SECRET_KEY environment variable. It is never in this repo.
Without it, the paywall stays locked and says so plainly.

Presentation: warrior_women/theme.py — the same design system as
King Warrior (black / deep purple / gold, card-based workout-app
layout) mirrored across every view.
"""

import html as _html
import json
import os
from datetime import date, datetime, timedelta

import streamlit as st

from warrior_women import auth, challenge, coach, db, paywall, theme
from warrior_women import program_data as pd

APP = pd.APP_NAME
EQUIPMENT_OPTIONS = [
    "Dumbbells and benches",
    "Barbells and racks",
    "Cable stations",
    "Selectorized chest/back/leg machines",
    "Leg press / hack squat",
    "Pull-up / assisted pull-up station",
    "Cardio machines",
    "Open floor / mat area",
    "Bands",
    "Kettlebells",
    "Sled",
    "Medicine ball",
    "Boxes / steps",
]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_LETTERS = ["M", "T", "W", "T", "F", "S", "S"]

st.set_page_config(page_title=APP, page_icon="💜", layout="centered")
theme.inject_css()


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------
def get_conn():
    if "conn" not in st.session_state:
        st.session_state.conn = db.connect()
    return st.session_state.conn


def get_secrets():
    try:
        return st.secrets
    except Exception:
        return {}


def current_member():
    mid = st.session_state.get("member_id")
    if not mid:
        return None
    return db.get_member(get_conn(), mid)


def logout():
    for key in ("member_id", "member_email", "member_name", "unlocked",
                "unlocked_at", "profile", "join_challenge"):
        st.session_state.pop(key, None)
    st.rerun()


def refresh_profile():
    member = current_member()
    st.session_state.profile = db.get_profile(get_conn(), member["id"]) if member else None


def check_subscription(force=False):
    """Return a PaywallResult, cached ~10 minutes per session."""
    now = datetime.now()
    cached = st.session_state.get("paywall_result")
    cached_at = st.session_state.get("paywall_at")
    if cached and cached_at and not force and (now - cached_at) < timedelta(minutes=10):
        return cached
    result = paywall.has_active_subscription(
        st.session_state.member_email, secrets=get_secrets()
    )
    st.session_state.paywall_result = result
    st.session_state.paywall_at = now
    st.session_state.unlocked = result.unlocked
    return result


def program_day_number(profile):
    start = profile.get("start_date") if profile else None
    return challenge.program_day(start)


# ---------------------------------------------------------------------------
# Design-system helpers (presentation only)
# ---------------------------------------------------------------------------
def chips_html(pairs):
    """pairs: list of (text, is_gold) rendered as pill chips."""
    inner = "".join(
        f'<span class="kw-chip{" gold" if gold else ""}">{_html.escape(str(text))}</span>'
        for text, gold in pairs
    )
    return f'<div class="kw-chips">{inner}</div>'


def render_topbar(member=None, badge=None, badge_purple=False):
    st.markdown(
        theme.topbar_html(
            "💜", "Warrior", "Women",
            member_name=(member["name"] if member else None),
            badge=badge, badge_purple=badge_purple,
        ),
        unsafe_allow_html=True,
    )


def render_nav(pages, key):
    """Pill navigation + log out, replacing the old sidebar."""
    col_nav, col_out = st.columns([5, 1])
    with col_nav:
        page = st.radio("Go to", pages, horizontal=True,
                        label_visibility="collapsed", key=key)
    with col_out:
        if st.button("Log out", key=f"{key}_logout"):
            logout()
    return page


def render_member_week_strip(conn, member):
    """Mon–Sun strip for the current week: done / today / rest / upcoming."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    done_dates = {log["date"] for log in db.all_set_logs(conn, member["id"])}
    rest_name = (st.session_state.profile or {}).get("rest_day") or "Sunday"
    days = []
    for i, weekday in enumerate(WEEKDAYS):
        d = monday + timedelta(days=i)
        state, mark = "", ""
        if d.isoformat() in done_dates:
            state, mark = "done", "✓"
        if weekday == rest_name and state == "":
            state, mark = "rest", "·"
        if d == today:
            state = "today"
        days.append({"letter": DAY_LETTERS[i], "num": d.day,
                     "state": state, "mark": mark})
    st.markdown(theme.week_strip_html(days), unsafe_allow_html=True)


def workout_started_today(conn, member_id):
    today_iso = date.today().isoformat()
    if st.session_state.get(f"started_{today_iso}"):
        return True
    return any(log["date"] == today_iso
               for log in db.all_set_logs(conn, member_id))


def start_button(conn, member_id):
    """The hero Start/Continue button. Presentation state only — it
    never touches program data; logging works exactly as before."""
    if workout_started_today(conn, member_id):
        st.success("🏋️ Workout in progress — let's go.")
        return
    if st.button("▶ Start workout", type="primary", key="start_workout"):
        st.session_state[f"started_{date.today().isoformat()}"] = True
        st.rerun()


# ---------------------------------------------------------------------------
# Public landing
# ---------------------------------------------------------------------------
def render_landing():
    st.markdown(
        f"""
        <div class="kw-land-hero">
          <div class="kw-land-icon">💜</div>
          <div class="kw-land-name">Warrior <span>Women</span></div>
          <div class="kw-land-tag">{_html.escape(pd.TAGLINE)}</div>
          <div class="kw-land-frame">{_html.escape(pd.GOAL_FRAMING)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.header("What you get")
    st.write(
        "A gym-based program for women, built around one goal: strong, "
        "athletic, and balanced — strong glutes and hips, a strong toned "
        "waist, and balanced shoulders and back."
    )
    features = [
        ("🗓️", "Six training days + one rest day",
         "Strength, glutes, mobility, footwork and conditioning."),
        ("🌅", "Seven-day re-entry week first",
         "Learn every movement, nothing assumed."),
        ("🏛️", "120-day Warrior Foundation",
         "Awakening, Earth, Fire, Water."),
        ("📈", "24-week progression",
         "Foundation, Build, Warrior, Beast, Ascension, Super Saiyan."),
        ("📚", "40-exercise movement library",
         "Setup, regressions, progressions and safety for every movement."),
        ("✅", "Per-set logging",
         "Prior-performance hints, readiness checks, progress tracking."),
        ("🥩", "Nutrition & recovery",
         "Protein target from your bodyweight, food, water and sleep logs."),
        ("🤖", "AI coach",
         "Answers from the program and your own logs."),
    ]
    for i in range(0, len(features), 2):
        cols = st.columns(2)
        for col, (icon, title, text) in zip(cols, features[i:i + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="kw-feature"><div class="kw-ficon">{icon}</div>'
                        f'<div class="kw-ftitle">{_html.escape(title)}</div>'
                        f'<div class="kw-ftext">{_html.escape(text)}</div></div>',
                        unsafe_allow_html=True,
                    )

    # The front door: free 7-Day Challenge.
    with st.container(border=True):
        st.markdown("### 💪 Start FREE — the 7-Day Challenge")
        st.write(
            "Not ready to commit? Start with the challenge. The full seven-day "
            "re-entry week — every day's session, the movement library and the "
            "AI coach — is **free for 7 days**. No card, no payment. Create a "
            "challenge account below and Day 1 starts today."
        )
        st.write(
            "On day 7, Founding Members can lock in the full program at "
            "**$10/month — that price stays yours** for as long as you stay a "
            "member."
        )
        if st.button("Join the FREE 7-Day Challenge", key="landing_challenge_btn",
                     use_container_width=True, type="primary"):
            st.session_state.join_challenge = True
            st.rerun()
        if st.session_state.get("join_challenge"):
            st.success(
                "💜 The challenge sign-up is in the first tab under "
                "'Sign up / Log in' just below — pick **FREE 7-Day Challenge**."
            )

    st.header("The week")
    with st.container(border=True):
        for split in pd.WEEKLY_SPLIT:
            if split["exercises"]:
                st.markdown(
                    f"**{split['day']}** — {split['title']}  "
                    f'<span class="kw-chip">⏱ {split["duration_min"]} min</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"**{split['day']}** — {split['title']} 😴")

    st.header("Membership")
    with st.container(border=True):
        st.markdown(
            '<div class="kw-price"><span class="kw-amount">$10</span> '
            '<span class="kw-per">/ month</span></div>',
            unsafe_allow_html=True,
        )
        st.write(
            "The full program, your own saved data, and the coach — $10 a month. "
            "Cancel anytime in Stripe. Sign up below with the same email you use "
            "at checkout, then pay, and your membership unlocks."
        )
        st.link_button("Subscribe — $10/month", pd.CHECKOUT_URL,
                       use_container_width=True, type="primary")
        st.caption(
            "Payment is verified against Stripe. If you paid but the app says "
            "you are not a member yet, check that the email matches, then tap "
            "'Check my subscription' on the member page."
        )
    with st.expander("Safety — please read"):
        for rule in pd.SAFETY_RULES:
            st.write(f"- {rule}")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def render_auth():
    st.header("Sign up / Log in")
    tab_challenge, tab_signup, tab_login = st.tabs(
        ["FREE 7-Day Challenge", "Create account", "Log in"]
    )
    conn = get_conn()

    with tab_challenge:
        st.write(
            "Join the **FREE 7-Day Challenge**: the seven-day re-entry week, "
            "free. Create your account and Day 1 starts today — no card, no "
            "payment. Use the email you would pay with later so your start "
            "date and logs carry straight over if you become a member."
        )
        cname = st.text_input("Your name", key="ch_name")
        cemail = st.text_input("Email", key="ch_email")
        cpw = st.text_input("Password (at least 8 characters)", type="password", key="ch_pw")
        cpw2 = st.text_input("Repeat password", type="password", key="ch_pw2")
        if st.button("Start my FREE challenge", key="ch_btn"):
            problems = auth.validate_signup(cemail, cpw, cname)
            if cpw != cpw2:
                problems.append("Passwords do not match.")
            if problems:
                for p in problems:
                    st.error(p)
            else:
                salt, digest = auth.hash_password(cpw)
                member_id = db.create_member(
                    conn, cemail, salt, digest, cname,
                    account_type=challenge.ACCOUNT_CHALLENGE,
                )
                if member_id is None:
                    st.error("An account with that email already exists. Try logging in.")
                else:
                    st.session_state.member_id = member_id
                    st.session_state.member_email = cemail.strip().lower()
                    st.session_state.member_name = cname.strip()
                    st.session_state.pop("join_challenge", None)
                    st.success("You're in! Your 7-Day Challenge starts with setup — Day 1 is today.")
                    st.rerun()

    with tab_signup:
        st.write("Create your Warrior Women account. Use the same email you will pay with.")
        name = st.text_input("Your name", key="su_name")
        email = st.text_input("Email", key="su_email")
        pw = st.text_input("Password (at least 8 characters)", type="password", key="su_pw")
        pw2 = st.text_input("Repeat password", type="password", key="su_pw2")
        if st.button("Create account", key="su_btn"):
            problems = auth.validate_signup(email, pw, name)
            if pw != pw2:
                problems.append("Passwords do not match.")
            if problems:
                for p in problems:
                    st.error(p)
            else:
                salt, digest = auth.hash_password(pw)
                member_id = db.create_member(conn, email, salt, digest, name)
                if member_id is None:
                    st.error("An account with that email already exists. Try logging in.")
                else:
                    st.session_state.member_id = member_id
                    st.session_state.member_email = email.strip().lower()
                    st.session_state.member_name = name.strip()
                    st.success("Account created. Next step: subscribe ($10/month).")
                    st.rerun()

    with tab_login:
        email = st.text_input("Email", key="li_email")
        pw = st.text_input("Password", type="password", key="li_pw")
        if st.button("Log in", key="li_btn"):
            member = db.get_member_by_email(conn, email)
            if not member or not auth.verify_password(pw, member["password_salt"], member["password_hash"]):
                st.error("Email or password is wrong.")
            else:
                st.session_state.member_id = member["id"]
                st.session_state.member_email = member["email"]
                st.session_state.member_name = member["name"]
                st.rerun()


# ---------------------------------------------------------------------------
# Paywall
# ---------------------------------------------------------------------------
def render_paywall(result):
    with st.container(border=True):
        st.markdown(
            '<div class="kw-price"><span class="kw-amount">$10</span> '
            '<span class="kw-per">/ month</span></div>',
            unsafe_allow_html=True,
        )
        st.header("Membership required")
        if result.reason == "not_configured":
            st.warning(
                "Payment verification is not set up on this app yet — the owner "
                "still needs to add the Stripe key. Your subscription cannot be "
                "checked until then, so the program stays locked."
            )
        elif result.reason == "error":
            st.error(
                "The subscription check failed. The program stays locked — "
                "it never unlocks on an error. Please try again in a few minutes."
            )
            st.caption(result.detail)
        else:
            st.write(
                "The full Warrior Women program is for members only — $10 a month. "
                "Subscribe with the same email as this account, then tap "
                "'Check my subscription'."
            )
        st.link_button("Subscribe — $10/month", pd.CHECKOUT_URL,
                       use_container_width=True, type="primary")
        if st.button("Check my subscription", use_container_width=True):
            result = check_subscription(force=True)
            if result.unlocked:
                st.success("Membership confirmed — welcome in!")
                st.rerun()
            else:
                st.info("No active subscription found for this email yet. "
                        "Make sure the checkout email matches your account email.")
        st.caption(
            "If you just paid, Stripe can take a minute. If it still does not "
            "unlock, check the email matches, then contact support."
        )


# ---------------------------------------------------------------------------
# Free 7-Day Challenge
# ---------------------------------------------------------------------------
def render_membership_offer(heading="Become a Founding Member"):
    """The day-7 conversion offer: Founding Member price lock + checkout."""
    with st.container(border=True):
        st.markdown(
            '<div class="kw-price"><span class="kw-amount">$10</span> '
            '<span class="kw-per">/ month · Founding price, locked</span></div>',
            unsafe_allow_html=True,
        )
        st.header(heading)
        st.write(
            "**Founding Member — $10/month, locked at that price** for as long "
            "as you stay a member. The full Warrior Women program unlocks: the "
            "weekly split, the 120-day Warrior Foundation, the 24-week "
            "progression, progress tracking, nutrition & recovery — everything "
            "past the re-entry week."
        )
        st.write(
            "Your challenge start date and every log you made carry straight "
            "over — you keep going from exactly where you are. Subscribe with "
            "the **same email** as this account, then tap 'Check my subscription'."
        )
        st.link_button("Become a member — $10/month", pd.CHECKOUT_URL,
                       use_container_width=True, type="primary")
        if st.button("Check my subscription", use_container_width=True, key="offer_check_btn"):
            result = check_subscription(force=True)
            if result.unlocked:
                st.success("Membership confirmed — welcome in, Founding Member!")
                st.rerun()
            else:
                st.info("No active subscription found for this email yet. "
                        "Make sure the checkout email matches your account email.")
        st.caption("Cancel anytime in Stripe.")


def render_challenge_program():
    """Program page for challenge members: the free week in full, the
    rest of the program behind a plain Members-only screen."""
    st.header("Program")
    st.subheader("Seven-day re-entry week — your FREE challenge")
    st.write("Low-fatigue orientation. Learn every movement before the real work starts.")
    for d in pd.REENTRY_WEEK:
        with st.expander(f"Day {d['day']}: {d['title']}"):
            st.caption(d["focus"])
            for item in d["items"]:
                st.write(f"- {item}")
            st.caption(d["note"])
    with st.container(border=True):
        st.subheader("🔒 Members only")
        st.write(
            "The weekly split, the 120-day Warrior Foundation, the 24-week "
            "progression, progression rules and deloads are the full program — "
            "they unlock with membership."
        )
        st.link_button("Become a member — $10/month", pd.CHECKOUT_URL,
                       use_container_width=True, type="primary")


def render_challenge_app():
    """The challenge view: days 1-7 of the re-entry week, nothing beyond."""
    member = current_member()
    if "profile" not in st.session_state:
        refresh_profile()
    if not st.session_state.profile or not st.session_state.profile.get("onboarding_done"):
        render_topbar(member)
        render_onboarding()
        return
    profile = st.session_state.profile
    day_no = challenge.challenge_day_number(profile)

    finished = challenge.challenge_finished(day_no)
    if finished:
        render_topbar(member, badge="Challenge complete", badge_purple=True)
        # The free week is over: the rest is members only.
        with st.container(border=True):
            st.markdown(
                theme.hero_html(
                    "7-Day Challenge",
                    "🎉 Challenge complete!",
                    focus="You finished the seven-day re-entry week — every "
                          "movement learned, every day logged. The rest of "
                          "the program is members only.",
                ),
                unsafe_allow_html=True,
            )
        render_membership_offer()
        if st.button("Log out", use_container_width=True):
            logout()
        return

    render_topbar(member, badge=f"Day {day_no} of 7", badge_purple=True)
    st.progress(day_no / challenge.CHALLENGE_DAYS)
    page = render_nav(
        ["Today", "Program", "Movement Library", "AI Coach", "Settings"],
        key="nav_challenge",
    )
    if page == "Today":
        st.info(f"💪 **Challenge Day {day_no} of 7** — your free re-entry week.")
        render_today()
        if challenge.show_membership_offer(day_no):
            render_membership_offer(heading="Last challenge day — keep going as a Founding Member")
    elif page == "Program":
        render_challenge_program()
    elif page == "Movement Library":
        render_library()
    elif page == "AI Coach":
        render_coach()
    elif page == "Settings":
        render_settings()
    st.markdown(
        '<div class="kw-footer">Membership: $10/month, Founding Member '
        "price lock. Cancel anytime in Stripe.</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------
def render_onboarding():
    st.header("Welcome — let's set up your program")
    st.write(
        "Answer for yourself. Waist measurement is optional and never blocks "
        "you. You start at the seven-day re-entry week — nothing is assumed."
    )
    member = current_member()
    if challenge.is_challenge_member(member):
        st.info(
            "💜 You're in the **FREE 7-Day Challenge** — this setup starts "
            "your challenge today. The seven-day re-entry week below is "
            "yours free; membership unlocks everything after it."
        )
    with st.form("onboarding"):
        height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=165.0, step=1.0)
        weight = st.number_input("Weight (kg)", min_value=35.0, max_value=200.0, value=70.0, step=0.5)
        location = st.text_input("Where do you train? (gym name / home gym)")
        days = st.number_input("Days available per week", min_value=1, max_value=7, value=6, step=1)
        injuries = st.text_area("Current pain or injuries (write 'none' if none)")
        health = st.text_area("Health notes your coach should know (optional)")
        sleep = st.number_input("Typical sleep (hours)", min_value=3.0, max_value=12.0, value=7.5, step=0.5)
        equipment = st.multiselect("Gym equipment you have", EQUIPMENT_OPTIONS,
                                   default=["Dumbbells and benches", "Cable stations", "Cardio machines", "Open floor / mat area"])
        rest_day = st.selectbox("Rest day", WEEKDAYS, index=6)
        waist = st.number_input("Waist (cm) — optional", min_value=0.0, max_value=200.0, value=0.0, step=0.5)
        submitted = st.form_submit_button("Start my program", use_container_width=True)
    if submitted:
        db.upsert_profile(
            get_conn(), member["id"],
            height_cm=height, weight_kg=weight, location=location.strip(),
            days_available=int(days), injuries=injuries.strip(),
            health_notes=health.strip(), sleep_hours=sleep,
            equipment=equipment, rest_day=rest_day,
            waist_cm=(waist if waist > 0 else None),
            start_date=date.today().isoformat(), onboarding_done=1,
        )
        refresh_profile()
        st.success("Your program starts today — Day 1 of the re-entry week.")
        st.rerun()

# ---------------------------------------------------------------------------
# Member app
# ---------------------------------------------------------------------------
def today_session(profile):
    """Return (label, day) for today's session: re-entry or weekly split."""
    day_no = program_day_number(profile)
    if day_no <= 7:
        return ("Re-entry", pd.REENTRY_WEEK[day_no - 1])
    weekday = WEEKDAYS[date.today().weekday()]
    split = next(s for s in pd.WEEKLY_SPLIT if s["day"] == weekday)
    return ("Program", split)


def render_readiness():
    """Daily readiness check + latest verdict."""
    member = current_member()
    conn = get_conn()
    with st.container(border=True):
        st.subheader("🩺 Readiness check")
        with st.form("readiness"):
            sleep = st.number_input("Sleep last night (hours)", min_value=0.0, max_value=14.0, value=7.0, step=0.5)
            energy = st.slider("Energy (1 low - 5 great)", 1, 5, 3)
            soreness = st.slider("Soreness (1 none - 5 very sore)", 1, 5, 2)
            stress = st.slider("Stress (1 calm - 5 very stressed)", 1, 5, 2)
            pain = st.checkbox("I have pain today")
            if st.form_submit_button("Save readiness", use_container_width=True):
                verdict = pd.readiness_verdict(sleep, energy, soreness, stress, pain)
                db.log_readiness(conn, member["id"], date.today().isoformat(),
                                 sleep, energy, soreness, stress, pain, verdict)
                st.success(f"Readiness: **{verdict}** — {pd.READINESS_RULES[verdict]}")
        latest = db.latest_readiness(conn, member["id"])
        if latest:
            st.info(f"Latest readiness: **{latest['verdict']}** ({latest['date']}) — "
                    f"{pd.READINESS_RULES[latest['verdict']]}")


def render_exercise_card(idx, ex_name, sets_reps, note, session, conn, member):
    """One exercise as a workout-app card: name + prescription chips,
    last performance, form cues, set-logging row. Widget keys and the
    log call are exactly as before. (Warrior Women has no demo clips —
    no demo slot is faked.)"""
    with st.container(border=True):
        st.markdown(
            f'<div class="kw-exhead"><span class="kw-exnum">{idx}</span>'
            f'<span class="kw-exname">{_html.escape(ex_name)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(chips_html([(sets_reps, True), (note, False)]),
                    unsafe_allow_html=True)
        ex = pd.get_exercise(ex_name.split(" (")[0].split(" or ")[0].split(" / ")[0])
        last = db.last_performance(conn, member["id"], ex_name)
        if last:
            prev = "; ".join(
                f"set {s['set_number']}: {s['reps']} reps"
                + (f" @ {s['load_kg']} kg" if s["load_kg"] else "")
                for s in last["sets"]
            )
            st.caption(f"Last time ({last['date']}): {prev}")
        if ex:
            with st.expander("How to do it — form & cues"):
                st.caption(f"**How:** {ex['execution']}")
                st.caption(f"**Easier:** {ex['regression']} | **Harder:** {ex['progression']}")
                st.caption(f"**Safety:** {ex['safety']}")
        n_sets = st.number_input(f"Sets for {ex_name}", 1, 6, 3, key=f"n_{ex_name}")
        cols = st.columns(2)
        reps = cols[0].number_input("Reps per set", 1, 50, 10, key=f"r_{ex_name}")
        load = cols[1].number_input("Load (kg, 0 = bodyweight)", 0.0, 300.0, 0.0, step=2.5, key=f"l_{ex_name}")
        rir = st.slider("Reps in reserve (RIR)", 0, 5, 2, key=f"rir_{ex_name}")
        if st.button(f"Log {ex_name}", key=f"log_{ex_name}", use_container_width=True):
            for s in range(1, int(n_sets) + 1):
                db.log_set(conn, member["id"], date.today().isoformat(),
                           f"{session['day']} — {session['title']}",
                           ex_name, s, reps=int(reps), load_kg=float(load),
                           rir=int(rir))
            st.success(f"Logged {int(n_sets)} sets of {ex_name}.")


def render_today():
    profile = st.session_state.profile
    conn = get_conn()
    member = current_member()
    kind, session = today_session(profile)
    today_label = date.today().strftime("%A, %b %d")

    if kind == "Re-entry":
        day_no = program_day_number(profile)
        with st.container(border=True):
            st.markdown(
                theme.hero_html(
                    f"Today's workout · Re-entry week · {today_label}",
                    f"Day {day_no} — {session['title']}",
                    focus=session["focus"],
                    chips=[(f"{len(session['items'])} movements", False),
                           ("Re-entry pace — learn the movements", True)],
                ),
                unsafe_allow_html=True,
            )
            start_button(conn, member["id"])
        render_member_week_strip(conn, member)
        render_readiness()
        with st.container(border=True):
            st.subheader("Session checklist")
            for item in session["items"]:
                st.write(f"- {item}")
            st.caption(session["note"])
            st.caption("Log any weights you used in the session below, or just tick it done.")
            if st.button("Mark re-entry day done", use_container_width=True, key="re_done"):
                db.log_set(conn, member["id"], date.today().isoformat(),
                           f"Re-entry Day {day_no}", "Re-entry session", 1,
                           notes=session["title"])
                st.success("Logged. See you tomorrow.")
    else:
        exercises = session["exercises"]
        with st.container(border=True):
            st.markdown(
                theme.hero_html(
                    f"Today's workout · {today_label}",
                    session["title"],
                    focus=session["focus"],
                    chips=[(f"⏱ {session['duration_min']} min", False),
                           (f"🏋️ {len(exercises)} exercises", False)],
                ),
                unsafe_allow_html=True,
            )
            if exercises:
                start_button(conn, member["id"])
            else:
                st.info("😴 Rest day — recover, eat, sleep. The work grows between sessions.")
        render_member_week_strip(conn, member)
        render_readiness()
        if session.get("note"):
            st.info(session["note"])
        for idx, (ex_name, sets_reps, note) in enumerate(exercises, 1):
            render_exercise_card(idx, ex_name, sets_reps, note, session, conn, member)

    # Week progress
    monday = date.today() - timedelta(days=date.today().weekday())
    sunday = monday + timedelta(days=6)
    done = db.sessions_this_week(conn, member["id"], monday.isoformat(), sunday.isoformat())
    day_no = program_day_number(profile)
    block, phase, week = pd.week_for_day_number(day_no)
    cols = st.columns(2)
    with cols[0]:
        st.metric("Training days logged this week", f"{done} / 6")
    with cols[1]:
        st.metric("Program week", f"Week {week}")
    st.write(f"**{block['name']}** ({block['days']}) · **Week {week}** — {phase['name']} phase")


def render_program():
    st.header("Program")
    st.subheader("Seven-day re-entry week")
    st.write("Low-fatigue orientation. Learn every movement before the real work starts.")
    for d in pd.REENTRY_WEEK:
        with st.expander(f"Day {d['day']}: {d['title']}"):
            st.caption(d["focus"])
            for item in d["items"]:
                st.write(f"- {item}")
            st.caption(d["note"])
    st.subheader("Weekly split")
    for split in pd.WEEKLY_SPLIT:
        with st.expander(f"{split['day']}: {split['title']}"):
            st.caption(split["focus"])
            for ex_name, sets_reps, note in split["exercises"]:
                st.write(f"- **{ex_name}** — {sets_reps} ({note})")
            if split.get("note"):
                st.info(split["note"])
    st.subheader("120-day Warrior Foundation")
    for block in pd.BLOCKS_120:
        with st.expander(f"Block {block['block']} — {block['days']}: {block['name']}"):
            st.write(block["focus"])
    st.subheader("24-week progression")
    for phase in pd.PHASES_24:
        st.write(f"**Weeks {phase['weeks']} — {phase['name']}:** {phase['focus']}")
    st.subheader("Progression rules")
    for rule in pd.PROGRESSION_RULES:
        st.write(f"- {rule}")
    st.subheader("Deloads")
    for rule in pd.DELOAD_RULES:
        st.write(f"- {rule}")


def render_library():
    st.header("Movement Library")
    query = st.text_input("Search exercises", "")
    for ex in pd.EXERCISE_LIBRARY:
        if query and query.lower() not in ex["name"].lower() and query.lower() not in ex["target"].lower():
            continue
        with st.expander(f"{ex['name']} — {ex['target']}"):
            st.write(f"**Setup:** {ex['setup']}")
            st.write(f"**How:** {ex['execution']}")
            st.write(f"**Easier:** {ex['regression']}")
            st.write(f"**Harder:** {ex['progression']}")
            st.write(f"**Safety:** {ex['safety']}")


def render_progress():
    st.header("Progress")
    conn = get_conn()
    member = current_member()
    history = db.progress_history(conn, member["id"])
    if history:
        latest = max(history, key=lambda h: h["date"])
        latest_waist = next((h for h in sorted(history, key=lambda h: h["date"], reverse=True)
                             if h.get("waist_cm")), None)
        latest_pushups = next((h for h in sorted(history, key=lambda h: h["date"], reverse=True)
                               if h.get("pushups")), None)
        cards = []
        if latest.get("weight_kg"):
            cards.append(("Weight", f"{latest['weight_kg']} kg"))
        if latest_waist:
            cards.append(("Waist", f"{latest_waist['waist_cm']} cm"))
        if latest_pushups:
            cards.append(("Clean push-ups", f"{latest_pushups['pushups']}"))
        cards.append(("Check-ins", f"{len(history)}"))
        cols = st.columns(len(cards))
        for col, (label, value) in zip(cols, cards):
            with col:
                st.metric(label, value)
    with st.container(border=True):
        st.subheader("Log a check-in (every 4 weeks, or when you weigh in)")
        with st.form("progress"):
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=200.0, value=0.0, step=0.5)
            waist = st.number_input("Waist (cm) — optional", min_value=0.0, max_value=200.0, value=0.0, step=0.5)
            balance_l = st.number_input("Single-leg balance, left (sec)", min_value=0.0, max_value=300.0, value=0.0, step=1.0)
            balance_r = st.number_input("Single-leg balance, right (sec)", min_value=0.0, max_value=300.0, value=0.0, step=1.0)
            pushups = st.number_input("Clean push-ups (your variation)", min_value=0, max_value=200, value=0, step=1)
            walk = st.number_input("Six-minute walk distance (m) — optional", min_value=0.0, max_value=2000.0, value=0.0, step=10.0)
            confidence = st.slider("Confidence (1-5)", 1, 5, 3)
            notes = st.text_area("Notes")
            if st.form_submit_button("Save check-in", use_container_width=True):
                db.log_progress(
                    conn, member["id"], date.today().isoformat(),
                    weight_kg=(weight or None), waist_cm=(waist or None),
                    balance_left_sec=(balance_l or None), balance_right_sec=(balance_r or None),
                    pushups=(pushups or None), walk_m=(walk or None),
                    confidence_rating=confidence, notes=notes.strip() or None,
                )
                st.success("Check-in saved.")
    st.subheader("Baseline tests (repeat every 4 weeks)")
    for test in pd.BASELINE_TESTS:
        st.write(f"- {test}")
    st.subheader("History")
    if not history:
        st.caption("No check-ins yet. Your first one appears here.")
    else:
        weights = {h["date"]: h["weight_kg"] for h in history if h.get("weight_kg")}
        if len(weights) >= 2:
            st.line_chart(weights)
        with st.container(border=True):
            for h in history[:10]:
                bits = [f"{h['date']}"]
                if h.get("weight_kg"):
                    bits.append(f"{h['weight_kg']} kg")
                if h.get("waist_cm"):
                    bits.append(f"waist {h['waist_cm']} cm")
                if h.get("pushups"):
                    bits.append(f"{h['pushups']} push-ups")
                if h.get("balance_left_sec"):
                    bits.append(f"balance L {h['balance_left_sec']}s / R {h['balance_right_sec']}s")
                st.write(" · ".join(bits))


def render_nutrition():
    st.header("Nutrition & Recovery")
    profile = st.session_state.profile or {}
    weight = profile.get("weight_kg")
    target = pd.protein_target_grams(weight) if weight else None
    if target:
        st.metric("Protein target", f"{target[0]}-{target[1]} g / day")
    else:
        st.caption("Add your weight in Settings to see your protein target.")
    conn = get_conn()
    member = current_member()
    with st.container(border=True):
        st.subheader("Log today")
        with st.form("nutrition"):
            meals = st.text_area("What you ate today (one meal per line)")
            protein = st.number_input("Protein today (g)", min_value=0.0, max_value=500.0, value=0.0, step=5.0)
            water = st.number_input("Water (ml)", min_value=0.0, max_value=6000.0, value=0.0, step=250.0)
            sleep = st.number_input("Sleep last night (hours)", min_value=0.0, max_value=14.0, value=7.0, step=0.5)
            if st.form_submit_button("Save day", use_container_width=True):
                meal_list = [m.strip() for m in meals.splitlines() if m.strip()]
                db.log_nutrition(conn, member["id"], date.today().isoformat(),
                                 meals=meal_list, protein_g=protein, water_ml=water,
                                 sleep_hours=sleep)
                st.success("Day saved.")
    st.subheader("Guidance")
    for line in pd.NUTRITION_GUIDANCE:
        st.write(f"- {line}")
    st.subheader("Recent days")
    for day in db.nutrition_history(conn, member["id"], limit=7):
        bits = [day["date"]]
        if day.get("protein_g"):
            bits.append(f"protein {day['protein_g']} g")
        if day.get("water_ml"):
            bits.append(f"water {day['water_ml']} ml")
        if day.get("sleep_hours"):
            bits.append(f"sleep {day['sleep_hours']} h")
        st.write(" · ".join(bits))


def render_coach():
    st.header("AI Coach")
    with st.container(border=True):
        st.caption(coach.COACH_IDENTITY)
    profile = st.session_state.profile or {}
    conn = get_conn()
    member = current_member()
    readiness = db.latest_readiness(conn, member["id"])
    question = st.text_input("Ask your coach", placeholder="e.g. What's my protein target? / substitute for hip thrust")
    if st.button("Ask", use_container_width=True):
        reply = coach.answer(question, member_weight_kg=profile.get("weight_kg"), readiness=readiness)
        st.markdown(reply)
        st.session_state.setdefault("coach_history", []).append((question, reply))
    for q, a in reversed(st.session_state.get("coach_history", [])):
        with st.container(border=True):
            st.markdown(f"**You:** {q}")
            st.markdown(a)


def render_settings():
    st.header("Settings")
    profile = st.session_state.profile or {}
    conn = get_conn()
    member = current_member()
    with st.container(border=True):
        st.subheader("Your profile")
        with st.form("settings"):
            height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0,
                                     value=float(profile.get("height_cm") or 165.0), step=1.0)
            weight = st.number_input("Weight (kg)", min_value=35.0, max_value=200.0,
                                     value=float(profile.get("weight_kg") or 70.0), step=0.5)
            equipment = st.multiselect("Gym equipment you have", EQUIPMENT_OPTIONS,
                                       default=profile.get("equipment") or [])
            rest_day = st.selectbox("Rest day", WEEKDAYS,
                                    index=WEEKDAYS.index(profile.get("rest_day") or "Sunday"))
            if st.form_submit_button("Save settings", use_container_width=True):
                db.upsert_profile(conn, member["id"], height_cm=height, weight_kg=weight,
                                  equipment=equipment, rest_day=rest_day)
                refresh_profile()
                st.success("Settings saved.")
    with st.container(border=True):
        st.subheader("Your data")
        export = {
            "member": {"email": member["email"], "name": member["name"]},
            "profile": {k: v for k, v in (profile or {}).items() if k != "member_id"},
            "set_logs": db.all_set_logs(conn, member["id"]),
            "progress": db.progress_history(conn, member["id"], limit=100),
            "nutrition": db.nutrition_history(conn, member["id"], limit=100),
        }
        st.download_button("Download my data (JSON)", json.dumps(export, indent=2, default=str),
                           file_name="warrior-women-my-data.json", mime="application/json",
                           use_container_width=True)
        st.caption("Your measurements and data are private to your account.")
        if st.button("Log out", use_container_width=True):
            logout()


def render_member_app():
    member = current_member()
    if "profile" not in st.session_state:
        refresh_profile()
    if not st.session_state.profile or not st.session_state.profile.get("onboarding_done"):
        render_topbar(member)
        render_onboarding()
        return
    render_topbar(member, badge="Member")
    page = render_nav(
        ["Today", "Program", "Movement Library", "Progress", "Nutrition & Recovery", "AI Coach", "Settings"],
        key="nav_member",
    )
    if page == "Today":
        render_today()
    elif page == "Program":
        render_program()
    elif page == "Movement Library":
        render_library()
    elif page == "Progress":
        render_progress()
    elif page == "Nutrition & Recovery":
        render_nutrition()
    elif page == "AI Coach":
        render_coach()
    elif page == "Settings":
        render_settings()
    st.markdown(
        '<div class="kw-footer">Membership: $10/month · Cancel anytime in Stripe.</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main routing
# ---------------------------------------------------------------------------
def main():
    member = current_member()
    if not member:
        render_landing()
        render_auth()
        return
    result = check_subscription()
    access = challenge.resolve_access(member, result)
    if access == challenge.FULL:
        # Conversion: a challenge account whose subscription is active is
        # a full member now. Flip the flag once; profile, start date and
        # logs are keyed by member id, so everything carries over.
        if challenge.is_challenge_member(member):
            db.set_account_type(get_conn(), member["id"], challenge.ACCOUNT_MEMBER)
        render_member_app()
        return
    if access == challenge.CHALLENGE:
        render_challenge_app()
        return
    render_topbar(member)
    render_paywall(result)
    if st.button("Log out", use_container_width=True):
        logout()


main()
