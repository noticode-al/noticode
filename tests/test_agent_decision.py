import pytest
from pydantic import ValidationError

from packages.agent.decision import (
    AgentAction,
    AgentDecision,
)


def test_tool_decision_is_valid() -> None:
    decision = AgentDecision(
        action=AgentAction.TOOL,
        tool_name="search",
        arguments={
            "request": {
                "query": "CHARACTER_MANAGER",
            }
        },
    )

    assert decision.action is AgentAction.TOOL
    assert decision.tool_name == "search"
    assert decision.is_tool_action is True
    assert decision.is_finish_action is False


def test_finish_decision_is_valid() -> None:
    decision = AgentDecision(
        action=AgentAction.FINISH,
        message="Task completed successfully.",
    )

    assert decision.action is AgentAction.FINISH
    assert decision.message == "Task completed successfully."
    assert decision.is_finish_action is True
    assert decision.is_tool_action is False


def test_tool_decision_requires_tool_name() -> None:
    with pytest.raises(
        ValidationError,
        match="tool_name is required for tool actions",
    ):
        AgentDecision(
            action=AgentAction.TOOL,
        )


def test_tool_decision_rejects_message() -> None:
    with pytest.raises(
        ValidationError,
        match="message is not allowed for tool actions",
    ):
        AgentDecision(
            action=AgentAction.TOOL,
            tool_name="search",
            message="Invalid message.",
        )


def test_finish_decision_requires_message() -> None:
    with pytest.raises(
        ValidationError,
        match="message is required for finish actions",
    ):
        AgentDecision(
            action=AgentAction.FINISH,
        )


def test_finish_decision_rejects_empty_message() -> None:
    with pytest.raises(
        ValidationError,
        match="message is required for finish actions",
    ):
        AgentDecision(
            action=AgentAction.FINISH,
            message="   ",
        )


def test_finish_decision_rejects_tool_name() -> None:
    with pytest.raises(
        ValidationError,
        match="tool_name is not allowed for finish actions",
    ):
        AgentDecision(
            action=AgentAction.FINISH,
            tool_name="search",
            message="Completed.",
        )


def test_finish_decision_rejects_arguments() -> None:
    with pytest.raises(
        ValidationError,
        match="arguments are not allowed for finish actions",
    ):
        AgentDecision(
            action=AgentAction.FINISH,
            message="Completed.",
            arguments={
                "query": "Noticode",
            },
        )


def test_decision_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action=AgentAction.FINISH,
            message="Completed.",
            unknown="invalid",  # type: ignore[call-arg]
        )


def test_decision_accepts_action_as_string() -> None:
    decision = AgentDecision(
        action="tool",  # type: ignore[arg-type]
        tool_name="search",
    )

    assert decision.action is AgentAction.TOOL
