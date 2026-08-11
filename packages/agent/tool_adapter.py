from typing import Any

from pydantic import BaseModel, ValidationError

from packages.tools.docker_tool import DockerRequest
from packages.tools.git_tool import GitRequest
from packages.tools.search_tool import SearchRequest
from packages.tools.terminal_tool import TerminalRequest

type ToolRequestModel = type[BaseModel]


class ToolRequestAdapterError(ValueError):
    """Raised when raw tool arguments cannot be adapted."""


class ToolRequestAdapter:
    """Convert model-generated dictionaries into typed tool requests."""

    def __init__(self) -> None:
        self._request_models: dict[str, ToolRequestModel] = {
            "search": SearchRequest,
            "terminal": TerminalRequest,
            "git": GitRequest,
            "docker": DockerRequest,
        }

    def register(
        self,
        tool_name: str,
        request_model: ToolRequestModel,
    ) -> None:
        """Register or replace a request model for a tool."""

        if not tool_name.strip():
            raise ValueError("tool_name cannot be empty.")

        self._request_models[tool_name] = request_model

    def supports(self, tool_name: str) -> bool:
        """Return whether the adapter knows a tool request model."""

        return tool_name in self._request_models

    def adapt(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Convert raw arguments into the format expected by a tool."""

        request_model = self._request_models.get(tool_name)

        if request_model is None:
            return dict(arguments)

        raw_request = arguments.get("request")

        if raw_request is None:
            raise ToolRequestAdapterError(f"Tool '{tool_name}' requires a request object.")

        if isinstance(raw_request, BaseModel):
            return {
                **arguments,
                "request": raw_request,
            }

        if not isinstance(raw_request, dict):
            raise ToolRequestAdapterError(f"Tool '{tool_name}' request must be a JSON object.")

        try:
            request = request_model.model_validate(raw_request)
        except ValidationError as exc:
            raise ToolRequestAdapterError(f"Tool '{tool_name}' request validation failed.") from exc

        return {
            **arguments,
            "request": request,
        }
