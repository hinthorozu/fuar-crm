"""Normalization helpers for duplicate detection and import workflows."""

import re
import unicodedata
from typing import Optional

LEGAL_SUFFIX_PATTERNS = [
    r"\bANONIM\s+SIRKETI\b",
    r"\bANONIM\b",
    r"\bA\s*S\b",
    r"\bAS\b",
    r"\bLIMITED\s+SIRKETI\b",
    r"\bLIMITED\b",
    r"\bLTD\s*STI\b",
    r"\bLTD\b",
    r"\bSIRKETI\b",
    r"\bSTI\b",
    r"\bSANAYI\b",
    r"\bTICARET\b",
    r"\bVE\b",
]

TURKISH_TRANSLATION = str.maketrans({
    "ç": "c", "Ç": "C",
    "ğ": "g", "Ğ": "G",
    "ı": "i", "I": "I",
    "İ": "I", "i": "i",
    "ö": "o", "Ö": "O",
    "ş": "s", "Ş": "S",
    "ü": "u", "Ü": "U",
})


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_text(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.translate(TURKISH_TRANSLATION)
    value = strip_accents(value)
    value = value.upper()
    value = re.sub(r"[^A-Z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def normalize_company_name(company_name: Optional[str]) -> Optional[str]:
    value = normalize_text(company_name)
    if not value:
        return None
    for pattern in LEGAL_SUFFIX_PATTERNS:
        value = re.sub(pattern, " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    if digits.startswith("90") and len(digits) == 12:
        return digits
    if digits.startswith("0") and len(digits) == 11:
        return "90" + digits[1:]
    if len(digits) == 10:
        return "90" + digits
    return digits


def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None
    value = email.strip().lower()
    return value or None


def normalize_website(website: Optional[str]) -> Optional[str]:
    if not website:
        return None
    value = website.strip().lower()
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"^www\.", "", value)
    value = value.split("/")[0]
    return value or None
