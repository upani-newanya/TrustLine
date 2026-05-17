import torch
from fastapi import HTTPException, status

# Use module-level import (not `from ... import`) so we always see the
# current value of the globals set by load_models() at startup.
import app.ml.model_loader as _loader


def predict_distress(text: str) -> tuple[str, float]:
    """Return (label, confidence) from the distress / suicide model."""
    if _loader.suicide_tokenizer is None or _loader.suicide_model is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Distress model not loaded")

    inputs = _loader.suicide_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    inputs.pop("token_type_ids", None)
    with torch.no_grad():
        logits = _loader.suicide_model(**inputs).logits

    probs = torch.softmax(logits, dim=1)
    confidence, predicted_idx = torch.max(probs, dim=1)
    label = _loader.suicide_model.config.id2label[predicted_idx.item()]
    return label, round(confidence.item(), 4)


def predict_emotion(text: str) -> tuple[str, float]:
    """Return (label, confidence) from the emotion model."""
    if _loader.emotion_tokenizer is None or _loader.emotion_model is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Emotion model not loaded")

    inputs = _loader.emotion_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    inputs.pop("token_type_ids", None)
    with torch.no_grad():
        logits = _loader.emotion_model(**inputs).logits

    probs = torch.softmax(logits, dim=1)
    confidence, predicted_idx = torch.max(probs, dim=1)
    label = _loader.emotion_model.config.id2label[predicted_idx.item()]
    return label, round(confidence.item(), 4)


def analyze_text(text: str) -> dict:
    """Run both models and return a combined result dict."""
    distress_label, distress_conf = predict_distress(text)
    emotion_label, emotion_conf = predict_emotion(text)

    return {
        "input_text": text,
        "distress_prediction": distress_label,
        "distress_confidence": distress_conf,
        "emotion_prediction": emotion_label,
        "emotion_confidence": emotion_conf,
    }
