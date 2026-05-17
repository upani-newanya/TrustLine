"""Integration test: verify action-oriented complaint flow.

Tests:
1. Bank fraud → immediate intake with name as first question
2. Photo leak → immediate intake
3. Emotional message without incident → stays in support, probes
4. Hard crisis → pauses intake
5. Field collection progresses correctly
6. Submission with tracking ID
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.chatbot.engine import MithuruEngine
from app.chatbot.state import ChatMode


class StubML:
    """Predictable ML stub."""
    def predict_distress(self, text):
        low = text.lower()
        if any(kw in low for kw in ("die", "kill myself", "suicide", "end my life")):
            return ("suicide", 0.95)
        if any(kw in low for kw in ("scared", "alone", "helpless")):
            return ("non-suicide", 0.6)
        return ("non-suicide", 0.1)

    def predict_emotion(self, text):
        low = text.lower()
        if any(kw in low for kw in ("scared", "afraid", "panic")):
            return ("fear", 0.75)
        if any(kw in low for kw in ("sad", "upset", "lost", "taken", "hacked", "leaked")):
            return ("sadness", 0.65)
        return ("neutral", 0.5)


class StubLLM:
    """Returns dummy responses; the test checks mode and state, not LLM text."""
    def generate(self, prompt, max_tokens=256, temperature=0.3):
        if "first complaint question" in prompt.lower() or "first intake" in prompt.lower() or "file this complaint now" in prompt.lower():
            return "I'm sorry this happened. I can help you file this complaint now. Can you tell me your full name?"
        if "full name" in prompt.lower() and "complaint" in prompt.lower():
            return "Can you tell me your full name so I can start your complaint?"
        if "bank name" in prompt.lower():
            return "Which bank is this account with?"
        if "phone" in prompt.lower():
            return "What phone number can we reach you on?"
        if "amount" in prompt.lower():
            return "About how much money was lost?"
        if "crisis" in prompt.lower():
            return "I hear you. Are you safe right now?"
        if "platform" in prompt.lower():
            return "Which platform was this on?"
        return "I hear you. Can you tell me more about what happened?"


def test_bank_fraud_immediate_intake():
    """Bank fraud message → should enter guided_intake immediately, ask name first."""
    print("=" * 60)
    print("TEST 1: Bank fraud → immediate guided intake")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())
    reply = engine.process_message("my bank account was hacked and all my money was taken")

    mode = engine.state.conversation.mode
    incident = engine.state.incident.incident_type
    first_field = engine.state.complaint.last_field_asked

    print(f"  Mode:     {mode.value}")
    print(f"  Incident: {incident}")
    print(f"  First Q:  {first_field}")
    print(f"  Reply:    {reply[:100]}...")

    assert mode == ChatMode.GUIDED_INTAKE, f"Expected GUIDED_INTAKE, got {mode.value}"
    assert incident == "bank_fraud", f"Expected bank_fraud, got {incident}"
    assert first_field == "victim_name", f"Expected victim_name first, got {first_field}"
    assert "incident_description" in engine.state.complaint.collected_fields, "Description should be auto-captured"
    print("  ✓ PASSED\n")


def test_photo_leak_immediate_intake():
    """Photo leak message → should enter guided_intake immediately."""
    print("=" * 60)
    print("TEST 2: Photo leak → immediate guided intake")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())
    reply = engine.process_message("my private photos were uploaded online")

    mode = engine.state.conversation.mode
    incident = engine.state.incident.incident_type
    first_field = engine.state.complaint.last_field_asked

    print(f"  Mode:     {mode.value}")
    print(f"  Incident: {incident}")
    print(f"  First Q:  {first_field}")
    print(f"  Reply:    {reply[:100]}...")

    assert mode == ChatMode.GUIDED_INTAKE, f"Expected GUIDED_INTAKE, got {mode.value}"
    assert incident == "photo_leak", f"Expected photo_leak, got {incident}"
    assert first_field == "victim_name", f"Expected victim_name first, got {first_field}"
    print("  ✓ PASSED\n")


def test_emotional_no_incident_stays_support():
    """Emotional message without clear incident → stays in support/vulnerable, probes."""
    print("=" * 60)
    print("TEST 3: Emotional message only → stays in support, probes")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())
    reply = engine.process_message("I feel so scared and alone right now")

    mode = engine.state.conversation.mode
    incident = engine.state.incident.incident_type

    print(f"  Mode:     {mode.value}")
    print(f"  Incident: {incident}")
    print(f"  Reply:    {reply[:100]}...")

    assert mode in (ChatMode.SUPPORT, ChatMode.VULNERABLE_SUPPORT), f"Expected support/vulnerable, got {mode.value}"
    assert incident is None, f"Expected no incident, got {incident}"
    print("  ✓ PASSED\n")


def test_hard_crisis_pauses_intake():
    """Suicide intent → hard_crisis even if incident was being collected."""
    print("=" * 60)
    print("TEST 4: Hard crisis pauses intake")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())
    # First: classify incident
    engine.process_message("my bank account was hacked")
    assert engine.state.incident.incident_type == "bank_fraud"

    # Then: crisis
    engine.process_message("i want to die")
    mode = engine.state.conversation.mode

    print(f"  Mode:     {mode.value}")
    assert mode == ChatMode.HARD_CRISIS, f"Expected HARD_CRISIS, got {mode.value}"
    print("  ✓ PASSED\n")


def test_field_progression():
    """Multiple turns → fields collected progressively, questions don't repeat."""
    print("=" * 60)
    print("TEST 5: Field progression through intake")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())

    # Turn 1: incident description → should classify + ask name
    engine.process_message("my bank account was hacked and all my money was taken")
    assert engine.state.complaint.last_field_asked == "victim_name"
    fields_asked_1 = set(engine.state.complaint.fields_asked)

    # Turn 2: give name → should ask next field
    engine.process_message("John Silva")
    collected = engine.state.complaint.collected_fields
    print(f"  After name: collected={dict(collected)}")
    assert "victim_name" in collected, f"Name should be captured, got {collected.keys()}"
    fields_asked_2 = set(engine.state.complaint.fields_asked)
    assert len(fields_asked_2) > len(fields_asked_1), "Should have asked a new field"

    # Turn 3: give bank name
    engine.process_message("Commercial Bank")
    collected = engine.state.complaint.collected_fields
    print(f"  After bank: collected keys={list(collected.keys())}")
    assert "bank_name" in collected, f"Bank should be captured"

    # Check that we're still in guided_intake
    mode = engine.state.conversation.mode
    print(f"  Mode: {mode.value}")
    assert mode == ChatMode.GUIDED_INTAKE
    print("  ✓ PASSED\n")


def test_intent_override_without_incident():
    """User asks to file complaint but hasn't described incident → probes for incident."""
    print("=" * 60)
    print("TEST 6: Intent override without incident")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())
    reply = engine.process_message("I want to file a complaint")

    mode = engine.state.conversation.mode
    incident = engine.state.incident.incident_type

    print(f"  Mode:     {mode.value}")
    print(f"  Incident: {incident}")
    print(f"  Reply:    {reply[:100]}...")

    assert mode == ChatMode.SUPPORT, f"Expected SUPPORT (probing for incident), got {mode.value}"
    assert incident is None, "Should not have classified yet"
    print("  ✓ PASSED\n")


def test_scam_detection():
    """'Someone scammed me' → should classify as scam and start intake."""
    print("=" * 60)
    print("TEST 7: Scam detection")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())
    reply = engine.process_message("someone scammed me out of my money")

    mode = engine.state.conversation.mode
    incident = engine.state.incident.incident_type

    print(f"  Mode:     {mode.value}")
    print(f"  Incident: {incident}")

    assert mode == ChatMode.GUIDED_INTAKE, f"Expected GUIDED_INTAKE, got {mode.value}"
    assert incident == "scam", f"Expected scam, got {incident}"
    print("  ✓ PASSED\n")


def test_blackmail_detection():
    """'Someone blackmailed me with my photos' → should classify."""
    print("=" * 60)
    print("TEST 8: Blackmail detection")
    print("=" * 60)

    engine = MithuruEngine(StubML(), StubLLM())
    reply = engine.process_message("someone blackmailed me with my photos")

    mode = engine.state.conversation.mode
    incident = engine.state.incident.incident_type

    print(f"  Mode:     {mode.value}")
    print(f"  Incident: {incident}")

    assert mode == ChatMode.GUIDED_INTAKE, f"Expected GUIDED_INTAKE, got {mode.value}"
    assert incident == "blackmail", f"Expected blackmail, got {incident}"
    print("  ✓ PASSED\n")


if __name__ == "__main__":
    test_bank_fraud_immediate_intake()
    test_photo_leak_immediate_intake()
    test_emotional_no_incident_stays_support()
    test_hard_crisis_pauses_intake()
    test_field_progression()
    test_intent_override_without_incident()
    test_scam_detection()
    test_blackmail_detection()
    print("=" * 60)
    print("ALL 8 TESTS PASSED")
    print("=" * 60)
