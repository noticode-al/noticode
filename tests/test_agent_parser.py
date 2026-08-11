import pytest

from packages.agent.decision import AgentAction
from packages.agent.parser import (
    AgentDecisionParseError,
    AgentDecisionParser,
)
from packages.models.gateway import ModelResponse


def test_parser_parses_tool_decision() -> None:
    parser = AgentDecisionParser()

    response = ModelResponse(
        content="""
        {
            "action": "tool",
            "tool_name": "search",
            "arguments": {
                "request": {
                    "query": "CHARACTER_MANAGER"
                }
            }
        }
        """,
        model="fake-model",
    )

    decision = parser.parse(response)

    assert decision.action is AgentAction.TOOL
    assert decision.tool_name == "search"
    assert decision.arguments["request"]["query"] == "CHARACTER_MANAGER"


def test_parser_parses_finish_decision() -> None:
    parser = AgentDecisionParser()

    response = ModelResponse(
        content="""
        {
            "action": "finish",
            "message": "Task completed."
        }
        """,
        model="fake-model",
    )

    decision = parser.parse(response)

    assert decision.action is AgentAction.FINISH
    assert decision.message == "Task completed."


def test_parser_rejects_empty_content() -> None:
    parser = AgentDecisionParser()

    response = ModelResponse(
        content="   ",
        model="fake-model",
    )

    with pytest.raises(
        AgentDecisionParseError,
        match="Model response content is empty",
    ):
        parser.parse(response)


def test_parser_rejects_invalid_json() -> None:
    parser = AgentDecisionParser()

    response = ModelResponse(
        content="this is not json",
        model="fake-model",
    )

    with pytest.raises(
        AgentDecisionParseError,
        match="Model response is not valid JSON",
    ):
        parser.parse(response)


def test_parser_rejects_json_array() -> None:
    parser = AgentDecisionParser()

    response = ModelResponse(
        content='["tool", "search"]',
        model="fake-model",
    )

    with pytest.raises(
        AgentDecisionParseError,
        match="Model response JSON must be an object",
    ):
        parser.parse(response)


def test_parser_rejects_invalid_decision_schema() -> None:
    parser = AgentDecisionParser()

    response = ModelResponse(
        content="""
        {
            "action": "tool"
        }
        """,
        model="fake-model",
    )

    with pytest.raises(
        AgentDecisionParseError,
        match="Model response does not match the AgentDecision schema",
    ):
        parser.parse(response)
