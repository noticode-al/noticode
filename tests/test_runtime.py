from uuid import uuid4

import pytest

from packages.core.event import EventType
from packages.core.runtime import Runtime, TaskNotFoundError
from packages.core.task import TaskPriority, TaskStatus


def test_runtime_creates_task_and_event() -> None:
    runtime = Runtime()

    task = runtime.create_task(
        goal="Runtime görev oluşturma işlemini test et.",
        priority=TaskPriority.HIGH,
    )

    events = runtime.list_events(task.id)

    assert task.goal == "Runtime görev oluşturma işlemini test et."
    assert task.priority is TaskPriority.HIGH
    assert task.status is TaskStatus.PENDING
    assert len(events) == 1
    assert events[0].type is EventType.TASK_CREATED
    assert events[0].payload["priority"] == "high"


def test_runtime_lists_tasks() -> None:
    runtime = Runtime()

    first_task = runtime.create_task("Birinci görevi oluştur.")
    second_task = runtime.create_task("İkinci görevi oluştur.")

    tasks = runtime.list_tasks()

    assert tasks == [first_task, second_task]


def test_runtime_gets_task_by_id() -> None:
    runtime = Runtime()
    created_task = runtime.create_task("Görevi kimliğine göre getir.")

    found_task = runtime.get_task(created_task.id)

    assert found_task is created_task


def test_runtime_raises_error_for_unknown_task() -> None:
    runtime = Runtime()

    with pytest.raises(TaskNotFoundError):
        runtime.get_task(uuid4())


def test_runtime_changes_status_and_records_event() -> None:
    runtime = Runtime()
    task = runtime.create_task("Görev durumunu değiştir.")

    updated_task = runtime.change_task_status(
        task.id,
        TaskStatus.PLANNING,
    )

    events = runtime.list_events(task.id)

    assert updated_task.status is TaskStatus.PLANNING
    assert len(events) == 2
    assert events[1].type is EventType.TASK_STATUS_CHANGED
    assert events[1].payload["previous_status"] == "pending"
    assert events[1].payload["new_status"] == "planning"


def test_runtime_lists_all_events() -> None:
    runtime = Runtime()

    runtime.create_task("Birinci görev.")
    runtime.create_task("İkinci görev.")

    events = runtime.list_events()

    assert len(events) == 2
    assert all(event.type is EventType.TASK_CREATED for event in events)
