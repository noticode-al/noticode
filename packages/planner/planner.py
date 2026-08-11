from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class PlanStepStatus(StrEnum):
    """Possible execution states of a plan step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep(BaseModel):
    """A single executable step inside a plan."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)
    order: int = Field(ge=1)
    description: str = Field(min_length=3, max_length=1000)
    status: PlanStepStatus = PlanStepStatus.PENDING
    requires_approval: bool = False


class Plan(BaseModel):
    """A structured execution plan for a Noticode task."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    goal: str = Field(min_length=3, max_length=2000)
    steps: list[PlanStep] = Field(default_factory=list)

    def add_step(
        self,
        description: str,
        requires_approval: bool = False,
    ) -> PlanStep:
        """Append a new step to the execution plan."""

        step = PlanStep(
            order=len(self.steps) + 1,
            description=description,
            requires_approval=requires_approval,
        )

        self.steps.append(step)

        return step

    def get_next_pending_step(self) -> PlanStep | None:
        """Return the next pending step in execution order."""

        for step in self.steps:
            if step.status is PlanStepStatus.PENDING:
                return step

        return None


class Planner:
    """Create structured execution plans for software engineering tasks."""

    def create_plan(
        self,
        task_id: UUID,
        goal: str,
        steps: list[str],
    ) -> Plan:
        """Create a plan from an ordered list of step descriptions."""

        plan = Plan(
            task_id=task_id,
            goal=goal,
        )

        for description in steps:
            plan.add_step(description)

        return plan
