import pytest
from app.schemas.documents import InvoiceFields


def test_valid_invoice_schema():
    data = {
        "invoice_number": "INV-001",
        "total_amount": 100.0,
        "line_items": [{"item_name": "Widget", "quantity": 2, "unit_price": 50.0, "amount": 100.0}],
    }
    invoice = InvoiceFields.model_validate(data)
    assert invoice.invoice_number == "INV-001"
    assert invoice.total_amount == 100.0
    assert len(invoice.line_items) == 1


def test_invoice_schema_rejects_negative_total():
    from app.services.validation_service import validate_invoice
    errors = validate_invoice({"total_amount": -50.0})
    assert any("positive" in e for e in errors)


def test_invoice_schema_optional_fields():
    invoice = InvoiceFields.model_validate({})
    assert invoice.invoice_number is None
    assert invoice.total_amount is None
    assert invoice.line_items == []
