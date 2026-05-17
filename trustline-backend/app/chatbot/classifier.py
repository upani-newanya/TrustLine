"""Incident type classifier for Mithuru.

Uses weighted keyword scoring to determine the most likely incident type
from user messages.  Falls back to LLM-based semantic classification
when keywords are insufficient.
"""
from __future__ import annotations

import re
from typing import Optional

from .incidents import IncidentType

# keyword → [(incident_type_value, weight), ...]
_KEYWORD_MAP: dict[str, list[tuple[str, float]]] = {
    # ── Photo leak / porn ──
    "photo leak":               [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked photo":             [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked my photo":          [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "private photo":            [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "personal photo":           [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "intimate photo":           [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "photos leaked":            [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "photos were leaked":       [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "videos leaked":            [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "videos were leaked":       [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked into internet":     [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked online":            [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked on the internet":   [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "shared my photo":          [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "shared my video":          [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "spread my photo":          [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "nude":                     [(IncidentType.PHOTO_LEAK.value, 1.5),
                                 (IncidentType.SEXTORTION.value, 1.5)],
    "porn site":                [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "porn website":             [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "pornhub":                  [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "xvideos":                  [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "xhamster":                 [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "xnxx":                     [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "onlyfans":                 [(IncidentType.PORN_SITE_UPLOAD.value, 2.5)],
    "adult site":               [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "adult website":            [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "adult web site":           [(IncidentType.PORN_SITE_UPLOAD.value, 3.0)],
    "uploaded my":              [(IncidentType.PHOTO_LEAK.value, 2.0)],
    "uploaded on":              [(IncidentType.PHOTO_LEAK.value, 2.0)],
    "uploaded to":              [(IncidentType.PHOTO_LEAK.value, 2.0)],
    "photos uploaded":          [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "videos uploaded":          [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "photos online":            [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "uploaded online":          [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "private photos":           [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "leaked video":             [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "private video":            [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "intimate video":           [(IncidentType.PHOTO_LEAK.value, 2.5)],
    # "pictures" synonyms (users say "pictures" as often as "photos")
    "picture leak":             [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "pictures leaked":          [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "pictures were leaked":     [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked picture":           [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked my picture":        [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "private pictures":         [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "personal pictures":        [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "intimate pictures":        [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "pictures uploaded":        [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "pictures online":          [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "shared my picture":        [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "spread my picture":        [(IncidentType.PHOTO_LEAK.value, 2.5)],
    # Generic "leaked" + content words (catches "was leaked", "got leaked")
    "was leaked":               [(IncidentType.PHOTO_LEAK.value, 2.0)],
    "got leaked":               [(IncidentType.PHOTO_LEAK.value, 2.0)],
    "being leaked":             [(IncidentType.PHOTO_LEAK.value, 2.0)],
    "leaked in":                [(IncidentType.PHOTO_LEAK.value, 2.0)],
    # "images" synonyms
    "images leaked":            [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "leaked images":            [(IncidentType.PHOTO_LEAK.value, 3.0)],
    "private images":           [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "personal images":          [(IncidentType.PHOTO_LEAK.value, 2.5)],
    # Ex-partner context (common in Sri Lanka photo leak cases)
    "ex boyfriend":             [(IncidentType.PHOTO_LEAK.value, 1.5),
                                 (IncidentType.SEXTORTION.value, 1.0)],
    "ex girlfriend":            [(IncidentType.PHOTO_LEAK.value, 1.5),
                                 (IncidentType.SEXTORTION.value, 1.0)],
    "ex-boyfriend":             [(IncidentType.PHOTO_LEAK.value, 1.5),
                                 (IncidentType.SEXTORTION.value, 1.0)],
    "ex-girlfriend":            [(IncidentType.PHOTO_LEAK.value, 1.5),
                                 (IncidentType.SEXTORTION.value, 1.0)],
    "sent to my ex":            [(IncidentType.PHOTO_LEAK.value, 2.0)],
    "my ex shared":             [(IncidentType.PHOTO_LEAK.value, 2.5)],
    "revenge porn":             [(IncidentType.PHOTO_LEAK.value, 3.0)],
    # "without consent" strong single signal
    "without my consent":       [(IncidentType.PHOTO_LEAK.value, 2.0),
                                 (IncidentType.HARASSMENT.value, 1.0)],
    "without consent":          [(IncidentType.PHOTO_LEAK.value, 1.5)],

    # ── Sextortion ──
    "sextortion":               [(IncidentType.SEXTORTION.value, 3.0)],
    "sexual extortion":         [(IncidentType.SEXTORTION.value, 3.0)],
    "send more photos or":      [(IncidentType.SEXTORTION.value, 2.5)],
    "send nudes or":            [(IncidentType.SEXTORTION.value, 2.5)],
    "threaten to share":        [(IncidentType.SEXTORTION.value, 2.0),
                                 (IncidentType.BLACKMAIL.value, 2.0)],
    "threatening to share":     [(IncidentType.SEXTORTION.value, 2.0),
                                 (IncidentType.BLACKMAIL.value, 2.0)],
    "threaten to expose":       [(IncidentType.SEXTORTION.value, 2.0),
                                 (IncidentType.BLACKMAIL.value, 2.0)],
    "threatening to expose":    [(IncidentType.SEXTORTION.value, 2.0),
                                 (IncidentType.BLACKMAIL.value, 2.0)],
    "threatening with my":      [(IncidentType.SEXTORTION.value, 2.0),
                                 (IncidentType.BLACKMAIL.value, 1.5)],
    "unless i pay":             [(IncidentType.SEXTORTION.value, 1.5),
                                 (IncidentType.BLACKMAIL.value, 1.5)],

    # ── Blackmail ──
    "blackmail":                [(IncidentType.BLACKMAIL.value, 3.0)],
    "blackmailing":             [(IncidentType.BLACKMAIL.value, 3.0)],
    "blackmailed me":           [(IncidentType.BLACKMAIL.value, 3.0)],
    "someone blackmailed":      [(IncidentType.BLACKMAIL.value, 3.0)],
    "blackmailed with":         [(IncidentType.BLACKMAIL.value, 2.5),
                                 (IncidentType.PHOTO_LEAK.value, 1.5)],
    "demanding money":          [(IncidentType.BLACKMAIL.value, 2.0),
                                 (IncidentType.SEXTORTION.value, 1.5)],
    "pay or else":              [(IncidentType.BLACKMAIL.value, 2.5)],
    "extortion":                [(IncidentType.BLACKMAIL.value, 2.5)],
    "extort":                   [(IncidentType.BLACKMAIL.value, 2.5)],

    # ── Bank fraud ──
    "bank fraud":               [(IncidentType.BANK_FRAUD.value, 3.0)],
    "bank account hacked":      [(IncidentType.BANK_FRAUD.value, 3.0)],
    "bank account was hacked":  [(IncidentType.BANK_FRAUD.value, 3.0)],
    "money stolen":             [(IncidentType.BANK_FRAUD.value, 2.5)],
    "money taken":              [(IncidentType.BANK_FRAUD.value, 2.5)],
    "money was taken":          [(IncidentType.BANK_FRAUD.value, 3.0)],
    "money was stolen":         [(IncidentType.BANK_FRAUD.value, 3.0)],
    "money was transferred":    [(IncidentType.BANK_FRAUD.value, 3.0)],
    "money missing":            [(IncidentType.BANK_FRAUD.value, 2.5)],
    "all my money":             [(IncidentType.BANK_FRAUD.value, 2.0)],
    "transferred from my account": [(IncidentType.BANK_FRAUD.value, 3.0)],
    "unauthorized transaction": [(IncidentType.BANK_FRAUD.value, 3.0)],
    "bank account":              [(IncidentType.BANK_FRAUD.value, 2.5)],
    "bank":                       [(IncidentType.BANK_FRAUD.value, 1.5)],
    "credit card":              [(IncidentType.BANK_FRAUD.value, 2.0)],
    "debit card":               [(IncidentType.BANK_FRAUD.value, 2.0)],
    "card fraud":               [(IncidentType.BANK_FRAUD.value, 3.0)],
    "otp":                      [(IncidentType.BANK_FRAUD.value, 1.5),
                                 (IncidentType.SCAM.value, 1.0)],

    # ── Account hack ──
    "account hacked":           [(IncidentType.ACCOUNT_HACK.value, 3.0)],
    "hacked my account":        [(IncidentType.ACCOUNT_HACK.value, 3.0)],
    "someone hacked":           [(IncidentType.ACCOUNT_HACK.value, 2.5)],
    "cant login":               [(IncidentType.ACCOUNT_HACK.value, 2.0)],
    "can't log in":             [(IncidentType.ACCOUNT_HACK.value, 2.0)],
    "locked out of my account": [(IncidentType.ACCOUNT_HACK.value, 2.5)],
    "password changed":         [(IncidentType.ACCOUNT_HACK.value, 2.0)],

    # ── Social-media hack ──
    "facebook hacked":          [(IncidentType.SOCIAL_MEDIA_HACK.value, 3.0)],
    "instagram hacked":         [(IncidentType.SOCIAL_MEDIA_HACK.value, 3.0)],
    "whatsapp hacked":          [(IncidentType.SOCIAL_MEDIA_HACK.value, 3.0)],
    "social media hacked":      [(IncidentType.SOCIAL_MEDIA_HACK.value, 3.0)],

    # ── Impersonation ──
    "fake account":             [(IncidentType.IMPERSONATION.value, 3.0)],
    "fake profile":             [(IncidentType.IMPERSONATION.value, 3.0)],
    "impersonat":               [(IncidentType.IMPERSONATION.value, 3.0)],
    "pretending to be me":      [(IncidentType.IMPERSONATION.value, 3.0)],
    "using my name":            [(IncidentType.IMPERSONATION.value, 2.5)],
    "using my photos":          [(IncidentType.IMPERSONATION.value, 2.5)],

    # ── Cyberbullying ──
    "cyberbully":               [(IncidentType.CYBERBULLYING.value, 3.0)],
    "cyber bully":              [(IncidentType.CYBERBULLYING.value, 3.0)],
    "bullying online":          [(IncidentType.CYBERBULLYING.value, 3.0)],
    "making fun of me":         [(IncidentType.CYBERBULLYING.value, 2.0)],
    "hateful messages":         [(IncidentType.CYBERBULLYING.value, 2.0),
                                 (IncidentType.HARASSMENT.value, 1.5)],
    "spreading rumors":         [(IncidentType.CYBERBULLYING.value, 2.0)],
    "mocking":                  [(IncidentType.CYBERBULLYING.value, 2.0)],

    # ── Harassment ──
    "harass":                   [(IncidentType.HARASSMENT.value, 2.5)],
    "harassment":               [(IncidentType.HARASSMENT.value, 3.0)],
    "stalking":                 [(IncidentType.HARASSMENT.value, 3.0)],
    "stalker":                  [(IncidentType.HARASSMENT.value, 3.0)],
    "won't leave me alone":     [(IncidentType.HARASSMENT.value, 2.5)],
    "keeps messaging me":       [(IncidentType.HARASSMENT.value, 2.0)],
    "creepy messages":          [(IncidentType.HARASSMENT.value, 2.0)],
    "unwanted messages":        [(IncidentType.HARASSMENT.value, 2.0)],

    # ── Scam ──
    "scam":                     [(IncidentType.SCAM.value, 3.0)],
    "scammed":                  [(IncidentType.SCAM.value, 3.0)],
    "phishing":                 [(IncidentType.SCAM.value, 2.5)],
    "fake website":             [(IncidentType.SCAM.value, 2.5)],
    "investment scam":          [(IncidentType.SCAM.value, 3.0)],
    "lottery":                  [(IncidentType.SCAM.value, 2.0)],
    "too good to be true":      [(IncidentType.SCAM.value, 1.5)],
    "fake job":                 [(IncidentType.SCAM.value, 2.5)],
    "tricked":                  [(IncidentType.SCAM.value, 1.5)],
}

_CLASSIFICATION_THRESHOLD = 2.0

# Common misspellings → corrected form (applied before keyword matching)
_TYPO_CORRECTIONS: dict[str, str] = {
    # hack
    "haked": "hacked",
    "hackd": "hacked",
    "hakced": "hacked",
    "hacke": "hacked",
    # scam
    "scamed": "scammed",
    "scamer": "scammer",
    "scamme": "scammer",
    "scammd": "scammed",
    "scamming": "scam",
    # harass
    "harrassed": "harassed",
    "harrass": "harass",
    "harras": "harass",
    # bully
    "bulling": "bullying",
    "bullied": "bullying",
    # stalk
    "stalkin": "stalking",
    # blackmail
    "blackmaild": "blackmailed",
    "blackmaled": "blackmailed",
    "blakmail": "blackmail",
    # misc
    "extorsion": "extortion",
    "phising": "phishing",
    "fradulent": "fraudulent",
    "frud": "fraud",
    "froud": "fraud",
    "predend": "pretend",
    "pretened": "pretend",
    "impersonat": "impersonat",
    "leakd": "leaked",
    "leeked": "leaked",
    # photo / video / picture typos (very common in Sri Lankan English)
    "vedio": "video",
    "vedios": "videos",
    "vidio": "video",
    "picures": "pictures",
    "picturs": "pictures",
    "pictur": "picture",
    "pikture": "picture",
    "piktures": "pictures",
    "fotos": "photos",
    "foto": "photo",
    "phtos": "photos",
    "photoes": "photos",
    "privet": "private",
    "privat": "private",
    "perosnal": "personal",
    "persnal": "personal",
    "persoanl": "personal",
    "leeked": "leaked",
    "leked": "leaked",
    "leacked": "leaked",
    "uploded": "uploaded",
    "uplaoded": "uploaded",
    "websit": "website",
    "wbsite": "website",
    "onlne": "online",
    "intrnet": "internet",
    "faceboo": "facebook",
    "instagm": "instagram",
    "whatapp": "whatsapp",
    "watsapp": "whatsapp",
}


class IncidentClassifier:
    """Classifies the incident type from user message text using keyword scoring."""

    @staticmethod
    def _fix_typos(text: str) -> str:
        """Replace common misspellings so keyword matching works."""
        for typo, correction in _TYPO_CORRECTIONS.items():
            if typo in text:
                text = text.replace(typo, correction)
        return text

    def classify(
        self,
        message: str,
        accumulated_messages: list[str] | None = None,
        turn_count: int = 0,
    ) -> str | None:
        """Return an IncidentType value string, or None if insufficient signal.

        After several turns without classification, the threshold is lowered
        so that weaker signals (single keywords) can still trigger intake.
        """
        texts = list(accumulated_messages or [])
        texts.append(message)
        combined = self._fix_typos(" ".join(texts).lower())

        scores: dict[str, float] = {}
        for keyword, mappings in _KEYWORD_MAP.items():
            if keyword in combined:
                for incident_type, weight in mappings:
                    scores[incident_type] = scores.get(incident_type, 0.0) + weight

        if not scores:
            return None

        best_type = max(scores, key=lambda k: scores[k])
        # After 4+ turns the user has been describing their problem — accept weaker signals
        threshold = _CLASSIFICATION_THRESHOLD if turn_count < 4 else _CLASSIFICATION_THRESHOLD * 0.6
        if scores[best_type] >= threshold:
            return best_type
        return None

    # ── LLM-based semantic fallback ──

    _LLM_CLASSIFICATION_PROMPT = (
        "You are a cybercrime incident classifier for TrustLine, a Sri Lankan victim support service.\n"
        "Given the victim's message(s), classify the incident into EXACTLY ONE of these types:\n\n"
        "- photo_leak: Private/intimate photos or videos shared or leaked without consent\n"
        "- porn_site_upload: Content uploaded to adult/porn websites without consent\n"
        "- sextortion: Sexual blackmail — threats to share intimate content unless demands are met\n"
        "- blackmail: Non-sexual blackmail or extortion — threats for money or other demands\n"
        "- bank_fraud: Unauthorized bank transactions, stolen money, card fraud\n"
        "- account_hack: Online account compromised, password changed, locked out\n"
        "- social_media_hack: Facebook/Instagram/WhatsApp/other social media hacked\n"
        "- impersonation: Fake accounts or profiles pretending to be the victim\n"
        "- cyberbullying: Online bullying, mocking, spreading rumors\n"
        "- harassment: Stalking, unwanted contact, threatening messages\n"
        "- scam: Phishing, fake jobs, investment scams, lottery scams\n"
        "- none: Not a cybercrime or insufficient information to classify\n\n"
        "Rules:\n"
        "- Reply with ONLY the type label (e.g. photo_leak). No explanation.\n"
        "- If the user describes multiple issues, pick the PRIMARY one.\n"
        "- If unclear, reply: none\n\n"
        "Victim's message(s):\n"
    )

    _VALID_LLM_TYPES = frozenset(t.value for t in IncidentType)

    def llm_classify(
        self,
        message: str,
        accumulated_messages: list[str] | None = None,
        llm_adapter=None,
    ) -> Optional[str]:
        """Use the LLM to semantically classify the incident type.

        Called as a fallback when keyword-based classification returns None.
        Returns an IncidentType value string, or None.
        """
        if llm_adapter is None:
            return None

        texts = list(accumulated_messages or [])
        texts.append(message)
        combined = "\n".join(f"- {t}" for t in texts if t.strip())

        prompt = self._LLM_CLASSIFICATION_PROMPT + combined

        try:
            raw = llm_adapter.generate(prompt, max_tokens=20, temperature=0.0)
            # Parse: extract the first valid incident type from the response
            cleaned = raw.strip().lower().strip('"\'.- ')
            # Handle cases like "photo_leak." or "Type: photo_leak"
            for token in re.split(r"[\s:,]+", cleaned):
                token = token.strip('"\'.-')
                if token in self._VALID_LLM_TYPES:
                    return token
            # Also check if the full cleaned string (minus quotes/dots) is valid
            if cleaned in self._VALID_LLM_TYPES:
                return cleaned
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("LLM classification failed: %s", exc)

        return None
