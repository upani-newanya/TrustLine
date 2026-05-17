"""Non-interactive test of the full Mithuru flow to catch LLM errors."""
import os, sys
from dotenv import load_dotenv
load_dotenv()

# Load ML models
try:
    import conversation_test as conv
    dt_tok, dt_mod = conv.load_model_and_tokenizer("./ml_models/suicide_model_distilbert_cpu_v2")
    em_tok, em_mod = conv.load_model_and_tokenizer("./ml_models/emotion_model_distilbert_cpu_4class_best")
    print("[ML] Models loaded.")
    d_pred = lambda t: conv.predict(dt_mod, dt_tok, t, max_length=256)
    e_pred = lambda t: conv.predict(em_mod, em_tok, t, max_length=128)
except Exception as e:
    print(f"[ML] Stubs ({e})")
    d_pred = lambda t: ("non-suicide", 0.0)
    e_pred = lambda t: ("neutral", 0.0)

from app.ml.fake_ml import FakeML
from app.agents.llm_adapter import LLMAdapter
from app.chatbot.engine import MithuruEngine

ml = FakeML(d_pred, e_pred)
llm = LLMAdapter()
engine = MithuruEngine(ml, llm)

test_messages = [
    "hi can you help me",
    "oky my personal pictures was leaked in toa adult web site",
    "xnxx.com",
    "im amanda cooray",
    "yes its still visible",
    "no",
    "0987656759",
    "bye",
]

for msg in test_messages:
    print(f"\n--- You: {msg}")
    reply = engine.process_message(msg)
    mode = engine.state.conversation.mode.value
    print(f"[{mode.upper()}] Mithuru: {reply}")
    # Show state
    inc = engine.state.incident.incident_type
    fields = dict(engine.state.complaint.collected_fields)
    tracker = {k: (e.value, e.status.value) for k, e in engine.state.complaint.field_tracker.items()}
    print(f"  incident={inc}, fields={fields}")
    if tracker:
        print(f"  tracker={tracker}")
