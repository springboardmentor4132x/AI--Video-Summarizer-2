from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.models import User, UserRole


def seed_admin(db: Session) -> User | None:
    existing = db.scalar(select(User).where(User.email == settings.admin_email))
    if existing:
        return existing
    admin = User(
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password),
        full_name="ClipMind Admin",
        role=UserRole.ADMINISTRATOR,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
