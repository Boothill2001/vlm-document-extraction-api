from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.services.extraction_service import run_extraction
from app.services.confidence_service import calculate_confidence

client = TestClient(app)

SAMPLE_TEXT = Path(__file__).resolve().parent.parent / "samples" / "sample_invoice.txt"


def test_mock_extraction_returns_fields():
    text = SAMPLE_TEXT.read_text(encoding="utf-8")
    result = run_extraction(text, "invoice", "mock")
    fields = result.extracted_fields
    assert fields.get("invoice_number") is not None
    assert fields.get("total_amount") is not None
    assert result.provider_used == "mock"


def test_text_endpoint_works():
    text = SAMPLE_TEXT.read_text(encoding="utf-8")
    resp = client.post("/v1/extract/text", json={
        "text": text,
        "document_type": "invoice",
        "provider": "mock",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["document_type"] == "invoice"
    assert data["extracted_fields"]["invoice_number"] is not None


def test_confidence_decreases_with_missing_fields():
    full = {"invoice_number": "X", "invoice_date": "2026-01-01", "seller_name": "A",
            "buyer_name": "B", "total_amount": 100, "currency": "USD", "line_items": [{}]}
    score_full, _, _ = calculate_confidence(full, [], "invoice")

    partial = {"invoice_number": "X"}
    score_partial, _, _ = calculate_confidence(partial, [], "invoice")

    assert score_full > score_partial


def test_evaluate_endpoint():
    resp = client.post("/v1/evaluate")
    assert resp.status_code == 200
    data = resp.json()
    assert "field_accuracy" in data
    assert "missing_fields" in data
