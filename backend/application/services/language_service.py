from __future__ import annotations

import re
import unicodedata
from typing import Literal


Language = Literal["vi", "en"]

# The detector intentionally stays small and deterministic. The chatbot only
# needs to distinguish Vietnamese from English, and Vietnamese users often
# type without tone marks (for example: "tao slide ve bac Ho").
_VIETNAMESE_HINTS = frozenset(
    {
        "anh",
        "bac",
        "ban",
        "bat",
        "bai",
        "bi",
        "bo",
        "cac",
        "can",
        "cho",
        "chieu",
        "chua",
        "co",
        "cua",
        "cung",
        "da",
        "dang",
        "de",
        "den",
        "du",
        "duoc",
        "dung",
        "dau",
        "gi",
        "giup",
        "hay",
        "hom",
        "khac",
        "khong",
        "khi",
        "la",
        "lai",
        "lam",
        "mot",
        "muon",
        "nang",
        "nay",
        "nen",
        "neu",
        "nguoi",
        "nhe",
        "noi",
        "ra",
        "rang",
        "se",
        "tao",
        "theo",
        "thi",
        "thong",
        "thuyet",
        "tin",
        "toi",
        "trinh",
        "va",
        "vao",
        "ve",
        "viec",
        "voi",
        "xin",
        "yeu",
        "y",
    }
)


def normalize_language_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or "").casefold())
    normalized = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return normalized.replace("đ", "d")


def detect_language(value: str) -> Language:
    original = str(value or "").strip().casefold()
    if not original:
        return "en"

    decomposed = unicodedata.normalize("NFKD", original)
    # A user-entered Vietnamese tone mark is a strong signal for this app's
    # vi/en boundary. The base letters below also survive accent removal.
    if any(unicodedata.combining(char) for char in decomposed) or any(
        char in original for char in "ăâêôơưđ"
    ):
        return "vi"

    normalized = normalize_language_text(original)
    tokens = re.findall(r"[a-z]+", normalized)
    if sum(token in _VIETNAMESE_HINTS for token in tokens) >= 1:
        return "vi"
    return "en"


def language_instruction(language: Language) -> str:
    if language == "vi":
        return (
            "Response language: Vietnamese (vi). Write every user-facing sentence "
            "and option label in Vietnamese. Do not switch to English unless the "
            "user explicitly asks for English."
        )
    return (
        "Response language: English (en). Write every user-facing sentence and "
        "option label in English unless the user explicitly asks for another language."
    )


def is_language_compatible(value: str, expected: Language) -> bool:
    if not str(value or "").strip():
        return False
    return detect_language(value) == expected
