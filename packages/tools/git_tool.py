import subprocess
from enum import StrEnum
from pathlib import Path
from time import perf_counter
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from packages.tools.base import Tool
from packages.tools.result import ToolResult


class GitOperation(StrEnum):
    """Supported read-only Git operations."""

    STATUS = "status"
    DIFF = "diff"
    BRANCH = "branch"
    LOG = "log"


class GitRequest(BaseModel):
    """Input model for Git operations."""

    model_config = ConfigDict(extra="forbid")

    operation: GitOperation
    args: list[str] = Field(default_factory=list)
    timeout_seconds: int = Field(default=30, ge=1, le=120)


class GitTool(Tool):
    """Execute safe read-only Git operations inside a repository."""

    name = "git"
    description = "Executes safe read-only Git operations inside the workspace."

    def __init__(self, workspace_root: Path) -> None:
        self._workspace_root = workspace_root.resolve()

    def validate(self, **kwargs: Any) -> bool:
        """Validate a Git request."""

        request = kwargs.get("request")

        if not isinstance(request, GitRequest):
            return False

        return self._is_git_repository()

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a supported Git operation."""

        started_at = perf_counter()

        request = kwargs.get("request")

        if not isinstance(request, GitRequest):
            return self._failure(
                error="A valid GitRequest is required.",
                started_at=started_at,
            )

        if not self._is_git_repository():
            return self._failure(
                error="Workspace is not a Git repository.",
                started_at=started_at,
            )

        command = self._build_command(request)

        try:
            completed = subprocess.run(
                command,
                cwd=self._workspace_root,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            return self._failure(
                error=f"Git command timed out after {request.timeout_seconds} seconds.",
                started_at=started_at,
            )
        except FileNotFoundError:
            return self._failure(
                error="Git executable was not found.",
                started_at=started_at,
            )
        except OSError as exc:
            return self._failure(
                error=f"Git command execution failed: {exc}",
                started_at=started_at,
            )

        stdout = completed.stdout
        stderr = completed.stderr

        return ToolResult(
            success=completed.returncode == 0,
            output={
                "operation": request.operation.value,
                "command": command,
                "returncode": completed.returncode,
                "stdout": stdout,
                "stderr": stderr,
            },
            error=None if completed.returncode == 0 else stderr.strip(),
            duration_ms=(perf_counter() - started_at) * 1000,
        )

    def _is_git_repository(self) -> bool:
        """Check whether the workspace is inside a Git repository."""

        try:
            completed = subprocess.run(
                [
                    "git",
                    "rev-parse",
                    "--is-inside-work-tree",
                ],
                cwd=self._workspace_root,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                shell=False,
            )
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            return False

        return completed.returncode == 0 and completed.stdout.strip().lower() == "true"

    def _build_command(self, request: GitRequest) -> list[str]:
        """Build a safe Git command."""

        if request.operation is GitOperation.STATUS:
            return [
                "git",
                "status",
                "--short",
                "--branch",
            ]

        if request.operation is GitOperation.DIFF:
            return [
                "git",
                "diff",
                "--",
                *request.args,
            ]

        if request.operation is GitOperation.BRANCH:
            return [
                "git",
                "branch",
                "--show-current",
            ]

        if request.operation is GitOperation.LOG:
            return [
                "git",
                "log",
                "--oneline",
                "--decorate",
                "-n",
                "20",
            ]

        raise ValueError(f"Unsupported Git operation: {request.operation}")

    def _failure(
        self,
        error: str,
        started_at: float,
    ) -> ToolResult:
        """Create a failed Git result."""

        return ToolResult(
            success=False,
            error=error,
            duration_ms=(perf_counter() - started_at) * 1000,
        )
