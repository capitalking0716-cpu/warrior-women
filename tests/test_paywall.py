"""Tests for Warrior Women — the REAL paywall.

The paywall must only unlock on an ACTIVE Stripe subscription for the
Warrior Women price. Everything else stays locked — including the case
where no Stripe key is configured at all.
"""

from warrior_women import paywall, program_data as pd


class FakeStripe:
    """Minimal stand-in for the stripe SDK, driven by a dict of customers."""

    def __init__(self, customers):
        # customers: email -> list of subscription dicts
        self._customers = customers
        self.api_key = None

    class _Customer:
        def __init__(self, outer):
            self._outer = outer

        def list(self, email=None, limit=10):
            subs = self._outer._customers.get(email, [])
            if subs is None:
                return {"data": []}
            return {"data": [{"id": f"cus_{email}", "email": email}]}

    class _Subscription:
        def __init__(self, outer):
            self._outer = outer

        def list(self, customer=None, limit=10):
            email = customer.replace("cus_", "")
            subs = self._outer._customers.get(email, []) or []
            return {"data": subs}

    @property
    def Customer(self):
        return self._Customer(self)

    @property
    def Subscription(self):
        return self._Subscription(self)


def _active_sub():
    return {
        "id": "sub_active1",
        "status": "active",
        "items": {"data": [{"price": {"id": pd.STRIPE_PRICE_ID}}]},
    }


def _canceled_sub():
    return {
        "id": "sub_canceled1",
        "status": "canceled",
        "items": {"data": [{"price": {"id": pd.STRIPE_PRICE_ID}}]},
    }


def _wrong_price_sub():
    return {
        "id": "sub_other1",
        "status": "active",
        "items": {"data": [{"price": {"id": "price_someone_elses_product"}}]},
    }


def test_no_key_never_unlocks(monkeypatch):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    result = paywall.has_active_subscription("ada@example.com", secrets={})
    assert result.unlocked is False
    assert result.reason == "not_configured"


def test_active_subscription_unlocks():
    client = FakeStripe({"ada@example.com": [_active_sub()]})
    result = paywall.has_active_subscription("ada@example.com", key="sk_test_fake", stripe_client=client)
    assert result.unlocked is True
    assert result.reason == "active"


def test_no_customer_stays_locked():
    client = FakeStripe({})
    result = paywall.has_active_subscription("nobody@example.com", key="sk_test_fake", stripe_client=client)
    assert result.unlocked is False
    assert result.reason == "no_subscription"


def test_canceled_subscription_stays_locked():
    client = FakeStripe({"ada@example.com": [_canceled_sub()]})
    result = paywall.has_active_subscription("ada@example.com", key="sk_test_fake", stripe_client=client)
    assert result.unlocked is False


def test_active_subscription_for_another_product_stays_locked():
    client = FakeStripe({"ada@example.com": [_wrong_price_sub()]})
    result = paywall.has_active_subscription("ada@example.com", key="sk_test_fake", stripe_client=client)
    assert result.unlocked is False


def test_stripe_error_stays_locked():
    class BrokenStripe:
        api_key = None

        class Customer:
            @staticmethod
            def list(email=None, limit=10):
                raise RuntimeError("network down")

    result = paywall.has_active_subscription("ada@example.com", key="sk_test_fake", stripe_client=BrokenStripe())
    assert result.unlocked is False
    assert result.reason == "error"


def test_key_from_env(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_from_env")
    assert paywall.get_stripe_key(secrets={}) == "sk_test_from_env"
    # Explicit secrets win over env
    assert paywall.get_stripe_key(secrets={"STRIPE_SECRET_KEY": "sk_test_secret"}) == "sk_test_secret"
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    assert paywall.get_stripe_key(secrets={}) is None
