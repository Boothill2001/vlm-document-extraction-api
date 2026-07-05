import json
import base64
from pathlib import Path
import httpx
from app.providers.base import BaseLLMProvider
from app.core.config import get_settings
from app.core.exceptions import ProviderError


class GPT4Provider(BaseLLMProvider):
    name = "gpt4"

    def _call_api(self, messages: list[dict]) -> str:
        settings = get_settings()
        if not settings.gpt4_api_key:
            raise ProviderError("gpt4", "GPT4_API_KEY not set in environment")

        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.gpt4_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            raise ProviderError("gpt4", f"API returned {e.response.status_code}: {e.response.text[:200]}")
        except (KeyError, IndexError) as e:
            raise ProviderError("gpt4", f"Unexpected response format: {e}")

    def extract(self, text: str, document_type: str) -> dict:
        prompt = self.build_prompt(text, document_type)
        messages = [{"role": "user", "content": prompt}]

        content = self._call_api(messages)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ProviderError("gpt4", f"Failed to parse JSON: {e}")

    def extract_from_image(self, image_path: str, document_type: str) -> dict:
        path = Path(image_path)
        image_bytes = path.read_bytes()
        ext = path.suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
        mime = mime_map.get(ext, "image/jpeg")

        b64 = base64.b64encode(image_bytes).decode()

        prompt = (
            f"Extract structured data from this {document_type} document image.\n"
            f"Return a JSON object with these fields for an invoice:\n"
            f"invoice_number, invoice_date, seller_name, buyer_name, currency, "
            f"subtotal, tax, total_amount, line_items (list of item_name, quantity, "
            f"unit_price, amount), payment_terms, due_date.\n\n"
            f"Return ONLY valid JSON, no markdown fences."
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ]

        content = self._call_api(messages)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ProviderError("gpt4", f"Failed to parse JSON: {e}")
