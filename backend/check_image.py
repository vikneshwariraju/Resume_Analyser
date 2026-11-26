"""Run: python check_image.py   (or: python check_image.py model-a model-b)
Tests whether your Gemini API key can generate images, using the image models from list_models.py.
If one works it saves test_image.png in this folder."""
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

DEFAULTS = ["gemini-3.1-flash-image", "gemini-2.5-flash-image", "gemini-3.1-flash-lite-image", "gemini-nano-banana-2.1"]
PROMPT = ("Clean flat vector infographic illustration with simple icons and connected nodes representing "
          "software skills, teal and amber colors on a white background, no text, no letters")

for model in (sys.argv[1:] or DEFAULTS):
    done = False
    for modalities in (["IMAGE"], ["TEXT", "IMAGE"]):
        try:
            resp = client.models.generate_content(
                model=model, contents=PROMPT,
                config=types.GenerateContentConfig(response_modalities=modalities),
            )
            parts = (resp.candidates[0].content.parts or []) if resp.candidates else []
            image = next((p.inline_data for p in parts if getattr(p, "inline_data", None)), None)
            if image:
                with open("test_image.png", "wb") as f:
                    f.write(image.data)
                print(f"OK       {model}  -> saved test_image.png ({len(image.data) // 1024} KB, {image.mime_type})")
                done = True
            else:
                print(f"NO IMAGE {model}  (modalities {modalities}) -> the model answered without an image")
        except errors.APIError as e:
            msg = (e.message or "").replace("\n", " ")[:150]
            print(f"FAIL {e.code}  {model}  (modalities {modalities}) -> {msg}")
        except Exception as e:
            print(f"ERROR    {model}  -> {str(e)[:150]}")
        if done:
            break
    if done:
        break