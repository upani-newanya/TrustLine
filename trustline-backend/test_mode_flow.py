"""Integration test for the refactored 5-mode crisis/vulnerable system.

Simulates the exact failing scenario:
  1. "my personal photos were leaked into internet"  → should NOT enter crisis
  2. "no i dont have any one to talk with me"         → vulnerable_support, not hard_crisis
  3. "how can i get a action for this"                → guided_intake (intent override)
"""
from app.chatbot.engine import MithuruEngine


class StubML:
    """Simulates ML that detects sadness on distressing messages."""
    def predict_distress(self, t):
        low = t.lower()
        if any(kw in low for kw in ("die", "kill myself", "suicide", "hurt myself")):
            return ("suicide", 0.92)
        if any(kw in low for kw in ("leaked", "no one", "alone", "scared")):
            return ("non-suicide", 0.65)
        return ("non-suicide", 0.1)

    def predict_emotion(self, t):
        low = t.lower()
        if any(kw in low for kw in ("leaked", "photos")):
            return ("fear", 0.7)
        if any(kw in low for kw in ("no one", "alone", "nobody")):
            return ("sadness", 0.75)
        return ("neutral", 0.5)


class StubLLM:
    def generate(self, prompt, max_tokens=256, temperature=0.2):
        if "safety" in prompt.lower() or "vulnerable" in prompt.lower():
            return "I'm here with you. You don't have to go through this alone."
        if "content_still_live" in prompt.lower() or "still visible" in prompt.lower():
            return "I'm really sorry this happened. Are the photos still visible online right now?"
        if "platform" in prompt.lower():
            return "To help you, could you tell me which website or platform the photos appeared on?"
        return "I hear you. Let's work through this together step by step."


def run_test():
    engine = MithuruEngine(StubML(), StubLLM())
    
    messages = [
        "my personal photos were leaked into internet",
        "no i dont have any one to talk with me",
        "how can i get a action for this",
        "yes they are still visible on a website",
        "i want to die",  # THIS should trigger hard_crisis
        "i'm feeling a bit calmer now",  # should exit crisis
    ]

    print("=" * 60)
    print("  MODE FLOW INTEGRATION TEST")
    print("=" * 60)

    for msg in messages:
        reply = engine.process_message(msg)
        mode = engine.state.conversation.mode.value
        incident = engine.state.incident.incident_type or "-"
        collected = len(engine.state.complaint.collected_fields)
        safety_checks = engine.state.emotional.safety_checks_given

        print(f"\nUser: \"{msg}\"")
        print(f"  Mode:           {mode}")
        print(f"  Incident:       {incident}")
        print(f"  Fields:         {collected} collected")
        print(f"  Safety checks:  {safety_checks}")
        print(f"  Mithuru: {reply}")
    
    print("\n" + "=" * 60)
    print("  COLLECTED FIELDS:")
    for k, v in engine.state.complaint.collected_fields.items():
        print(f"    {k}: {v}")
    print("=" * 60)


if __name__ == "__main__":
    run_test()
