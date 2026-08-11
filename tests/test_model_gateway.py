import pytest

from packages.models.gateway import (
    ModelGateway,
    ModelMessage,
    ModelProvider,
    ModelRequest,
    ModelResponse,
    ModelUsage,
)


class FakeModelProvider(ModelProvider):
    """Fake provider used by unit tests."""

    @property
    def name(self) -> str:
        return "fake"

    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        last_message = request.messages[-1]

        return ModelResponse(
            content=f"Echo: {last_message.content}",
            model="fake-model",
            usage=ModelUsage(
                input_tokens=10,
                output_tokens=5,
            ),
        )


def test_model_usage_calculates_total_tokens() -> None:
    usage = ModelUsage(
        input_tokens=10,
        output_tokens=5,
    )

    assert usage.total_tokens == 15


def test_gateway_exposes_provider_name() -> None:
    gateway = ModelGateway(
        provider=FakeModelProvider(),
    )

    assert gateway.provider_name == "fake"


@pytest.mark.asyncio
async def test_gateway_generates_response() -> None:
    gateway = ModelGateway(
        provider=FakeModelProvider(),
    )

    request = ModelRequest(
        messages=[
            ModelMessage(
                role="user",
                content="Hello Noticode",
            )
        ]
    )

    response = await gateway.generate(request)

    assert response.content == "Echo: Hello Noticode"
    assert response.model == "fake-model"
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 5
    assert response.usage.total_tokens == 15


@pytest.mark.asyncio
async def test_gateway_supports_multiple_messages() -> None:
    gateway = ModelGateway(
        provider=FakeModelProvider(),
    )

    request = ModelRequest(
        messages=[
            ModelMessage(
                role="system",
                content="You are Noticode.",
            ),
            ModelMessage(
                role="user",
                content="Inspect the project.",
            ),
        ]
    )

    response = await gateway.generate(request)

    assert response.content == "Echo: Inspect the project."


def test_model_response_supports_metadata() -> None:
    response = ModelResponse(
        content="Completed",
        model="fake-model",
        metadata={
            "request_id": "test-123",
        },
    )

    assert response.metadata["request_id"] == "test-123"
