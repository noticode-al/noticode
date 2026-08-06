from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventType(StrEnum):
    """Noticode içerisinde oluşabilecek temel olay türleri."""

    TASK_CREATED = "task.created"
    TASK_STATUS_CHANGED = "task.status_changed"
    PLAN_CREATED = "plan.created"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    VERIFICATION_STARTED = "verification.started"
    VERIFICATION_COMPLETED = "verification.completed"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


class EventSeverity(StrEnum):
    """Olayın önem seviyesini temsil eder."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Event(BaseModel):
    """Noticode içerisinde gerçekleşen bir sistem olayını temsil eder."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    type: EventType
    source: str = Field(min_length=2, max_length=100)
    severity: EventSeverity = EventSeverity.INFO
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
