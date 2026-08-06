from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolResult(BaseModel):
    """
    Standard result returned by every Noticode tool.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    success: bool

    output: Any | None = None

    error: str | None = None

    duration_ms: float = Field(
        ge=0,
        default=0,
    )
