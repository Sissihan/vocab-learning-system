"""Shared API dependencies."""
from fastapi import Header, Query

from app.i18n import normalize_lang


def get_language(
    lang: str | None = Query(None, description="Locale: zh-CN, en, zh-TW"),
    accept_language: str | None = Header(None, alias="Accept-Language"),
) -> str:
    """Resolve language from query param or Accept-Language header."""
    if lang:
        return normalize_lang(lang)
    if accept_language:
        first = accept_language.split(",")[0].split(";")[0].strip()
        return normalize_lang(first)
    return normalize_lang(None)
