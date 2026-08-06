import pytest
from pydantic import ValidationError

from packages.tools.result import ToolResult


def test_success_result() -> None:
    result = ToolResult(
        success=True,
        output="README.md",
        duration_ms=15.4,
    )

    assert result.success is True
    assert result.output == "README.md"
    assert result.error is None


def test_failed_result() -> None:
    result = ToolResult(
        success=False,
        error="File not found",
    )

    assert result.success is False
    assert result.error == "File not found"


def test_negative_duration_is_invalid() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            success=True,
            duration_ms=-1,
        )
