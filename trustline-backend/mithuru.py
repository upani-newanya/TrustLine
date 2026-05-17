"""Interactive Mithuru chatbot — TrustLine cybercrime victim support companion.

Usage:
    cd G:\\TrustLine\\trustline-backend
    python mithuru.py
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)


def _load_ml():
    """Load local DistilBERT models; return stub predictors if unavailable."""
    try:
        import conversation_test as conv

        distress_path = os.getenv(
            "DISTRESS_MODEL_PATH",
            "./ml_models/suicide_model_distilbert_cpu_v2",
        )
        emotion_path = os.getenv(
            "EMOTION_MODEL_PATH",
            "./ml_models/emotion_model_distilbert_cpu_4class_best",
        )

        dt_tok, dt_mod = conv.load_model_and_tokenizer(distress_path)
        em_tok, em_mod = conv.load_model_and_tokenizer(emotion_path)

        print("[ML] Distress model loaded.")
        print("[ML] Emotion model loaded.")

        def distress_pred(text):
            return conv.predict(dt_mod, dt_tok, text, max_length=256)

        def emotion_pred(text):
            return conv.predict(em_mod, em_tok, text, max_length=128)

        return distress_pred, emotion_pred
    except Exception as exc:
        print(f"[ML] Models unavailable ({exc}); using stubs.")
        return lambda t: ("non-suicide", 0.0), lambda t: ("neutral", 0.0)


def main():
    from app.ml.fake_ml import FakeML
    from app.agents.llm_adapter import LLMAdapter
    from app.chatbot.engine import MithuruEngine

    print("=" * 50)
    print("  Mithuru — TrustLine Support Companion")
    print("=" * 50)
    print()

    d_pred, e_pred = _load_ml()
    ml = FakeML(d_pred, e_pred)
    llm = LLMAdapter()
    engine = MithuruEngine(ml, llm)

    print("\nMithuru is ready. Type your message (type 'exit' to quit).\n")

    while True:
        try:
            text = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text.strip().lower() in {"exit", "quit"}:
            print("\nTake care. Remember, you're not alone. 💛")
            break

        reply = engine.process_message(text)
        mode = engine.state.conversation.mode.value
        print(f"\n[{mode.upper()}] Mithuru: {reply}\n")


if __name__ == "__main__":
    main()
