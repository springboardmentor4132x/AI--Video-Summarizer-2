from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def require_roles(*roles: UserRole):
    def checker(current_user: User) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission for this action",
            )
        return current_user

    return checker


def ensure_role(user: User, *roles: UserRole) -> None:
    if user.role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this action",
        )
