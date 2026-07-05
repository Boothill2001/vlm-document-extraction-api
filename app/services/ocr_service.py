from app.services.document_loader import extract_text_from_file
from app.core.logging import logger


def extract_text(file_path: str) -> str:
    logger.info(f"Extracting text from: {file_path}")
    text = extract_text_from_file(file_path)
    logger.info(f"Extracted {len(text)} characters")
    return text
