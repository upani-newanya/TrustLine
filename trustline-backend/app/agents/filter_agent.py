from typing import Dict
import re

class FilterAgent:
    """Validates and sanitizes chatbot outputs to ensure safety and appropriateness."""

    def __init__(self):
        # simple banned patterns for demonstration
        self.banned_patterns = [re.compile(r"kill yourself", re.I), re.compile(r"i can't be bothered", re.I)]
        # Patterns for external hotlines (block or rewrite)
        self.external_hotline_patterns = [
            re.compile(r"suicide prevention hotline", re.I),
            re.compile(r"crisis text line", re.I),
            re.compile(r"1-800-273-talk", re.I),
            re.compile(r"741741", re.I),
            re.compile(r"national domestic violence hotline", re.I),
            re.compile(r"1-800-799-7233", re.I),
            re.compile(r"national center for victims of crime", re.I),
            re.compile(r"call\s*\d{3,}", re.I),
            re.compile(r"text\s*home\s*to\s*\d{3,}", re.I),
            re.compile(r"hotline", re.I),
        ]

    def process(self, candidate_reply: str, understanding: Dict) -> Dict:
        # Check banned phrases
        for pat in self.banned_patterns:
            if pat.search(candidate_reply):
                return {"ok": False, "reason": "contains banned phrasing", "reply": None}
        # Remove or rewrite any external hotline references
        for pat in self.external_hotline_patterns:
            if pat.search(candidate_reply):
                # Replace with TrustLine/Mithuru hotline only
                candidate_reply = pat.sub("Mithuru hotline (1898)", candidate_reply)
        # Ensure only TrustLine/Mithuru hotline is mentioned
        if "hotline" in candidate_reply.lower() and "mithuru" not in candidate_reply.lower():
            return {"ok": False, "reason": "external hotline reference", "reply": None}
        # Simple safety: ensure we include an offer of help if distress is high
        if understanding["distress_label"].lower().startswith("suicide") and "help" not in candidate_reply.lower():
            return {"ok": False, "reason": "missing help offer", "reply": None}
        # If this is a complaint/cybercrime flow, ensure the reply encourages reporting or offers to draft a complaint
        if understanding.get("intent") in ("complaint", "cybercrime"):
            low = candidate_reply.lower()
            if not any(k in low for k in ("report", "complain", "file", "reporting", "report to", "report it", "report this")):
                return {"ok": False, "reason": "missing encouragement to report or file a complaint", "reply": None}
        # Passed checks
        return {"ok": True, "reply": candidate_reply}
