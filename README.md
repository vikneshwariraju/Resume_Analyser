# Resume Analyzer: AI-Powered Document Intelligence (Task 2)

Upload a resume (PDF or TXT) and get an AI summary, structured details as validated JSON, a skills chart and a completeness score. Anything the AI cannot find in the document is returned as `null` and marked as missing, never guessed.

- **Live demo:** `<paste your Vercel URL>`
- **Note for reviewers:** the backend runs on Render's free tier and sleeps when idle. The first request after a quiet period can take 30 to 60 seconds. Open the demo once, wait for the page to say it is connected, then test.

## Features

| Requirement | Where it lives |
|---|---|
| PDF/TXT upload, sample documents, graceful errors | `backend/extractor.py`, `backend/samples/` |
| Summary with selectable style (brief, detailed, bullet points) | `backend/prompts.py`, `backend/llm.py` |
| Structured extraction as JSON, `null` for missing values | `backend/schemas.py`, `backend/analysis.py` |
| Analysis levels (basic, standard, detailed) and focus fields | `backend/prompts.py` (`LEVEL_FIELDS`), `backend/analysis.py` |
| Visual insight: skills by category chart | `backend/insights.py`, `frontend/src/components/SkillsChart.jsx` |
| Review UI, missing/uncertain flags, completeness score | `frontend/src/components/`, `backend/scoring.py` |

## Technologies

- **Backend:** Python, FastAPI, Uvicorn, Pydantic v2, pypdf, python-dotenv
- **Frontend:** React 18, Vite (plain CSS, no chart library)
- **AI:** Google Gemini through the `google-genai` SDK (Google AI Studio free tier). The model is set with `GEMINI_MODEL` (tested with `gemini-3.5-flash`), with optional backups in `GEMINI_FALLBACK_MODELS`.
- **Hosting:** Render (backend), Vercel (frontend)

## Environment variables

Backend (`backend/.env` locally, Render dashboard in production):

| Name | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | yes | Google AI Studio API key |
| `GEMINI_MODEL` | no | Main model name (see `python list_models.py`) |
| `GEMINI_FALLBACK_MODELS` | no | Comma-separated backup models used when the main one is busy or over quota |
| `FRONTEND_ORIGIN` | production | Deployed frontend URL, no trailing slash (CORS). Defaults to `*` locally |

Frontend (`frontend/.env` locally, Vercel dashboard in production):

| Name | Purpose |
|---|---|
| `VITE_API_URL` | Backend URL, e.g. `http://127.0.0.1:8000` locally |

No secrets are included in this repository. Copy `.env.example` files and fill in your own values.

## Run locally

Requirements: Python 3.11+, Node.js 18+, a free Gemini API key from https://aistudio.google.com/apikey

```bash
# 1. Backend
cd backend
python -m venv venv
venv\Scripts\activate            # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env  then add GEMINI_API_KEY
python list_models.py            # optional: shows which models your key can use
uvicorn main:app --reload        # http://127.0.0.1:8000  (API docs at /docs)

# 2. Frontend (second terminal)
cd frontend
copy .env.example .env
npm install
npm run dev                      # http://localhost:5173
```

## How to test the main features

1. **Sample, complete:** choose `sample_resume_1.txt`, level Detailed, style Bullet points. Expect a high completeness score and a populated skills chart.
2. **Sample, incomplete:** choose `sample_resume_2_incomplete.txt`. Email, phone and experience appear as amber "Not found" rows, nothing is invented, and the score is lower.
3. **Your own PDF:** upload a text-based resume PDF.
4. **Levels:** Basic returns 3 fields, Standard 6, Detailed 9.
5. **Focus:** tick only "Skills" and "Education". Only those fields are extracted and scored, and the summary emphasises them.
6. **Error handling:** try an empty file, a `.docx` file, or a scanned (image-only) PDF. Each returns a clear message instead of failing.

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Health check |
| `GET /api/options` | Summary styles and the fields available at each level |
| `GET /api/samples` | Bundled sample documents |
| `POST /api/extract-text` | Extracted text only |
| `POST /api/summarize` | Summary only |
| `POST /api/extract` | Structured extraction only |
| `POST /api/analyze` | Summary, extraction, completeness and insights in one call (used by the UI) |

Form fields: `file` or `sample`, `style`, `level`, `focus` (comma-separated field names).

## How it works

**Text extraction.** `pypdf` reads text from PDFs and TXT files are decoded directly. The extractor rejects empty files, unsupported types, files over 5 MB, corrupted or password-protected PDFs, and PDFs with no readable text (scanned images).

**Summaries.** One prompt per style (brief, detailed, bullets). A system prompt tells the model to use only information in the document. The level adds a depth instruction, and focus fields add an instruction to emphasise those parts.

**Structured extraction and validation.** The prompt asks for JSON in an exact shape built from the selected fields. The response then passes four checks:
1. JSON parsing, tolerating markdown code fences, with one retry if the output is malformed.
2. Pydantic schema validation. Every field is optional, and blank or placeholder values ("N/A", "none") become `null`.
3. A grounding check: the name, email, skills, certifications, links, institutions and companies must actually appear in the source text. Values that do not are set to `null` or removed, and a warning is shown. Emails must also match an email pattern.
4. Cleanup: duplicates and all-null entries are removed, and empty lists become `null`.

**Analysis levels and focus.**

| Level | Fields extracted | Summary depth |
|---|---|---|
| Basic | name, email, skills | short, high-level |
| Standard | adds phone, education, experience | balanced |
| Detailed | adds projects, certifications, links | thorough |

Focus narrows a level to the chosen fields. Only requested fields are returned, so "not requested" is never confused with "not found".

**Completeness score.** Each field has a weight (name 15, email 15, phone 10, skills 20, education 15, experience 15, projects 5, certifications 3, links 2). A field earns its full weight when complete, partial credit when some expected details are missing, and nothing when absent. Skills earn full marks at 5 or more. Education, experience and projects are scored by the share of expected details present in each entry. The score is points earned divided by points available for the fields in the current analysis. 85% and above is "Complete", 60 to 84% "Mostly complete", below 60% "Needs more detail".

**Visual insight.** Skills are grouped into categories (AI and machine learning, backend, databases, frontend, languages, tools) with keyword rules and drawn as bars. This is deterministic, needs no extra AI call, and always matches the extracted data.

**Reliability.** All Gemini calls go through `backend/llm.py`. Server errors (500, 503, 504) are retried with a short wait. Quota errors (429) or exhausted retries move to the next model in `GEMINI_FALLBACK_MODELS`. Failures are shown to the user as plain-language messages.

## Known limitations

- Scanned or image-only PDFs are rejected with a message. OCR is not implemented.
- Designed for resumes. Other document types are summarised, but the extracted fields are resume-specific.
- Skill categories use keyword rules, so uncommon skills appear under "Other".
- The grounding check matches text exactly. A correct value that the model reworded can occasionally be dropped and flagged.
- Layout-heavy PDFs (multi-column, tables) can produce jumbled text, which lowers extraction quality.
- Free-tier Gemini has rate limits and occasional high-demand errors. Backup models reduce this but cannot remove it.
- Each analysis makes two model calls (summary and extraction).
- No user accounts or storage: uploaded files are processed in memory and not saved.

## Possible improvements

- OCR for scanned PDFs.
- One combined model call for summary and extraction to halve quota use.
- DOCX support and additional document types with their own schemas.
- Per-field confidence from the model, alongside the grounding check.
- Automated tests for the validation and scoring rules.