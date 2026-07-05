from pathlib import Path
from app.core.logging import logger


def extract_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".txt":
        return _load_txt(path)
    elif ext == ".pdf":
        return _load_pdf(path)
    elif ext in (".png", ".jpg", ".jpeg"):
        return _load_image_ocr(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pdf(path: Path) -> str:
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")

    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    result = "\n\n".join(text_parts)
    if not result.strip():
        logger.warning(f"PDF '{path.name}' yielded no text — may need OCR")
    return result


def _load_image_ocr(path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "pytesseract/Pillow not installed. For image OCR, install both. "
            "Alternatively, use .txt or .pdf files."
        )

    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image)
        if not text.strip():
            logger.warning(f"OCR on '{path.name}' yielded no text")
        return text
    except Exception as e:
        raise RuntimeError(
            f"OCR failed on '{path.name}': {e}. "
            "Ensure Tesseract is installed, or use .txt/.pdf files."
        )
