import json

from pydantic import ValidationError

from packages.agent.decision import AgentDecision
from packages.models.gateway import ModelResponse


class AgentDecisionParseError(ValueError):
    """Raised when a model response cannot be parsed into an agent decision."""


class AgentDecisionParser:
    """Parse structured model output into AgentDecision objects."""

    def parse(self, response: ModelResponse) -> AgentDecision:
        """Parse a model response containing JSON."""

        raw_content = response.content.strip()

        if not raw_content:
            raise AgentDecisionParseError("Model response content is empty.")

        try:
            payload = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise AgentDecisionParseError("Model response is not valid JSON.") from exc

        if not isinstance(payload, dict):
            raise AgentDecisionParseError("Model response JSON must be an object.")

        try:
            return AgentDecision.model_validate(payload)
        except ValidationError as exc:
            raise AgentDecisionParseError(
                "Model response does not match the AgentDecision schema."
            ) from exc
