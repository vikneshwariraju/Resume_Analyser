"""Step 6: completeness score. The rules are explicit so the score can be explained line by line."""

# Points available per field. The score is normalised over the fields actually analysed,
# so a "basic" analysis is not penalised for fields it never asked for.
WEIGHTS = {
    "name": 15, "email": 15, "phone": 10, "skills": 20, "education": 15,
    "experience": 15, "projects": 5, "certifications": 3, "links": 2,
}

# Details expected inside each list entry.
ENTRY_KEYS = {
    "education": ("degree", "institution", "year"),
    "experience": ("role", "company", "duration"),
    "projects": ("name", "description"),
}

SKILLS_FULL_MARKS = 5     # 5 or more skills earns the full skills weight


def _field_score(field: str, value):
    """Return (score between 0 and 1, short explanation)."""
    if value is None:
        return 0.0, "Not found in the document"

    if field in ("name", "email", "phone"):
        return 1.0, "Found"

    if field == "skills":
        n = len(value)
        return min(n / SKILLS_FULL_MARKS, 1.0), f"{n} skill(s) found; {SKILLS_FULL_MARKS} or more earns full marks"

    if field in ("certifications", "links"):
        return 1.0, f"{len(value)} found"

    if field in ENTRY_KEYS:
        keys = ENTRY_KEYS[field]
        per_entry = [sum(1 for k in keys if e.get(k)) / len(keys) for e in value]
        avg = sum(per_entry) / len(per_entry)
        found = f"{round(avg * len(keys), 1):g}"
        return avg, f"{len(value)} entr{'y' if len(value) == 1 else 'ies'}; on average {found} of {len(keys)} details ({', '.join(keys)})"

    return 1.0, "Found"


def compute_completeness(data: dict, fields: list[str]) -> dict:
    items, earned, total = [], 0.0, 0
    for f in fields:
        weight = WEIGHTS.get(f, 0)
        score, note = _field_score(f, data.get(f))
        status = "complete" if score >= 1 else "partial" if score > 0 else "missing"
        items.append({"field": f, "weight": weight, "score": round(score, 2), "status": status, "note": note})
        earned += weight * score
        total += weight

    pct = round(earned / total * 100) if total else 0
    label = "Complete" if pct >= 85 else "Mostly complete" if pct >= 60 else "Needs more detail"
    return {"score": pct, "label": label, "fields": items}