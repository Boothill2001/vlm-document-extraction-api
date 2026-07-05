import json
from pathlib import Path
from app.services.extraction_service import run_extraction
from app.schemas.extraction import EvaluationResult
from app.utils.timing import timer


SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "samples"
GROUND_TRUTH_PATH = SAMPLE_DIR / "sample_invoice_ground_truth.json"
SAMPLE_INVOICE_PATH = SAMPLE_DIR / "sample_invoice.txt"

COMPARE_FIELDS = [
    "invoice_number", "invoice_date", "seller_name", "buyer_name",
    "currency", "subtotal", "tax", "total_amount", "payment_terms", "due_date",
]


def run_evaluation() -> EvaluationResult:
    text = SAMPLE_INVOICE_PATH.read_text(encoding="utf-8")
    ground_truth = json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))

    with timer() as t:
        result = run_extraction(text, "invoice", "mock")

    extracted = result.extracted_fields

    missing = []
    extra = []
    mismatched = {}
    matched = 0

    for field in COMPARE_FIELDS:
        gt_val = ground_truth.get(field)
        ex_val = extracted.get(field)

        if gt_val is not None and ex_val is None:
            missing.append(field)
        elif gt_val is None and ex_val is not None:
            extra.append(field)
        elif _normalize(gt_val) != _normalize(ex_val):
            mismatched[field] = {"expected": gt_val, "got": ex_val}
        else:
            matched += 1

    total = len(COMPARE_FIELDS)
    accuracy = round(matched / total, 4) if total else 0.0

    return EvaluationResult(
        exact_match=len(mismatched) == 0 and len(missing) == 0,
        field_accuracy=accuracy,
        missing_fields=missing,
        extra_fields=extra,
        mismatched_fields=mismatched,
        latency_ms=t["ms"],
    )


def _normalize(val) -> str:
    if val is None:
        return ""
    if isinstance(val, float):
        return str(round(val, 2))
    return str(val).strip().lower()
