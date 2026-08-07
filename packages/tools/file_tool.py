from enum import StrEnum
from pathlib import Path
from time import perf_counter
from typing import Any

from packages.tools.base import Tool
from packages.tools.result import ToolResult


class FileOperation(StrEnum):
    """Supported file operations."""

    READ = "read"
    WRITE = "write"
    EXISTS = "exists"


class FileTool(Tool):
    """Safely read and write UTF-8 files inside an allowed workspace."""

    name = "file"
    description = "Safely reads and writes files inside the configured workspace."

    def __init__(self, workspace_root: Path) -> None:
        self._workspace_root = workspace_root.resolve()

    def validate(self, **kwargs: Any) -> bool:
        """Validate the requested file path before execution."""

        raw_path = kwargs.get("path")

        if not isinstance(raw_path, str) or not raw_path.strip():
            return False

        try:
            self._resolve_path(raw_path)
        except ValueError:
            return False

        return True

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a supported file operation."""

        started_at = perf_counter()

        operation = kwargs.get("operation")
        raw_path = kwargs.get("path")

        if isinstance(operation, FileOperation):
            operation_value = operation.value
        elif isinstance(operation, str):
            operation_value = operation
        else:
            return self._failure(
                error="Operation must be a string or FileOperation.",
                started_at=started_at,
            )

        if not isinstance(raw_path, str):
            return self._failure(
                error="Path must be a string.",
                started_at=started_at,
            )

        try:
            path = self._resolve_path(raw_path)

            if operation_value == FileOperation.EXISTS:
                return self._success(
                    output=path.exists(),
                    started_at=started_at,
                )

            if operation_value == FileOperation.READ:
                return self._read_file(
                    path=path,
                    started_at=started_at,
                )

            if operation_value == FileOperation.WRITE:
                content = kwargs.get("content")

                if not isinstance(content, str):
                    return self._failure(
                        error="Content must be a string.",
                        started_at=started_at,
                    )

                return self._write_file(
                    path=path,
                    content=content,
                    started_at=started_at,
                )

            return self._failure(
                error=f"Unsupported operation: {operation_value}",
                started_at=started_at,
            )

        except ValueError as exc:
            return self._failure(
                error=str(exc),
                started_at=started_at,
            )

    def _resolve_path(self, raw_path: str) -> Path:
        """Resolve a path and ensure it remains inside the workspace."""

        candidate = (self._workspace_root / raw_path).resolve()

        if candidate != self._workspace_root and self._workspace_root not in candidate.parents:
            raise ValueError("Path is outside the allowed workspace.")

        return candidate

    def _read_file(
        self,
        path: Path,
        started_at: float,
    ) -> ToolResult:
        """Read a UTF-8 text file."""

        if not path.exists():
            return self._failure(
                error="File does not exist.",
                started_at=started_at,
            )

        if not path.is_file():
            return self._failure(
                error="Path is not a file.",
                started_at=started_at,
            )

        if not self._is_text_file(path):
            return self._failure(
                error="File is not valid UTF-8 text.",
                started_at=started_at,
            )

        content = path.read_text(encoding="utf-8")

        return self._success(
            output={
                "path": str(path),
                "content": content,
                "size": self._file_size(path),
                "encoding": "utf-8",
            },
            started_at=started_at,
        )

    def _write_file(
        self,
        path: Path,
        content: str,
        started_at: float,
    ) -> ToolResult:
        """Write UTF-8 text to a file."""

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )

        return self._success(
            output={
                "path": str(path),
                "bytes_written": len(content.encode("utf-8")),
                "size": self._file_size(path),
                "encoding": "utf-8",
            },
            started_at=started_at,
        )

    def _file_size(self, path: Path) -> int:
        """Return file size in bytes."""

        return path.stat().st_size

    def _is_text_file(self, path: Path) -> bool:
        """Check whether a file is valid UTF-8 text."""

        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return False

        return True

    def _success(
        self,
        output: object,
        started_at: float,
    ) -> ToolResult:
        """Create a successful tool result."""

        return ToolResult(
            success=True,
            output=output,
            duration_ms=(perf_counter() - started_at) * 1000,
        )

    def _failure(
        self,
        error: str,
        started_at: float,
    ) -> ToolResult:
        """Create a failed tool result."""

        return ToolResult(
            success=False,
            error=error,
            duration_ms=(perf_counter() - started_at) * 1000,
        )
