# Warrior Women — Membership App ($10/month)

A standalone, sellable membership product: a public app any woman can open,
sign up for, pay $10/month, log in to, and train with — her own saved data,
separate from every other member.

**This is the real thing, not a demo.** The full program is locked behind a
real Stripe check: only an active $10/month subscription for the Warrior
Women price unlocks it. If no Stripe key is configured, the app stays locked
and says so — it never auto-approves anyone.

## What it is

- **Public landing** — what Warrior Women is (strong, athletic hourglass:
  strong glutes and hips, strong toned waist, balanced shoulders and back),
  the six-day schedule, 120-day foundation, 24-week progression, $10/month,
  Stripe checkout link.
- **Member sign-up and login** — email + password. Passwords are hashed
  (PBKDF2, per-user salt, 200,000 iterations). Plaintext passwords are never
  stored, logged, or written to disk.
- **REAL paywall** — checks Stripe for an active subscription under the
  member's email (same email as checkout). Uses `STRIPE_SECRET_KEY` from
  Streamlit Secrets or the environment. No key = locked, with a clear
  message. A Stripe check that errors = locked, never unlocked.
- **The full program** — seven-day re-entry week first (nothing assumed),
  six training days + one rest day, 40-exercise movement library, per-set
  logging with prior-performance hints, readiness checks (Green/Yellow/Red),
  progress tracking and four-week reassessments, nutrition & recovery
  (protein target from bodyweight), and a rule-based AI coach that answers
  from the program data and the member's own logs.
- **Safety rules throughout** — no one-rep-max testing, no steroids or
  hormones, never train through pain, stop for sharp pain / dizziness /
  chest pain / unusual shortness of breath / numbness / loss of coordination
  and seek medical care, realistic 12-18 month timeline, no promised body
  or guaranteed date.

## Files

| File | What it is |
|---|---|
| `app.py` | The Streamlit app (landing, auth, paywall, member app) |
| `warrior_women/program_data.py` | The whole program: re-entry week, split, blocks, phases, 40-exercise library, rules |
| `warrior_women/auth.py` | Password hashing + sign-up validation |
| `warrior_women/db.py` | SQLite storage — members, profiles, readiness, set logs, progress, nutrition |
| `warrior_women/paywall.py` | Stripe subscription check |
| `warrior_women/coach.py` | Rule-based coach + guardrails |
| `requirements.txt` | streamlit, stripe, pytest |
| `tests/` | pytest suite |
| `DEPLOY.md` | Exact Streamlit Cloud deploy steps |
| `NEKO-CHECKLIST.md` | What Neko must do himself vs what is already done |

## Run it locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Without a Stripe key the app runs, but the member area stays locked with a
message that payment verification is not set up yet. To test the paywall
locally with a test key:

```bash
STRIPE_SECRET_KEY=sk_test_... .venv/bin/streamlit run app.py
```

## Tests

```bash
.venv/bin/python -m pytest tests/ -q
```

34 tests: program data correctness (7-day re-entry, 6+1 split, 40-exercise
library, progression/readiness rules), auth (hashing, duplicate email,
login), paywall (active unlocks; no key / no customer / canceled / wrong
product / Stripe error all stay locked), per-member data isolation and
logging, coach guardrails.

The Stripe verification itself cannot be tested end-to-end without a live
secret key and a real paid subscription — the tests use a fake Stripe client
to prove the gating logic. See DEPLOY.md for the live check Neko does after
deploying.

## Data and privacy

- Member data lives in `data/warrior_women.db` (SQLite). It is gitignored
  and never committed.
- Each member only ever sees her own data (every query is keyed by her
  member id).
- Members can download all their own data as JSON from Settings.
- The Stripe secret key is never in this repo. It lives only in Streamlit
  Secrets (or a local environment variable).
