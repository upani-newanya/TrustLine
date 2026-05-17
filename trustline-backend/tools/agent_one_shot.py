#!/usr/bin/env python3
"""Run a single message through the agent pipeline (non-interactive).

Usage:
  python tools/agent_one_shot.py "your message here"
"""
import sys
import os
from dotenv import load_dotenv

# Ensure project root is on sys.path so we can import top-level modules when running from tools/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

load_dotenv()

from agent_pipeline import make_predictors_from_conversation_test
from app.agents.understanding import UnderstandingAgent
from app.agents.planner import PlannerAgent
from app.agents.chatbot_agent import ChatbotAgent
from app.agents.filter_agent import FilterAgent
from app.agents.llm_adapter import LLMAdapter
from app.ml.fake_ml import FakeML


def run_once(message: str):
    distress_pred, emotion_pred = make_predictors_from_conversation_test()
    ml = FakeML(distress_pred, emotion_pred)

    understanding_agent = UnderstandingAgent(ml)
    planner_agent = PlannerAgent()
    chatbot_agent = ChatbotAgent()
    filter_agent = FilterAgent()
    llm = LLMAdapter()

    understanding = understanding_agent.process(message)
    rules = planner_agent.process(understanding)
    candidate_prompt = chatbot_agent.process(message, understanding, rules)

    print("=== Understanding ===")
    for k, v in understanding.items():
        print(f"{k}: {v}")

    print("\n=== Candidate Prompt ===")
    print(candidate_prompt)

    print("\n=== LLM Adapter State ===")
    try:
        print(f"provider={llm.provider}, api_url={llm.api_url}, model={llm.model or llm.groq_model}, has_api_key={bool(llm.api_key)}")
    except Exception:
        pass

    try:
        reply = llm.generate(candidate_prompt)
    except Exception as e:
        print("\nLLM generation failed:", e)
        reply = "[LLM generation failed]"

    print("\n=== Raw LLM Reply ===")
    print(reply)

    checked = filter_agent.process(reply, understanding)
    print("\n=== Filter Result ===")
    print(checked)


def main():
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = "I feel like ending my life"
    run_once(msg)


if __name__ == '__main__':
    main()
