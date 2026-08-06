from uuid import UUID

from packages.core.event import Event, EventType
from packages.core.task import Task, TaskPriority, TaskStatus


class TaskNotFoundError(KeyError):
    """İstenen görev bulunamadığında oluşur."""


class Runtime:
    """Noticode görev yaşam döngüsünü yöneten çekirdek çalışma zamanı."""

    def __init__(self) -> None:
        self._tasks: dict[UUID, Task] = {}
        self._events: list[Event] = []

    def create_task(
        self,
        goal: str,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> Task:
        """Yeni görev oluşturur ve TASK_CREATED olayı üretir."""

        task = Task(
            goal=goal,
            priority=priority,
        )

        self._tasks[task.id] = task

        self._record_event(
            task_id=task.id,
            event_type=EventType.TASK_CREATED,
            source="runtime",
            payload={
                "goal": task.goal,
                "priority": task.priority.value,
            },
        )

        return task

    def get_task(self, task_id: UUID) -> Task:
        """Kimliğe göre görev döndürür."""

        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise TaskNotFoundError(str(task_id)) from exc

    def list_tasks(self) -> list[Task]:
        """Tüm görevleri oluşturulma sırasıyla döndürür."""

        return list(self._tasks.values())

    def change_task_status(
        self,
        task_id: UUID,
        new_status: TaskStatus,
    ) -> Task:
        """Görev durumunu değiştirir ve olay kaydı oluşturur."""

        task = self.get_task(task_id)
        previous_status = task.status

        task.change_status(new_status)

        self._record_event(
            task_id=task.id,
            event_type=EventType.TASK_STATUS_CHANGED,
            source="runtime",
            payload={
                "previous_status": previous_status.value,
                "new_status": new_status.value,
            },
        )

        return task

    def list_events(self, task_id: UUID | None = None) -> list[Event]:
        """Tüm olayları veya belirli göreve ait olayları döndürür."""

        if task_id is None:
            return list(self._events)

        return [event for event in self._events if event.task_id == task_id]

    def _record_event(
        self,
        task_id: UUID,
        event_type: EventType,
        source: str,
        payload: dict[str, object] | None = None,
    ) -> Event:
        """Yeni olay oluşturur ve olay listesine ekler."""

        event = Event(
            task_id=task_id,
            type=event_type,
            source=source,
            payload=payload or {},
        )

        self._events.append(event)
        return event
