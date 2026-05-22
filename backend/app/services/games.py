"""Gamification module data generators."""
import random
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.i18n import t
from app.models import Root, Vocabulary, WordSemanticLink
from app.services.knowledge_graph import KnowledgeGraphService

logger = logging.getLogger(__name__)

AFFIXES = [
    {"affix": "un-", "type": "prefix", "key": "affix.un"},
    {"affix": "re-", "type": "prefix", "key": "affix.re"},
    {"affix": "pre-", "type": "prefix", "key": "affix.pre"},
    {"affix": "dis-", "type": "prefix", "key": "affix.dis"},
    {"affix": "-tion", "type": "suffix", "key": "affix.tion"},
    {"affix": "-able", "type": "suffix", "key": "affix.able"},
    {"affix": "-ment", "type": "suffix", "key": "affix.ment"},
    {"affix": "-ive", "type": "suffix", "key": "affix.ive"},
]


def _localize_affix(affix: dict, lang: str) -> dict:
    return {
        "affix": affix["affix"],
        "type": affix["type"],
        "meaning": t(affix["key"], lang),
    }


def _infer_affix_from_words(words: List[Vocabulary]) -> dict:
    """Pick affix that actually appears in example vocabulary."""
    for word in words:
        w = word.word.lower()
        for affix in AFFIXES:
            a = affix["affix"]
            if a.startswith("-"):
                stem = a[1:]
                if w.endswith(stem):
                    return affix
            else:
                stem = a.rstrip("-")
                if w.startswith(stem):
                    return affix
    return random.choice(AFFIXES)


class GameService:
    """Generate game payloads for three cognitive games."""

    def __init__(self, db: Session):
        self.db = db

    def root_puzzle(self, count: int = 6, lang: str = "zh-CN") -> dict:
        """Root-affix matching puzzle with inferable correct answers."""
        roots = self.db.query(Root).order_by(Root.difficulty).limit(count).all()
        if not roots:
            return {
                "game_type": "root_puzzle",
                "title": t("game.root_puzzle.title", lang),
                "description": t("game.root_puzzle.desc", lang),
                "lang": lang,
                "puzzles": [],
            }

        puzzles = []
        used_affixes = set()

        for root in roots:
            words = (
                self.db.query(Vocabulary)
                .filter(Vocabulary.root_id == root.id)
                .limit(5)
                .all()
            )
            correct_affix = _infer_affix_from_words(words)
            if correct_affix["affix"] in used_affixes:
                correct_affix = random.choice(
                    [a for a in AFFIXES if a["affix"] not in used_affixes] or AFFIXES
                )
            used_affixes.add(correct_affix["affix"])

            distractors = [a for a in AFFIXES if a != correct_affix]
            option_count = min(4, len(AFFIXES))
            options = [correct_affix] + random.sample(
                distractors, min(option_count - 1, len(distractors))
            )
            random.shuffle(options)

            puzzles.append({
                "root_id": root.id,
                "root": root.root,
                "meaning": root.meaning,
                "example_words": [w.word for w in words[:3]],
                "correct_affix": correct_affix["affix"],
                "options": [_localize_affix(o, lang) for o in options],
                "hint": t(
                    "game.root_puzzle.hint",
                    lang,
                    root=root.root,
                    meaning=root.meaning,
                ),
            })

        return {
            "game_type": "root_puzzle",
            "title": t("game.root_puzzle.title", lang),
            "description": t("game.root_puzzle.desc", lang),
            "lang": lang,
            "puzzles": puzzles,
        }

    def semantic_match(self, pair_count: int = 6, lang: str = "zh-CN") -> dict:
        """Word-meaning matching game."""
        all_words = self.db.query(Vocabulary).all()
        if len(all_words) < 4:
            return {
                "game_type": "semantic_match",
                "title": t("game.semantic_match.title", lang),
                "description": t("game.semantic_match.desc", lang),
                "lang": lang,
                "words": [],
                "meanings": [],
                "bonus_pairs": [],
            }

        selected = random.sample(all_words, min(pair_count, len(all_words)))
        word_items = [{"id": w.id, "word": w.word} for w in selected]
        meaning_items = [{"id": w.id, "meaning": w.meaning} for w in selected]
        random.shuffle(meaning_items)

        semantic_pairs = []
        word_ids = [w.id for w in selected]
        links = (
            self.db.query(WordSemanticLink)
            .filter(WordSemanticLink.word_id1.in_(word_ids))
            .limit(5)
            .all()
        )
        id_to_word = {w.id: w.word for w in selected}
        for link in links:
            if link.word_id1 in id_to_word and link.word_id2 in id_to_word:
                semantic_pairs.append({
                    "word1": id_to_word[link.word_id1],
                    "word2": id_to_word[link.word_id2],
                    "similarity": link.similarity_score,
                    "hint": t("game.semantic_match.bonus_hint", lang),
                })

        return {
            "game_type": "semantic_match",
            "title": t("game.semantic_match.title", lang),
            "description": t("game.semantic_match.desc", lang),
            "lang": lang,
            "words": word_items,
            "meanings": meaning_items,
            "bonus_pairs": semantic_pairs,
            "pair_count": len(selected),
        }

    def word_planet(self, root_id: int | None = None, lang: str = "zh-CN") -> dict:
        """Visual root derivation network."""
        if root_id is None:
            root = self.db.query(Root).order_by(Root.difficulty).first()
            root_id = root.id if root else None

        if not root_id:
            return {
                "game_type": "word_planet",
                "title": t("game.word_planet.title", lang),
                "description": t("game.word_planet.desc", lang),
                "lang": lang,
                "network": {"nodes": [], "edges": []},
                "available_roots": [],
            }

        graph = KnowledgeGraphService(self.db)
        graph.build()
        network = graph.get_root_network(root_id)

        all_roots = self.db.query(Root).order_by(Root.difficulty).all()
        return {
            "game_type": "word_planet",
            "title": t("game.word_planet.title", lang),
            "description": t("game.word_planet.desc", lang),
            "lang": lang,
            "current_root_id": root_id,
            "network": network,
            "available_roots": [
                {"id": r.id, "root": r.root, "meaning": r.meaning}
                for r in all_roots[:20]
            ],
        }

    def evaluate_root_puzzle(self, answers: List[dict]) -> dict:
        """Score root puzzle submissions."""
        if not answers:
            return {
                "correct_count": 0,
                "total": 0,
                "score": 0.0,
                "results": [],
                "complete": False,
            }

        correct = 0
        results = []
        for ans in answers:
            selected = ans.get("selected_affix")
            expected = ans.get("correct_affix")
            is_ok = bool(selected) and selected == expected
            if is_ok:
                correct += 1
            results.append({
                "root_id": ans.get("root_id"),
                "is_correct": is_ok,
                "selected_affix": selected,
                "correct_affix": expected,
            })

        total = len(answers)
        return {
            "correct_count": correct,
            "total": total,
            "score": round(correct / total * 100, 1),
            "results": results,
            "complete": all(r.get("selected_affix") for r in answers),
        }

    def evaluate_semantic_match(self, pairs: List[dict]) -> dict:
        """Score word-meaning pairs. Correct when word_id == meaning_id."""
        if not pairs:
            return {
                "correct_count": 0,
                "total": 0,
                "score": 0.0,
                "results": [],
            }

        correct = 0
        results = []
        for p in pairs:
            word_id = int(p.get("word_id", 0))
            meaning_id = int(p.get("meaning_id", 0))
            is_ok = word_id > 0 and word_id == meaning_id
            if is_ok:
                correct += 1
            results.append({
                "word_id": word_id,
                "meaning_id": meaning_id,
                "is_correct": is_ok,
            })

        total = len(pairs)
        return {
            "correct_count": correct,
            "total": total,
            "score": round(correct / total * 100, 1),
            "results": results,
        }
