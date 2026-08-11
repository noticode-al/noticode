from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModelMessage(BaseModel):
    """A single message exchanged with a language model."""

    model_config = ConfigDict(extra="forbid")

    role: str = Field(min_length=1)
    content: str


class ModelRequest(BaseModel):
    """Provider-independent language model request."""

    model_config = ConfigDict(extra="forbid")

    messages: list[ModelMessage] = Field(min_length=1)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)


class ModelUsage(BaseModel):
    """Token usage reported by a model provider."""

    model_config = ConfigDict(extra="forbid")

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)

    @property
    def total_tokens(self) -> int:
        """Return total token usage."""

        return self.input_tokens + self.output_tokens


class ModelResponse(BaseModel):
    """Provider-independent language model response."""

    model_config = ConfigDict(extra="forbid")

    content: str
    model: str
    usage: ModelUsage = Field(default_factory=ModelUsage)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelProvider(ABC):
    """Interface implemented by every model provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return provider name."""

    @abstractmethod
    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        """Generate a response from the model."""


class ModelGateway:
    """Route model requests through a configured provider."""

    def __init__(self, provider: ModelProvider) -> None:
        self._provider = provider

    @property
    def provider_name(self) -> str:
        """Return active provider name."""

        return self._provider.name

    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        """Send a request through the active provider."""

        return await self._provider.generate(request)
