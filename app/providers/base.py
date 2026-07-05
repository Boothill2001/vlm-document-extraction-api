from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def extract(self, text: str, document_type: str) -> dict:
        """Extract structured fields from text. Returns a dict of fields."""
        ...

    def build_prompt(self, text: str, document_type: str) -> str:
        return (
            f"Extract structured data from the following {document_type} document.\n"
            f"Return a JSON object with these fields for an invoice:\n"
            f"invoice_number, invoice_date, seller_name, buyer_name, currency, "
            f"subtotal, tax, total_amount, line_items (list of item_name, quantity, "
            f"unit_price, amount), payment_terms, due_date.\n\n"
            f"Document text:\n{text}\n\n"
            f"Return ONLY valid JSON, no markdown."
        )
