import json
import base64
from pathlib import Path
from google import genai
from app.providers.base import BaseLLMProvider
from app.core.config import get_settings
from app.core.exceptions import ProviderError


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    def extract(self, text: str, document_type: str) -> dict:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ProviderError("gemini", "GEMINI_API_KEY not set in environment")

        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = self.build_prompt(text, document_type)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                raw = raw.rsplit("```", 1)[0]
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ProviderError("gemini", f"Failed to parse JSON: {e}\nRaw: {raw[:200]}")
        except Exception as e:
            raise ProviderError("gemini", str(e))

    def extract_from_image(self, image_path: str, document_type: str) -> dict:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ProviderError("gemini", "GEMINI_API_KEY not set in environment")

        client = genai.Client(api_key=settings.gemini_api_key)

        path = Path(image_path)
        image_bytes = path.read_bytes()
        ext = path.suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
        mime = mime_map.get(ext, "image/jpeg")

        prompt = (
            f"Extract structured data from this {document_type} document image.\n"
            f"Return a JSON object with these fields for an invoice:\n"
            f"invoice_number, invoice_date, seller_name, buyer_name, currency, "
            f"subtotal, tax, total_amount, line_items (list of item_name, quantity, "
            f"unit_price, amount), payment_terms, due_date.\n\n"
            f"Return ONLY valid JSON, no markdown fences."
        )

        image_part = genai.types.Part.from_bytes(data=image_bytes, mime_type=mime)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image_part],
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                raw = raw.rsplit("```", 1)[0]
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ProviderError("gemini", f"Failed to parse JSON: {e}\nRaw: {raw[:300]}")
        except Exception as e:
            raise ProviderError("gemini", str(e))
