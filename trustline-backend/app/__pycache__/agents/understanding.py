from typing import Dict

class UnderstandingAgent:
    """Analyzes user message and returns a structured understanding.

    Output dict includes:
    - `tone`: raw label from distress/emotion models
    - `distress_label`, `distress_conf`
    - `emotion_label`, `emotion_conf`
    - `summary`: short natural-language summary of user's state
    """

    def __init__(self, ml_api):
        self.ml_api = ml_api

    def process(self, message: str) -> Dict:
        d_label, d_conf = self.ml_api.predict_distress(message)
        e_label, e_conf = self.ml_api.predict_emotion(message)
        lower = message.lower()
        intent = "general"
        suicide_risk = False
        # Complaint / reporting intent (includes data breaches / leaks)
        if any(k in lower for k in ("complain", "complaint", "report", "leak", "leaked", "police", "report to")):
            intent = "complaint"
        # Cybercrime / account compromise detection
        elif any(k in lower for k in ("phish", "phishing", "scam", "scammed", "hacked", "account compromised", "doxx", "doxed", "doxxing", "doxed", "ransomware", "extortion", "card fraud", "credit card", "unauthorized transaction", "identity theft", "fraud")):
            intent = "cybercrime"
        # Self-harm detection
        if any(k in lower for k in ("suicide", "kill myself", "end my life", "i'm going to jump", "i want to die")) or d_label.lower() in ("suicide", "self-harm") or d_conf > 0.7:
            suicide_risk = True
            if intent == "general":
                intent = "self-harm"
        # Compose a richer summary for LLM and planner
        summary = (
            f"User message: '{message}'.\n"
            f"Emotion detected: {e_label} (confidence {e_conf:.2f}).\n"
            f"Distress detected: {d_label} (confidence {d_conf:.2f}).\n"
            f"Intent: {intent}.\n"
            f"Suicide/self-harm risk: {'yes' if suicide_risk else 'no'}."
        )
        return {
            "distress_label": d_label,
            "distress_conf": d_conf,
            "emotion_label": e_label,
            "emotion_conf": e_conf,
            "summary": summary,
            "intent": intent,
            "suicide_risk": suicide_risk,
        }
