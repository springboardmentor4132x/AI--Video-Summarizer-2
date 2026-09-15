"""
dependencies.py
----------------
- get_current_user: JWT token se logged-in user nikalta hai (protected routes ke liye)
- require_role: Role-Based Access Control (RBAC) — sirf specific roles ko
  kisi endpoint tak access dene ke liye.
"""

from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import decode_access_token
from app.models import User, UserRole

# Swagger UI ("/docs") mein "Authorize" button ke liye tokenUrl batana zaroori hai
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Har protected API isse call karti hai. Yeh:
    1. Token decode karta hai
    2. Token se user_id nikalta hai
    3. Database se woh user fetch karta hai
    Agar kuch bhi galat ho -> 401 Unauthorized error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def require_role(allowed_roles: List[UserRole]):
    """
    Role-Based Access Control ke liye dependency factory.

    Example usage in a route:
        @router.get("/admin-only")
        def admin_route(user: User = Depends(require_role([UserRole.ADMIN]))):
            ...
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. This action requires one of these roles: "
                       f"{[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker
