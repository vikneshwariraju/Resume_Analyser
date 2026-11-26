"""One small wrapper around Gemini. All LLM calls in the app go through generate().

Reliability on the free tier:
  - 500/503/504 (Google is busy): retry the same model with a short wait
  - 429 (quota) or retries used up: move on to the next model in GEMINI_FALLBACK_MODELS
  - everything is turned into a plain-language LLMError for the API layer
"""
import logging
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

log = logging.getLogger("uvicorn.error")   # shows up in the uvicorn terminal

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACKS = [m.strip() for m in os.getenv("GEMINI_FALLBACK_MODELS", "").split(",") if m.strip()]
_client = None


class LLMError(Exception):
    """User-friendly error message; the API turns it into HTTP 502."""


def _get_client():
    global _client
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise LLMError("Server is missing GEMINI_API_KEY.")
    if _client is None:
        _client = genai.Client(api_key=key)
    return _client


def _friendly(code) -> LLMError:
    if code == 429:
        return LLMError("AI rate limit reached (free tier). Wait a minute and try again.")
    if code in (500, 503, 504):
        return LLMError("The AI service is busy right now. Wait a few seconds and try again.")
    if code in (400, 403):
        return LLMError("AI request was rejected. Check GEMINI_API_KEY and GEMINI_MODEL.")
    if code == 404:
        return LLMError("AI model not found. Update GEMINI_MODEL.")
    return LLMError(f"AI service error ({code}). Please try again.")


def generate(prompt: str, system: str | None = None, temperature: float = 0.2,
             json_mode: bool = False, retries: int = 3) -> str:
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json" if json_mode else None,
    )
    models = [MODEL] + [m for m in FALLBACKS if m != MODEL]
    last_code = None

    for i, model in enumerate(models):
        has_next = i < len(models) - 1
        for attempt in range(retries):
            try:
                resp = client.models.generate_content(model=model, contents=prompt, config=config)
                text = resp.text
                if not text:
                    raise LLMError("The AI returned an empty response. Please try again.")
                return text.strip()
            except errors.APIError as e:
                last_code = e.code
                log.warning("Gemini %s attempt %d/%d failed: code=%s", model, attempt + 1, retries, e.code)
                if e.code in (500, 503, 504) and attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))      # 2s, 4s
                    continue
                if has_next and e.code in (404, 429, 500, 503, 504):
                    break                              # try the next model
                raise _friendly(e.code)
    raise _friendly(last_code)