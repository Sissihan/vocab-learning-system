"""Simplified Deep Knowledge Tracing for mastery updates."""
import logging
import math
from datetime import datetime
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models import LearningRecord, UserKnowledge, Vocabulary

logger = logging.getLogger(__name__)


class DKTService:
    """
    Simplified DKT using logistic update on mastery probability.
    P(master|interaction) = σ(w·[prev_mastery, correct, time, attempts])
    """

    WEIGHTS = {
        "correct": 0.35,
        "incorrect": -0.25,
        "time_fast": 0.05,
        "time_slow": -0.05,
        "review": 0.08,
    }

    def update_mastery(
        self,
        db: Session,
        user_id: int,
        word_id: int,
        is_correct: bool,
        response_time: float,
    ) -> UserKnowledge:
        state = (
            db.query(UserKnowledge)
            .filter(
                UserKnowledge.user_id == user_id,
                UserKnowledge.word_id == word_id,
            )
            .first()
        )
        if not state:
            state = UserKnowledge(
                user_id=user_id,
                word_id=word_id,
                mastery_level=0.1,
                morph_ability=0.2,
                semantic_density=0.2,
                review_count=0,
            )
            db.add(state)
            db.flush()

        mastery = state.mastery_level or 0.1
        morph = state.morph_ability or 0.0
        semantic = state.semantic_density or 0.0
        reviews = state.review_count or 0

        delta = self.WEIGHTS["correct"] if is_correct else self.WEIGHTS["incorrect"]
        if response_time < 3:
            delta += self.WEIGHTS["time_fast"]
        elif response_time > 15:
            delta += self.WEIGHTS["time_slow"]
        delta += self.WEIGHTS["review"] * min(reviews, 5) * 0.02

        logit = math.log(max(mastery, 0.01) / max(1 - mastery, 0.01))
        logit += delta
        state.mastery_level = max(0.0, min(1.0, 1 / (1 + math.exp(-logit))))

        if is_correct:
            state.morph_ability = min(1.0, morph + 0.03)
            state.semantic_density = min(1.0, semantic + 0.02)
        else:
            state.morph_ability = max(0.0, morph - 0.01)

        state.review_count = reviews + 1
        state.last_review = datetime.utcnow()
        db.commit()
        db.refresh(state)
        return state

    def compute_five_dimensions(
        self, db: Session, user_id: int
    ) -> Dict[str, float]:
        """Aggregate five-dimensional learner profile."""
        states = (
            db.query(UserKnowledge)
            .filter(UserKnowledge.user_id == user_id)
            .all()
        )
        records = (
            db.query(LearningRecord)
            .filter(LearningRecord.user_id == user_id)
            .order_by(LearningRecord.timestamp.desc())
            .limit(100)
            .all()
        )

        if not states:
            return {
                "mastery": 0.0,
                "morph_ability": 0.0,
                "semantic_density": 0.0,
                "engagement": 0.0,
                "cognitive_load": 0.3,
            }

        mastery = sum(s.mastery_level for s in states) / len(states)
        morph = sum(s.morph_ability for s in states) / len(states)
        semantic = sum(s.semantic_density for s in states) / len(states)

        engagement = min(1.0, len(records) / 50)
        if records:
            avg_time = sum(r.response_time for r in records) / len(records)
            error_rate = 1 - sum(1 for r in records if r.is_correct) / len(records)
            cognitive_load = min(1.0, 0.4 * error_rate + 0.3 * (avg_time / 20) + 0.3 * (1 - mastery))
        else:
            cognitive_load = 0.3

        return {
            "mastery": round(mastery, 3),
            "morph_ability": round(morph, 3),
            "semantic_density": round(semantic, 3),
            "engagement": round(engagement, 3),
            "cognitive_load": round(cognitive_load, 3),
        }

    def get_knowledge_graph_data(self, db: Session, user_id: int) -> dict:
        states = (
            db.query(UserKnowledge)
            .filter(UserKnowledge.user_id == user_id)
            .all()
        )
        words = []
        nodes = []
        edges = []

        for s in states:
            word = db.query(Vocabulary).filter(Vocabulary.id == s.word_id).first()
            if not word:
                continue
            words.append({
                "word_id": word.id,
                "word": word.word,
                "mastery": s.mastery_level,
                "last_review": s.last_review.isoformat() if s.last_review else None,
                "review_count": s.review_count,
            })
            nodes.append({
                "id": word.id,
                "label": word.word,
                "mastery": s.mastery_level,
                "group": "mastered" if s.mastery_level > 0.7 else "learning",
            })

        return {"words": words, "nodes": nodes, "edges": edges}
