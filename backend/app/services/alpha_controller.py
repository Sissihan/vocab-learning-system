"""Dynamic alpha weight controller (rule-based DQN substitute)."""
import logging
from typing import Dict

from app.i18n import t

logger = logging.getLogger(__name__)

SCENE_ALPHA_BIAS = {
    "commute": 0.05,
    "focus": -0.05,
    "fragment": 0.08,
    "review": -0.03,
}

LEVEL_ALPHA = {
    "beginner": 0.65,
    "intermediate": 0.50,
    "advanced": 0.35,
    "expert": 0.25,
}


class AlphaController:
    """
    Simplified rule engine replacing DQN for alpha tuning.
    α > 0.5 emphasizes morphology; α < 0.5 emphasizes semantics.
    """

    def compute(
        self,
        user_level: str,
        mastery_avg: float,
        morph_ability: float,
        scene_type: str,
        recent_accuracy: float,
    ) -> float:
        base = LEVEL_ALPHA.get(user_level, 0.55)
        mastery_factor = 0.15 * (1 - mastery_avg)
        morph_factor = 0.1 * morph_ability
        scene_bias = SCENE_ALPHA_BIAS.get(scene_type, 0.0)
        accuracy_factor = -0.08 * (recent_accuracy - 0.5)

        alpha = base + mastery_factor + morph_factor + scene_bias + accuracy_factor
        alpha = max(0.2, min(0.85, alpha))

        logger.debug(
            "Alpha computed: %.3f (level=%s, mastery=%.2f, scene=%s)",
            alpha,
            user_level,
            mastery_avg,
            scene_type,
        )
        return round(alpha, 3)

    def explain(
        self, alpha: float, scene_type: str, user_level: str, lang: str = "zh-CN"
    ) -> Dict[str, str]:
        morph_weight = alpha
        semantic_weight = 1 - alpha
        strategy_key = "alpha.strategy_morph" if alpha > 0.5 else "alpha.strategy_semantic"
        scene_label = t(f"scene.{scene_type}", lang)
        level_label = t(f"level.{user_level}", lang)

        return {
            "alpha": str(alpha),
            "morph_weight": f"{morph_weight:.0%}",
            "semantic_weight": f"{semantic_weight:.0%}",
            "strategy": t(strategy_key, lang),
            "scene_influence": t("alpha.scene_influence", lang, scene=scene_label),
            "level_influence": t("alpha.level_influence", lang, level=level_label),
        }
