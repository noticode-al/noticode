from typing import Any
from uuid import uuid4

from packages.agent.agent import Agent, AgentStatus
from packages.planner.planner import Plan, PlanStepStatus
from packages.tools.base import Tool
from packages.tools.registry import ToolRegistry
from packages.tools.result import ToolResult


class SuccessfulTool(Tool):
    """Tool used to test successful agent execution."""

    name = "success"
    description = "Always succeeds."

    def validate(self, **kwargs: Any) -> bool:
        return True

    def execute(self, **kwargs: Any) -> ToolResult:
        return ToolResult(
            success=True,
            output={
                "message": "completed",
            },
        )


class FailingTool(Tool):
    """Tool used to test failed agent execution."""

    name = "failure"
    description = "Always fails."

    def validate(self, **kwargs: Any) -> bool:
        return True

    def execute(self, **kwargs: Any) -> ToolResult:
        return ToolResult(
            success=False,
            error="Tool failed.",
        )


def create_plan(
    requires_approval: bool = False,
) -> Plan:
    plan = Plan(
        task_id=uuid4(),
        goal="Test the agent loop.",
    )

    plan.add_step(
        "Execute test tool.",
        requires_approval=requires_approval,
    )

    return plan


def test_agent_creates_run() -> None:
    registry = ToolRegistry()
    agent = Agent(registry)

    run = agent.create_run(create_plan())

    assert run.status is AgentStatus.CREATED
    assert run.results == []
    assert run.error is None


def test_agent_executes_successful_tool() -> None:
    registry = ToolRegistry()
    registry.register(SuccessfulTool())

    agent = Agent(registry)
    run = agent.create_run(create_plan())

    result = agent.execute_step(
        run=run,
        tool_name="success",
        tool_arguments={},
    )

    assert result.success is True
    assert run.status is AgentStatus.COMPLETED
    assert run.plan.steps[0].status is PlanStepStatus.COMPLETED
    assert len(run.results) == 1
    assert run.results[0].tool_name == "success"


def test_agent_marks_failed_tool_execution() -> None:
    registry = ToolRegistry()
    registry.register(FailingTool())

    agent = Agent(registry)
    run = agent.create_run(create_plan())

    result = agent.execute_step(
        run=run,
        tool_name="failure",
        tool_arguments={},
    )

    assert result.success is False
    assert run.status is AgentStatus.FAILED
    assert run.plan.steps[0].status is PlanStepStatus.FAILED
    assert run.error == "Tool failed."


def test_agent_rejects_unknown_tool() -> None:
    registry = ToolRegistry()
    agent = Agent(registry)
    run = agent.create_run(create_plan())

    result = agent.execute_step(
        run=run,
        tool_name="missing",
        tool_arguments={},
    )

    assert result.success is False
    assert run.status is AgentStatus.FAILED
    assert run.plan.steps[0].status is PlanStepStatus.FAILED
    assert result.error == "Tool is not registered: missing"


def test_agent_waits_for_approval() -> None:
    registry = ToolRegistry()
    registry.register(SuccessfulTool())

    agent = Agent(registry)

    run = agent.create_run(
        create_plan(
            requires_approval=True,
        )
    )

    result = agent.execute_step(
        run=run,
        tool_name="success",
        tool_arguments={},
    )

    assert result.success is False
    assert run.status is AgentStatus.WAITING_APPROVAL
    assert run.plan.steps[0].status is PlanStepStatus.PENDING
    assert result.error == "Plan step requires approval."


def test_agent_completes_multiple_steps() -> None:
    registry = ToolRegistry()
    registry.register(SuccessfulTool())

    plan = Plan(
        task_id=uuid4(),
        goal="Execute multiple steps.",
    )

    plan.add_step("First operation.")
    plan.add_step("Second operation.")

    agent = Agent(registry)
    run = agent.create_run(plan)

    first_result = agent.execute_step(
        run=run,
        tool_name="success",
        tool_arguments={},
    )

    assert first_result.success is True
    assert run.status is AgentStatus.RUNNING

    second_result = agent.execute_step(
        run=run,
        tool_name="success",
        tool_arguments={},
    )

    assert second_result.success is True
    assert run.status.value == "completed"
    assert len(run.results) == 2
    assert all(step.status is PlanStepStatus.COMPLETED for step in run.plan.steps)


def test_agent_reports_when_no_steps_remain() -> None:
    registry = ToolRegistry()
    registry.register(SuccessfulTool())

    agent = Agent(registry)
    run = agent.create_run(create_plan())

    agent.execute_step(
        run=run,
        tool_name="success",
        tool_arguments={},
    )

    result = agent.execute_step(
        run=run,
        tool_name="success",
        tool_arguments={},
    )

    assert result.success is False
    assert run.status.value == "completed"
    assert result.error == "No pending plan step is available."
