import uuid
from app.services.llm_client import get_provider
from app.services.validation_service import validate_invoice
from app.services.confidence_service import calculate_confidence
from app.schemas.extraction import ExtractionResponse
from app.schemas.documents import DOCUMENT_SCHEMAS
from app.utils.timing import timer
from app.core.logging import logger


def run_extraction(
    text: str,
    document_type: str = "invoice",
    provider_name: str | None = None,
    require_strict_schema: bool = True,
) -> ExtractionResponse:
    doc_id = str(uuid.uuid4())[:12]
    warnings: list[str] = []

    provider = get_provider(provider_name)
    logger.info(f"[{doc_id}] Using provider: {provider.name}, doc_type: {document_type}")

    with timer() as t:
        raw_fields = provider.extract(text, document_type)

    extracted = raw_fields
    if require_strict_schema and document_type in DOCUMENT_SCHEMAS:
        schema_cls = DOCUMENT_SCHEMAS[document_type]
        try:
            parsed = schema_cls.model_validate(raw_fields)
            extracted = parsed.model_dump()
        except Exception as e:
            warnings.append(f"Schema validation warning: {e}")
            extracted = raw_fields

    if document_type == "invoice":
        validation_errors = validate_invoice(extracted)
    else:
        validation_errors = []

    confidence, field_conf, needs_review = calculate_confidence(
        extracted, validation_errors, document_type
    )

    if needs_review:
        warnings.append("Low confidence or validation errors — flagged for human review")

    logger.info(
        f"[{doc_id}] Done in {t['ms']}ms | confidence={confidence} | "
        f"errors={len(validation_errors)} | review={needs_review}"
    )

    return ExtractionResponse(
        document_id=doc_id,
        document_type=document_type,
        extracted_fields=extracted,
        confidence_score=confidence,
        field_confidences=field_conf,
        validation_errors=validation_errors,
        requires_human_review=needs_review,
        warnings=warnings,
        processing_time_ms=t["ms"],
        provider_used=provider.name,
        raw_text_preview=text[:300],
    )


def run_extraction_from_image(
    image_path: str,
    document_type: str = "invoice",
    provider_name: str | None = None,
    require_strict_schema: bool = True,
) -> ExtractionResponse:
    doc_id = str(uuid.uuid4())[:12]
    warnings: list[str] = []

    provider = get_provider(provider_name)
    logger.info(f"[{doc_id}] Vision extraction via {provider.name}, doc_type: {document_type}")

    if not hasattr(provider, "extract_from_image"):
        raise ValueError(f"Provider '{provider.name}' does not support image extraction")

    with timer() as t:
        raw_fields = provider.extract_from_image(image_path, document_type)

    extracted = raw_fields
    if require_strict_schema and document_type in DOCUMENT_SCHEMAS:
        schema_cls = DOCUMENT_SCHEMAS[document_type]
        try:
            parsed = schema_cls.model_validate(raw_fields)
            extracted = parsed.model_dump()
        except Exception as e:
            warnings.append(f"Schema validation warning: {e}")
            extracted = raw_fields

    if document_type == "invoice":
        validation_errors = validate_invoice(extracted)
    else:
        validation_errors = []

    confidence, field_conf, needs_review = calculate_confidence(
        extracted, validation_errors, document_type
    )

    if needs_review:
        warnings.append("Low confidence or validation errors — flagged for human review")

    logger.info(
        f"[{doc_id}] Done in {t['ms']}ms | confidence={confidence} | "
        f"errors={len(validation_errors)} | review={needs_review}"
    )

    return ExtractionResponse(
        document_id=doc_id,
        document_type=document_type,
        extracted_fields=extracted,
        confidence_score=confidence,
        field_confidences=field_conf,
        validation_errors=validation_errors,
        requires_human_review=needs_review,
        warnings=warnings,
        processing_time_ms=t["ms"],
        provider_used=f"{provider.name}-vision",
        raw_text_preview="[Image extracted via VLM]",
    )
