"""Content generation endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_language
from app.database import get_db
from app.models import User
from app.services.content import ContentService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/generate")
def generate_content(
    word_id: int = Query(...),
    level: str = Query("intermediate"),
    scene_type: str = Query("focus"),
    lang: str = Depends(get_language),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ContentService(db).generate(word_id, level, scene_type, lang)
