"""User profile management."""
from sqlalchemy.orm import Session

from app.models import User
from app.i18n import t
from app.services.dkt import DKTService
from app.utils.json_helpers import dumps, loads

DIM_KEYS = [
    "mastery",
    "morph_ability",
    "semantic_density",
    "engagement",
    "cognitive_load",
]


class ProfileService:
    """Manage learner profile and dynamic updates."""

    def __init__(self, db: Session):
        self.db = db
        self.dkt = DKTService()

    def get_profile(self, user: User, lang: str = "zh-CN") -> dict:
        profile = loads(user.profile_json, {})
        dimensions = self.dkt.compute_five_dimensions(self.db, user.id)
        dimension_labels = {k: t(f"dim.{k}", lang) for k in DIM_KEYS}
        return {
            "id": user.id,
            "username": user.username,
            "level": user.level,
            "level_label": t(f"level.{user.level}", lang),
            "learning_goal": user.learning_goal,
            "cognitive_style": user.cognitive_style,
            "profile": profile,
            "dimensions": dimensions,
            "dimension_labels": dimension_labels,
            "lang": lang,
        }

    def update_profile(self, user: User, data: dict, lang: str = "zh-CN") -> dict:
        if data.get("level"):
            user.level = data["level"]
        if data.get("learning_goal"):
            user.learning_goal = data["learning_goal"]
        if data.get("cognitive_style"):
            user.cognitive_style = data["cognitive_style"]

        profile = loads(user.profile_json, {})
        if data.get("vocab_level") is not None:
            profile["vocab_level"] = data["vocab_level"]
        if data.get("preferred_scene"):
            profile["preferred_scene"] = data["preferred_scene"]
        if data.get("language"):
            profile["language"] = data["language"]
        user.profile_json = dumps(profile)

        self.db.commit()
        self.db.refresh(user)
        response_lang = profile.get("language") or lang
        return self.get_profile(user, response_lang)
