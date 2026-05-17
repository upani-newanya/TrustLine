#!/usr/bin/env python3
"""Simple interactive chat client for Groq LLM.

Usage:
  - Put your `GROQ_API_KEY` and `GROQ_MODEL` (or `GROQ_API_URL`) in `.env` in the repo root.
  - Run: `python tools/groq_chat.py`

This script is intentionally standalone and does not use the agent pipeline.
"""
import json
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_TIMEOUT_S = int(os.getenv("GROQ_TIMEOUT_S", "12"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "350"))
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in .env")
    sys.exit(2)

if not GROQ_API_URL:
    # Prefer an OpenAI-compatible base path; if not provided but model present, use Groq's OpenAI-compatible base
    if not GROQ_MODEL:
        print("ERROR: Either GROQ_API_URL or GROQ_MODEL must be set in .env")
        sys.exit(2)
    GROQ_API_URL = "https://api.groq.com/openai/v1"

HEADERS = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

print("Groq chat client")
print(f"API: {GROQ_API_URL}")
print("Type messages and press Enter. Type 'exit' or Ctrl-C to quit.")

session = requests.Session()


def parse_groq_response(resp_json):
    # Try common shapes seen in Groq-like responses
    if isinstance(resp_json, dict):
        if "outputs" in resp_json and isinstance(resp_json["outputs"], list) and len(resp_json["outputs"]) > 0:
            first = resp_json["outputs"][0]
            if isinstance(first, dict):
                for k in ("content", "text", "output"):
                    if k in first:
                        return first[k]
            if isinstance(first, str):
                return first
        for k in ("text", "generated_text", "response", "output"):
            if k in resp_json:
                return resp_json[k]
        if "choices" in resp_json and len(resp_json["choices"]) > 0:
            c0 = resp_json["choices"][0]
            if isinstance(c0, dict) and "text" in c0:
                return c0["text"]
    # fallback to returning the full JSON as string
    return json.dumps(resp_json, indent=2)


try:
    while True:
        try:
            prompt = input("You: ")
        except EOFError:
            break
        if not prompt:
            continue
        if prompt.strip().lower() in {"exit", "quit"}:
            break

        # Use OpenAI-compatible Chat Completions when possible
        endpoint = GROQ_API_URL.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint = endpoint + "/chat/completions"

        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": GROQ_MAX_TOKENS,
            "temperature": GROQ_TEMPERATURE,
        }
        try:
            resp = session.post(endpoint, json=payload, headers=HEADERS, timeout=GROQ_TIMEOUT_S)
        except requests.RequestException as e:
            print("Network error:", e)
            print("If DNS resolution fails, try changing network/DNS or set GROQ_API_URL to a reachable endpoint.")
            continue

        try:
            resp.raise_for_status()
        except requests.HTTPError:
            print(f"HTTP {resp.status_code}: {resp.text}")
            continue

        try:
            data = resp.json()
        except Exception:
            print(resp.text)
            continue

        reply = parse_groq_response(data)
        print("\nAssistant:")
        print(reply)
        print()
except KeyboardInterrupt:
    print("\nExiting.")

