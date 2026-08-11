from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class ContextItem(BaseModel):
    """A single piece of context provided to the model."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1, max_length=500)
    content: str
    priority: int = Field(default=100, ge=0, le=1000)


class ContextBundle(BaseModel):
    """A collection of context items selected for a task."""

    model_config = ConfigDict(extra="forbid")

    items: list[ContextItem] = Field(default_factory=list)

    def add_item(
        self,
        source: str,
        content: str,
        priority: int = 100,
    ) -> ContextItem:
        """Add an item to the context bundle."""

        item = ContextItem(
            source=source,
            content=content,
            priority=priority,
        )

        self.items.append(item)
        self.items.sort(key=lambda current: current.priority)

        return item

    def total_characters(self) -> int:
        """Return total character count across all context items."""

        return sum(len(item.content) for item in self.items)


class ContextManager:
    """Build task context from workspace files."""

    def __init__(
        self,
        workspace_root: Path,
        max_characters: int = 50_000,
    ) -> None:
        self._workspace_root = workspace_root.resolve()
        self._max_characters = max_characters

    def build_from_files(
        self,
        relative_paths: list[str],
    ) -> ContextBundle:
        """Build a context bundle from selected workspace files."""

        bundle = ContextBundle()

        for relative_path in relative_paths:
            path = self._resolve_path(relative_path)

            if not path.exists() or not path.is_file():
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError, OSError):
                continue

            if bundle.total_characters() + len(content) > self._max_characters:
                remaining = self._max_characters - bundle.total_characters()

                if remaining <= 0:
                    break

                content = content[:remaining]

            bundle.add_item(
                source=relative_path,
                content=content,
            )

            if bundle.total_characters() >= self._max_characters:
                break

        return bundle

    def _resolve_path(self, relative_path: str) -> Path:
        """Resolve and restrict paths to the workspace."""

        candidate = (self._workspace_root / relative_path).resolve()

        if candidate != self._workspace_root and self._workspace_root not in candidate.parents:
            raise ValueError("Path is outside the allowed workspace.")

        return candidate
