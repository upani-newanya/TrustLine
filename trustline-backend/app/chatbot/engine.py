"""Mithuru conversation engine.

Orchestrates the full conversation flow with deterministic control:
  ML analysis → state updates → risk assessment → intent override →
  incident classification → field extraction → mode decision →
  question selection → LLM prompting → output filtering → reply.

The LLM is used ONLY for natural-language generation.
All control-flow decisions are rule-based.

Modes:
  SUPPORT            → initial listening, trust-building
  GUIDED_INTAKE      → one complaint question at a time, emotionally gentle
  VULNERABLE_SUPPORT → user is distressed; brief safety check + gentle intake continues
  HARD_CRISIS        → imminent self-harm/suicide; full intake pause
  POST_COMPLAINT     → complaint submitted; emotional support only
"""
from __future__ import annotations

import re
from typing import Optional

from .state import SessionState, ChatMode
from .incidents import (
    IncidentType, get_schema_for_incident, get_required_fields,
    get_field_spec, COMMON_CONTACT_FIELDS, FieldSpec,
)
from .classifier import IncidentClassifier
from .extractor import FieldExtractor
from .question_selector import QuestionSelector
from .repetition_guard import RepetitionGuard
from .prompt_builder import PromptBuilder
from .crisis_handler import CrisisHandler


class MithuruEngine:
    """Main conversation engine for the Mithuru chatbot.

    Args:
        ml_predictor: object with predict_distress(text) and predict_emotion(text)
                      each returning (label: str, confidence: float)
        llm_adapter:  object with generate(prompt, max_tokens, temperature) -> str
    """

    def __init__(self, ml_predictor, llm_adapter):
        self.state = SessionState.new()
        self.ml = ml_predictor
        self.llm = llm_adapter

        self.classifier = IncidentClassifier()
        self.extractor = FieldExtractor()
        self.question_selector = QuestionSelector()
        self.repetition_guard = RepetitionGuard()
        self.prompt_builder = PromptBuilder()
        self.crisis_handler = CrisisHandler()

    # ────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────

    def process_message(self, user_message: str) -> str:
        """Process a single user message and return Mithuru's response.

        Flow: record → greeting check → ML → classify incident (early!) →
              extract fields → risk assessment → mode routing.

        Key design: incident classification happens BEFORE risk assessment
        so that emotional messages describing a cybercrime still trigger
        guided intake instead of getting stuck in emotional support.
        """

        # 1. Record the message
        self.state.add_user_message(user_message)

        # 2a. Farewell detection — give a clean goodbye
        if self._is_farewell(user_message):
            reply = self._farewell_reply()
            self._finalize(reply)
            return reply

        # 2b. Handle first-turn greetings
        if self.state.conversation.turn_count == 1 and self._is_greeting(user_message):
            reply = self._greeting_reply()
            self._finalize(reply)
            return reply

        # 3. ML analysis
        self._run_ml(user_message)

        # 4. Update emotional flags (safety, alone status)
        self.crisis_handler.update_emotional_state(self.state, user_message)

        # 5. Classify incident EARLY (before risk assessment)
        just_classified = False
        if not self.state.incident.incident_type:
            past = [m["content"] for m in self.state.conversation.message_history if m["role"] == "user"]
            itype = self.classifier.classify(
                user_message, past,
                turn_count=self.state.conversation.turn_count,
            )
            # LLM semantic fallback when keywords miss
            if not itype and self.state.conversation.turn_count >= 2:
                itype = self.classifier.llm_classify(
                    user_message, past, llm_adapter=self.llm,
                )
            if itype:
                self._init_incident(itype, user_message)
                just_classified = True

        # 6. Extract fields (runs whenever incident is known)
        if self.state.incident.incident_type:
            locked_keys = {
                k for k in self.state.complaint.field_tracker
                if self.state.complaint.is_field_locked(k)
            }
            extracted = self.extractor.extract_with_confidence(
                user_message,
                self.state.incident.incident_type,
                locked_keys,
            )
            # Direct-answer fallback for last asked field
            last_field = self.state.complaint.last_field_asked
            if (
                last_field
                and not self.state.complaint.is_field_filled(last_field)
                and last_field not in extracted
            ):
                spec = get_field_spec(self.state.incident.incident_type, last_field)
                if spec:
                    if spec.field_type == "boolean":
                        yn = self.extractor.extract_yes_no(user_message)
                        if yn is not None:
                            extracted[last_field] = ("yes" if yn else "no", 0.90)
                    elif spec.field_type in ("text",) and not self._is_emotional_or_question(user_message):
                        # Only use the whole message as the answer if it's
                        # short enough to be a plausible direct answer
                        # (not a long narrative that's really new info).
                        words = user_message.strip().split()
                        max_words = 4 if last_field in ("victim_name", "bank_name", "platform_name") else 25
                        # Don't capture domains/URLs as names
                        looks_like_domain = bool(re.search(
                            r"\b[a-z0-9][-a-z0-9]*\.(com|org|net|lk|io|co|me)\b",
                            user_message, re.IGNORECASE,
                        ))
                        if last_field == "victim_name" and looks_like_domain:
                            pass  # skip — this is a URL, not a name
                        elif len(words) <= max_words:
                            extracted[last_field] = (user_message.strip(), 0.85)

            self._apply_extractions_with_confidence(extracted)
            self._update_incident_flags()

        # 7. Risk-level assessment
        risk = self.crisis_handler.determine_risk_level(self.state)

        # 8. HARD CRISIS takes absolute priority — pause everything
        if risk == "hard_crisis":
            self.state.conversation.mode = ChatMode.HARD_CRISIS
            self.state.emotional.crisis_turns += 1
            return self._handle_hard_crisis()

        # 9. If currently in hard_crisis but risk dropped → check exit
        if self.state.conversation.mode == ChatMode.HARD_CRISIS:
            if self.crisis_handler.can_exit_hard_crisis(self.state):
                self._exit_hard_crisis()
                # Fall through to normal routing below
            else:
                self.state.emotional.crisis_turns += 1
                return self._handle_hard_crisis()

        # 10. Post-complaint check
        if self.state.complaint.complaint_submitted:
            self.state.conversation.mode = ChatMode.POST_COMPLAINT
            return self._handle_post_complaint()

        # 11. INCIDENT CLASSIFIED → GUIDED INTAKE (core behavior change)
        #     Once the incident is clear, ALWAYS go to intake regardless
        #     of emotional state (unless hard_crisis, handled above).
        if self.state.incident.incident_type:
            if self.question_selector.ready_for_submission(self.state):
                return self._handle_submission()

            self.state.conversation.mode = ChatMode.GUIDED_INTAKE

            # First intake turn: action-oriented intro with first question
            if just_classified:
                return self._handle_first_intake(is_vulnerable=(risk == "vulnerable"))

            # Ongoing intake: ask next question (with empathy if distressed)
            return self._handle_guided_intake(empathetic=(risk == "vulnerable"))

        # ── NO INCIDENT CLASSIFIED YET ──

        # 12. Intent override: user asks for help but no incident classified
        if self.crisis_handler.has_help_seeking_intent(user_message):
            self.state.conversation.mode = ChatMode.SUPPORT
            return self._handle_support_with_probe()

        # 13. Vulnerable but no incident → gentle support + probe for incident
        if risk == "vulnerable":
            self.state.conversation.mode = ChatMode.VULNERABLE_SUPPORT
            self.state.emotional.vulnerable_turns += 1
            return self._handle_vulnerable_support()

        # 14. Default: support mode
        self.state.conversation.mode = ChatMode.SUPPORT
        return self._handle_support()

    # ────────────────────────────────────────────
    # Mode handlers
    # ────────────────────────────────────────────

    def _handle_support(self) -> str:
        prompt = self.prompt_builder.build(self.state)
        reply = self._gen(prompt)
        self._finalize(reply)
        return reply

    def _handle_support_with_probe(self) -> str:
        """User wants to take action but incident type isn't classified yet."""
        prompt = self.prompt_builder.build(
            self.state,
            directive=(
                "The user wants to take action or file a complaint. "
                "Acknowledge their desire to act, then ask what specifically happened "
                "so you can help them. Be direct and helpful."
            ),
        )
        reply = self._gen(prompt)
        self._finalize(reply)
        return reply

    def _handle_first_intake(self, is_vulnerable: bool = False) -> str:
        """First response after incident classification — action-oriented intro + first question."""
        nf = self.question_selector.select_next(self.state)
        if nf is None:
            return self._handle_submission()

        prompt = self.prompt_builder.build_first_intake(
            self.state, next_field=nf, is_vulnerable=is_vulnerable,
        )
        reply = self._gen(prompt)

        self.state.complaint.fields_asked.add(nf.key)
        self.state.complaint.last_field_asked = nf.key
        self.state.complaint.last_question_asked = nf.question
        self.state.complaint.increment_asked(nf.key)
        self.repetition_guard.record_question(nf.key)

        self._finalize(reply)
        return reply

    def _handle_guided_intake(self, empathetic: bool = False) -> str:
        nf = self.question_selector.select_next(self.state)
        if nf is None:
            if not self.state.complaint.complaint_submitted:
                return self._handle_submission()
            self.state.conversation.mode = ChatMode.POST_COMPLAINT
            return self._handle_post_complaint()

        prompt = self.prompt_builder.build(
            self.state,
            next_field=nf,
            directive="be_empathetic" if empathetic else "",
        )
        reply = self._gen(prompt)

        self.state.complaint.fields_asked.add(nf.key)
        self.state.complaint.last_field_asked = nf.key
        self.state.complaint.last_question_asked = nf.question
        self.state.complaint.increment_asked(nf.key)
        self.repetition_guard.record_question(nf.key)

        self._finalize(reply)
        return reply

    def _handle_vulnerable_support(self) -> str:
        """Vulnerable mode with no incident classified: support + probe for incident."""
        give_safety_check = (
            self.state.emotional.safety_checks_given == 0
            and not self.repetition_guard.too_many_safety_checks()
        )

        if give_safety_check:
            self.state.emotional.safety_checks_given += 1
            self.repetition_guard.record_safety_check()

        prompt = self.prompt_builder.build(
            self.state,
            directive="give_safety_check" if give_safety_check else "",
        )
        reply = self._gen(prompt)
        self._finalize(reply)
        return reply

    def _handle_hard_crisis(self) -> str:
        # Track safety checks
        if not self.repetition_guard.too_many_safety_checks():
            self.state.emotional.safety_checks_given += 1
            self.repetition_guard.record_safety_check()

        prompt = self.prompt_builder.build(self.state)
        reply = self._gen(prompt, max_tokens=150)
        self._finalize(reply)
        return reply

    def _handle_post_complaint(self) -> str:
        prompt = self.prompt_builder.build(self.state)
        reply = self._gen(prompt)
        self._finalize(reply)
        return reply

    def _handle_submission(self) -> str:
        from app.utils.complaint_handler import create_case, find_duplicate

        record = {
            "user_input": self.state.conversation.last_user_message,
            "incident_type": self.state.incident.incident_type,
            "collected_fields": dict(self.state.complaint.collected_fields),
            "emotional_state": {
                "dominant_emotion": self.state.emotional.dominant_emotion,
                "distress_label": self.state.emotional.distress_label,
                "suicide_risk": self.state.emotional.suicide_risk,
            },
            "metadata": dict(self.state.complaint.collected_fields),
        }

        dup = find_duplicate(record)
        tracking_id = dup if dup else create_case(record)

        self.state.complaint.complaint_submitted = True
        self.state.complaint.tracking_id = tracking_id
        self.state.conversation.mode = ChatMode.POST_COMPLAINT

        name = self.state.complaint.collected_fields.get("victim_name", "")
        greeting = f" {name}" if name else ""

        reply = (
            f"Your complaint has been submitted successfully{greeting}. "
            f"Your trackable ID is: {tracking_id}. "
            f"One of our team members will contact you soon. "
            f"Please don't panic \u2014 we are here with you. "
            f"Do you want to share anything else with me, or would you like to talk a little more?"
        )
        self._finalize(reply)
        return reply

    # ────────────────────────────────────────────
    # ML
    # ────────────────────────────────────────────

    def _run_ml(self, message: str) -> None:
        d_label, d_conf = self.ml.predict_distress(message)
        e_label, e_conf = self.ml.predict_emotion(message)

        e_st = self.state.emotional
        e_st.distress_label = d_label
        e_st.distress_confidence = d_conf
        e_st.dominant_emotion = e_label
        e_st.emotion_confidence = e_conf

        low = message.lower()
        # suicide_risk: only for EXPLICIT suicidal language or very high model confidence
        e_st.suicide_risk = (
            (d_label.lower() in ("suicide",) and d_conf > 0.85)
            or any(kw in low for kw in ("suicide", "kill myself", "end my life", "want to die"))
        )
        # self_harm_risk: explicit self-harm language
        e_st.self_harm_risk = (
            e_st.suicide_risk
            or any(kw in low for kw in ("hurt myself", "self harm", "self-harm", "cut myself"))
        )

        if e_label.lower() == "fear":
            e_st.panic_level = max(e_st.panic_level, e_conf)
            e_st.shame_fear_present = True
        elif e_label.lower() == "sadness":
            e_st.hopelessness_level = max(e_st.hopelessness_level, e_conf * 0.6)
        if any(kw in low for kw in ("ashamed", "shame", "embarrass", "humiliat")):
            e_st.shame_fear_present = True

    # ────────────────────────────────────────────
    # Incident & field helpers
    # ────────────────────────────────────────────

    def _init_incident(self, incident_type: str, triggering_message: str = "") -> None:
        self.state.incident.incident_type = incident_type
        self.state.incident.classified_at_turn = self.state.conversation.turn_count

        schema = get_schema_for_incident(incident_type)
        all_fields = list(schema) + list(COMMON_CONTACT_FIELDS)
        self.state.complaint.required_fields = [f.key for f in all_fields if f.required]
        self.state.complaint.optional_fields = [f.key for f in all_fields if not f.required]
        self.state.complaint.missing_fields = list(self.state.complaint.required_fields)

        # Auto-capture the triggering message as incident description
        if triggering_message.strip():
            self.state.complaint.set_field(
                "incident_description",
                triggering_message.strip(),
                confidence=1.0,
                turn=self.state.conversation.turn_count,
            )

        if incident_type in (
            IncidentType.PHOTO_LEAK.value,
            IncidentType.PORN_SITE_UPLOAD.value,
            IncidentType.SEXTORTION.value,
        ):
            self.state.incident.sexual_exploitation = True
        if incident_type == IncidentType.BANK_FRAUD.value:
            self.state.incident.financial_loss = True
        if incident_type in (
            IncidentType.ACCOUNT_HACK.value,
            IncidentType.SOCIAL_MEDIA_HACK.value,
        ):
            self.state.incident.account_access_lost = True

    def _apply_extractions(self, extracted: dict[str, str]) -> None:
        for key, value in extracted.items():
            self.state.complaint.set_field(
                key, value,
                confidence=0.85,
                turn=self.state.conversation.turn_count,
            )

    def _apply_extractions_with_confidence(
        self, extracted: dict[str, tuple[str, float]],
    ) -> None:
        """Apply extracted fields with confidence-based locking."""
        for key, (value, confidence) in extracted.items():
            self.state.complaint.set_field(
                key, value,
                confidence=confidence,
                turn=self.state.conversation.turn_count,
            )

    def _update_incident_flags(self) -> None:
        f = self.state.complaint.collected_fields
        if any(
            f.get(k) == "yes"
            for k in ("content_still_live", "threats_ongoing",
                       "unauthorized_transactions_ongoing", "harassment_ongoing")
        ):
            self.state.incident.ongoing_threat = True
            self.state.incident.urgency = "immediate"
        if any(f.get(k) == "yes" for k in ("screenshots_available", "evidence_available")):
            self.state.incident.evidence_available = True
        if any(f.get(k) == "yes" for k in ("blackmail_present", "threats_present")):
            self.state.incident.ongoing_threat = True

    def _exit_hard_crisis(self) -> None:
        """Transition out of hard_crisis to the best available mode."""
        if self.state.complaint.complaint_submitted:
            self.state.conversation.mode = ChatMode.POST_COMPLAINT
        elif self.state.incident.incident_type:
            self.state.conversation.mode = ChatMode.GUIDED_INTAKE
        else:
            self.state.conversation.mode = ChatMode.SUPPORT
        self.state.emotional.crisis_turns = 0

    def _exit_vulnerable(self) -> None:
        """Transition out of vulnerable_support to guided_intake or support."""
        if self.state.complaint.complaint_submitted:
            self.state.conversation.mode = ChatMode.POST_COMPLAINT
        elif self.state.incident.incident_type:
            self.state.conversation.mode = ChatMode.GUIDED_INTAKE
        else:
            self.state.conversation.mode = ChatMode.SUPPORT
        self.state.emotional.vulnerable_turns = 0

    @staticmethod
    def _is_emotional_or_question(message: str) -> bool:
        """Check if a message is emotional/question rather than a direct field answer."""
        low = message.strip().lower()
        if "?" in message:
            return True
        markers = (
            "i feel", "i'm scared", "im scared", "help me", "what should",
            "how can", "want to die", "kill myself", "i'm so", "im so",
            "i cant", "i can't", "i don't know", "i dont know",
            "i'm afraid", "im afraid", "please help",
        )
        return any(kw in low for kw in markers)

    # ────────────────────────────────────────────
    # LLM generation + cleaning
    # ────────────────────────────────────────────

    def _gen(self, prompt: str, max_tokens: int = 256) -> str:
        try:
            raw = self.llm.generate(prompt, max_tokens=max_tokens, temperature=0.3)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).error("LLM generation failed: %s", exc, exc_info=True)
            print(f"[ERROR] LLM call failed: {exc}")
            raw = "I'm here with you. Take your time — there's no rush."
        return self._clean(raw)

    @staticmethod
    def _clean(text: str) -> str:
        # Strip JSON blocks
        text = re.sub(r"```json[\s\S]*?```", "", text)
        text = re.sub(r"\{[\s\S]*?\}", "", text)
        # Strip system-instruction leakage
        lines = text.splitlines()
        out: list[str] = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            low = s.lower()
            if low.startswith(("step ", "rule ", "note:", "task:", "current task:", "tone rules:", "crisis mode")):
                continue
            if low.startswith("- ") and any(kw in low for kw in ("never", "always", "do not", "must", "should")):
                continue
            if "mithuru:" in low[:12]:
                s = s[s.index(":") + 1:].strip()
            out.append(s)
        result = " ".join(out).strip()
        return result or "I'm here with you. Take your time."

    @staticmethod
    def _sanitize_hotlines(text: str) -> str:
        bad = [
            "national suicide prevention", "1-800-273-talk", "741741",
            "crisis text line", "national domestic violence hotline",
            "1-800-799-7233", "national center for victims",
        ]
        for phrase in bad:
            if phrase in text.lower():
                text = re.sub(re.escape(phrase), "TrustLine support", text, flags=re.IGNORECASE)
        return text

    # ────────────────────────────────────────────
    # Misc
    # ────────────────────────────────────────────

    @staticmethod
    def _is_farewell(text: str) -> bool:
        low = text.strip().lower().rstrip(".,!?")
        # Exact matches
        farewells = {
            "bye", "goodbye", "good bye", "good night", "gn",
            "see you", "see ya", "take care", "thanks bye",
            "thank you bye", "ok bye", "oky bye", "okay bye",
            "ok bay", "oky bay", "okay bay",
            "ok buy", "oky buy", "okay buy",
            "bay", "buy",  # common typos for bye
        }
        if low in farewells:
            return True
        # Short messages (≤6 words) containing farewell signals
        if len(low.split()) <= 6:
            farewell_phrases = (
                "going to go", "going to sleep", "going to seleep",
                "gotta go", "have to go", "need to go",
                "talk later", "catch you later", "im going",
                "i'm going", "i am going", "heading off",
                "signing off", "logging off",
            )
            if any(fp in low for fp in farewell_phrases):
                return True
            if low.startswith(("bye", "bay", "buy")) and len(low.split()) <= 3:
                return True
        return False

    def _farewell_reply(self) -> str:
        name = self.state.complaint.collected_fields.get("victim_name", "")
        first_name = name.split()[0] if name else ""
        greeting = f", {first_name}" if first_name else ""
        tid = self.state.complaint.tracking_id
        if tid:
            return (
                f"Okay{greeting}. Stay safe and take care of yourself. "
                f"Your tracking ID is {tid} — reach out anytime if you need us. Goodbye!"
            )
        return f"Okay{greeting}. Stay safe and take care of yourself. Reach out anytime if you need us. Goodbye!"

    @staticmethod
    def _is_greeting(text: str) -> bool:
        low = text.strip().lower().rstrip(".,!?")
        greetings = {
            "hi", "hello", "hey", "good morning", "good evening",
            "good afternoon", "help", "help me", "anyone there",
        }
        # Exact match only for very short messages (pure greetings).
        # Long messages that happen to start with "hi" are NOT greetings.
        if low in greetings:
            return True
        if len(low.split()) <= 3 and any(low.startswith(g) for g in greetings):
            return True
        return False

    @staticmethod
    def _greeting_reply() -> str:
        return (
            "Hi, I'm Mithuru from TrustLine. I'm here with you. "
            "Tell me what happened, and we'll take it step by step together."
        )

    def _finalize(self, reply: str) -> None:
        reply = self._sanitize_hotlines(reply)
        self.state.add_bot_message(reply)
        self.repetition_guard.record_reply(reply)
