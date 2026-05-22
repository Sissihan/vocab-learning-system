"""Learning record and knowledge tracking endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_language
from app.database import get_db
from app.i18n import t
from app.models import LearningRecord, User
from app.schemas.learning import LearningRecordCreate
from app.services.dkt import DKTService
from app.utils.auth import get_current_user
from app.utils.json_helpers import dumps

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.post("/record")
def record_learning(
    payload: LearningRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = LearningRecord(
        user_id=current_user.id,
        word_id=payload.word_id,
        scene_type=payload.scene_type,
        score=payload.score,
        response_time=payload.response_time,
        is_correct=payload.is_correct,
        activity_type=payload.activity_type,
        detail_json=dumps(payload.detail),
    )
    db.add(record)
    db.flush()

    if payload.word_id:
        DKTService().update_mastery(
            db,
            current_user.id,
            payload.word_id,
            payload.is_correct,
            payload.response_time,
        )

    db.commit()
    db.refresh(record)
    return {"status": "ok", "record_id": record.id}


def _knowledge_status(current_user: User, db: Session, lang: str):
    dkt = DKTService()
    dimensions = dkt.compute_five_dimensions(db, current_user.id)
    graph_data = dkt.get_knowledge_graph_data(db, current_user.id)
    dim_keys = [
        "mastery",
        "morph_ability",
        "semantic_density",
        "engagement",
        "cognitive_load",
    ]
    return {
        "mastery": dimensions["mastery"],
        "morph_ability": dimensions["morph_ability"],
        "semantic_density": dimensions["semantic_density"],
        "engagement": dimensions["engagement"],
        "cognitive_load": dimensions["cognitive_load"],
        "dimension_labels": {k: t(f"dim.{k}", lang) for k in dim_keys},
        "words": graph_data["words"],
        "graph": graph_data,
        "lang": lang,
    }


@router.get("/knowledge/status")
def knowledge_status(
    lang: str = Depends(get_language),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _knowledge_status(current_user, db, lang)


knowledge_router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@knowledge_router.get("/status")
def knowledge_status_alias(
    lang: str = Depends(get_language),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _knowledge_status(current_user, db, lang)
