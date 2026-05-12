import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

try:
    import docx
except ImportError:  # pragma: no cover
    docx = None


def extract_text_from_pdf(path: str) -> str:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber není nainstalovaný. Nainstalujte závislosti.")
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    result = "\n".join(text)
    logger.debug("Extrahovaný text z PDF: %d znaků", len(result))
    return result


def extract_text_from_docx(path: str) -> str:
    if docx is None:
        raise RuntimeError("python-docx není nainstalovaný. Nainstalujte závislosti.")
    document = docx.Document(path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    result = "\n".join(paragraphs)
    logger.debug("Extrahovaný text z DOCX: %d znaků", len(result))
    return result


def extract_text_from_file(path: str) -> str:
    path_obj = Path(path)
    ext = path_obj.suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".docx":
        return extract_text_from_docx(path)
    raise ValueError(f"Nepodporovaný formát souboru: {ext}")
