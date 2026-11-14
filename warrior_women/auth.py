"""Warrior Women — member accounts.

Email + password sign-up and login. Passwords are hashed with PBKDF2
(stdlib hashlib, per-user random salt, 200,000 iterations). Plaintext
passwords are never stored, never logged, never written to disk.
"""

import hashlib
import hmac
import os
import re

PBKDF2_ITERATIONS = 200_000

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_email(email):
    """Basic shape check — not a deliverability check."""
    return bool(email) and bool(_EMAIL_RE.match(email.strip()))


def hash_password(password):
    """Return (salt_hex, hash_hex) for a plaintext password."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return salt.hex(), digest.hex()


def verify_password(password, salt_hex, hash_hex):
    """Constant-time check of a plaintext password against a stored hash."""
    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(digest, expected)


def validate_signup(email, password, name):
    """Return a list of problems with a sign-up attempt (empty = OK)."""
    problems = []
    if not valid_email(email or ""):
        problems.append("Enter a valid email address.")
    if not (name or "").strip():
        problems.append("Enter your name.")
    if len(password or "") < 8:
        problems.append("Password must be at least 8 characters.")
    return problems
