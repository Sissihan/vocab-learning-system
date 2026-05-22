"""Recommendation endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_language
from app.database import get_db
from app.models import User
from app.services.context import ContextService
from app.services.recommendation import RecommendationEngine
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api", tags=["recommend"])


@router.get("/recommend")
def get_recommendations(
    scene_type: str = Query("fragment"),
    limit: int = Query(10, ge=1, le=30),
    location_type: str = Query("unknown"),
    device_state: str = Query("desktop"),
    auto_scene: bool = Query(False),
    lang: str = Depends(get_language),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ctx = ContextService()
    if auto_scene:
        scene_type = ctx.infer_scene(location_type, device_state)
        ctx.log_context(db, current_user.id, location_type, device_state, scene_type)

    valid_scenes = {"commute", "focus", "fragment", "review"}
    if scene_type not in valid_scenes:
        scene_type = "fragment"

    engine = RecommendationEngine(db)
    return engine.recommend(current_user, scene_type, {}, limit, lang)
