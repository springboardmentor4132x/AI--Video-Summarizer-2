"""
auth.py
-------
Password hashing aur JWT token banane/verify karne ke helper functions.

Document ka requirement:
  - Passwords plain text mein store NAHI hone chahiye -> bcrypt hashing
  - JWT login ka proof hai -> protected APIs isse verify karengi
"""

import datetime
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Password ko bcrypt se hash karta hai (kabhi plain text store nahi karna)."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Login ke time password check karne ke liye."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """
    JWT token banata hai. 'data' mein hum user id aur role daalenge
    taki protected routes easily user ko identify kar sakein.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Token verify karta hai. Invalid/expired hone par None return karta hai."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
