from collections import deque
from pathlib import Path

import pytest

from packages.agent.agent import AgentStatus
from packages.agent.loop import AIAgentLoop
from packages.models.gateway import (
    ModelGateway,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from packages.tools.registry import ToolRegistry
from packages.tools.search_tool import SearchTool


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


@pytest.mark.asyncio
async def test_agent_loop_adapts_search_request(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "example.cpp"

    source_file.write_text(
        "void CHARACTER_MANAGER::Initialize() {}\n",
        encoding="utf-8",
    )

    provider = SequentialModelProvider(
        [
            """
            {
                "action": "tool",
                "tool_name": "search",
                "arguments": {
                    "request": {
                        "query": "CHARACTER_MANAGER",
                        "max_results": 10
                    }
                }
            }
            """,
            """
            {
                "action": "finish",
                "message": "Search completed."
            }
            """,
        ]
    )

    registry = ToolRegistry()
    registry.register(SearchTool(tmp_path))

    loop = AIAgentLoop(
        model_gateway=ModelGateway(provider),
        tool_registry=registry,
    )

    run = await loop.run(
        "Find CHARACTER_MANAGER.",
    )

    assert run.status is AgentStatus.COMPLETED
    assert run.final_message == "Search completed."
    assert len(run.tool_results) == 1

    result = run.tool_results[0]

    assert result.success is True
    assert isinstance(result.output, list)
    assert len(result.output) == 1

    match = result.output[0]

    assert match["file"] == "example.cpp"
    assert match["line"] == 1
    assert "CHARACTER_MANAGER" in match["text"]


@pytest.mark.asyncio
async def test_agent_loop_reports_invalid_typed_request(
    tmp_path: Path,
) -> None:
    provider = SequentialModelProvider(
        [
            """
            {
                "action": "tool",
                "tool_name": "search",
                "arguments": {
                    "request": {
                        "query": ""
                    }
                }
            }
            """,
            """
            {
                "action": "finish",
                "message": "Invalid request was detected."
            }
            """,
        ]
    )

    registry = ToolRegistry()
    registry.register(SearchTool(tmp_path))

    loop = AIAgentLoop(
        model_gateway=ModelGateway(provider),
        tool_registry=registry,
    )

    run = await loop.run(
        "Perform an invalid search.",
    )

    assert run.status is AgentStatus.COMPLETED
    assert len(run.tool_results) == 1

    result = run.tool_results[0]

    assert result.success is False
    assert result.error == "Tool 'search' request validation failed."
