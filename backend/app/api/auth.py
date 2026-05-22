"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.auth import Token, UserLogin, UserProfile, UserRegister
from app.services.profile import ProfileService
from app.utils.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.utils.json_helpers import dumps

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        level=payload.level,
        learning_goal=payload.learning_goal,
        cognitive_style=payload.cognitive_style,
        profile_json=dumps({
            "vocab_level": 1,
            "preferred_scene": "fragment",
            "onboarding_complete": True,
            "language": payload.language or "zh-CN",
        }),
    )
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
def login_json(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
