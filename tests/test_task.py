from time import sleep

import pytest
from pydantic import ValidationError

from packages.core.task import Task, TaskPriority, TaskStatus


def test_task_is_created_with_defaults() -> None:
    task = Task(goal="Noticode görev modelini oluştur.")

    assert task.goal == "Noticode görev modelini oluştur."
    assert task.status is TaskStatus.PENDING
    assert task.priority is TaskPriority.NORMAL
    assert task.id is not None
    assert task.created_at is not None
    assert task.updated_at is not None


def test_task_accepts_custom_priority() -> None:
    task = Task(
        goal="Kritik güvenlik hatasını düzelt.",
        priority=TaskPriority.CRITICAL,
    )

    assert task.priority is TaskPriority.CRITICAL


def test_task_rejects_short_goal() -> None:
    with pytest.raises(ValidationError):
        Task(goal="x")


def test_task_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Task(
            goal="Geçersiz alanı kontrol et.",
            unknown_field="test",  # type: ignore[call-arg]
        )


def test_change_status_updates_task() -> None:
    task = Task(goal="Durum değişikliğini test et.")
    previous_updated_at = task.updated_at

    sleep(0.001)
    task.change_status(TaskStatus.PLANNING)

    assert task.status is TaskStatus.PLANNING
    assert task.updated_at > previous_updated_at
