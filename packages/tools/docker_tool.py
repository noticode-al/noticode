import subprocess
from enum import StrEnum
from pathlib import Path
from time import perf_counter
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from packages.tools.base import Tool
from packages.tools.result import ToolResult


class DockerOperation(StrEnum):
    """Supported Docker operations."""

    PS = "ps"
    IMAGES = "images"
    COMPOSE_PS = "compose_ps"
    COMPOSE_CONFIG = "compose_config"


class DockerRequest(BaseModel):
    """Input model for Docker operations."""

    model_config = ConfigDict(extra="forbid")

    operation: DockerOperation
    timeout_seconds: int = Field(default=30, ge=1, le=120)


class DockerTool(Tool):
    """Execute safe read-only Docker operations."""

    name = "docker"
    description = "Executes safe read-only Docker inspection commands."

    def __init__(self, workspace_root: Path) -> None:
        self._workspace_root = workspace_root.resolve()

    def validate(self, **kwargs: Any) -> bool:
        """Validate Docker request."""

        request = kwargs.get("request")

        return isinstance(request, DockerRequest)

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a supported Docker operation."""

        started_at = perf_counter()

        request = kwargs.get("request")

        if not isinstance(request, DockerRequest):
            return self._failure(
                error="A valid DockerRequest is required.",
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
                error=f"Docker command timed out after {request.timeout_seconds} seconds.",
                started_at=started_at,
            )

        except FileNotFoundError:
            return self._failure(
                error="Docker executable was not found.",
                started_at=started_at,
            )

        except OSError as exc:
            return self._failure(
                error=f"Docker command execution failed: {exc}",
                started_at=started_at,
            )

        stderr = completed.stderr.strip()

        return ToolResult(
            success=completed.returncode == 0,
            output={
                "operation": request.operation.value,
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            error=None if completed.returncode == 0 else stderr,
            duration_ms=(perf_counter() - started_at) * 1000,
        )

    def _build_command(self, request: DockerRequest) -> list[str]:
        """Build a safe Docker command."""

        if request.operation is DockerOperation.PS:
            return [
                "docker",
                "ps",
                "--format",
                "{{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}",
            ]

        if request.operation is DockerOperation.IMAGES:
            return [
                "docker",
                "images",
                "--format",
                "{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}",
            ]

        if request.operation is DockerOperation.COMPOSE_PS:
            return [
                "docker",
                "compose",
                "ps",
            ]

        if request.operation is DockerOperation.COMPOSE_CONFIG:
            return [
                "docker",
                "compose",
                "config",
            ]

        raise ValueError(f"Unsupported Docker operation: {request.operation}")

    def _failure(
        self,
        error: str,
        started_at: float,
    ) -> ToolResult:
        """Create a failed Docker result."""

        return ToolResult(
            success=False,
            error=error,
            duration_ms=(perf_counter() - started_at) * 1000,
        )
