import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Form
from app.core.config import get_settings
from app.core.exceptions import UnsupportedFileError, FileTooLargeError
from app.schemas.extraction import TextExtractionRequest, ExtractionResponse, EvaluationResult
from app.services.extraction_service import run_extraction, run_extraction_from_image
from app.services.ocr_service import extract_text
from app.utils.file_utils import is_supported_file, get_file_extension
from app.eval.evaluator import run_evaluation

router = APIRouter()


@router.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.app_version,
        "provider": settings.default_provider,
    }


@router.post("/v1/extract", response_model=ExtractionResponse)
async def extract_file(
    file: UploadFile = File(...),
    document_type: str = Form("invoice"),
    provider: str | None = Form(None),
    require_strict_schema: bool = Form(True),
):
    if not is_supported_file(file.filename or ""):
        raise UnsupportedFileError(file.filename or "unknown")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    settings = get_settings()
    if size_mb > settings.max_file_size_mb:
        raise FileTooLargeError(size_mb, settings.max_file_size_mb)

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)
    tmp_name = f"{uuid.uuid4().hex}_{file.filename}"
    tmp_path = upload_dir / tmp_name

    try:
        tmp_path.write_bytes(content)
        ext = get_file_extension(file.filename or "")
        use_provider = provider or settings.default_provider

        if ext in (".png", ".jpg", ".jpeg") and use_provider in ("gemini", "gpt4"):
            return run_extraction_from_image(
                str(tmp_path), document_type, use_provider, require_strict_schema
            )
        else:
            text = extract_text(str(tmp_path))
            return run_extraction(text, document_type, use_provider, require_strict_schema)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.post("/v1/extract/text", response_model=ExtractionResponse)
def extract_from_text(req: TextExtractionRequest):
    return run_extraction(
        req.text, req.document_type, req.provider, req.require_strict_schema
    )


@router.post("/v1/evaluate", response_model=EvaluationResult)
def evaluate():
    return run_evaluation()
