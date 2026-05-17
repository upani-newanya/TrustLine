"""Field extraction from natural user messages.

Pulls structured values from free text using pattern matching, keyword
analysis, and known-entity lists (platforms, banks, etc.).

Design goals:
  - Extract ALL detectable fields from a single message (multi-field merging)
  - Normalize values (platforms → proper names, yes/no → "yes"/"no")
  - Extract domains/websites even without http prefix
  - Accept approximate dates/times without over-clarifying
  - Assign confidence scores for field locking
"""
from __future__ import annotations

import re
from typing import Optional

from .incidents import get_schema_for_incident, FieldSpec, COMMON_CONTACT_FIELDS

# ── Known entities ──

_PLATFORMS = {
    "telegram": "Telegram", "whatsapp": "WhatsApp", "facebook": "Facebook",
    "instagram": "Instagram", "twitter": "Twitter",
    "tiktok": "TikTok", "snapchat": "Snapchat", "reddit": "Reddit",
    "youtube": "YouTube", "linkedin": "LinkedIn", "messenger": "Messenger",
    "pornhub": "Pornhub", "xvideos": "XVideos", "xhamster": "xHamster",
    "xnxx": "XNXX",
    "onlyfans": "OnlyFans", "gmail": "Gmail", "email": "Email",
    "tinder": "Tinder", "viber": "Viber",
}

_BANKS = {
    "boc": "Bank of Ceylon", "bank of ceylon": "Bank of Ceylon",
    "nsb": "NSB", "national savings bank": "NSB",
    "commercial bank": "Commercial Bank", "hnb": "HNB",
    "hatton national": "HNB", "sampath": "Sampath Bank",
    "peoples bank": "People's Bank", "people's bank": "People's Bank",
    "seylan": "Seylan Bank", "dfcc": "DFCC Bank", "ndb": "NDB Bank",
    "nations trust": "Nations Trust Bank", "pan asia": "Pan Asia Bank",
}

_YES_WORDS = frozenset({
    "yes", "yeah", "yep", "yea", "ya", "i do", "i did", "i have",
    "correct", "right", "true", "of course", "definitely",
})
_NO_WORDS = frozenset({
    "no", "nope", "nah", "i don't", "i didn't", "i haven't",
    "not really", "never", "none",
})

_URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+")
_DOMAIN_PATTERN = re.compile(r"\b([a-z0-9][-a-z0-9]*\.(?:com|org|net|lk|io|co|me|info|xyz|live|online|site))\b", re.IGNORECASE)
_PHONE_PATTERN = re.compile(r"(?:\+94|0)\d[\d\s\-]{7,}")
_AMOUNT_PATTERN = re.compile(
    r"(?:rs\.?|lkr|rupees?)\s*[\d,]+|\d[\d,]+\s*(?:rs|lkr|rupees?|lakhs?|thousand|k\b)",
    re.IGNORECASE,
)
_DATE_PATTERN = re.compile(
    r"\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b"   # 03/04/2026, 3-4-26
    r"|\b\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}\b",     # 2026-04-03
    re.IGNORECASE,
)
_APPROX_TIME_KEYWORDS = (
    # Multi-word first so they match before single words
    "last night", "last week", "last month",
    "this morning", "this evening", "this afternoon",
    "few days ago", "few hours ago", "hours ago", "days ago",
    "yesterday evening", "yesterday morning", "yesterday afternoon",
    "yesterday", "today", "just now", "recently",
)

_NAME_PATTERN = re.compile(
    r"(?:my name is|i'm|i am|im|this is|call me|hi i'm|hi i am|hi im|hi am|hello i'm|hello i am|hello im)\s+"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"  # 1–3 capitalized words
)
# Fallback for all-lowercase: "my name is kamal perera"
_NAME_PATTERN_LOWER = re.compile(
    r"(?:my name is|call me|hi i'm|hi i am|hi im|hi am|hello i'm|hello i am|hello im|^im|^i'm)\s+([a-z]+(?:\s+[a-z]+)?)\b",
    re.IGNORECASE,
)
# Stop words that signal end of a name in a longer sentence
_NAME_STOP = frozenset({
    "my", "and", "the", "from", "in", "on", "at", "to", "is", "was",
    "i", "they", "we", "he", "she", "it", "a", "an", "but", "or",
    "personal", "private", "public", "photo", "video", "account", "bank",
})
# Pattern to detect domain-like strings (not names)
_DOMAIN_LIKE = re.compile(r"\b[a-z0-9][-a-z0-9]*\.(com|org|net|lk|io|co|me|info|xyz|live|online|site)\b", re.IGNORECASE)


class ExtractionResult:
    """Holds extracted fields with confidence scores."""

    def __init__(self):
        self.fields: dict[str, tuple[str, float]] = {}  # key → (value, confidence)

    def add(self, key: str, value: str, confidence: float = 1.0) -> None:
        # Don't downgrade — keep higher confidence
        if key in self.fields and self.fields[key][1] >= confidence:
            return
        self.fields[key] = (value, confidence)

    def to_dict(self) -> dict[str, str]:
        return {k: v for k, (v, _) in self.fields.items()}

    def to_dict_with_confidence(self) -> dict[str, tuple[str, float]]:
        return dict(self.fields)


class FieldExtractor:
    """Extracts structured field values from user messages.

    Designed for multi-field merging: a single user message like
    "yes they are visible on abc.com" fills both content_still_live
    and platform_link/platform_name.
    """

    def extract_with_confidence(
        self,
        message: str,
        incident_type: str,
        already_locked: set[str],
    ) -> dict[str, tuple[str, float]]:
        """Return {field_key: (extracted_value, confidence)} — skips locked fields."""
        result = ExtractionResult()
        low = message.lower()

        # ── Global extractors (applied before field-specific) ──

        # Platform detection
        if "platform_name" not in already_locked:
            p = self._extract_platform(low)
            if p:
                result.add("platform_name", p, 0.95)
        if "platform_used" not in already_locked:
            p = self._extract_platform(low)
            if p:
                result.add("platform_used", p, 0.95)

        # Bank detection
        if "bank_name" not in already_locked:
            b = self._extract_bank(low)
            if b:
                result.add("bank_name", b, 0.95)

        # URL / domain extraction → fills platform_link AND platform_name
        urls = _URL_PATTERN.findall(message)
        if urls:
            if "platform_link" not in already_locked:
                result.add("platform_link", urls[0], 0.95)
            # Also try to extract platform from URL
            if "platform_name" not in already_locked and "platform_name" not in result.fields:
                for key, name in _PLATFORMS.items():
                    if key in urls[0].lower():
                        result.add("platform_name", name, 0.90)
                        break
        else:
            # Try bare domain match (abc.com)
            domains = _DOMAIN_PATTERN.findall(message)
            if domains:
                if "platform_link" not in already_locked:
                    result.add("platform_link", domains[0], 0.85)

        # Date extraction
        dates = _DATE_PATTERN.findall(message)
        if dates:
            date_str = dates[0]
            for fkey in ("when_discovered", "transaction_time", "incident_date"):
                if fkey not in already_locked:
                    result.add(fkey, date_str, 0.90)
                    break  # only fill the first matching date field

        # Name extraction
        if "victim_name" not in already_locked:
            name = self._extract_name(message)
            if name:
                result.add("victim_name", name, 0.95)

        # Approximate time references (accept without over-clarifying)
        for kw in _APPROX_TIME_KEYWORDS:
            if kw in low:
                for fkey in ("when_discovered", "transaction_time", "incident_date"):
                    if fkey not in already_locked and fkey not in result.fields:
                        result.add(fkey, kw, 0.80)
                        break
                break  # one match is enough

        # Phone extraction
        phones = _PHONE_PATTERN.findall(message)
        if phones:
            phone_val = phones[0].strip()
            if "victim_phone" not in already_locked:
                result.add("victim_phone", phone_val, 0.95)

        # Amount extraction
        amounts = _AMOUNT_PATTERN.findall(message)
        if amounts:
            if "amount_lost" not in already_locked:
                result.add("amount_lost", amounts[0].strip(), 0.90)

        # ── Field-specific extraction from schema ──
        all_fields = get_schema_for_incident(incident_type) + COMMON_CONTACT_FIELDS
        for spec in all_fields:
            if spec.key in already_locked or spec.key in result.fields:
                continue
            value, conf = self._try_extract_with_conf(spec, message, low)
            if value is not None:
                result.add(spec.key, value, conf)

        return result.to_dict_with_confidence()

    def extract(
        self,
        message: str,
        incident_type: str,
        already_collected: dict,
    ) -> dict[str, str]:
        """Legacy compat: return {field_key: value} without confidence."""
        locked = set(already_collected.keys())
        raw = self.extract_with_confidence(message, incident_type, locked)
        return {k: v for k, (v, _) in raw.items()}

    def extract_yes_no(self, message: str) -> Optional[bool]:
        """Check if a message is a clear yes/no answer.

        Only applies to short, direct responses (≤8 words).
        """
        low = message.strip().lower().rstrip(".,!?")
        if len(low.split()) > 8:
            return None
        if low in _YES_WORDS or any(low.startswith(w) for w in _YES_WORDS):
            return True
        if low in _NO_WORDS or any(low.startswith(w) for w in _NO_WORDS):
            return False
        return None

    # ── internal helpers ──

    def _try_extract_with_conf(
        self, spec: FieldSpec, message: str, low: str,
    ) -> tuple[Optional[str], float]:
        """Return (value, confidence) or (None, 0)."""
        if spec.field_type == "boolean":
            val = self._extract_boolean(spec, low)
            return (val, 0.90) if val is not None else (None, 0.0)
        if spec.field_type == "url":
            urls = _URL_PATTERN.findall(message)
            return (urls[0], 0.95) if urls else (None, 0.0)
        if spec.field_type == "phone":
            phones = _PHONE_PATTERN.findall(message)
            return (phones[0].strip(), 0.95) if phones else (None, 0.0)
        if spec.field_type == "amount":
            amounts = _AMOUNT_PATTERN.findall(message)
            return (amounts[0].strip(), 0.90) if amounts else (None, 0.0)
        # text / choice / date — keyword match
        if spec.extraction_keywords:
            for kw in spec.extraction_keywords:
                if kw in low:
                    return (kw, 0.80)
        return (None, 0.0)

    @staticmethod
    def _extract_name(message: str) -> Optional[str]:
        """Extract a person's name from the message."""
        # Prefer capitalized pattern: "My name is John Doe"
        m = _NAME_PATTERN.search(message)
        if m:
            raw = m.group(1).strip()
            # Trim trailing stop words
            words = raw.split()
            clean = []
            for w in words:
                if w.lower() in _NAME_STOP:
                    break
                clean.append(w)
            if clean:
                return " ".join(clean)

        # Fallback: lowercase "my name is kamal"
        m = _NAME_PATTERN_LOWER.search(message)
        if m:
            raw = m.group(1).strip()
            words = raw.split()
            clean = []
            for w in words:
                if w.lower() in _NAME_STOP:
                    break
                clean.append(w.capitalize())
            if clean:
                return " ".join(clean)

        return None

    @staticmethod
    def _extract_boolean(spec: FieldSpec, low: str) -> Optional[str]:
        if not spec.extraction_keywords:
            return None
        for kw in spec.extraction_keywords:
            if kw in low:
                negated = any(
                    neg in low
                    for neg in ("not ", "no ", "don't ", "didn't ", "haven't ", "can't ", "never ")
                )
                return "no" if negated else "yes"
        return None

    @staticmethod
    def _extract_platform(low: str) -> Optional[str]:
        for key, name in _PLATFORMS.items():
            if key in low:
                return name
        return None

    @staticmethod
    def _extract_bank(low: str) -> Optional[str]:
        for key, name in _BANKS.items():
            if key in low:
                return name
        return None
