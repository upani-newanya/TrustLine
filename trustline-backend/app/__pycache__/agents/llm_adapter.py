import os
import requests
from typing import Optional
from dotenv import load_dotenv
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class LLMAdapter:
    """Simple LLM adapter supporting an `api` mode and a `stub` mode.

    - If `LLM_MODE=api`, it will POST to `LLM_API_URL` with `Authorization: Bearer {LLM_API_KEY}` and
      return the `text` field from a JSON response (adapt as needed for your provider).
    - If `LLM_MODE=stub` or env not configured, it returns a safe echo-style reply for testing.
    """

    def __init__(self):
        # Load .env if present so adapter works when called directly
        load_dotenv(override=True)
        self.mode = os.getenv("LLM_MODE", "stub")
        self.api_url = os.getenv("LLM_API_URL")
        self.api_key = os.getenv("LLM_API_KEY")
        self.provider = os.getenv("LLM_PROVIDER", "")
        self.model = os.getenv("LLM_MODEL", "")
        # GROQ-specific env (preferred if provider==groq)
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL")
        self.groq_api_url = os.getenv("GROQ_API_URL")
        try:
            self.groq_timeout = int(os.getenv("GROQ_TIMEOUT_S", "12"))
        except Exception:
            self.groq_timeout = 12
        try:
            self.groq_max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "350"))
        except Exception:
            self.groq_max_tokens = 350
        try:
            self.groq_temperature = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
        except Exception:
            self.groq_temperature = 0.2
        # If using GROQ provider, prefer GROQ_* env vars and prefer OpenAI-compatible base URL
        if self.provider.lower() == "groq":
            if self.groq_api_key:
                self.api_key = self.groq_api_key
            # Prefer an explicit GROQ_API_URL (expected to be an OpenAI-compatible base like
            # https://api.groq.com/openai/v1). If not provided but a model is set, use the
            # Groq OpenAI-compatible base; requests will target `/chat/completions`.
            if self.groq_api_url:
                self.api_url = self.groq_api_url
            elif not self.api_url and self.groq_model:
                self.api_url = "https://api.groq.com/openai/v1"
        self._session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429,500,502,503,504])
        self._session.mount("https://", HTTPAdapter(max_retries=retries))
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        if self.mode == "api":
            # ensure api_url/api_key available
            if not self.api_url or not self.api_key:
                raise RuntimeError("LLM API mode selected but LLM_API_URL or LLM_API_KEY is missing in env")
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

            # Provider-specific handling (Groq) - use OpenAI-compatible chat completions
            if self.provider.lower() == "groq":
                use_max_tokens = max_tokens or self.groq_max_tokens
                use_temp = temperature or self.groq_temperature
                timeout = self.groq_timeout

                # Determine endpoint: if api_url already contains the full chat/completions
                # path, use it; otherwise append `/chat/completions` to the base.
                if self.api_url.endswith("/chat/completions") or "/chat/completions" in self.api_url:
                    endpoint = self.api_url
                else:
                    endpoint = self.api_url.rstrip("/") + "/chat/completions"

                payload = {
                    "model": self.groq_model or self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": use_max_tokens,
                    "temperature": use_temp,
                }

                try:
                    resp = self._session.post(endpoint, json=payload, headers=headers, timeout=timeout)
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    if resp.status_code == 401:
                        logging.getLogger(__name__).error(
                            "Groq API 401 Unauthorized — check GROQ_API_KEY in .env "
                            "(key length=%d, prefix=%s...)",
                            len(self.api_key or ""), (self.api_key or "")[:8],
                        )
                    raise
                except Exception as e:
                    logging.getLogger(__name__).warning("Groq API request failed: %s", e)
                    raise

                data = resp.json()
                # OpenAI-compatible ChatCompletion response parsing
                if isinstance(data, dict):
                    if "choices" in data and len(data["choices"]) > 0:
                        choice0 = data["choices"][0]
                        # Chat message style
                        if isinstance(choice0, dict) and "message" in choice0 and isinstance(choice0["message"], dict) and "content" in choice0["message"]:
                            return choice0["message"]["content"]
                        # Older/text field style
                        if isinstance(choice0, dict) and "text" in choice0:
                            return choice0["text"]
                    # Groq-specific shapes (fallbacks)
                    if "outputs" in data and isinstance(data["outputs"], list) and len(data["outputs"]) > 0:
                        first = data["outputs"][0]
                        if isinstance(first, dict):
                            for k in ("content", "text", "output"):
                                if k in first:
                                    return first[k]
                        if isinstance(first, str):
                            return first
                    for key in ("text", "generated_text", "response", "output"):
                        if key in data:
                            return data[key]
                return str(data)

            # Generic provider fallback
            payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
            try:
                resp = self._session.post(self.api_url, json=payload, headers=headers, timeout=30)
                resp.raise_for_status()
            except Exception as e:
                logging.getLogger(__name__).warning("Generic API request failed: %s", e)
                raise
            data = resp.json()
            if isinstance(data, dict):
                for key in ("text", "generated_text", "response", "output"):
                    if key in data:
                        return data[key]
                if "choices" in data and len(data["choices"]) > 0 and "text" in data["choices"][0]:
                    return data["choices"][0]["text"]
            return str(data)

        # stub mode: be context-aware based on prompt content
        p = prompt.lower()
        if "crisis" in p or "suicide" in p or "self-harm" in p or "safety" in p:
            lines = [
                "I'm here with you. I hear how much pain you're in.",
                "It sounds like you're feeling overwhelmed and unsafe right now.",
                "Would you consider contacting a trusted person or a local helpline right now?",
                "If you are in immediate danger, please call your local emergency number.",
            ]
            return " ".join(lines)
        # non-crisis stub reply: helpful, complaint-resolution oriented
        lines = [
            "Thanks for letting me know. I can help with that.",
            "Could you give me a few more details about the complaint and what outcome you'd like?",
            "I can suggest next steps and draft a complaint message if you want.",
        ]
        return " ".join(lines)
