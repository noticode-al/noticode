from enum import StrEnum
from typing import Any, cast
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from packages.planner.planner import Plan, PlanStep, PlanStepStatus
from packages.tools.registry import ToolRegistry
from packages.tools.result import ToolResult


class AgentStatus(StrEnum):
    """Possible states of an agent run."""

    CREATED = "created"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStepResult(BaseModel):
    """Execution result associated with a plan step."""

    model_config = ConfigDict(extra="forbid")

    step_id: UUID
    tool_name: str
    result: ToolResult


class AgentRun(BaseModel):
    """Runtime state of a single agent execution."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)
    plan: Plan
    status: AgentStatus = AgentStatus.CREATED
    results: list[AgentStepResult] = Field(default_factory=list)
    error: str | None = None


class Agent:
    """Execute plan steps through registered tools."""

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry

    def create_run(self, plan: Plan) -> AgentRun:
        """Create a new agent run."""

        return AgentRun(plan=plan)

    def next_step(self, run: AgentRun) -> PlanStep | None:
        """Return the next executable plan step."""

        return run.plan.get_next_pending_step()

    def execute_step(
        self,
        run: AgentRun,
        tool_name: str,
        tool_arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute the next pending plan step with a registered tool."""

        step = self.next_step(run)

        if step is None:
            run.status = AgentStatus.COMPLETED

            return ToolResult(
                success=False,
                error="No pending plan step is available.",
            )

        if step.requires_approval:
            run.status = AgentStatus.WAITING_APPROVAL

            return ToolResult(
                success=False,
                error="Plan step requires approval.",
            )

        try:
            tool = self._tool_registry.get(tool_name)
        except KeyError:
            run.status = AgentStatus.FAILED
            step.status = PlanStepStatus.FAILED
            run.error = f"Tool is not registered: {tool_name}"

            return ToolResult(
                success=False,
                error=run.error,
            )

        run.status = AgentStatus.RUNNING
        step.status = PlanStepStatus.IN_PROGRESS

        try:
            raw_result = tool.execute(**tool_arguments)
        except Exception as exc:
            step.status = PlanStepStatus.FAILED
            run.status = AgentStatus.FAILED
            run.error = f"Tool execution raised an exception: {exc}"

            return ToolResult(
                success=False,
                error=run.error,
            )

        result = cast(ToolResult, raw_result)

        run.results.append(
            AgentStepResult(
                step_id=step.id,
                tool_name=tool_name,
                result=result,
            )
        )

        if result.success:
            step.status = PlanStepStatus.COMPLETED

            if self.next_step(run) is None:
                run.status = AgentStatus.COMPLETED
        else:
            step.status = PlanStepStatus.FAILED
            run.status = AgentStatus.FAILED
            run.error = result.error

        return result
