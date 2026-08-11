from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class MemoryScope(StrEnum):
    """Supported memory scopes."""

    SESSION = "session"
    TASK = "task"
    PROJECT = "project"
    USER = "user"


class MemoryEntry(BaseModel):
    """A single memory record."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)
    scope: MemoryScope
    key: str = Field(min_length=1, max_length=200)
    value: Any
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryStore:
    """In-memory storage for Noticode memory entries."""

    def __init__(self) -> None:
        self._entries: dict[UUID, MemoryEntry] = {}

    def add(
        self,
        scope: MemoryScope,
        key: str,
        value: Any,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """Add a new memory entry."""

        entry = MemoryEntry(
            scope=scope,
            key=key,
            value=value,
            metadata=metadata or {},
        )

        self._entries[entry.id] = entry
        return entry

    def get(self, entry_id: UUID) -> MemoryEntry | None:
        """Return a memory entry by ID."""

        return self._entries.get(entry_id)

    def find(
        self,
        scope: MemoryScope | None = None,
        key: str | None = None,
    ) -> list[MemoryEntry]:
        """Find memory entries by scope and/or key."""

        results: list[MemoryEntry] = []

        for entry in self._entries.values():
            if scope is not None and entry.scope is not scope:
                continue

            if key is not None and entry.key != key:
                continue

            results.append(entry)

        return results

    def remove(self, entry_id: UUID) -> bool:
        """Remove a memory entry."""

        return self._entries.pop(entry_id, None) is not None

    def clear(self) -> None:
        """Remove all memory entries."""

        self._entries.clear()

    def count(self) -> int:
        """Return number of stored memory entries."""

        return len(self._entries)
