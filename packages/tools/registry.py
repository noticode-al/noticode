from packages.tools.base import Tool


class ToolRegistry:
    """Registry responsible for managing available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool by its unique name."""

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Return a tool by name."""

        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool '{name}' not found.") from exc

    def exists(self, name: str) -> bool:
        """Check whether a tool exists."""

        return name in self._tools

    def list_tools(self) -> list[str]:
        """Return all registered tool names."""

        return sorted(self._tools.keys())
