"""Session state management for Mithuru chatbot.

Tracks conversation context, emotional signals, incident details,
and complaint intake progress across the entire session.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ChatMode(str, Enum):
    SUPPORT = "support"
    GUIDED_INTAKE = "guided_intake"
    VULNERABLE_SUPPORT = "vulnerable_support"
    HARD_CRISIS = "hard_crisis"
    POST_COMPLAINT = "post_complaint"


class FieldStatus(str, Enum):
    MISSING = "missing"
    PARTIAL = "partial"       # hinted at but not confirmed
    CONFIRMED = "confirmed"   # user provided but not yet validated
    LOCKED = "locked"         # high-confidence answer — never re-ask


@dataclass
class FieldEntry:
    """Tracked field with value, confidence, and lock status."""
    value: str = ""
    confidence: float = 0.0
    status: FieldStatus = FieldStatus.MISSING
    asked_count: int = 0      # how many times we asked this field
    source_turn: int = 0      # turn where value was captured

    @property
    def is_filled(self) -> bool:
        return self.status in (FieldStatus.CONFIRMED, FieldStatus.LOCKED)

    @property
    def is_locked(self) -> bool:
        return self.status == FieldStatus.LOCKED


@dataclass
class ConversationState:
    session_id: str = ""
    mode: ChatMode = ChatMode.SUPPORT
    turn_count: int = 0
    message_history: list[dict] = field(default_factory=list)
    last_user_message: str = ""
    last_bot_message: str = ""
    started_at: str = ""


@dataclass
class EmotionalState:
    dominant_emotion: str = "unknown"
    emotion_confidence: float = 0.0
    distress_label: str = "non-suicide"
    distress_confidence: float = 0.0
    panic_level: float = 0.0          # 0.0 – 1.0
    hopelessness_level: float = 0.0   # 0.0 – 1.0
    shame_fear_present: bool = False
    self_harm_risk: bool = False
    suicide_risk: bool = False
    user_feels_safe: Optional[bool] = None
    user_is_alone: Optional[bool] = None
    trusted_person_nearby: Optional[bool] = None
    crisis_turns: int = 0             # consecutive turns in hard_crisis
    vulnerable_turns: int = 0         # consecutive turns in vulnerable_support
    safety_checks_given: int = 0      # how many times we asked "are you safe?"


@dataclass
class IncidentState:
    incident_type: Optional[str] = None   # IncidentType.value
    incident_subtype: str = ""
    severity: str = "unknown"             # low / medium / high / critical
    urgency: str = "unknown"              # low / medium / high / immediate
    ongoing_threat: Optional[bool] = None
    financial_loss: Optional[bool] = None
    sexual_exploitation: Optional[bool] = None
    account_access_lost: Optional[bool] = None
    evidence_available: Optional[bool] = None
    classified_at_turn: int = 0


@dataclass
class ComplaintState:
    # ── per-field tracking ──
    field_tracker: dict[str, FieldEntry] = field(default_factory=dict)

    # ── legacy flat dict (still used by submission & prompt context) ──
    collected_fields: dict = field(default_factory=dict)
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    fields_asked: set[str] = field(default_factory=set)
    fields_answered: set[str] = field(default_factory=set)
    last_question_asked: str = ""
    last_field_asked: str = ""
    draft_created: bool = False
    complaint_submitted: bool = False
    tracking_id: str = ""

    # ── field tracker helpers ──

    def set_field(
        self,
        key: str,
        value: str,
        confidence: float = 1.0,
        turn: int = 0,
    ) -> None:
        """Store a field value and auto-lock if confidence >= 0.8."""
        status = FieldStatus.LOCKED if confidence >= 0.8 else FieldStatus.CONFIRMED
        entry = self.field_tracker.get(key, FieldEntry())
        # Don't downgrade a locked field
        if entry.is_locked and entry.value:
            return
        entry.value = value
        entry.confidence = confidence
        entry.status = status
        entry.source_turn = turn
        self.field_tracker[key] = entry

        # Sync to flat dict
        self.collected_fields[key] = value
        self.fields_answered.add(key)
        if key in self.missing_fields:
            self.missing_fields.remove(key)

    def is_field_locked(self, key: str) -> bool:
        entry = self.field_tracker.get(key)
        return entry is not None and entry.is_locked

    def is_field_filled(self, key: str) -> bool:
        entry = self.field_tracker.get(key)
        return entry is not None and entry.is_filled

    def get_field_value(self, key: str) -> str:
        entry = self.field_tracker.get(key)
        return entry.value if entry else ""

    def increment_asked(self, key: str) -> None:
        entry = self.field_tracker.setdefault(key, FieldEntry())
        entry.asked_count += 1

    def times_asked(self, key: str) -> int:
        entry = self.field_tracker.get(key)
        return entry.asked_count if entry else 0


@dataclass
class SessionState:
    conversation: ConversationState = field(default_factory=ConversationState)
    emotional: EmotionalState = field(default_factory=EmotionalState)
    incident: IncidentState = field(default_factory=IncidentState)
    complaint: ComplaintState = field(default_factory=ComplaintState)

    @classmethod
    def new(cls) -> SessionState:
        state = cls()
        state.conversation.session_id = uuid.uuid4().hex[:12]
        state.conversation.started_at = datetime.now().isoformat()
        return state

    # ── convenience helpers ──

    def add_user_message(self, message: str) -> None:
        self.conversation.turn_count += 1
        self.conversation.last_user_message = message
        self.conversation.message_history.append({
            "role": "user",
            "content": message,
            "turn": self.conversation.turn_count,
        })

    def add_bot_message(self, message: str) -> None:
        self.conversation.last_bot_message = message
        self.conversation.message_history.append({
            "role": "assistant",
            "content": message,
            "turn": self.conversation.turn_count,
        })

    def recent_history(self, n: int = 8) -> list[dict]:
        return self.conversation.message_history[-n:]

    def completion_ratio(self) -> float:
        total = len(self.complaint.required_fields)
        if total == 0:
            return 0.0
        answered = len(self.complaint.fields_answered & set(self.complaint.required_fields))
        return answered / total
