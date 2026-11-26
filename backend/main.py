import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from extractor import extract_text, ExtractionError
from llm import generate, LLMError
from prompts import SYSTEM, SUMMARY_STYLES, LEVEL_FIELDS, build_summary_prompt
from analysis import extract_resume, resolve_fields

app = FastAPI(title="Resume Analyzer API")

# FRONTEND_ORIGIN = your deployed frontend URL (no trailing slash). Comma-separate several. Defaults to "*" for local dev.
ORIGINS = [o.strip().rstrip("/") for o in os.getenv("FRONTEND_ORIGIN", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")


def load_document(file: UploadFile | None, data: bytes | None, sample: str | None) -> tuple[str, str]:
    """Return (filename, text). An uploaded file wins; otherwise use a bundled sample."""
    try:
        if file is not None and file.filename:
            return file.filename, extract_text(file.filename, data or b"")
        if sample:
            safe = os.path.basename(sample)            # blocks path tricks like ../../etc
            path = os.path.join(SAMPLES_DIR, safe)
            if not os.path.isfile(path):
                raise HTTPException(status_code=404, detail="Sample not found.")
            with open(path, "rb") as f:
                return safe, extract_text(safe, f.read())
        raise HTTPException(status_code=400, detail="Upload a file or choose a sample.")
    except ExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))


def parse_options(style: str, level: str, focus: str | None):
    """Validate style/level/focus once, for every endpoint. Returns (focus_list, fields)."""
    if style not in SUMMARY_STYLES:
        raise HTTPException(status_code=400, detail=f"style must be one of {list(SUMMARY_STYLES)}")
    focus_list = None
    if focus:
        focus_list = list(dict.fromkeys(f.strip().lower() for f in focus.split(",") if f.strip())) or None
    try:
        fields = resolve_fields(level, focus_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return focus_list, fields


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/options")
def options():
    """The frontend builds its dropdowns and field checkboxes from this."""
    return {"styles": list(SUMMARY_STYLES), "levels": LEVEL_FIELDS}


@app.get("/api/samples")
def list_samples():
    if not os.path.isdir(SAMPLES_DIR):
        return {"samples": []}
    return {"samples": sorted(os.listdir(SAMPLES_DIR))}


@app.post("/api/extract-text")
async def extract_text_endpoint(file: UploadFile | None = File(None), sample: str | None = Form(None)):
    data = await file.read() if file else None
    name, text = load_document(file, data, sample)
    return {"filename": name, "characters": len(text), "text": text}


@app.post("/api/summarize")
async def summarize(
    file: UploadFile | None = File(None),
    sample: str | None = Form(None),
    style: str = Form("brief"),
    level: str = Form("standard"),
    focus: str | None = Form(None),      # comma-separated, e.g. "skills,education"
):
    focus_list, _ = parse_options(style, level, focus)
    data = await file.read() if file else None
    name, text = load_document(file, data, sample)
    try:
        summary = generate(build_summary_prompt(text, style, level, focus_list), system=SYSTEM)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"filename": name, "style": style, "level": level, "focus": focus_list, "summary": summary}


@app.post("/api/extract")
async def extract(
    file: UploadFile | None = File(None),
    sample: str | None = Form(None),
    level: str = Form("standard"),
    focus: str | None = Form(None),
):
    focus_list, _ = parse_options("brief", level, focus)
    data = await file.read() if file else None
    name, text = load_document(file, data, sample)
    try:
        result = extract_resume(text, level, focus_list)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"filename": name, **result}


@app.post("/api/analyze")
async def analyze(
    file: UploadFile | None = File(None),
    sample: str | None = Form(None),
    style: str = Form("brief"),
    level: str = Form("standard"),
    focus: str | None = Form(None),
):
    """One call for the frontend: summary + structured extraction with the same options."""
    focus_list, _ = parse_options(style, level, focus)
    data = await file.read() if file else None
    name, text = load_document(file, data, sample)
    try:
        summary = generate(build_summary_prompt(text, style, level, focus_list), system=SYSTEM)
        result = extract_resume(text, level, focus_list)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"filename": name, "style": style, "focus": focus_list, "summary": summary, **result}