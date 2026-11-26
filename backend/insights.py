"""Step 6: visual insight. Groups extracted skills into categories with simple keyword rules.
Deterministic and free (no extra AI call), so the chart always matches the extracted data."""
import re

# Order matters: the first category with a matching keyword wins (e.g. "SQL" is a database, not a language).
CATEGORIES = [
    ("Databases", ["sql", "mysql", "postgresql", "postgres", "mongodb", "sqlite", "redis", "chromadb",
                   "pinecone", "faiss", "firebase", "oracle", "dynamodb", "vector database"]),
    ("AI and machine learning", [
        "machine learning", "deep learning", "rag", "llm", "langchain", "langgraph", "hugging face", "embeddings",
        "semantic search", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras", "svm", "random forest",
        "knn", "neural networks", "transformer", "attention", "nlp", "computer vision", "opencv", "whisper", "ocr",
        "model evaluation", "feature extraction", "mfcc", "librosa", "numpy", "pandas", "spectral",
        "zero-crossing", "prompt engineering", "generative ai", "xgboost"]),
    ("Frontend", ["react", "html", "css", "tailwind", "bootstrap", "next.js", "nextjs", "vue", "angular",
                  "redux", "vite", "jquery", "streamlit"]),
    ("Backend and APIs", ["fastapi", "django", "flask", "node", "express", "spring", "rest", "api", "apis",
                          "graphql", "jwt", "microservices", "websocket"]),
    ("Programming languages", ["python", "java", "javascript", "typescript", "c", "c++", "c#", "go", "golang",
                               "rust", "kotlin", "swift", "php", "ruby", "r", "scala", "bash", "matlab"]),
    ("Tools and deployment", ["git", "github", "gitlab", "docker", "kubernetes", "github actions", "postman",
                              "render", "netlify", "vercel", "aws", "azure", "gcp", "linux", "jenkins", "ci/cd",
                              "jira", "vs code", "heroku", "nginx"]),
]


def _matches(skill: str, keyword: str) -> bool:
    pattern = r"(?<![a-z0-9+#])" + re.escape(keyword) + r"(?![a-z0-9+#])"
    return re.search(pattern, skill) is not None


def categorize(skill: str) -> str:
    s = skill.lower()
    for category, keywords in CATEGORIES:
        if any(_matches(s, k) for k in keywords):
            return category
    return "Other"


def build_insights(data: dict) -> dict:
    skills = data.get("skills")
    if not skills:
        return {"skill_categories": None}
    groups: dict[str, list[str]] = {}
    for s in skills:
        groups.setdefault(categorize(s), []).append(s)
    cats = [{"category": c, "count": len(v), "skills": v} for c, v in groups.items()]
    cats.sort(key=lambda c: (c["category"] == "Other", -c["count"]))   # biggest first, "Other" last
    return {"skill_categories": cats}