from typing import Any

import pytest

from packages.tools.base import Tool
from packages.tools.registry import ToolRegistry


class DummyTool(Tool):
    name = "dummy"
    description = "Dummy tool"

    def execute(self, **kwargs: Any) -> str:
        return "ok"

    def validate(self, **kwargs: Any) -> bool:
        return True


def test_register_tool() -> None:
    registry = ToolRegistry()
    tool = DummyTool()

    registry.register(tool)

    assert registry.exists("dummy") is True


def test_get_registered_tool() -> None:
    registry = ToolRegistry()
    tool = DummyTool()

    registry.register(tool)

    assert registry.get("dummy") is tool


def test_duplicate_registration_raises_error() -> None:
    registry = ToolRegistry()
    tool = DummyTool()

    registry.register(tool)

    with pytest.raises(ValueError):
        registry.register(tool)


def test_unknown_tool_raises_error() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_list_tools() -> None:
    registry = ToolRegistry()

    registry.register(DummyTool())

    assert registry.list_tools() == ["dummy"]
