"""Run: python check_models.py   (or: python check_models.py model-a model-b)
Sends a tiny prompt to each model and shows which ones work with your key right now."""
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

DEFAULTS = [
    "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-flash-lite",
]
models = sys.argv[1:] or DEFAULTS

for m in models:
    try:
        r = client.models.generate_content(model=m, contents="Reply with the single word: ok")
        print(f"OK       {m}  -> {r.text.strip()[:20]}")
    except errors.APIError as e:
        msg = (e.message or "").replace("\n", " ")[:160]
        print(f"FAIL {e.code}  {m}  -> {msg}")
    except Exception as e:
        print(f"ERROR    {m}  -> {e}")