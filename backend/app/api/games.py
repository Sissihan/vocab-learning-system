"""Gamification API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_language
from app.database import get_db
from app.models import LearningRecord, User, Vocabulary
from app.services.dkt import DKTService
from app.services.games import GameService
from app.utils.auth import get_current_user
from app.utils.json_helpers import dumps

router = APIRouter(prefix="/api/games", tags=["games"])


class PuzzleAnswer(BaseModel):
    root_id: int
    selected_affix: str | None = None
    correct_affix: str


class PuzzleResultPayload(BaseModel):
    answers: list[PuzzleAnswer] = Field(default_factory=list)
    scene_type: str = "focus"


class SemanticPair(BaseModel):
    word_id: int
    meaning_id: int


class SemanticMatchPayload(BaseModel):
    pairs: list[SemanticPair] = Field(default_factory=list)
    scene_type: str = "focus"


def _record_game_activity(
    db: Session,
    user_id: int,
    activity_type: str,
    score: float,
    is_correct: bool,
    scene_type: str,
    detail: dict,
    word_id: int | None = None,
):
    record = LearningRecord(
        user_id=user_id,
        word_id=word_id,
        scene_type=scene_type,
        score=score,
        response_time=0.0,
        is_correct=is_correct,
        activity_type=activity_type,
        detail_json=dumps(detail),
    )
    db.add(record)


@router.get("/root-puzzle")
def get_root_puzzle(
    count: int = Query(6, ge=3, le=12),
    lang: str = Depends(get_language),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = GameService(db).root_puzzle(count, lang)
    if not data.get("puzzles"):
        raise HTTPException(status_code=404, detail="No root puzzle data available")
    return data


@router.post("/root-puzzle/result")
def submit_root_puzzle(
    payload: PuzzleResultPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = GameService(db)
    answers = [a.model_dump() for a in payload.answers]
    result = svc.evaluate_root_puzzle(answers)

    if not result.get("complete"):
        raise HTTPException(
            status_code=400,
            detail="Please select an affix for every root before submitting",
        )

    _record_game_activity(
        db,
        current_user.id,
        "root_puzzle",
        result["score"] / 100.0,
        result["correct_count"] == result["total"],
        payload.scene_type,
        {"results": result["results"], "game": "root_puzzle"},
    )
    db.commit()
    return result


@router.get("/semantic-match")
def get_semantic_match(
    pairs: int = Query(6, ge=4, le=12),
    lang: str = Depends(get_language),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = GameService(db).semantic_match(pairs, lang)
    if not data.get("words"):
        raise HTTPException(status_code=404, detail="No semantic match data available")
    return data


@router.post("/semantic-match/result")
def submit_semantic_match(
    payload: SemanticMatchPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.pairs:
        raise HTTPException(status_code=400, detail="No pairs submitted")

    svc = GameService(db)
    pairs = [p.model_dump() for p in payload.pairs]
    result = svc.evaluate_semantic_match(pairs)
    dkt = DKTService()

    for item in result["results"]:
        wid = item["word_id"]
        if wid:
            dkt.update_mastery(
                db,
                current_user.id,
                wid,
                item["is_correct"],
                5.0,
            )

    _record_game_activity(
        db,
        current_user.id,
        "semantic_match",
        result["score"] / 100.0,
        result["correct_count"] == result["total"],
        payload.scene_type,
        {"results": result["results"], "game": "semantic_match"},
    )
    db.commit()
    return result


@router.get("/word-planet")
def get_word_planet(
    root_id: int | None = Query(None),
    lang: str = Depends(get_language),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GameService(db).word_planet(root_id, lang)
