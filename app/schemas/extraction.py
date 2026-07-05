from pydantic import BaseModel, Field


class TextExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    document_type: str = "invoice"
    provider: str | None = None
    require_strict_schema: bool = True


class ExtractionResponse(BaseModel):
    document_id: str
    document_type: str
    extracted_fields: dict
    confidence_score: float
    field_confidences: dict[str, float]
    validation_errors: list[str] = Field(default_factory=list)
    requires_human_review: bool
    warnings: list[str] = Field(default_factory=list)
    processing_time_ms: float
    provider_used: str
    raw_text_preview: str


class EvaluationResult(BaseModel):
    exact_match: bool
    field_accuracy: float
    missing_fields: list[str]
    extra_fields: list[str]
    mismatched_fields: dict[str, dict]
    latency_ms: float
