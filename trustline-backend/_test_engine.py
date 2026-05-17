"""Test engine directly to diagnose the chatbot error."""
import os, sys, traceback, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv(override=True)

from app.chatbot.engine import MithuruEngine
from app.ml.fake_ml import FakeML
from app.agents.llm_adapter import LLMAdapter

# Use stub ML to skip model loading time
ml = FakeML(lambda t: ("non-suicide", 0.0), lambda t: ("neutral", 0.0))
llm = LLMAdapter()
engine = MithuruEngine(ml, llm)

msg = "my personal privet photos was leaked in to a porn website"
print(f"Input: {msg}")
print("Processing...", flush=True)

t0 = time.time()
try:
    reply = engine.process_message(msg)
    print(f"Reply ({time.time()-t0:.1f}s): {reply}")
except Exception as e:
    print(f"ERROR ({time.time()-t0:.1f}s): {type(e).__name__}: {e}")
    traceback.print_exc()
