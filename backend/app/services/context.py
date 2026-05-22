"""Context-aware scene detection and adaptation."""
import logging
from datetime import datetime
from typing import Optional

from app.i18n.core import localize_scene_config

logger = logging.getLogger(__name__)

SCENE_CONFIGS = {
    "commute": {
        "duration_minutes": "3-5",
        "presentation": "audio+cards",
        "gamification": "root_puzzle",
        "content_depth": "light",
        "batch_size": 5,
        "show_phonetic": True,
        "show_examples": False,
    },
    "focus": {
        "duration_minutes": "15-20",
        "presentation": "deep_analysis",
        "gamification": "semantic_match",
        "content_depth": "deep",
        "batch_size": 12,
        "show_phonetic": True,
        "show_examples": True,
    },
    "fragment": {
        "duration_minutes": "1-2",
        "presentation": "flashcard",
        "gamification": "speed_quiz",
        "content_depth": "minimal",
        "batch_size": 3,
        "show_phonetic": False,
        "show_examples": False,
    },
    "review": {
        "duration_minutes": "flexible",
        "presentation": "spaced_repetition",
        "gamification": "diagnostic_quiz",
        "content_depth": "adaptive",
        "batch_size": 8,
        "show_phonetic": True,
        "show_examples": True,
    },
}


class ContextService:
    """Scene inference and content adaptation."""

    def get_scene_config(self, scene_type: str, lang: str = "zh-CN") -> dict:
        raw = SCENE_CONFIGS.get(scene_type, SCENE_CONFIGS["fragment"])
        return localize_scene_config(scene_type, raw, lang)

    def infer_scene(
        self,
        location_type: str = "unknown",
        device_state: str = "desktop",
        hour: Optional[int] = None,
        duration_available: Optional[int] = None,
    ) -> str:
        """
        Rule-based scene inference (MVP auto-detection).
        """
        hour = hour if hour is not None else datetime.now().hour

        if location_type in ("transit", "vehicle", "subway"):
            return "commute"
        if duration_available is not None and duration_available <= 3:
            return "fragment"
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            if device_state in ("mobile", "phone"):
                return "commute"
        if device_state == "desktop" and (9 <= hour <= 11 or 14 <= hour <= 16):
            return "focus"
        if duration_available and duration_available >= 15:
            return "focus"
        return "fragment"

    def log_context(
        self,
        db,
        user_id: int,
        location_type: str,
        device_state: str,
        manual_scene: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> str:
        from app.models import ContextLog
        from app.utils.json_helpers import dumps

        inferred = manual_scene or self.infer_scene(location_type, device_state)
        log = ContextLog(
            user_id=user_id,
            location_type=location_type,
            device_state=device_state,
            inferred_scene=inferred,
            context_json=dumps(extra or {}),
        )
        db.add(log)
        db.commit()
        return inferred
