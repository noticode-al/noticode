from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AgentAction(StrEnum):
    """Actions that can be requested by the model."""

    TOOL = "tool"
    FINISH = "finish"


class AgentDecision(BaseModel):
    """A structured decision produced by the language model."""

    model_config = ConfigDict(extra="forbid")

    action: AgentAction

    tool_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    arguments: dict[str, Any] = Field(
        default_factory=dict,
    )

    message: str | None = Field(
        default=None,
        max_length=10_000,
    )

    @model_validator(mode="after")
    def validate_action_fields(self) -> "AgentDecision":
        """Validate fields required by the selected action."""

        if self.action is AgentAction.TOOL:
            if self.tool_name is None:
                raise ValueError("tool_name is required for tool actions.")

            if self.message is not None:
                raise ValueError("message is not allowed for tool actions.")

        if self.action is AgentAction.FINISH:
            if self.message is None or not self.message.strip():
                raise ValueError("message is required for finish actions.")

            if self.tool_name is not None:
                raise ValueError("tool_name is not allowed for finish actions.")

            if self.arguments:
                raise ValueError("arguments are not allowed for finish actions.")

        return self

    @property
    def is_tool_action(self) -> bool:
        """Return whether this decision requests a tool."""

        return self.action is AgentAction.TOOL

    @property
    def is_finish_action(self) -> bool:
        """Return whether this decision finishes the task."""

        return self.action is AgentAction.FINISH
