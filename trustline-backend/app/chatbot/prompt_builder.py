"""Dynamic LLM prompt builder for Mithuru.

Constructs mode-aware, state-aware prompts that give the LLM enough context
to generate natural, empathetic responses while the system controls the flow.

Modes: SUPPORT, GUIDED_INTAKE, VULNERABLE_SUPPORT, HARD_CRISIS, POST_COMPLAINT
"""
from __future__ import annotations

from .state import SessionState, ChatMode, FieldStatus
from .incidents import FieldSpec

_PERSONA = (
    "You are Mithuru, a warm, caring, and deeply empathetic cybercrime victim support "
    "companion for TrustLine Sri Lanka. You speak like a trusted friend — calm, gentle, "
    "and reassuring. You are NOT a generic chatbot. You are a safe presence for people "
    "going through frightening and humiliating experiences online. You never judge. "
    "You never rush. You never sound robotic."
)

_TONE_RULES = (
    "TONE RULES:\n"
    "- Speak naturally, like a caring friend. Not formal. Not clinical.\n"
    "- Keep responses concise — 2 to 4 sentences maximum.\n"
    "- NEVER ask more than one question at a time.\n"
    "- NEVER repeat something you already said in this conversation.\n"
    "- NEVER mention external hotlines or crisis lines. Only refer to TrustLine (1898) or Mithuru.\n"
    "- If the user already gave information, acknowledge it — do NOT re-ask.\n"
    "- Use the user's name if you know it.\n"
    "- Reflect the user's emotion naturally.\n"
    "- Do NOT use emojis."
)


class PromptBuilder:
    """Builds structured LLM prompts based on session state and current mode."""

    def build(
        self,
        state: SessionState,
        next_field: FieldSpec | None = None,
        directive: str = "",
    ) -> str:
        mode = state.conversation.mode
        if mode == ChatMode.HARD_CRISIS:
            return self._build_hard_crisis(state)
        if mode == ChatMode.VULNERABLE_SUPPORT:
            return self._build_vulnerable_support(state, directive)
        if mode == ChatMode.GUIDED_INTAKE:
            return self._build_guided_intake(state, next_field, directive)
        if mode == ChatMode.POST_COMPLAINT:
            return self._build_post_complaint(state)
        return self._build_support(state, directive)

    def build_first_intake(
        self,
        state: SessionState,
        next_field: FieldSpec,
        is_vulnerable: bool = False,
    ) -> str:
        """Special prompt for the first response after incident classification.

        Combines: ONE line emotional validation → action declaration → first question.
        """
        incident_label = self._incident_label(state.incident.incident_type)

        if is_vulnerable:
            empathy_note = (
                "Start with ONE brief sentence of genuine emotional validation — "
                "acknowledge their pain. "
            )
        else:
            empathy_note = (
                "Start with ONE brief sentence of empathy — acknowledge the situation. "
            )

        task = (
            f"CURRENT TASK: The user has just described a {incident_label} case. "
            f"{empathy_note}"
            f"Then tell them clearly that you can help them file a complaint right now. "
            f"Then ask the FIRST complaint question: \"{next_field.question}\" "
            f"\n\nExample structure:\n"
            f"\"I'm really sorry this happened to you. I can help you file this complaint now. "
            f"Let's do it step by step. {next_field.question}\"\n\n"
            f"Keep it to 3-4 sentences TOTAL. Be warm but ACTION-ORIENTED. "
            f"Do NOT spend more than one sentence on emotions. "
            f"Do NOT say 'tell me more about how you feel'. "
            f"Do NOT ask multiple questions — ONLY ask about '{next_field.label}'. "
            f"Make it clear you're here to HELP them take action."
        )

        return "\n\n".join([
            _PERSONA,
            _TONE_RULES,
            self._context_block(state),
            self._history_block(state),
            task,
            f'User\'s latest message: "{state.conversation.last_user_message}"',
            "Respond as Mithuru. 3-4 sentences. Empathy → action → question.",
        ])

    # ── mode-specific builders ──

    def _build_support(self, state: SessionState, directive: str = "") -> str:
        if directive:
            task = f"CURRENT TASK: {directive}"
        else:
            task = (
                "CURRENT TASK: The user is reaching out for help. "
                "Listen to what they're saying. If they describe a cybercrime incident "
                "(hacking, scam, photo leak, blackmail, harassment, etc.), "
                "acknowledge their situation briefly and ask ONE clarifying question "
                "to understand what happened. "
                "Do NOT spend many sentences on sympathy alone. "
                "Do NOT say 'tell me more about how you felt'. "
                "If the incident is clear, let them know you can help them take action. "
                "Be warm but focused — you are a helper, not just a listener."
            )

        return "\n\n".join([
            _PERSONA,
            _TONE_RULES,
            self._context_block(state),
            self._history_block(state),
            task,
            f'User\'s latest message: "{state.conversation.last_user_message}"',
            "Respond as Mithuru. 2-3 sentences.",
        ])

    def _build_guided_intake(
        self,
        state: SessionState,
        next_field: FieldSpec | None,
        directive: str,
    ) -> str:
        locked_block = self._locked_fields_block(state)
        progress = self._progress_note(state)

        if next_field:
            if directive == "be_empathetic":
                task = (
                    f"CURRENT TASK: The user may be emotional. "
                    f"Give ONE brief reassuring sentence (e.g., 'I know this is hard, but we're making "
                    f"progress together.'), then ask about '{next_field.label}': "
                    f'"{next_field.question}" '
                    f"Do NOT ask reflective or therapy-style questions. "
                    f"Do NOT re-ask about any field listed in ALREADY COLLECTED below. "
                    f"Keep progressing. Ask only ONE question."
                )
            else:
                task = (
                    f"CURRENT TASK: You are collecting complaint details step by step. "
                    f"Briefly acknowledge what the user just shared (if relevant), "
                    f"then ask about '{next_field.label}': "
                    f'"{next_field.question}" '
                    f"\n\nExample response shape:\n"
                    f'"I\'ve noted that. [next question]"\n'
                    f"or: \"Thanks, [name]. [next question]\"\n\n"
                    f"Keep it to 1-2 sentences TOTAL. Ask only ONE question. "
                    f"Do NOT repeat sympathy given in earlier turns. "
                    f"Do NOT ask about any field listed in ALREADY COLLECTED below. "
                    f"Do NOT ask therapy-style questions like 'how did that make you feel?'. "
                    f"Do NOT over-clarify approximate answers (accept 'yesterday evening', "
                    f"'around 9 pm', 'last night' as good enough). "
                    f"Be direct, helpful, and human."
                )
        elif directive and directive != "be_empathetic":
            task = f"CURRENT TASK: {directive}"
        else:
            task = (
                "CURRENT TASK: You have collected the main complaint details. "
                "Ask if they want to add anything else before you submit."
            )

        return "\n\n".join([
            _PERSONA,
            _TONE_RULES,
            self._context_block(state),
            locked_block,
            progress,
            self._history_block(state),
            task,
            f'User\'s latest message: "{state.conversation.last_user_message}"',
            "Respond as Mithuru. 1-2 sentences. Acknowledge + ONE question.",
        ])

    def _build_vulnerable_support(
        self,
        state: SessionState,
        directive: str,
    ) -> str:
        """The user is distressed and we don't know the incident yet.
        Be gentle, but try to understand what happened so we can help."""

        if directive == "give_safety_check":
            task = (
                "CURRENT TASK: The user is emotionally vulnerable right now. "
                "Start with a brief, genuine acknowledgment — let them know you're here "
                "and they don't have to face this alone. "
                "Then gently ask what happened to them so you can help. "
                "Do NOT repeat 'are you safe right now?' if it was already asked. "
                "Do NOT ask multiple questions. "
                "Keep the tone warm but try to understand the situation."
            )
        else:
            task = (
                "CURRENT TASK: The user is going through a tough time. "
                "Give brief emotional validation, then gently ask them to tell you "
                "what happened so you can help them take action. "
                "Be warm but also move toward understanding the specific incident. "
                "Do NOT just say 'I'm here for you' without asking what happened. "
                "One question only."
            )

        return "\n\n".join([
            _PERSONA,
            _TONE_RULES,
            self._context_block(state),
            self._history_block(state),
            task,
            f'User\'s latest message: "{state.conversation.last_user_message}"',
            "Respond as Mithuru. 2-3 sentences. Warm but not stuck.",
        ])

    def _build_hard_crisis(self, state: SessionState) -> str:
        safety = []
        if state.emotional.user_feels_safe is not None:
            safety.append(f"User feels safe: {'yes' if state.emotional.user_feels_safe else 'no'}")
        if state.emotional.user_is_alone is not None:
            safety.append(f"User is alone: {'yes' if state.emotional.user_is_alone else 'no'}")
        safety_block = "\n".join(safety) if safety else "Safety status: unknown"

        # Vary the crisis prompt based on how many safety checks already given
        checks = state.emotional.safety_checks_given
        if checks == 0:
            crisis_task = (
                "Ask gently if they are safe right now. "
                "Keep it brief and caring."
            )
        elif checks == 1:
            crisis_task = (
                "The user has been asked if they're safe. "
                "Now ask if there is anyone with them or someone they trust nearby. "
                "Do NOT re-ask 'are you safe right now?'"
            )
        else:
            crisis_task = (
                "You have already asked safety questions. Do NOT repeat them. "
                "Now be present. Speak gently. Offer grounding — remind them you're here. "
                "You may mention that TrustLine (1898) support team is available. "
                "Do NOT loop on the same safety questions."
            )

        return "\n\n".join([
            _PERSONA,
            (
                "HARD CRISIS MODE — READ CAREFULLY:\n"
                "The user is in severe emotional distress with signs of self-harm risk.\n"
                "PAUSE all complaint collection. Your ONLY goal is to keep them safe.\n"
                "- Speak very gently and briefly.\n"
                "- Do NOT dump hotline numbers mechanically.\n"
                "- Be present. Be warm. Be human.\n"
                "- Keep responses SHORT — 1 to 3 sentences.\n"
                f"- {crisis_task}"
            ),
            safety_block,
            self._history_block(state, n=4),
            f'User\'s latest message: "{state.conversation.last_user_message}"',
            "Respond as Mithuru in crisis mode. 1-3 sentences. Do NOT repeat previous messages.",
        ])

    def _build_post_complaint(self, state: SessionState) -> str:
        tracking = state.complaint.tracking_id or "pending"
        return "\n\n".join([
            _PERSONA,
            _TONE_RULES,
            self._context_block(state),
            self._history_block(state),
            (
                f"POST-COMPLAINT MODE:\n"
                f"The complaint has been submitted (tracking ID: {tracking}).\n"
                "There is nothing more to collect. Stay with the user. Be emotionally present.\n"
                "If they want to talk, listen. If they want advice, give gentle guidance.\n"
                "Do NOT repeat the tracking ID. Do NOT re-ask complaint questions.\n"
                "Just be a supportive friend."
            ),
            f'User\'s latest message: "{state.conversation.last_user_message}"',
            "Respond as Mithuru. 2-4 sentences.",
        ])

    # ── helpers ──

    def _context_block(self, state: SessionState) -> str:
        parts = []
        e = state.emotional
        parts.append(f"User emotion: {e.dominant_emotion} ({e.emotion_confidence:.0%})")
        if e.distress_label != "non-suicide":
            parts.append(f"Distress signal: {e.distress_label} ({e.distress_confidence:.0%})")
        if e.suicide_risk:
            parts.append("WARNING: Suicide/self-harm risk detected.")
        if state.incident.incident_type:
            parts.append(f"Incident type: {state.incident.incident_type}")

        # Show locked (confirmed) vs remaining fields explicitly
        tracker = state.complaint.field_tracker
        locked = {
            k: entry.value
            for k, entry in tracker.items()
            if entry.is_locked
        }
        partial = {
            k: entry.value
            for k, entry in tracker.items()
            if entry.is_filled and not entry.is_locked
        }
        if locked:
            items = ", ".join(f"{k}={v}" for k, v in locked.items())
            parts.append(f"ALREADY COLLECTED (do NOT re-ask): {items}")
        if partial:
            items = ", ".join(f"{k}={v}" for k, v in partial.items())
            parts.append(f"Partially collected (may need confirmation): {items}")

        # Fallback: show raw collected_fields for any not in tracker
        tracked_keys = set(tracker.keys())
        extra = {
            k: v
            for k, v in state.complaint.collected_fields.items()
            if k not in tracked_keys
        }
        if extra:
            items = ", ".join(f"{k}={v}" for k, v in extra.items())
            parts.append(f"Also collected: {items}")

        name = (
            locked.get("victim_name")
            or state.complaint.collected_fields.get("victim_name", "")
        )
        if name:
            parts.append(f"User's name: {name}")
        return "CONTEXT:\n" + "\n".join(parts)

    def _locked_fields_block(self, state: SessionState) -> str:
        """Explicit list of locked fields the LLM must never re-ask."""
        tracker = state.complaint.field_tracker
        locked = [
            f"- {k}: {entry.value}"
            for k, entry in tracker.items()
            if entry.is_locked
        ]
        if not locked:
            return ""
        header = "LOCKED FIELDS — these are confirmed. Do NOT ask about them again:"
        return header + "\n" + "\n".join(locked)

    def _progress_note(self, state: SessionState) -> str:
        """Short progress indicator so the LLM knows how far along we are."""
        tracker = state.complaint.field_tracker
        filled = sum(1 for e in tracker.values() if e.is_filled)
        total = len(state.complaint.collected_fields) + len(tracker)
        # Deduplicate: only count unique keys
        all_keys = set(state.complaint.collected_fields.keys()) | set(tracker.keys())
        filled_keys = {k for k, e in tracker.items() if e.is_filled} | set(
            state.complaint.collected_fields.keys()
        )
        if not all_keys:
            return ""
        return f"PROGRESS: {len(filled_keys)} of {len(all_keys)} fields collected so far."

    def _history_block(self, state: SessionState, n: int = 6) -> str:
        history = state.recent_history(n)
        if not history:
            return ""
        lines = ["RECENT CONVERSATION:"]
        for turn in history:
            role = "User" if turn["role"] == "user" else "Mithuru"
            lines.append(f"{role}: {turn['content']}")
        return "\n".join(lines)

    @staticmethod
    def _incident_label(incident_type: str | None) -> str:
        labels = {
            "bank_fraud": "bank fraud / financial cybercrime",
            "photo_leak": "private photo leak",
            "sextortion": "sextortion",
            "porn_site_upload": "content uploaded to an adult site",
            "account_hack": "account hack",
            "social_media_hack": "social media hack",
            "impersonation": "impersonation / fake account",
            "cyberbullying": "cyberbullying",
            "harassment": "online harassment",
            "scam": "online scam",
            "blackmail": "blackmail / extortion",
            "general_cybercrime": "cybercrime",
        }
        return labels.get(incident_type or "", "cybercrime")
