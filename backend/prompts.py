"""Prompt templates and level/field definitions. Kept out of the routes so they are easy to explain and tweak."""

MAX_CHARS = 30_000   # resumes are short; this protects against huge files

SYSTEM = (
    "You are a careful resume analysis assistant. "
    "Use ONLY information that appears in the document. "
    "Never invent names, companies, dates, skills or numbers. "
    "If something is not in the document, do not mention it."
)

# ---------- summary styles (format) ----------
SUMMARY_STYLES = {
    "brief": "Write a brief summary in 2-3 sentences: who the candidate is, their main strengths, and their most relevant experience.",
    "detailed": (
        "Write a detailed summary in 2-3 short paragraphs covering: background and education, "
        "technical skills, work experience and projects, and key strengths. Mention concrete details from the resume."
    ),
    "bullets": (
        "Write a bullet-point summary using '- ' bullets under these headings: "
        "Profile, Education, Skills, Experience, Key Highlights. Skip a heading if the resume has nothing for it."
    ),
}

# ---------- analysis levels (depth) ----------
LEVEL_FIELDS = {
    "basic": ["name", "email", "skills"],
    "standard": ["name", "email", "phone", "skills", "education", "experience"],
    "detailed": ["name", "email", "phone", "skills", "education", "experience",
                 "projects", "certifications", "links"],
}

DEPTH = {
    "basic": "Keep the summary short and high-level.",
    "standard": "Use a balanced level of detail.",
    "detailed": "Be thorough: include concrete details such as technologies, durations, projects and achievements.",
}

FIELD_SPECS = {
    "name": '"name": string or null',
    "email": '"email": string or null',
    "phone": '"phone": string or null',
    "skills": '"skills": [string, ...] or null',
    "education": '"education": [{"degree": string or null, "institution": string or null, "year": string or null, "score": string or null}, ...] or null',
    "experience": '"experience": [{"role": string or null, "company": string or null, "duration": string or null, "description": string or null}, ...] or null',
    "projects": '"projects": [{"name": string or null, "description": string or null, "technologies": [string, ...] or null}, ...] or null',
    "certifications": '"certifications": [string, ...] or null',
    "links": '"links": [string, ...] or null',
}

FIELD_RULES = {
    "education": "'score' is the CGPA or percentage, if given.",
    "experience": "'experience' means jobs and internships only (not academic projects); 'description' is at most one short sentence from the resume.",
    "projects": "'projects' are personal or academic projects; 'description' is at most one short sentence; list 'technologies' only if the resume names them.",
    "links": "'links' are URLs or profile links (LinkedIn, GitHub, portfolio) exactly as written.",
}


def build_summary_prompt(doc_text: str, style: str, level: str = "standard", focus: list[str] | None = None) -> str:
    focus_line = f"Pay special attention to these parts of the resume: {', '.join(focus)}.\n" if focus else ""
    return (
        f"{SUMMARY_STYLES[style]}\n"
        f"{DEPTH[level]}\n"
        f"{focus_line}"
        "Highlight the most important findings (strongest skills, standout projects, notable achievements).\n"
        "Do not repeat the same job, internship, company, or project heading. "
        "Combine multiple achievements from the same role under one heading or bullet. "
        "Keep each experience entry together instead of repeating its role and company for every achievement.\n\n"
        f"RESUME:\n\"\"\"\n{doc_text[:MAX_CHARS]}\n\"\"\""
    )


def build_extraction_prompt(doc_text: str, fields: list[str]) -> str:
    shape = "{\n  " + ",\n  ".join(FIELD_SPECS[f] for f in fields) + "\n}"
    rules = [FIELD_RULES[f] for f in fields if f in FIELD_RULES]
    rule_text = "".join(f"- {r}\n" for r in rules)
    return (
        "Extract the following fields from the resume and return ONLY valid JSON in exactly this shape:\n"
        f"{shape}\n\n"
        "Rules:\n"
        "- If a field or value is not present in the resume, use null. Never guess or invent.\n"
        "- Copy names, emails, skills, institutions and companies exactly as written in the resume.\n"
        f"{rule_text}"
        "- No markdown, no explanations, only the JSON object.\n\n"
        f"RESUME:\n\"\"\"\n{doc_text[:MAX_CHARS]}\n\"\"\""
    )