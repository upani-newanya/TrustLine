"""In-memory session manager for MithuruEngine instances.

Each chat session gets its own engine instance that maintains conversation
state across messages.  Engines are lazily created on the first message
and cached by session_id.

Note: This is an in-memory store — engine state is lost on server restart.
For production, you'd persist conversation state to the database.
"""
from __future__ import annotations

import threading
from typing import Optional

from app.chatbot.engine import MithuruEngine
from app.ml.fake_ml import FakeML
from app.agents.llm_adapter import LLMAdapter

# Stub predictors used when ML models aren't loaded
_DISTRESS_STUB = lambda t: ("non-suicide", 0.0)
_EMOTION_STUB = lambda t: ("neutral", 0.0)


def _make_ml() -> FakeML:
    """Create ML wrapper using real models if available, otherwise stubs."""
    try:
        from app.ml.inference import predict_distress, predict_emotion
        from app.ml.model_loader import suicide_model, emotion_model
        if suicide_model is not None and emotion_model is not None:
            return FakeML(predict_distress, predict_emotion)
    except Exception:
        pass
    return FakeML(_DISTRESS_STUB, _EMOTION_STUB)


class _EngineManager:
    """Thread-safe singleton that maps session_id → MithuruEngine."""

    def __init__(self) -> None:
        self._engines: dict[str, MithuruEngine] = {}
        self._lock = threading.Lock()

    def get_or_create(self, session_id: str) -> MithuruEngine:
        """Return the engine for this session, creating one if needed."""
        with self._lock:
            if session_id not in self._engines:
                ml = _make_ml()
                llm = LLMAdapter()
                self._engines[session_id] = MithuruEngine(ml, llm)
            return self._engines[session_id]

    def remove(self, session_id: str) -> None:
        """Remove a session's engine (e.g. after complaint submission)."""
        with self._lock:
            self._engines.pop(session_id, None)

    def get_state_summary(self, session_id: str) -> Optional[dict]:
        """Return a summary of the engine state for API responses."""
        with self._lock:
            engine = self._engines.get(session_id)
            if not engine:
                return None
            state = engine.state
            return {
                "mode": state.conversation.mode.value,
                "incident_type": state.incident.incident_type,
                "fields_collected": dict(state.complaint.collected_fields),
                "complaint_submitted": state.complaint.complaint_submitted,
                "tracking_id": state.complaint.tracking_id,
            }


engine_manager = _EngineManager()
