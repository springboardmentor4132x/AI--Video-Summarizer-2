"""
routers/auth.py
----------------
Registration aur Login APIs.

Flow (jaise document mein diagram diya hai):

Registration:
  Frontend -> POST /api/auth/register -> Validate -> Hash password -> Store user -> DB

Login:
  Frontend -> POST /api/auth/login -> Check user -> Verify password -> Generate JWT -> Return token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserOut
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    # 1. Password aur confirm password match hone chahiye
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Password and Confirm Password do not match.")

    # 2. Email pehle se registered to nahi hai
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    # 3. Password hash karo (plain text kabhi store nahi karte)
    hashed_pw = hash_password(payload.password)

    # 4. User create karo aur DB mein save karo
    new_user = User(
        name=payload.name,
        email=payload.email,
        password=hashed_pw,
        role=payload.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # 1. User dhoondo email se
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # 2. Password verify karo
    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # 3. JWT generate karo — isme user_id aur role daalte hain taki
    #    baad mein role-based access control isse check kar sake
    access_token = create_access_token(data={"user_id": user.id, "role": user.role.value})

    return Token(access_token=access_token, user=user)


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Logged-in user apni profile dekh sakta hai (dashboard ke liye use hoga)."""
    return current_user
