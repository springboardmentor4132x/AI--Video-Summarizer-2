from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

# bcrypt has a 72-byte password limit
_MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    payload = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(payload, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    payload = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.checkpw(payload, hashed.encode("utf-8"))


def create_access_token(*, subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
