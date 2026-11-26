"""Optional AI illustration. The backend calls the image service so the API key never reaches the browser."""
import os
import urllib.error
import urllib.parse
import urllib.request

from dotenv import load_dotenv
from insights import IMAGE_PROMPT_PREFIX

load_dotenv()

BASE = os.getenv("IMAGE_API_BASE", "https://gen.pollinations.ai/image")
MAX_PROMPT = 700
MAX_BYTES = 8 * 1024 * 1024


class VisualError(Exception):
    """User-friendly message plus the HTTP status the API should return."""

    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


def fetch_visual(prompt: str, seed: int) -> tuple[bytes, str]:
    key = os.getenv("POLLINATIONS_API_KEY")
    if not key:
        raise VisualError("The AI visual is not set up on this server. The skills chart still shows the full breakdown.", 503)
    # Only our own prompt template is accepted, so this endpoint cannot be used as a free general image generator.
    if not prompt.startswith(IMAGE_PROMPT_PREFIX) or len(prompt) > MAX_PROMPT:
        raise VisualError("Invalid image prompt.", 400)

    query = urllib.parse.urlencode({"model": "flux", "width": 1024, "height": 576, "nologo": "true", "seed": seed})
    url = f"{BASE}/{urllib.parse.quote(prompt, safe='')}?{query}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "resume-analyzer"})

    try:
        with urllib.request.urlopen(request, timeout=75) as resp:
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise VisualError("The image service rejected the API key.")
        if e.code == 402:
            raise VisualError("The image service has no credit left.")
        raise VisualError("The image service is busy right now. Try again in a moment.")
    except (urllib.error.URLError, TimeoutError, OSError):
        raise VisualError("The image service did not respond. Try again in a moment.")

    if not content_type.startswith("image/") or not body:
        raise VisualError("The image service returned an unexpected response.")
    return body, content_type