"""
routers/dashboard.py
---------------------
Role-based dashboard data. Har role ko alag response milta hai —
document ke section 8 (User Roles) aur 12 (Role-Based Access Control /
Dashboard) ka implementation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import User, Video, UserRole

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sabhi logged-in users iss route ko access kar sakte hain,
    lekin response unke role ke hisaab se different hota hai.
    """
    video_count = db.query(Video).filter(Video.user_id == current_user.id).count()

    base_info = {
        "name": current_user.name,
        "role": current_user.role.value,
        "total_uploads": video_count,
    }

    if current_user.role == UserRole.ADMIN:
        total_users = db.query(User).count()
        total_videos = db.query(Video).count()
        base_info["admin_stats"] = {
            "total_users": total_users,
            "total_videos": total_videos,
        }
    elif current_user.role == UserRole.EDUCATOR:
        base_info["message"] = "Welcome Educator! Yahan aap apne learners ke uploads dekh payenge (future module)."
    elif current_user.role == UserRole.CONTENT_CREATOR:
        base_info["message"] = "Welcome Content Creator! Apni videos upload karke processing shuru karein."
    else:  # LEARNER
        base_info["message"] = "Welcome Learner! Educators ke shared content yahan dikhega (future module)."

    return base_info


@router.get("/admin-only")
def admin_only_route(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    """RBAC ka example — sirf Administrator role isko access kar sakta hai."""
    return {"message": f"Hello Admin {current_user.name}, you have full access."}
