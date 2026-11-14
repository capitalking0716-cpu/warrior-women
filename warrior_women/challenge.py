"""Warrior Women — FREE 7-Day Challenge access rules.

The challenge is the front door of the funnel: the program's first week
(the seven-day re-entry week) is free. A challenge account is a normal
account flagged ``account_type == 'challenge'`` in the members table.

Access resolution (see :func:`resolve_access`):

  - An ACTIVE Stripe subscription always wins — the account is a full
    member, whatever its flag says. A converted challenge member keeps
    her start date and logs; only the flag's job is done.
  - A challenge account without a subscription gets the challenge view:
    program days 1-7 only, anchored to her own start date exactly like
    a member's program days.
  - Any other account without a subscription stays on the paywall.

Day 7 is the conversion moment: the membership offer shows on day 7
and keeps showing after day 7 (when the challenge is finished and the
rest of the program stays locked behind it).

This module is pure logic — no Streamlit, no database, no network —
so it is easy to test, like paywall.py.
"""

from datetime import date

CHALLENGE_DAYS = 7

ACCOUNT_CHALLENGE = "challenge"
ACCOUNT_MEMBER = "member"

# Access kinds returned by resolve_access.
FULL = "full"          # full member app (active subscription)
CHALLENGE = "challenge"  # challenge view (days 1-7, no subscription)
LOCKED = "locked"      # paywall screen


def account_type_of(member):
    """The account_type flag of a member row/dict; 'member' when absent."""
    if member is None:
        return ACCOUNT_MEMBER
    if isinstance(member, dict):
        return member.get("account_type") or ACCOUNT_MEMBER
    try:  # sqlite3.Row and friends
        return member["account_type"] or ACCOUNT_MEMBER
    except (KeyError, IndexError, TypeError):
        return ACCOUNT_MEMBER


def is_challenge_member(member):
    return account_type_of(member) == ACCOUNT_CHALLENGE


def resolve_access(member, paywall_result):
    """Resolve what a signed-in account may see.

    ``paywall_result`` is a paywall.PaywallResult (only its ``unlocked``
    attribute is read). An active subscription resolves to FULL even
    for challenge-flagged accounts — that is the conversion path.
    """
    if paywall_result is not None and getattr(paywall_result, "unlocked", False):
        return FULL
    if is_challenge_member(member):
        return CHALLENGE
    return LOCKED


def program_day(start_date, today=None):
    """1-based program day for an ISO start date, anchored like members'.

    Mirrors the member app: no/invalid start date means day 1, and the
    count never drops below 1.
    """
    if not start_date:
        return 1
    try:
        start = date.fromisoformat(start_date)
    except (ValueError, TypeError):
        return 1
    today = today or date.today()
    return max(1, (today - start).days + 1)


def challenge_day_number(profile, today=None):
    """The challenge day (1-based) for a profile dict, or 1 pre-onboarding."""
    start = profile.get("start_date") if profile else None
    return program_day(start, today=today)


def within_challenge(day_no):
    """True while the day is one of the free challenge days (1-7)."""
    return 1 <= day_no <= CHALLENGE_DAYS


def is_final_day(day_no):
    return day_no == CHALLENGE_DAYS


def challenge_finished(day_no):
    """True once the free week is over (day 8+)."""
    return day_no > CHALLENGE_DAYS


def show_membership_offer(day_no):
    """The membership offer shows on day 7 and ever after."""
    return day_no >= CHALLENGE_DAYS
