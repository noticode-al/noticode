from uuid import uuid4

import pytest
from pydantic import ValidationError

from packages.core.event import Event, EventSeverity, EventType


def test_event_is_created_with_defaults() -> None:
    task_id = uuid4()

    event = Event(
        task_id=task_id,
        type=EventType.TASK_CREATED,
        source="runtime",
    )

    assert event.task_id == task_id
    assert event.type is EventType.TASK_CREATED
    assert event.source == "runtime"
    assert event.severity is EventSeverity.INFO
    assert event.payload == {}
    assert event.metadata == {}
    assert event.id is not None
    assert event.created_at is not None


def test_event_accepts_payload_and_metadata() -> None:
    event = Event(
        task_id=uuid4(),
        type=EventType.TOOL_COMPLETED,
        source="terminal_tool",
        severity=EventSeverity.DEBUG,
        payload={
            "command": "pytest",
            "exit_code": 0,
        },
        metadata={
            "duration_ms": 125,
        },
    )

    assert event.payload["command"] == "pytest"
    assert event.payload["exit_code"] == 0
    assert event.metadata["duration_ms"] == 125
    assert event.severity is EventSeverity.DEBUG


def test_event_rejects_short_source() -> None:
    with pytest.raises(ValidationError):
        Event(
            task_id=uuid4(),
            type=EventType.TASK_CREATED,
            source="x",
        )


def test_event_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Event(
            task_id=uuid4(),
            type=EventType.TASK_CREATED,
            source="runtime",
            unknown_field="invalid",  # type: ignore[call-arg]
        )
