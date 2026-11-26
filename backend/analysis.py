
"""Resume extraction: field selection, LLM extraction, validation and grounding."""

import json
import re

from pydantic import ValidationError

from llm import generate, LLMError
from prompts import SYSTEM, LEVEL_FIELDS, build_extraction_prompt
from schemas import Resume
from scoring import compute_completeness
from insights import build_insights


EMAIL_RE = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def resolve_fields(level: str, focus: list[str] | None) -> list[str]:
    """Resolve requested fields based on analysis level and focus."""

    if level not in LEVEL_FIELDS:
        raise ValueError(
            f"level must be one of {list(LEVEL_FIELDS)}"
        )

    allowed = LEVEL_FIELDS[level]

    if not focus:
        return list(allowed)

    bad = [field for field in focus if field not in allowed]

    if bad:
        raise ValueError(
            f"Field(s) {bad} are not available at the "
            f"'{level}' level. Allowed: {allowed}"
        )

    return [field for field in allowed if field in focus]


def _norm(value: str) -> str:
    """Normalize text for comparison."""
    return " ".join(value.lower().split())


def _parse_json(raw: str) -> dict:
    """Parse JSON returned by the LLM, including fenced responses."""

    raw = raw.strip()

    raw = re.sub(
        r"^\s*```(?:json)?\s*",
        "",
        raw,
        flags=re.IGNORECASE
    )

    raw = re.sub(r"\s*```\s*$", "", raw)

    return json.loads(raw)


def _dedupe_entries(
    entries: list,
    identity_fields: list[str]
) -> tuple[list, int]:
    """Remove duplicate entries while preserving original order."""

    seen = set()
    unique = []

    for item in entries:

        signature = tuple(
            _norm(str(item.get(field) or ""))
            for field in identity_fields
        )

        # Keep entries that do not have enough information to identify them.
        if not any(signature):
            unique.append(item)
            continue

        if signature not in seen:
            seen.add(signature)
            unique.append(item)

    return unique, len(entries) - len(unique)


def _ground(
    resume: Resume,
    source_text: str
) -> tuple[dict, list]:
    """Verify extracted values against source text."""

    text = _norm(source_text)
    warnings = []
    data = resume.model_dump()

    def found(value: str) -> bool:
        return _norm(value) in text

    # Name
    if data["name"] and not found(data["name"]):
        warnings.append(
            "Name could not be verified in the document, so it was set to null."
        )
        data["name"] = None

    # Email
    if data["email"]:
        if not EMAIL_RE.match(data["email"]):
            warnings.append(
                "Email format looks invalid, so it was set to null."
            )
            data["email"] = None
        elif not found(data["email"]):
            warnings.append(
                "Email could not be verified in the document, so it was set to null."
            )
            data["email"] = None

    # Phone: basic normalization before source verification.
    if data["phone"]:
        phone_digits = re.sub(r"\D", "", data["phone"])
        source_digits = re.sub(r"\D", "", source_text)

        if len(phone_digits) < 7 or phone_digits not in source_digits:
            warnings.append(
                "Phone number could not be verified, so it was set to null."
            )
            data["phone"] = None

    # Skills, certifications and links
    for key, label in (
        ("skills", "skill"),
        ("certifications", "certification"),
        ("links", "link")
    ):
        if data[key]:
            seen = set()
            kept = []

            for value in data[key]:
                value = (value or "").strip()
                normalized = _norm(value)

                if value and normalized not in seen and found(value):
                    seen.add(normalized)
                    kept.append(value)

            dropped = len(data[key]) - len(kept)

            if dropped:
                warnings.append(
                    f"{dropped} {label}(s) were removed because "
                    "they were duplicates, blank or not found in the document."
                )

            data[key] = kept or None

    # Education
    for item in data["education"] or []:
        institution = item.get("institution")

        if institution and not found(institution):
            warnings.append(
                "An institution name could not be verified, so it was set to null."
            )
            item["institution"] = None

    # Experience
    for item in data["experience"] or []:
        company = item.get("company")

        if company and not found(company):
            warnings.append(
                "A company name could not be verified, so it was set to null."
            )
            item["company"] = None

    # Remove empty entries and duplicate entries.
    dedupe_config = {
        "education": ["institution", "degree", "year"],
        "experience": ["company", "role", "duration"],
        "projects": ["name"]
    }

    for key, identity_fields in dedupe_config.items():

        entries = [
            item
            for item in (data[key] or [])
            if any(
                value is not None and (
                    bool(value.strip()) if isinstance(value, str)
                    else bool(value)
                )
                for value in item.values()
            )
        ]

        unique_entries, duplicates = _dedupe_entries(
            entries,
            identity_fields
        )

        if duplicates:
            warnings.append(
                f"{duplicates} duplicate {key} entry/entries were removed."
            )

        data[key] = unique_entries or None

    return data, warnings


def extract_resume(
    text: str,
    level: str = "standard",
    focus: list[str] | None = None
) -> dict:
    """Extract, validate and ground resume information."""

    fields = resolve_fields(level, focus)
    resume = None

    # Retry once if the model returns invalid JSON or schema data.
    for attempt in range(2):

        raw = generate(
            build_extraction_prompt(text, fields),
            system=SYSTEM,
            temperature=0,
            json_mode=True
        )

        try:
            parsed = _parse_json(raw)
            resume = Resume.model_validate(parsed)
            break

        except (json.JSONDecodeError, ValidationError):
            if attempt == 1:
                raise LLMError(
                    "The AI returned data in an unexpected format. "
                    "Please try again."
                )

    if resume is None:
        raise LLMError(
            "Unable to extract resume information. Please try again."
        )

    data, warnings = _ground(resume, text)

    # Only return requested fields.
    data = {
        key: data[key]
        for key in fields
    }

    missing = [
        key
        for key in fields
        if data[key] is None
    ]

    return {
        "level": level,
        "fields": fields,
        "data": data,
        "missing_fields": missing,
        "warnings": warnings,
        "completeness": compute_completeness(data, fields),
        "insights": build_insights(data)
    }
