import json
import httpx
from app.providers.base import BaseLLMProvider
from app.core.config import get_settings
from app.core.exceptions import ProviderError


class ClaudeProvider(BaseLLMProvider):
    name = "claude"

    def extract(self, text: str, document_type: str) -> dict:
        settings = get_settings()
        if not settings.claude_api_key:
            raise ProviderError("claude", "CLAUDE_API_KEY not set in environment")

        prompt = self.build_prompt(text, document_type)

        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.claude_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60,
            )
            response.raise_for_status()
            content = response.json()["content"][0]["text"]
            return json.loads(content)
        except httpx.HTTPStatusError as e:
            raise ProviderError("claude", f"API returned {e.response.status_code}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ProviderError("claude", f"Failed to parse response: {e}")
