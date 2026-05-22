"""RAG-constrained content generation from knowledge graph."""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.i18n import t
from app.models import Root, Vocabulary
from app.utils.json_helpers import loads

logger = logging.getLogger(__name__)


class ContentService:
    """Generate layered learning content with KG validation."""

    def __init__(self, db: Session):
        self.db = db

    def generate(
        self,
        word_id: int,
        level: str = "intermediate",
        scene_type: str = "focus",
        lang: str = "zh-CN",
    ) -> dict:
        word = self.db.query(Vocabulary).filter(Vocabulary.id == word_id).first()
        if not word:
            return {"error": t("error.word_not_found", lang), "validated": False}

        root = None
        if word.root_id:
            root = self.db.query(Root).filter(Root.id == word.root_id).first()

        root_text = root.root if root else "unknown"
        root_meaning = root.meaning if root else "N/A"

        level_key = level if level in ("beginner", "intermediate", "advanced") else "advanced"

        sentence = t(
            f"content.sentence.{level_key}",
            lang,
            word=word.word,
            meaning=word.meaning,
            root=root_text,
            root_meaning=root_meaning,
        )
        quiz = t(f"content.quiz.{level_key}", lang, word=word.word)

        stored_examples = loads(word.example_json, [])
        if lang == "en" and stored_examples:
            examples = stored_examples[:3]
        else:
            examples = self._generate_examples(word, root, level_key, lang)

        validated, validation_notes = self._validate_content(
            word, root, sentence, examples, lang
        )

        return {
            "word_id": word.id,
            "word": word.word,
            "meaning": word.meaning,
            "phonetic": word.phonetic,
            "level": level,
            "scene_type": scene_type,
            "lang": lang,
            "sentence": sentence,
            "examples": examples,
            "quiz": quiz,
            "root_analysis": {
                "root": root_text,
                "root_meaning": root_meaning,
                "origin": root.origin if root else "",
            },
            "validated": validated,
            "validation_notes": validation_notes,
            "scene_hint": t(f"content.hint.{scene_type}", lang),
        }

    def _generate_examples(self, word, root, level: str, lang: str) -> list:
        root_name = root.root if root else "word"
        patterns = [
            t("content.example1", lang, word=word.word),
            t(
                "content.example2",
                lang,
                root=root_name,
                word=word.word,
                meaning=word.meaning,
            ),
            t("content.example3", lang, word=word.word),
        ]
        if level == "beginner":
            return [patterns[0]]
        return patterns[:2 if level == "intermediate" else 3]

    def _validate_content(
        self, word, root, sentence: str, examples: list, lang: str
    ) -> tuple:
        """Accuracy check against knowledge graph facts."""
        notes = []
        valid = True

        if root and root.root not in sentence and root.root not in word.word:
            notes.append(t("content.validate.root_missing", lang))
            valid = False

        meaning_in_sentence = (
            word.meaning.lower() in sentence.lower()
            or word.word.lower() in sentence.lower()
        )
        if meaning_in_sentence:
            notes.append(t("content.validate.meaning_embedded", lang))

        for ex in examples:
            if word.word not in ex:
                notes.append(
                    t(
                        "content.validate.example_missing_word",
                        lang,
                        excerpt=ex[:40],
                    )
                )
                valid = False

        if not notes:
            notes.append(t("content.validate.ok", lang))

        return valid, notes
