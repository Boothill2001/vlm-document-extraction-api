from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import MockProvider
from app.providers.claude_provider import ClaudeProvider
from app.providers.openai_provider import DeepSeekProvider
from app.core.config import get_settings

PROVIDERS: dict[str, type[BaseLLMProvider]] = {
    "mock": MockProvider,
    "claude": ClaudeProvider,
    "deepseek": DeepSeekProvider,
}


def get_provider(name: str | None = None) -> BaseLLMProvider:
    provider_name = name or get_settings().default_provider
    cls = PROVIDERS.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDERS)}")
    return cls()
