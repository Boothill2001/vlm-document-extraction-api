import re
import time
import random
from app.providers.base import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    name = "mock"

    def extract(self, text: str, document_type: str) -> dict:
        time.sleep(random.uniform(0.05, 0.15))

        if document_type == "invoice":
            return self._extract_invoice(text)
        return {"raw_text": text[:200]}

    def _extract_invoice(self, text: str) -> dict:
        return {
            "invoice_number": self._find(r"Invoice\s*(?:#|No\.?)\s*:?\s*([A-Z0-9][\w-]+)", text),
            "invoice_date": self._find(r"Date\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", text),
            "seller_name": self._find(r"From\s*:?\s*(.+?)(?:\n|$)", text),
            "buyer_name": self._find(r"(?:To|Bill\s*To)\s*:?\s*(.+?)(?:\n|$)", text),
            "currency": self._find_currency(text),
            "subtotal": self._find_amount(r"Subtotal\s*:?\s*\$?([\d,]+\.?\d*)", text),
            "tax": self._find_amount(r"Tax\s*(?:\([^)]*\))?\s*:?\s*\$?([\d,]+\.?\d*)", text),
            "total_amount": self._find_amount(r"Total\s+Amount\s*:?\s*\$?([\d,]+\.?\d*)", text)
                            or self._find_amount(r"(?<!Sub)Total\s*:?\s*\$?([\d,]+\.?\d*)", text),
            "line_items": self._extract_line_items(text),
            "payment_terms": self._find(r"Payment\s*Terms?\s*:?\s*(.+?)(?:\n|$)", text),
            "due_date": self._find(r"Due\s*Date\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", text),
        }

    def _find(self, pattern: str, text: str) -> str | None:
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    def _find_amount(self, pattern: str, text: str) -> float | None:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                return None
        return None

    def _find_currency(self, text: str) -> str:
        if "$" in text or "USD" in text.upper():
            return "USD"
        if "EUR" in text.upper() or "€" in text:
            return "EUR"
        if "VND" in text.upper():
            return "VND"
        return "USD"

    def _extract_line_items(self, text: str) -> list[dict]:
        items = []
        pattern = r"(\d+)\s+(.+?)\s+(\d+)\s+\$?([\d,]+\.?\d*)\s+\$?([\d,]+\.?\d*)"
        for m in re.finditer(pattern, text):
            items.append({
                "item_name": m.group(2).strip(),
                "quantity": float(m.group(3)),
                "unit_price": float(m.group(4).replace(",", "")),
                "amount": float(m.group(5).replace(",", "")),
            })

        if not items:
            pattern2 = r"[-•]\s*(.+?)\s*[-–]\s*\$?([\d,]+\.?\d*)"
            for m in re.finditer(pattern2, text):
                items.append({
                    "item_name": m.group(1).strip(),
                    "quantity": 1,
                    "unit_price": float(m.group(2).replace(",", "")),
                    "amount": float(m.group(2).replace(",", "")),
                })

        return items
