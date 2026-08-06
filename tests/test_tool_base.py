from typing import Any

from packages.tools.base import Tool


class DummyTool(Tool):
    name = "dummy"
    description = "Dummy Tool"

    def execute(self, **kwargs: Any) -> str:
        return "ok"

    def validate(self, **kwargs: Any) -> bool:
        return True


def test_dummy_tool_execute() -> None:
    tool = DummyTool()

    assert tool.execute() == "ok"


def test_dummy_tool_validate() -> None:
    tool = DummyTool()

    assert tool.validate() is True
