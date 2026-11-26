"""Steps 3-4: choose fields by level/focus -> LLM extraction -> schema validation -> grounding check."""
import json
import re
from pydantic import ValidationError

from llm import generate, LLMError
from prompts import SYSTEM, LEVEL_FIELDS, build_extraction_prompt
from schemas import Resume
from scoring import compute_completeness
from insights import build_insights

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def resolve_fields(level: str, focus: list[str] | None) -> list[str]:
    """Level decides which fields are available; focus narrows them down. Raises ValueError if invalid."""
    if level not in LEVEL_FIELDS:
        raise ValueError(f"level must be one of {list(LEVEL_FIELDS)}")
    allowed = LEVEL_FIELDS[level]
    if not focus:
        return allowed
    bad = [f for f in focus if f not in allowed]
    if bad:
        raise ValueError(f"Field(s) {bad} are not available at the '{level}' level. Allowed: {allowed}")
    return [f for f in allowed if f in focus]      # keep the canonical order


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _parse_json(raw: str):
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())   # strip ```json fences if present
    return json.loads(raw)


def _ground(resume: Resume, source_text: str):
    """Keep only values that actually appear in the document. Returns (dict, warnings)."""
    text = _norm(source_text)
    warnings = []
    data = resume.model_dump()

    def found(value: str) -> bool:
        return _norm(value) in text

    if data["name"] and not found(data["name"]):
        warnings.append("Name could not be verified in the document, so it was set to null.")
        data["name"] = None

    if data["email"]:
        if not EMAIL_RE.match(data["email"]):
            warnings.append("Email format looks invalid, so it was set to null.")
            data["email"] = None
        elif not found(data["email"]):
            warnings.append("Email could not be verified in the document, so it was set to null.")
            data["email"] = None

    for key, label in (("skills", "skill"), ("certifications", "certification"), ("links", "link")):
        if data[key]:
            seen, kept = set(), []
            for s in data[key]:
                s = (s or "").strip()
                if s and s.lower() not in seen and found(s):
                    seen.add(s.lower())
                    kept.append(s)
            dropped = len(data[key]) - len(kept)
            if dropped:
                warnings.append(f"{dropped} {label}(s) were removed because they are duplicates, blank or not in the document.")
            data[key] = kept or None

    for item in data["education"] or []:
        if item["institution"] and not found(item["institution"]):
            warnings.append("An institution name could not be verified, so it was set to null.")
            item["institution"] = None
    for item in data["experience"] or []:
        if item["company"] and not found(item["company"]):
            warnings.append("A company name could not be verified, so it was set to null.")
            item["company"] = None

    # drop list entries where every field is null, and turn empty lists into null
    for key in ("education", "experience", "projects"):
        entries = [e for e in (data[key] or []) if any(v is not None for v in e.values())]
        data[key] = entries or None

    return data, warnings


def extract_resume(text: str, level: str = "standard", focus: list[str] | None = None) -> dict:
    fields = resolve_fields(level, focus)
    resume = None
    for _ in range(2):   # one retry if the model returns bad JSON
        raw = generate(build_extraction_prompt(text, fields), system=SYSTEM, temperature=0, json_mode=True)
        try:
            resume = Resume.model_validate(_parse_json(raw))
            break
        except (json.JSONDecodeError, ValidationError):
            continue
    if resume is None:
        raise LLMError("The AI returned data in an unexpected format. Please try again.")

    data, warnings = _ground(resume, text)
    data = {k: data[k] for k in fields}                       # only requested fields are returned
    missing = [k for k in fields if data[k] is None]          # "missing" = requested but not found
    return {"level": level, "fields": fields, "data": data,
            "missing_fields": missing, "warnings": warnings,
            "completeness": compute_completeness(data, fields),
            "insights": build_insights(data)}