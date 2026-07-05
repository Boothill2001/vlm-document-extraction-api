from app.core.config import get_settings

REQUIRED_INVOICE_FIELDS = [
    "invoice_number", "invoice_date", "seller_name", "buyer_name",
    "total_amount", "currency",
]


def calculate_confidence(
    fields: dict,
    validation_errors: list[str],
    document_type: str = "invoice",
) -> tuple[float, dict[str, float], bool]:
    score = 1.0
    field_conf: dict[str, float] = {}

    required = REQUIRED_INVOICE_FIELDS if document_type == "invoice" else []

    for field in required:
        val = fields.get(field)
        if val is None or val == "" or val == []:
            score -= 0.10
            field_conf[field] = 0.0
        else:
            field_conf[field] = 1.0

    if not fields.get("line_items"):
        score -= 0.08
        field_conf["line_items"] = 0.0
    else:
        field_conf["line_items"] = 1.0

    for opt in ("subtotal", "tax", "payment_terms", "due_date"):
        val = fields.get(opt)
        if val is None or val == "":
            field_conf[opt] = 0.0
        else:
            field_conf[opt] = 1.0

    score -= 0.05 * len(validation_errors)

    score = round(max(0.0, min(1.0, score)), 3)

    threshold = get_settings().confidence_threshold
    needs_review = score < threshold or len(validation_errors) > 0

    return score, field_conf, needs_review
