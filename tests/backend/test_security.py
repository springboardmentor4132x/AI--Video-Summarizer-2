from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_roundtrip() -> None:
    hashed = hash_password("Secret123!")
    assert hashed != "Secret123!"
    assert verify_password("Secret123!", hashed)
    assert not verify_password("wrong-pass", hashed)


def test_access_token_roundtrip() -> None:
    token = create_access_token(subject="user-1", role="learner")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-1"
    assert payload["role"] == "learner"
