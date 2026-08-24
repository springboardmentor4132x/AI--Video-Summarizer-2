"""
auth.py
--------
Core security logic for the authentication module:

1. Password hashing/verification (bcrypt via passlib)
2. JWT creation/verification (python-jose)
3. FastAPI dependencies:
      - get_current_user  -> resolves the logged-in User from a Bearer token
      - require_role(...) -> restricts a route to specific roles (RBAC)
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# Load variables from backend/.env regardless of current working directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set. Check your .env file.")

# ---- Password hashing ----

def hash_password(plain_password: str) -> str:
    """Hash a plain-text password before storing it in password_hash."""
    pw_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against the stored bcrypt hash."""
    pw_bytes = plain_password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(pw_bytes, hash_bytes)



# ---- JWT creation/verification ----

def create_access_token(user: User) -> str:
    """
    Build a signed JWT containing the user's id, email, and role.
    The role is embedded so protected routes can check permissions
    without hitting the database every time, if desired.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),       # "subject" — standard JWT claim for the user identifier
        "email": user.email,
        "role": user.role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT. Raises HTTPException(401) if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---- Dependencies ----

# Tells FastAPI/Swagger where clients should send credentials to get a token.
# tokenUrl is just used for the interactive docs "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency for protected routes.
    Extracts the Bearer token, decodes it, and loads the matching User
    from the database. Use like:

        def some_route(current_user: User = Depends(get_current_user)):
            ...
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_role(*allowed_roles: str):
    """
    Dependency FACTORY for role-based access control.
    Usage:

        @router.get("/admin-only")
        def admin_route(current_user: User = Depends(require_role("administrator"))):
            ...

    Any authenticated user whose role is NOT in allowed_roles gets a 403.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker