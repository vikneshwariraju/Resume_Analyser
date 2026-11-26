
"""Completeness scoring based on explicit and explainable validation rules."""

WEIGHTS = {
    "name": 15,
    "email": 15,
    "phone": 10,
    "skills": 20,
    "education": 15,
    "experience": 15,
    "projects": 5,
    "certifications": 3,
    "links": 2,
}

ENTRY_KEYS = {
    "education": ("degree", "institution", "year"),
    "experience": ("role", "company", "duration"),
    "projects": ("name", "description"),
}

SKILLS_FULL_MARKS = 5


def _field_score(field: str, value):
    """Return a score between 0 and 1 with an explanation."""

    if value is None or value == [] or value == "":
        return 0.0, "Not found in the document"

    if field in ("name", "email", "phone"):
        return 1.0, "Found and validated"

    if field == "skills":
        n = len(value)
        score = min(n / SKILLS_FULL_MARKS, 1.0)

        return (
            score,
            f"{n} skill(s) found; "
            f"{SKILLS_FULL_MARKS} or more earns full marks"
        )

    if field in ("certifications", "links"):
        count = len(value)

        if count == 0:
            return 0.0, "Not found in the document"

        return 1.0, f"{count} found"

    if field in ENTRY_KEYS:

        keys = ENTRY_KEYS[field]

        if not value:
            return 0.0, "Not found in the document"

        per_entry = []

        for entry in value:
            available = sum(
                1 for key in keys
                if entry.get(key)
            )

            per_entry.append(available / len(keys))

        avg = sum(per_entry) / len(per_entry)

        found = f"{round(avg * len(keys), 1):g}"

        explanation = (
            f"{len(value)} entr{'y' if len(value) == 1 else 'ies'}; "
            f"on average {found} of {len(keys)} details "
            f"({', '.join(keys)})"
        )

        return avg, explanation

    return 1.0, "Found"


def compute_completeness(data: dict, fields: list[str]) -> dict:
    """Calculate completeness using only the fields actually analysed."""

    items = []
    earned = 0.0
    total = 0

    for field in fields:

        weight = WEIGHTS.get(field, 0)

        if weight == 0:
            continue

        score, note = _field_score(
            field,
            data.get(field)
        )

        status = (
            "complete" if score >= 1
            else "partial" if score > 0
            else "missing"
        )

        items.append({
            "field": field,
            "weight": weight,
            "score": round(score, 2),
            "status": status,
            "note": note
        })

        earned += weight * score
        total += weight

    percentage = (
        round(earned / total * 100)
        if total else 0
    )

    label = (
        "Complete" if percentage >= 85
        else "Mostly complete" if percentage >= 60
        else "Needs more detail"
    )

    return {
        "score": percentage,
        "label": label,
        "fields": items
    }
