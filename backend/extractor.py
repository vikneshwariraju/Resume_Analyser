"""Step 1: turn an uploaded file into clean text, or a clear error."""
import io
from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_BYTES = 5 * 1024 * 1024      # 5 MB limit
MIN_TEXT_CHARS = 50              # below this we treat the file as "no readable text"
ALLOWED = {".pdf", ".txt"}


class ExtractionError(Exception):
    """Raised with a user-friendly message; the API turns it into HTTP 400."""


def _ext(filename: str) -> str:
    return "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def extract_text(filename: str, data: bytes) -> str:
    if not data:
        raise ExtractionError("The file is empty.")
    if len(data) > MAX_BYTES:
        raise ExtractionError("File is too large (max 5 MB).")

    ext = _ext(filename)
    if ext not in ALLOWED:
        raise ExtractionError("Unsupported file type. Please upload a PDF or TXT file.")

    if ext == ".txt":
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1", errors="ignore")
    else:
        try:
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                raise ExtractionError("This PDF is password-protected.")
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        except ExtractionError:
            raise
        except (PdfReadError, Exception):
            raise ExtractionError("Could not read this PDF. It may be corrupted.")

    # keep line breaks (useful for the LLM), drop blank lines and extra spaces
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(text) < MIN_TEXT_CHARS:
        raise ExtractionError(
            "No readable text found. If this is a scanned PDF (image only), "
            "please upload a text-based PDF or a TXT file."
        )
    return text