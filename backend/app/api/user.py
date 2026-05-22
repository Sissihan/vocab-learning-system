"""User profile endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_language
from app.database import get_db
from app.models import User
from app.schemas.auth import ProfileUpdate, UserProfile
from app.services.profile import ProfileService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile", response_model=UserProfile)
def get_profile(
    lang: str = Depends(get_language),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProfileService(db).get_profile(current_user, lang)


@router.put("/profile", response_model=UserProfile)
def update_profile(
    payload: ProfileUpdate,
    lang: str = Depends(get_language),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_none=True)
    save_lang = data.pop("language", None) or lang
    return ProfileService(db).update_profile(current_user, data, save_lang)
