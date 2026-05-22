"""Context awareness endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_language
from app.database import get_db
from app.models import User
from app.services.context import ContextService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/context", tags=["context"])


class ContextInferRequest(BaseModel):
    location_type: str = "unknown"
    device_state: str = "desktop"
    manual_scene: str | None = None
    duration_available: int | None = None


@router.get("/scenes")
def list_scenes(lang: str = Depends(get_language)):
    svc = ContextService()
    return {
        scene: svc.get_scene_config(scene, lang)
        for scene in ["commute", "focus", "fragment", "review"]
    }


@router.post("/infer")
def infer_context(
    payload: ContextInferRequest,
    lang: str = Depends(get_language),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = ContextService()
    scene = svc.log_context(
        db,
        current_user.id,
        payload.location_type,
        payload.device_state,
        payload.manual_scene,
        {"duration": payload.duration_available},
    )
    return {
        "inferred_scene": scene,
        "config": svc.get_scene_config(scene, lang),
        "lang": lang,
    }
