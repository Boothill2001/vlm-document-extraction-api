from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import MockProvider
from app.providers.claude_provider import ClaudeProvider
from app.providers.openai_provider import DeepSeekProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.gpt4_provider import GPT4Provider
from app.core.config import get_settings

PROVIDERS: dict[str, type[BaseLLMProvider]] = {
    "mock": MockProvider,
    "claude": ClaudeProvider,
    "deepseek": DeepSeekProvider,
    "gemini": GeminiProvider,
    "gpt4": GPT4Provider,
}


def get_provider(name: str | None = None) -> BaseLLMProvider:
    provider_name = name or get_settings().default_provider
    cls = PROVIDERS.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDERS)}")
    return cls()
