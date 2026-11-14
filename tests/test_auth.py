"""Tests for Warrior Women — auth (hashing, sign-up, login)."""

from warrior_women import auth, db


def test_hash_roundtrip_and_wrong_password():
    salt, digest = auth.hash_password("correct horse battery staple")
    assert auth.verify_password("correct horse battery staple", salt, digest) is True
    assert auth.verify_password("wrong password", salt, digest) is False
    assert auth.verify_password("", salt, digest) is False
    # Same password, different salt -> different hash
    salt2, digest2 = auth.hash_password("correct horse battery staple")
    assert salt != salt2 and digest != digest2
    # Corrupt stored values never verify
    assert auth.verify_password("correct horse battery staple", "not-hex", digest) is False
    assert auth.verify_password("correct horse battery staple", salt, "not-hex") is False


def test_signup_validation():
    assert auth.validate_signup("bad-email", "longenough1", "Ada") != []
    assert auth.validate_signup("ada@example.com", "short", "Ada") != []
    assert auth.validate_signup("ada@example.com", "longenough1", "") != []
    assert auth.validate_signup("ada@example.com", "longenough1", "Ada") == []
    assert auth.valid_email("ada@example.com") is True
    assert auth.valid_email("not an email") is False


def test_create_and_authenticate_member(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    salt, digest = auth.hash_password("supersecret1")
    member_id = db.create_member(conn, "ada@example.com", salt, digest, "Ada")
    assert member_id is not None
    # Duplicate email is rejected
    assert db.create_member(conn, "ada@example.com", salt, digest, "Ada") is None
    # Case-insensitive email lookup
    member = db.get_member_by_email(conn, "ADA@EXAMPLE.COM")
    assert member is not None
    assert member["name"] == "Ada"
    assert auth.verify_password("supersecret1", member["password_salt"], member["password_hash"]) is True
    assert auth.verify_password("nope-nope-nope", member["password_salt"], member["password_hash"]) is False
    # Password hash is stored, plaintext is not
    assert "supersecret1" not in (member["password_salt"] + member["password_hash"])
