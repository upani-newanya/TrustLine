"""Test LLM fallback classification with phrases that keywords miss."""
from dotenv import load_dotenv
load_dotenv(override=True)

from app.chatbot.classifier import IncidentClassifier
from app.agents.llm_adapter import LLMAdapter

classifier = IncidentClassifier()
llm = LLMAdapter()

# Phrases that keyword matching CANNOT catch
test_cases = [
    ("someone put my face on a naked body", "photo_leak"),
    ("they morphed my photo onto pornographic content", "photo_leak"),
    ("a stranger is asking me to send inappropriate pictures or he'll ruin my life", "sextortion"),
    ("i received a suspicious email asking for my bank details", "scam"),
    ("someone created a profile using my identity on instagram", "impersonation"),
    ("kids at school keep posting hurtful things about my daughter online", "cyberbullying"),
    ("my ex won't stop sending me threatening messages every night", "harassment"),
    ("somebody got into my email and changed all my passwords", "account_hack"),
    ("they want 50000 rupees or they'll send my private clips to everyone", "blackmail"),
    ("i found unauthorized charges on my credit card statement", "bank_fraud"),
]

print("=== Keyword-only classification ===")
for msg, expected in test_cases:
    kw_result = classifier.classify(msg, [], turn_count=2)
    status = "HIT" if kw_result else "MISS"
    print(f"  [{status}] \"{msg[:60]}...\" -> {kw_result} (expected: {expected})")

print("\n=== LLM fallback classification ===")
for msg, expected in test_cases:
    kw_result = classifier.classify(msg, [], turn_count=2)
    if kw_result:
        result = kw_result
        source = "keyword"
    else:
        result = classifier.llm_classify(msg, [], llm_adapter=llm)
        source = "LLM"
    match = "OK" if result == expected else "WRONG"
    print(f"  [{match}] ({source}) \"{msg[:60]}...\" -> {result} (expected: {expected})")
