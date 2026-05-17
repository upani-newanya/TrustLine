"""Non-interactive test for the agent pipeline using stub predictors and stub LLM.

Runs a set of example messages through Understanding -> Planner -> Chatbot -> LLM Adapter -> Filter
and prints the final reply or filter reason.
"""
import os
from app.agents.understanding import UnderstandingAgent
from app.agents.planner import PlannerAgent
from app.agents.chatbot_agent import ChatbotAgent
from app.agents.filter_agent import FilterAgent
from app.agents.llm_adapter import LLMAdapter
from app.ml.fake_ml import FakeML
from app.utils.logger import log_interaction

# Force stub LLM for tests
os.environ.setdefault("LLM_MODE", "stub")

def make_stub_predictors():
    def distress_predictor(text: str):
        low = ("non-suicide", 0.2)
        high = ("suicide", 0.95)
        t = text.lower()
        if any(k in t for k in ["suicide", "finish my life", "end my life", "jump"]):
            return high
        if any(k in t for k in ["cant handle", "i'm overwhelmed", "i can't handle"]):
            return ("possible", 0.6)
        return low

    def emotion_predictor(text: str):
        t = text.lower()
        if "angry" in t or "cheated" in t:
            return ("anger", 0.7)
        if "sad" in t or "dont love" in t or "i'm overwhelmed" in t or "i cant" in t:
            return ("sadness", 0.8)
        if "scared" in t or "jump" in t:
            return ("fear", 0.75)
        return ("neutral", 0.5)

    return distress_predictor, emotion_predictor


def run_test(messages):
    distress_pred, emotion_pred = make_stub_predictors()
    ml = FakeML(distress_pred, emotion_pred)
    understanding_agent = UnderstandingAgent(ml)
    planner_agent = PlannerAgent()
    chatbot_agent = ChatbotAgent()
    filter_agent = FilterAgent()
    llm = LLMAdapter()

    for msg in messages:
        print("\nUser:", msg)
        understanding = understanding_agent.process(msg)
        rules = planner_agent.process(understanding)
        candidate_prompt = chatbot_agent.process(msg, understanding, rules)
        reply = llm.generate(candidate_prompt)
        checked = filter_agent.process(reply, understanding)
        record = {
            "user": msg,
            "understanding": understanding,
            "rules": rules,
            "candidate_prompt": candidate_prompt,
            "llm_reply": reply,
            "filter": checked,
        }
        log_interaction(record)
        if checked.get("ok"):
            print('\nAssistant:')
            print(checked.get("reply"))
        else:
            print('\nAssistant: (filtered)')
            print('Fallback: Please contact emergency services or a trusted person right away.')
            print(f"[Filter reason: {checked.get('reason')}]")


if __name__ == '__main__':
    sample_messages = [
        "My private photos were leaked to a Telegram group, I don't know what to do",
        "My mom and father are blaming me, I can't handle this situation",
        "I am going to jump from a tall building",
        "Buddy I can't handle this anymore I am going to finish my life",
        "She cheated on me, I don't want a life like this",
    ]
    run_test(sample_messages)
