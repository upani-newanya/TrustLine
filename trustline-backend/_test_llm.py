"""Quick LLM diagnostic."""
import traceback
from dotenv import load_dotenv
load_dotenv()
from app.agents.llm_adapter import LLMAdapter

a = LLMAdapter()
print("mode:", a.mode, "provider:", a.provider, "url:", a.api_url)
print("key present:", bool(a.api_key), "model:", a.groq_model or a.model)
try:
    r = a.generate("Say hello in one sentence.", max_tokens=50)
    print("OK:", r[:200])
except Exception as e:
    traceback.print_exc()
