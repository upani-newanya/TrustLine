"""Next-best-question selector for Mithuru complaint intake.

Picks the most appropriate next question based on field priority,
field lock status, and what has already been collected.

Rules:
  - LOCKED fields are NEVER re-asked
  - CONFIRMED fields are not re-asked unless specifically unresolved
  - MISSING required fields get priority, sorted by FieldPriority
  - A field asked 2+ times without answer is deprioritized
  - Contact fields (name, phone) use FIRST priority, merged into main flow
"""
from __future__ import annotations

from typing import Optional

from .state import SessionState, ChatMode
from .incidents import (
    get_schema_for_incident, COMMON_CONTACT_FIELDS,
    FieldSpec, FieldPriority,
)

_MAX_ASK_ATTEMPTS = 2  # stop re-asking after 2 unanswered attempts


class QuestionSelector:
    """Selects the next field to ask about during complaint intake."""

    def select_next(self, state: SessionState) -> Optional[FieldSpec]:
        """Return the next FieldSpec to ask about, or None if done.

        Skips locked/confirmed fields. Deprioritizes fields asked
        multiple times without an answer.
        """
        if not state.incident.incident_type:
            return None

        schema = get_schema_for_incident(state.incident.incident_type)
        all_fields = list(COMMON_CONTACT_FIELDS) + list(schema)

        # Build skip set: any field that is already filled or locked
        skip = set()
        for f in all_fields:
            if state.complaint.is_field_filled(f.key):
                skip.add(f.key)
            elif f.key in state.complaint.collected_fields:
                # In flat dict but maybe not tracked — still skip
                skip.add(f.key)

        # Phase 1 — required fields not yet filled, sorted by priority
        candidates = [
            f for f in all_fields
            if f.key not in skip
            and f.required
        ]
        candidates.sort(key=lambda f: f.priority.value)

        pick = self._pick_unexhausted(candidates, state)
        if pick:
            return pick

        # Phase 2 — optional fields ≤ MEDIUM priority, not yet asked
        optional = [
            f for f in all_fields
            if f.key not in skip
            and not f.required
            and f.priority.value <= FieldPriority.MEDIUM.value
            and state.complaint.times_asked(f.key) == 0
        ]
        optional.sort(key=lambda f: f.priority.value)
        if optional:
            return optional[0]

        return None  # all fields collected or exhausted

    def should_pause_for_emotion(self, state: SessionState) -> bool:
        """True only for HARD crisis — imminent self-harm/suicide risk."""
        e = state.emotional
        return e.suicide_risk or e.self_harm_risk

    def ready_for_submission(self, state: SessionState) -> bool:
        """True if all required fields are collected (incident + contact)."""
        if not state.incident.incident_type:
            return False
        schema = get_schema_for_incident(state.incident.incident_type)
        all_fields = list(schema) + list(COMMON_CONTACT_FIELDS)
        required_keys = {f.key for f in all_fields if f.required}
        collected_keys = set(state.complaint.collected_fields.keys())
        return required_keys.issubset(collected_keys)

    # ── internal ──

    @staticmethod
    def _pick_unexhausted(
        candidates: list[FieldSpec], state: SessionState,
    ) -> Optional[FieldSpec]:
        """Pick the best candidate that hasn't been asked too many times."""
        if not candidates:
            return None

        # Prefer fields not yet asked at all
        fresh = [f for f in candidates if state.complaint.times_asked(f.key) == 0]
        if fresh:
            return fresh[0]

        # Then fields asked < MAX attempts
        retryable = [
            f for f in candidates
            if state.complaint.times_asked(f.key) < _MAX_ASK_ATTEMPTS
        ]
        if retryable:
            return retryable[0]

        # All required fields have been asked MAX times — skip to optionals
        return None
