"""Anti-repetition guard for Mithuru.

Tracks recently used comfort phrases, asked questions, bot replies,
and safety-check prompts to prevent the chatbot from sounding robotic
or getting stuck in loops.
"""
from __future__ import annotations

from collections import deque

_MAX_SAFETY_CHECKS = 2  # max "are you safe?" style messages per session


class RepetitionGuard:
    """Tracks recent bot outputs to prevent repetition."""

    def __init__(self, max_recent: int = 12):
        self._recent_phrases: deque[str] = deque(maxlen=max_recent)
        self._recent_questions: deque[str] = deque(maxlen=max_recent)
        self._comfort_used: set[str] = set()
        self._safety_check_count: int = 0

    def record_reply(self, reply: str) -> None:
        self._recent_phrases.append(reply.strip().lower())

    def record_question(self, field_key: str) -> None:
        self._recent_questions.append(field_key)

    def record_comfort_phrase(self, phrase: str) -> None:
        self._comfort_used.add(phrase.strip().lower()[:80])

    def record_safety_check(self) -> None:
        self._safety_check_count += 1

    def too_many_safety_checks(self) -> bool:
        return self._safety_check_count >= _MAX_SAFETY_CHECKS

    def was_recently_said(self, text: str, threshold: float = 0.65) -> bool:
        """True if something very similar was recently said (Jaccard overlap)."""
        low = text.strip().lower()
        for recent in self._recent_phrases:
            if self._jaccard(low, recent) > threshold:
                return True
        return False

    def was_question_recently_asked(self, field_key: str) -> bool:
        return field_key in self._recent_questions

    def was_comfort_used(self, phrase: str) -> bool:
        return phrase.strip().lower()[:80] in self._comfort_used

    @staticmethod
    def _jaccard(a: str, b: str) -> float:
        wa = set(a.split())
        wb = set(b.split())
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)
