from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

from packages.agent.tool_adapter import (
    ToolRequestAdapter,
    ToolRequestAdapterError,
)
from packages.tools.docker_tool import DockerOperation, DockerRequest
from packages.tools.git_tool import GitOperation, GitRequest
from packages.tools.search_tool import SearchRequest
from packages.tools.terminal_tool import TerminalRequest


def test_adapter_supports_builtin_tools() -> None:
    adapter = ToolRequestAdapter()

    assert adapter.supports("search") is True
    assert adapter.supports("terminal") is True
    assert adapter.supports("git") is True
    assert adapter.supports("docker") is True


def test_adapter_converts_search_request() -> None:
    adapter = ToolRequestAdapter()

    arguments = adapter.adapt(
        "search",
        {
            "request": {
                "query": "CHARACTER_MANAGER",
                "max_results": 10,
            }
        },
    )

    request = arguments["request"]

    assert isinstance(request, SearchRequest)
    assert request.query == "CHARACTER_MANAGER"
    assert request.max_results == 10


def test_adapter_converts_terminal_request() -> None:
    adapter = ToolRequestAdapter()

    arguments = adapter.adapt(
        "terminal",
        {
            "request": {
                "command": ["pytest", "-q"],
                "timeout_seconds": 60,
            }
        },
    )

    request = arguments["request"]

    assert isinstance(request, TerminalRequest)
    assert request.command == ["pytest", "-q"]
    assert request.timeout_seconds == 60


def test_adapter_converts_git_request() -> None:
    adapter = ToolRequestAdapter()

    arguments = adapter.adapt(
        "git",
        {
            "request": {
                "operation": "status",
            }
        },
    )

    request = arguments["request"]

    assert isinstance(request, GitRequest)
    assert request.operation is GitOperation.STATUS


def test_adapter_converts_docker_request() -> None:
    adapter = ToolRequestAdapter()

    arguments = adapter.adapt(
        "docker",
        {
            "request": {
                "operation": "ps",
            }
        },
    )

    request = arguments["request"]

    assert isinstance(request, DockerRequest)
    assert request.operation is DockerOperation.PS


def test_adapter_preserves_existing_request_model() -> None:
    adapter = ToolRequestAdapter()

    original_request = SearchRequest(
        query="Noticode",
    )

    arguments = adapter.adapt(
        "search",
        {
            "request": original_request,
        },
    )

    assert arguments["request"] is original_request


def test_adapter_rejects_missing_request() -> None:
    adapter = ToolRequestAdapter()

    with pytest.raises(
        ToolRequestAdapterError,
        match="requires a request object",
    ):
        adapter.adapt(
            "search",
            {},
        )


def test_adapter_rejects_non_object_request() -> None:
    adapter = ToolRequestAdapter()

    with pytest.raises(
        ToolRequestAdapterError,
        match="request must be a JSON object",
    ):
        adapter.adapt(
            "search",
            {
                "request": "invalid",
            },
        )


def test_adapter_rejects_invalid_request_schema() -> None:
    adapter = ToolRequestAdapter()

    with pytest.raises(
        ToolRequestAdapterError,
        match="request validation failed",
    ):
        adapter.adapt(
            "terminal",
            {
                "request": {
                    "command": [],
                }
            },
        )


def test_adapter_returns_arguments_for_unknown_tool() -> None:
    adapter = ToolRequestAdapter()

    original = {
        "value": 123,
    }

    adapted = adapter.adapt(
        "custom",
        original,
    )

    assert adapted == original
    assert adapted is not original


class CustomRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: int


def test_adapter_can_register_custom_request_model() -> None:
    adapter = ToolRequestAdapter()

    adapter.register(
        "custom",
        CustomRequest,
    )

    arguments = adapter.adapt(
        "custom",
        {
            "request": {
                "value": 42,
            }
        },
    )

    request: Any = arguments["request"]

    assert isinstance(request, CustomRequest)
    assert request.value == 42


def test_adapter_rejects_empty_tool_name() -> None:
    adapter = ToolRequestAdapter()

    with pytest.raises(
        ValueError,
        match="tool_name cannot be empty",
    ):
        adapter.register(
            "",
            CustomRequest,
        )
