import json
import httpx
from app.providers.base import BaseLLMProvider
from app.core.config import get_settings
from app.core.exceptions import ProviderError


class DeepSeekProvider(BaseLLMProvider):
    name = "deepseek"

    def extract(self, text: str, document_type: str) -> dict:
        settings = get_settings()
        if not settings.deepseek_api_key:
            raise ProviderError("deepseek", "DEEPSEEK_API_KEY not set in environment")

        prompt = self.build_prompt(text, document_type)

        try:
            response = httpx.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                },
                timeout=60,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except httpx.HTTPStatusError as e:
            raise ProviderError("deepseek", f"API returned {e.response.status_code}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ProviderError("deepseek", f"Failed to parse response: {e}")
