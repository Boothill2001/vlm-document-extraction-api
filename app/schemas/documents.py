from pydantic import BaseModel, Field


class LineItem(BaseModel):
    item_name: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    amount: float | None = None


class InvoiceFields(BaseModel):
    invoice_number: str | None = None
    invoice_date: str | None = None
    seller_name: str | None = None
    buyer_name: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total_amount: float | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    payment_terms: str | None = None
    due_date: str | None = None


DOCUMENT_SCHEMAS: dict[str, type[BaseModel]] = {
    "invoice": InvoiceFields,
}
