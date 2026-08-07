from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from packages.tools.base import Tool
from packages.tools.result import ToolResult


class SearchRequest(BaseModel):
    """Input model for workspace text searches."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    case_sensitive: bool = False
    max_results: int = Field(default=50, ge=1, le=500)


class SearchTool(Tool):
    """Search text inside UTF-8 files in an allowed workspace."""

    name = "search"
    description = "Searches text inside UTF-8 workspace files."

    def __init__(self, workspace_root: Path) -> None:
        self._workspace_root = workspace_root.resolve()

    def validate(self, **kwargs: Any) -> bool:
        """Validate a SearchRequest before execution."""

        request = kwargs.get("request")

        return isinstance(request, SearchRequest) and bool(request.query.strip())

    def execute(self, **kwargs: Any) -> ToolResult:
        """Search workspace files using a validated SearchRequest."""

        request = kwargs.get("request")

        if not isinstance(request, SearchRequest):
            return ToolResult(
                success=False,
                error="A valid SearchRequest is required.",
            )

        if not self.validate(request=request):
            return ToolResult(
                success=False,
                error="Search request is invalid.",
            )

        results: list[dict[str, object]] = []

        search_query = request.query
        if not request.case_sensitive:
            search_query = search_query.lower()

        for file_path in self._workspace_root.rglob("*"):
            if not file_path.is_file():
                continue

            try:
                lines = file_path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, PermissionError, OSError):
                continue

            for line_number, line in enumerate(lines, start=1):
                searchable_line = line

                if not request.case_sensitive:
                    searchable_line = searchable_line.lower()

                if search_query not in searchable_line:
                    continue

                results.append(
                    {
                        "file": str(file_path.relative_to(self._workspace_root)),
                        "line": line_number,
                        "text": line.strip(),
                    }
                )

                if len(results) >= request.max_results:
                    return ToolResult(
                        success=True,
                        output=results,
                    )

        return ToolResult(
            success=True,
            output=results,
        )
