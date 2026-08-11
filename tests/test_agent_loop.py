from collections import deque
from typing import Any

import pytest

from packages.agent.agent import AgentStatus
from packages.agent.loop import AIAgentLoop
from packages.models.gateway import (
    ModelGateway,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from packages.tools.base import Tool
from packages.tools.registry import ToolRegistry
from packages.tools.result import ToolResult


class SequentialModelProvider(ModelProvider):
    """Return predefined model responses in sequence."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = deque(responses)

    @property
    def name(self) -> str:
        return "sequential-test-provider"

    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        if not self._responses:
            raise RuntimeError("No fake responses remain.")

        return ModelResponse(
            content=self._responses.popleft(),
            model="fake-model",
        )


class EchoTool(Tool):
    """Simple tool used by agent loop tests."""

    name = "echo"
    description = "Returns the provided text."

    def validate(self, **kwargs: Any) -> bool:
        return isinstance(kwargs.get("text"), str)

    def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text")

        if not isinstance(text, str):
            return ToolResult(
                success=False,
                error="Text is required.",
            )

        return ToolResult(
            success=True,
            output={
                "text": text,
            },
        )


def create_gateway(
    responses: list[str],
) -> ModelGateway:
    provider = SequentialModelProvider(responses)

    return ModelGateway(provider)


@pytest.mark.asyncio
async def test_agent_loop_can_finish_immediately() -> None:
    gateway = create_gateway(
        [
            """
            {
                "action": "finish",
                "message": "Task completed."
            }
            """
        ]
    )

    loop = AIAgentLoop(
        model_gateway=gateway,
        tool_registry=ToolRegistry(),
    )

    run = await loop.run(
        "Explain the project.",
    )

    assert run.status is AgentStatus.COMPLETED
    assert run.final_message == "Task completed."
    assert run.iterations == 1
    assert len(run.decisions) == 1
    assert run.tool_results == []


@pytest.mark.asyncio
async def test_agent_loop_executes_tool_then_finishes() -> None:
    gateway = create_gateway(
        [
            """
            {
                "action": "tool",
                "tool_name": "echo",
                "arguments": {
                    "text": "Hello Noticode"
                }
            }
            """,
            """
            {
                "action": "finish",
                "message": "Echo completed successfully."
            }
            """,
        ]
    )

    registry = ToolRegistry()
    registry.register(EchoTool())

    loop = AIAgentLoop(
        model_gateway=gateway,
        tool_registry=registry,
    )

    run = await loop.run(
        "Use the echo tool.",
    )

    assert run.status is AgentStatus.COMPLETED
    assert run.iterations == 2
    assert len(run.decisions) == 2
    assert len(run.tool_results) == 1

    tool_result = run.tool_results[0]

    assert tool_result.success is True
    assert isinstance(tool_result.output, dict)
    assert tool_result.output["text"] == "Hello Noticode"
    assert run.final_message == "Echo completed successfully."


@pytest.mark.asyncio
async def test_agent_loop_returns_unknown_tool_result_to_model() -> None:
    gateway = create_gateway(
        [
            """
            {
                "action": "tool",
                "tool_name": "missing",
                "arguments": {}
            }
            """,
            """
            {
                "action": "finish",
                "message": "The requested tool was unavailable."
            }
            """,
        ]
    )

    loop = AIAgentLoop(
        model_gateway=gateway,
        tool_registry=ToolRegistry(),
    )

    run = await loop.run(
        "Use a missing tool.",
    )

    assert run.status is AgentStatus.COMPLETED
    assert len(run.tool_results) == 1
    assert run.tool_results[0].success is False
    assert run.tool_results[0].error == "Tool is not registered: missing"


@pytest.mark.asyncio
async def test_agent_loop_returns_invalid_arguments_to_model() -> None:
    gateway = create_gateway(
        [
            """
            {
                "action": "tool",
                "tool_name": "echo",
                "arguments": {}
            }
            """,
            """
            {
                "action": "finish",
                "message": "Invalid arguments were detected."
            }
            """,
        ]
    )

    registry = ToolRegistry()
    registry.register(EchoTool())

    loop = AIAgentLoop(
        model_gateway=gateway,
        tool_registry=registry,
    )

    run = await loop.run(
        "Call echo incorrectly.",
    )

    assert run.status is AgentStatus.COMPLETED
    assert len(run.tool_results) == 1
    assert run.tool_results[0].success is False
    assert run.tool_results[0].error == "Tool arguments are invalid: echo"


@pytest.mark.asyncio
async def test_agent_loop_fails_on_invalid_model_json() -> None:
    gateway = create_gateway(
        [
            "This is not JSON.",
        ]
    )

    loop = AIAgentLoop(
        model_gateway=gateway,
        tool_registry=ToolRegistry(),
    )

    run = await loop.run(
        "Generate invalid output.",
    )

    assert run.status is AgentStatus.FAILED
    assert run.error is not None
    assert "Model decision could not be parsed" in run.error


@pytest.mark.asyncio
async def test_agent_loop_stops_at_iteration_limit() -> None:
    gateway = create_gateway(
        [
            """
            {
                "action": "tool",
                "tool_name": "echo",
                "arguments": {
                    "text": "one"
                }
            }
            """,
            """
            {
                "action": "tool",
                "tool_name": "echo",
                "arguments": {
                    "text": "two"
                }
            }
            """,
        ]
    )

    registry = ToolRegistry()
    registry.register(EchoTool())

    loop = AIAgentLoop(
        model_gateway=gateway,
        tool_registry=registry,
        max_iterations=2,
    )

    run = await loop.run(
        "Never finish.",
    )

    assert run.status is AgentStatus.FAILED
    assert run.iterations == 2
    assert run.error == "Maximum iteration limit reached: 2."
    assert len(run.tool_results) == 2


def test_agent_loop_rejects_invalid_iteration_limit() -> None:
    gateway = create_gateway([])

    with pytest.raises(
        ValueError,
        match="max_iterations must be at least 1",
    ):
        AIAgentLoop(
            model_gateway=gateway,
            tool_registry=ToolRegistry(),
            max_iterations=0,
        )
