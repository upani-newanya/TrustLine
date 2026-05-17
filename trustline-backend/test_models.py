"""
Quick offline test — loads both ML models and runs sample texts through them.
Run from the trustline-backend folder:
    python test_models.py
"""

import sys, os, json, torch
from pathlib import Path

# Make sure app imports resolve
sys.path.insert(0, os.getcwd())

from transformers import AutoTokenizer, AutoModelForSequenceClassification

SUICIDE_PATH = "./ml_models/suicide_model_distilbert_cpu_v2"
EMOTION_PATH = "./ml_models/emotion_model_distilbert_cpu_4class_best"

# ---------- load models ----------
print("Loading distress model …")
s_tok = AutoTokenizer.from_pretrained(SUICIDE_PATH, local_files_only=True)
s_mod = AutoModelForSequenceClassification.from_pretrained(SUICIDE_PATH, local_files_only=True)
s_mod.eval()

print("Loading emotion model …")
e_tok = AutoTokenizer.from_pretrained(EMOTION_PATH, local_files_only=True)
e_mod = AutoModelForSequenceClassification.from_pretrained(EMOTION_PATH, local_files_only=True)
e_mod.eval()
print("Models loaded.\n")

# ---------- helper ----------
def analyze(text: str) -> dict:
    # distress
    inp = s_tok(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        logits = s_mod(**inp).logits
    probs = torch.softmax(logits, dim=1)
    conf, idx = torch.max(probs, dim=1)
    distress_label = s_mod.config.id2label[idx.item()]
    distress_conf  = round(conf.item(), 4)

    # emotion
    inp = e_tok(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        logits = e_mod(**inp).logits
    probs = torch.softmax(logits, dim=1)
    conf, idx = torch.max(probs, dim=1)
    emotion_label = e_mod.config.id2label[idx.item()]
    emotion_conf  = round(conf.item(), 4)

    return {
        "input_text": text,
        "distress_prediction": distress_label,
        "distress_confidence": distress_conf,
        "emotion_prediction": emotion_label,
        "emotion_confidence": emotion_conf,
    }

# ---------- test cases ----------
SAMPLES = [
    # Sad / distressed
    "I feel broken and I cannot handle this anymore",
    "Nobody cares about me, I just want to disappear",
    "I lost everything and I do not see any reason to keep going",
    "I have been crying all night and I feel so alone",
    # Angry
    "I am so furious right now, they betrayed my trust",
    "This makes me extremely angry, I want to scream",
    # Fearful
    "I am terrified that someone is following me online",
    "I received threats and I am scared for my safety",
    "Someone is blackmailing me with my private photos, I am so afraid",
    # Happy / neutral
    "I got a new job today and I am so excited!",
    "Life is beautiful, I love spending time with my family",
    "I passed my final exam with flying colors!",
    # Cyberbullying context
    "People keep sending me hateful messages every day",
    "They created a fake account and are spreading lies about me",
    "Someone leaked my private video and now everyone is laughing at me",
]

print(f"{'='*100}")
print(f"{'TEXT':<60} {'DISTRESS':<18} {'EMOTION':<18}")
print(f"{'='*100}")

for text in SAMPLES:
    r = analyze(text)
    short = text[:57] + "..." if len(text) > 60 else text
    d = f"{r['distress_prediction']} ({r['distress_confidence']:.2f})"
    e = f"{r['emotion_prediction']} ({r['emotion_confidence']:.2f})"
    print(f"{short:<60} {d:<18} {e:<18}")

print(f"{'='*100}")
print("\nDone. Review the predictions above to verify model quality.")
