from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}


def is_supported_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()
