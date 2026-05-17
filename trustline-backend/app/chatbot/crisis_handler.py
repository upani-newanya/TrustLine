"""Crisis detection and handling for Mithuru.

Splits risk into two tiers:
  - hard_crisis   → imminent self-harm / suicide danger (full intake pause)
  - vulnerable    → distressed, lonely, ashamed, panicked (gentle support + intake continues)
  - none          → no elevated risk

Also detects help-seeking intent that should override emotional holds.
"""
from __future__ import annotations

from .state import SessionState, ChatMode

# ── Hard crisis: explicit suicidal / self-harm intent ──
_HARD_CRISIS_KEYWORDS = frozenset([
    "want to die", "kill myself", "end my life", "end it all",
    "no reason to live", "better off dead", "want to hurt myself",
    "self harm", "self-harm", "cut myself", "jump off",
    "don't want to live", "i want out of life",
    "im done with life", "want everything to end",
    "i want to end it", "i can't go on living",
])

# ── Vulnerable: distressed but NOT actively suicidal ──
_VULNERABLE_KEYWORDS = frozenset([
    "i feel lonely", "i have no one", "nobody to talk",
    "no one to talk", "don't know what to do", "dont know what to do",
    "i feel helpless", "feel helpless",
    "i'm scared", "im scared", "i'm ashamed", "im ashamed",
    "i'm panicking", "im panicking", "i feel hopeless",
    "i can't do this", "i feel alone", "nobody cares",
    "i don't have anyone", "i dont have anyone",
    "i don't have any one", "i dont have any one",
    "no friends", "all alone", "have no one",
    "overwhelmed", "can't handle this", "cant handle this",
    "can't cope", "cant cope",
    "can't take this", "cant take this",
    "i give up", "nothing matters",
    "i'm done", "im done", "there's no point",
    "no one to help", "nobody to help",
    "any one to talk", "anyone to talk",
])

# ── Help-seeking intent: user wants action, not just comfort ──
_HELP_SEEKING_KEYWORDS = frozenset([
    "how can i", "how do i", "what should i do",
    "can you help", "help me report", "help me complain",
    "take action", "get action", "file a complaint",
    "file my complaint", "make a complaint", "lodge a complaint",
    "report this", "what can i do", "what are my options",
    "how to stop this", "how to remove", "how to get it taken down",
    "i want to report", "i want to complain", "i need to act",
    "i want to take action", "want to report", "want to complain",
    "help me file", "i want to file",
    "next step", "what now", "what do i do now",
    "can something be done", "is there anything i can do",
])

_CRISIS_EXIT_KEYWORDS = frozenset([
    "feeling better", "feeling calmer", "calmer now", "bit calmer",
    "bit better", "little better", "not as bad",
    "i'm okay", "im okay", "i'm fine", "im fine",
    "i feel safe", "yes i'm safe", "yes im safe",
    "i'm with someone", "not alone", "my friend is here",
    "thank you", "thanks for listening", "i feel calmer",
    "i feel better", "i'll be okay", "ill be okay",
])


class CrisisHandler:
    """Detects risk level and manages mode transitions."""

    # ── Risk classification ──

    def determine_risk_level(self, state: SessionState) -> str:
        """Return 'hard_crisis', 'vulnerable', or 'none'."""
        low = (state.conversation.last_user_message or "").lower()

        # 1) Help-seeking intent overrides vulnerable (but NOT hard crisis)
        if self._has_help_seeking_intent(low):
            # Only stay in hard crisis if there's still real suicide risk
            if self._has_hard_crisis_signal(state, low):
                return "hard_crisis"
            return "none"  # let engine route to guided_intake

        # 2) Check for hard crisis signals
        if self._has_hard_crisis_signal(state, low):
            return "hard_crisis"

        # 3) Check for vulnerable signals
        if self._has_vulnerable_signal(state, low):
            return "vulnerable"

        return "none"

    def _has_hard_crisis_signal(self, state: SessionState, low: str) -> bool:
        """True only for imminent self-harm / suicide indicators."""
        # Explicit hard-crisis keywords
        for kw in _HARD_CRISIS_KEYWORDS:
            if kw in low:
                return True
        # ML: distress model flags suicide/self-harm with HIGH confidence
        if (
            state.emotional.distress_label.lower() in ("suicide", "self-harm")
            and state.emotional.distress_confidence > 0.85
        ):
            return True
        # Explicit suicide phrasing even with lower ML confidence
        if state.emotional.suicide_risk and any(
            kw in low for kw in ("die", "kill", "suicide", "end my life", "hurt myself")
        ):
            return True
        return False

    def _has_vulnerable_signal(self, state: SessionState, low: str) -> bool:
        """True for emotional distress that is NOT imminent self-harm."""
        for kw in _VULNERABLE_KEYWORDS:
            if kw in low:
                return True
        e = state.emotional
        if e.panic_level > 0.75:
            return True
        if e.hopelessness_level > 0.8:
            return True
        if e.shame_fear_present and e.emotion_confidence >= 0.7:
            return True
        return False

    # ── Intent detection ──

    @staticmethod
    def has_help_seeking_intent(message: str) -> bool:
        """Public API: True if the user is asking for action/help/reporting."""
        low = message.lower()
        return CrisisHandler._has_help_seeking_intent(low)

    @staticmethod
    def _has_help_seeking_intent(low: str) -> bool:
        for kw in _HELP_SEEKING_KEYWORDS:
            if kw in low:
                return True
        return False

    # ── Exit conditions ──

    def can_exit_hard_crisis(self, state: SessionState) -> bool:
        """True if safe to leave hard_crisis mode."""
        low = (state.conversation.last_user_message or "").lower()

        # Still has hard crisis keywords → stay
        for kw in _HARD_CRISIS_KEYWORDS:
            if kw in low:
                return False

        # Explicit exit signals
        for kw in _CRISIS_EXIT_KEYWORDS:
            if kw in low:
                return True
        if state.emotional.user_feels_safe is True:
            return True
        # After 2+ crisis turns with lowered distress confidence
        if state.emotional.crisis_turns >= 2 and state.emotional.distress_confidence < 0.5:
            return True
        # Help-seeking intent overrides after at least 1 safety check
        if self._has_help_seeking_intent(low) and state.emotional.safety_checks_given >= 1:
            return True
        return False

    def can_exit_vulnerable(self, state: SessionState) -> bool:
        """True if safe to transition from vulnerable_support to guided_intake."""
        low = (state.conversation.last_user_message or "").lower()

        # Help-seeking intent → always exit vulnerable
        if self._has_help_seeking_intent(low):
            return True
        # User answered safety check
        if state.emotional.user_feels_safe is not None and state.emotional.safety_checks_given >= 1:
            return True
        # User is giving incident details (has new field data)
        if state.emotional.vulnerable_turns >= 1 and len(state.complaint.collected_fields) > 0:
            return True
        # After 2 vulnerable turns, auto-transition to gentle intake
        if state.emotional.vulnerable_turns >= 2:
            return True
        return False

    # ── State updates ──

    def update_emotional_state(self, state: SessionState, message: str) -> None:
        """Update emotional flags from message content."""
        low = message.lower()

        # Safety responses
        if any(w in low for w in ("i'm safe", "im safe", "i feel safe", "yes safe", "feeling safe")):
            state.emotional.user_feels_safe = True
        elif any(w in low for w in ("not safe", "unsafe", "don't feel safe")):
            state.emotional.user_feels_safe = False

        # Alone status
        if any(w in low for w in ("alone", "by myself", "no one", "nobody", "i'm alone", "im alone")):
            state.emotional.user_is_alone = True
        elif any(w in low for w in (
            "someone is with me", "friend is here", "family is here",
            "not alone", "my mom", "my dad", "my sister", "my brother",
        )):
            state.emotional.user_is_alone = False
            state.emotional.trusted_person_nearby = True

        # Track consecutive turns per mode
        if state.conversation.mode == ChatMode.HARD_CRISIS:
            state.emotional.crisis_turns += 1
        elif state.conversation.mode == ChatMode.VULNERABLE_SUPPORT:
            state.emotional.vulnerable_turns += 1
