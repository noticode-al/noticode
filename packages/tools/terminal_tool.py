import subprocess
from pathlib import Path
from time import perf_counter
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from packages.tools.base import Tool
from packages.tools.result import ToolResult


class TerminalRequest(BaseModel):
    """Input model for terminal command execution."""

    model_config = ConfigDict(extra="forbid")

    command: list[str] = Field(min_length=1)
    timeout_seconds: int = Field(default=30, ge=1, le=300)


class TerminalTool(Tool):
    """Execute approved commands inside an allowed workspace."""

    name = "terminal"
    description = "Executes approved terminal commands inside the workspace."

    DEFAULT_ALLOWED_COMMANDS = {
        "python",
        "python3",
        "pytest",
        "ruff",
        "mypy",
        "ls",
        "pwd",
        "cat",
    }

    def __init__(
        self,
        workspace_root: Path,
        allowed_commands: set[str] | None = None,
    ) -> None:
        self._workspace_root = workspace_root.resolve()
        self._allowed_commands = (
            allowed_commands
            if allowed_commands is not None
            else self.DEFAULT_ALLOWED_COMMANDS.copy()
        )

    def validate(self, **kwargs: Any) -> bool:
        """Validate terminal request before execution."""

        request = kwargs.get("request")

        if not isinstance(request, TerminalRequest):
            return False

        if not request.command:
            return False

        executable = Path(request.command[0]).name

        return executable in self._allowed_commands

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute an approved terminal command."""

        started_at = perf_counter()

        request = kwargs.get("request")

        if not isinstance(request, TerminalRequest):
            return self._failure(
                error="A valid TerminalRequest is required.",
                started_at=started_at,
            )

        if not self.validate(request=request):
            return self._failure(
                error="Command is not allowed.",
                started_at=started_at,
            )

        try:
            completed = subprocess.run(
                request.command,
                cwd=self._workspace_root,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                check=False,
                shell=False,
            )

        except subprocess.TimeoutExpired:
            return self._failure(
                error=f"Command timed out after {request.timeout_seconds} seconds.",
                started_at=started_at,
            )

        except FileNotFoundError:
            return self._failure(
                error="Command executable was not found.",
                started_at=started_at,
            )

        except OSError as exc:
            return self._failure(
                error=f"Command execution failed: {exc}",
                started_at=started_at,
            )

        return ToolResult(
            success=completed.returncode == 0,
            output={
                "command": request.command,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            error=None if completed.returncode == 0 else completed.stderr.strip(),
            duration_ms=(perf_counter() - started_at) * 1000,
        )

    def _failure(
        self,
        error: str,
        started_at: float,
    ) -> ToolResult:
        """Create a failed terminal result."""

        return ToolResult(
            success=False,
            error=error,
            duration_ms=(perf_counter() - started_at) * 1000,
        )
