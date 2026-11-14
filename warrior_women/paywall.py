"""Warrior Women — REAL paywall.

The full program is locked until the member has an ACTIVE $10/month
subscription in Stripe, matched by the member's email.

How it works:
  1. STRIPE_SECRET_KEY is read from Streamlit Secrets (st.secrets) or the
     environment. It is never hardcoded and never stored in the repo.
  2. We look up Stripe customers with this email, then list their
     subscriptions with status='active' for the Warrior Women price.
  3. Only an active subscription unlocks the program.

If no Stripe key is configured, the app must NOT grant access — it reports
"not_configured" and the UI shows the checkout link and a clear message
that payment verification is not set up yet.

Nothing here auto-approves anyone. There is no shared password, no demo
bypass, no "unlock for now" path.
"""

import os

from . import program_data

# Statuses that count as "paying". A trialing subscription does NOT unlock
# (the member has not paid yet); past_due / unpaid / canceled do not unlock.
ACTIVE_STATUSES = {"active"}


class PaywallResult:
    """Outcome of a subscription check."""

    def __init__(self, unlocked, reason, detail=""):
        self.unlocked = unlocked
        self.reason = reason  # 'active' | 'no_subscription' | 'not_configured' | 'error'
        self.detail = detail

    def __bool__(self):
        return self.unlocked


def get_stripe_key(secrets=None):
    """Stripe secret key from Streamlit secrets, then the environment.

    ``secrets`` is an optional mapping (st.secrets in the app, a plain dict
    in tests). Returns None when no key is configured.
    """
    if secrets is not None:
        try:
            key = secrets.get("STRIPE_SECRET_KEY")
        except Exception:
            key = None
        if key:
            return key
    return os.environ.get("STRIPE_SECRET_KEY") or None


def _stripe_module():
    """Import the stripe SDK lazily so tests can run without it installed."""
    import stripe
    return stripe


def has_active_subscription(email, secrets=None, stripe_client=None, key=None):
    """Check Stripe for an active Warrior Women subscription for this email.

    Returns a PaywallResult. ``stripe_client`` is injectable (a fake in
    tests); when omitted, the real stripe SDK is used with the configured key.
    """
    api_key = key or get_stripe_key(secrets)
    if not api_key:
        return PaywallResult(False, "not_configured",
                             "No Stripe key configured — payment verification is not set up yet.")

    try:
        client = stripe_client or _stripe_module()
        client.api_key = api_key

        customers = client.Customer.list(email=email.strip().lower(), limit=10)
        customer_list = customers.get("data") or getattr(customers, "data", []) or []
        if not customer_list:
            return PaywallResult(False, "no_subscription",
                                 "No Stripe customer found for this email.")

        for customer in customer_list:
            customer_id = customer.get("id") if isinstance(customer, dict) else getattr(customer, "id", None)
            subs = client.Subscription.list(customer=customer_id, limit=10)
            sub_list = subs.get("data") if isinstance(subs, dict) else getattr(subs, "data", []) or []
            for sub in sub_list:
                status = sub.get("status") if isinstance(sub, dict) else getattr(sub, "status", None)
                if status not in ACTIVE_STATUSES:
                    continue
                items = sub.get("items", {}) if isinstance(sub, dict) else getattr(sub, "items", {})
                item_data = items.get("data", []) if isinstance(items, dict) else getattr(items, "data", []) or []
                for item in item_data:
                    price = item.get("price", {}) if isinstance(item, dict) else getattr(item, "price", {})
                    price_id = price.get("id") if isinstance(price, dict) else getattr(price, "id", None)
                    if price_id == program_data.STRIPE_PRICE_ID:
                        return PaywallResult(True, "active",
                                             f"Active subscription {sub.get('id') if isinstance(sub, dict) else getattr(sub, 'id', '')}.")
        return PaywallResult(False, "no_subscription",
                             "No active Warrior Women subscription found for this email.")
    except Exception as exc:  # network error, bad key, Stripe outage — deny, never grant
        return PaywallResult(False, "error", f"Stripe check failed: {exc}")
