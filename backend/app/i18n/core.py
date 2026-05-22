"""i18n core: language normalization and lookup."""
from typing import Any

from app.i18n.messages import MESSAGES

SUPPORTED_LANGS = ("zh-CN", "en", "zh-TW")
DEFAULT_LANG = "zh-CN"

_ALIASES = {
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-hans": "zh-CN",
    "zh-hans-cn": "zh-CN",
    "cn": "zh-CN",
    "zh-tw": "zh-TW",
    "zh-hant": "zh-TW",
    "zh-hk": "zh-TW",
    "tw": "zh-TW",
    "en-us": "en",
    "en-gb": "en",
}


def normalize_lang(lang: str | None) -> str:
    """Map request language to supported locale."""
    if not lang:
        return DEFAULT_LANG
    key = lang.strip().replace("_", "-").lower()
    if key in _ALIASES:
        return _ALIASES[key]
    for supported in SUPPORTED_LANGS:
        if key == supported.lower():
            return supported
    return DEFAULT_LANG


def t(key: str, lang: str | None = None, **kwargs: Any) -> str:
    """Translate message key for locale."""
    locale = normalize_lang(lang)
    catalog = MESSAGES.get(locale, MESSAGES[DEFAULT_LANG])
    text = (
        catalog.get(key)
        or MESSAGES[DEFAULT_LANG].get(key)
        or MESSAGES["en"].get(key, key)
    )
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text


def localize_scene_config(scene_type: str, config: dict, lang: str) -> dict:
    """Add human-readable labels to scene config."""
    return {
        **config,
        "scene_type": scene_type,
        "scene_label": t(f"scene.{scene_type}", lang),
        "presentation_label": t(f"presentation.{config['presentation']}", lang),
        "gamification_label": t(f"gamification.{config['gamification']}", lang),
        "content_depth_label": t(f"depth.{config['content_depth']}", lang),
    }
