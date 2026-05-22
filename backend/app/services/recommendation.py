"""Dual-channel root-semantic fusion recommendation engine."""
import logging
from typing import List, Optional

import numpy as np
from sqlalchemy.orm import Session, joinedload

from app.models import LearningRecord, User, UserKnowledge, Vocabulary
from app.i18n import t
from app.services.alpha_controller import AlphaController
from app.services.context import ContextService
from app.services.embeddings import parse_embedding, semantic_similarity
from app.services.knowledge_graph import KnowledgeGraphService

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Score = α × R_sim + (1-α) × S_sim
    """

    def __init__(self, db: Session):
        self.db = db
        self.graph = KnowledgeGraphService(db)
        self.alpha_ctrl = AlphaController()
        self.context_svc = ContextService()

    def recommend(
        self,
        user: User,
        scene_type: str = "fragment",
        context: Optional[dict] = None,
        limit: int = 10,
        lang: str = "zh-CN",
    ) -> dict:
        self.graph.build()
        context = context or {}

        knowledge = (
            self.db.query(UserKnowledge)
            .filter(UserKnowledge.user_id == user.id)
            .all()
        )
        mastery_map = {k.word_id: k.mastery_level for k in knowledge}
        mastery_avg = (
            sum(mastery_map.values()) / len(mastery_map) if mastery_map else 0.3
        )
        morph_avg = (
            sum(k.morph_ability for k in knowledge) / len(knowledge)
            if knowledge
            else 0.3
        )

        recent_records = (
            self.db.query(LearningRecord)
            .filter(LearningRecord.user_id == user.id)
            .order_by(LearningRecord.timestamp.desc())
            .limit(20)
            .all()
        )
        recent_accuracy = (
            sum(1 for r in recent_records if r.is_correct) / len(recent_records)
            if recent_records
            else 0.5
        )

        alpha = self.alpha_ctrl.compute(
            user.level, mastery_avg, morph_avg, scene_type, recent_accuracy
        )
        scene_config = self.context_svc.get_scene_config(scene_type, lang)

        anchor_word = self._select_anchor(user.id, mastery_map)
        anchor_vec = np.zeros(64)
        if anchor_word:
            anchor_vec = parse_embedding(anchor_word.embedding_json)

        all_words = (
            self.db.query(Vocabulary)
            .options(joinedload(Vocabulary.primary_root))
            .all()
        )
        scored: List[dict] = []

        for word in all_words:
            mastery = mastery_map.get(word.id, 0.0)
            if mastery > 0.95:
                continue

            r_sim = 0.0
            if anchor_word and anchor_word.root_id and word.root_id:
                r_sim = self.graph.shortest_path_strength(
                    anchor_word.root_id, word.root_id
                )
                if anchor_word.root_id == word.root_id:
                    r_sim = max(r_sim, 0.85)
            elif anchor_word:
                r_sim = self.graph.shortest_path_strength(anchor_word.id, word.id) * 0.7

            word_vec = parse_embedding(word.embedding_json)
            s_sim = semantic_similarity(anchor_vec, word_vec) if anchor_word else 0.5

            difficulty_penalty = abs(word.difficulty - self._level_to_difficulty(user.level)) * 0.05
            score = alpha * r_sim + (1 - alpha) * s_sim - difficulty_penalty
            forget_boost = max(0, 0.3 - mastery) if scene_type == "review" else 0
            score += forget_boost

            explanation = self._build_explanation(
                word, r_sim, s_sim, alpha, anchor_word, lang
            )

            scored.append({
                "word_id": word.id,
                "word": word.word,
                "meaning": word.meaning,
                "score": round(score, 4),
                "r_sim": round(r_sim, 4),
                "s_sim": round(s_sim, 4),
                "alpha": alpha,
                "explanation": explanation,
                "scene_config": scene_config,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        items = scored[:limit]

        return {
            "scene_type": scene_type,
            "alpha": alpha,
            "items": items,
            "scene_adaptation": scene_config,
            "lang": lang,
            "alpha_explanation": self.alpha_ctrl.explain(
                alpha, scene_type, user.level, lang
            ),
        }

    def _select_anchor(self, user_id: int, mastery_map: dict) -> Optional[Vocabulary]:
        partial = sorted(
            [(wid, m) for wid, m in mastery_map.items() if 0.2 < m < 0.8],
            key=lambda x: abs(x[1] - 0.5),
        )
        if partial:
            word_id = partial[0][0]
            return (
                self.db.query(Vocabulary)
                .options(joinedload(Vocabulary.primary_root))
                .filter(Vocabulary.id == word_id)
                .first()
            )

        return (
            self.db.query(Vocabulary)
            .options(joinedload(Vocabulary.primary_root))
            .order_by(Vocabulary.difficulty)
            .first()
        )

    def _level_to_difficulty(self, level: str) -> int:
        return {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}.get(
            level, 2
        )

    def _build_explanation(
        self, word, r_sim: float, s_sim: float, alpha: float, anchor, lang: str
    ) -> str:
        sep = "; " if lang == "en" else "；"
        parts = [
            t(
                "rec.score_formula",
                lang,
                alpha=alpha,
                r_sim=r_sim,
                beta=1 - alpha,
                s_sim=s_sim,
            )
        ]
        if anchor:
            parts.append(t("rec.anchor", lang, word=anchor.word))
        if r_sim > 0.6:
            parts.append(t("rec.high_morph", lang))
        if s_sim > 0.6:
            parts.append(t("rec.high_semantic", lang))
        if word.root_id and word.primary_root:
            parts.append(
                t(
                    "rec.root_link",
                    lang,
                    root=word.primary_root.root,
                    meaning=word.primary_root.meaning,
                )
            )
        return sep.join(parts)
