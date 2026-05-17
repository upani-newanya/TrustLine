import logging
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Module-level references — populated once by load_models().
suicide_tokenizer = None
suicide_model = None
emotion_tokenizer = None
emotion_model = None


def load_models() -> None:
    """Load both Hugging Face models from local paths. Call once at startup."""
    global suicide_tokenizer, suicide_model, emotion_tokenizer, emotion_model

    settings = get_settings()

    # --- Distress / suicide model ---
    suicide_path = Path(settings.suicide_model_path)
    if not suicide_path.exists():
        raise RuntimeError(f"Suicide model path not found: {suicide_path.resolve()}")

    logger.info("Loading distress model from %s …", suicide_path)
    suicide_tokenizer = AutoTokenizer.from_pretrained(str(suicide_path), local_files_only=True)
    suicide_model = AutoModelForSequenceClassification.from_pretrained(str(suicide_path), local_files_only=True)
    suicide_model.to(torch.device("cpu"))
    suicide_model.eval()

    # --- Emotion model ---
    emotion_path = Path(settings.emotion_model_path)
    if not emotion_path.exists():
        raise RuntimeError(f"Emotion model path not found: {emotion_path.resolve()}")

    logger.info("Loading emotion model from %s …", emotion_path)
    emotion_tokenizer = AutoTokenizer.from_pretrained(str(emotion_path), local_files_only=True)
    emotion_model = AutoModelForSequenceClassification.from_pretrained(str(emotion_path), local_files_only=True)
    emotion_model.to(torch.device("cpu"))
    emotion_model.eval()

    logger.info("Both ML models loaded successfully.")
