from uuid import uuid4

from packages.planner.planner import (
    Plan,
    Planner,
    PlanStepStatus,
)


def test_plan_adds_steps_in_order() -> None:
    plan = Plan(
        task_id=uuid4(),
        goal="Test plan ordering.",
    )

    first = plan.add_step("Inspect project files.")
    second = plan.add_step("Run project tests.")

    assert first.order == 1
    assert second.order == 2
    assert len(plan.steps) == 2


def test_plan_step_defaults_to_pending() -> None:
    plan = Plan(
        task_id=uuid4(),
        goal="Test plan step status.",
    )

    step = plan.add_step("Inspect repository.")

    assert step.status is PlanStepStatus.PENDING


def test_plan_can_mark_step_as_requiring_approval() -> None:
    plan = Plan(
        task_id=uuid4(),
        goal="Test approval requirement.",
    )

    step = plan.add_step(
        "Restart production service.",
        requires_approval=True,
    )

    assert step.requires_approval is True


def test_get_next_pending_step_returns_first_pending_step() -> None:
    plan = Plan(
        task_id=uuid4(),
        goal="Test next pending step.",
    )

    first = plan.add_step("First step.")
    second = plan.add_step("Second step.")

    first.status = PlanStepStatus.COMPLETED

    next_step = plan.get_next_pending_step()

    assert next_step is second


def test_get_next_pending_step_returns_none_when_complete() -> None:
    plan = Plan(
        task_id=uuid4(),
        goal="Test completed plan.",
    )

    step = plan.add_step("Only step.")
    step.status = PlanStepStatus.COMPLETED

    assert plan.get_next_pending_step() is None


def test_planner_creates_plan_from_step_descriptions() -> None:
    planner = Planner()
    task_id = uuid4()

    plan = planner.create_plan(
        task_id=task_id,
        goal="Fix failing tests.",
        steps=[
            "Run tests.",
            "Inspect failures.",
            "Apply fix.",
            "Run tests again.",
        ],
    )

    assert plan.task_id == task_id
    assert plan.goal == "Fix failing tests."
    assert len(plan.steps) == 4
    assert plan.steps[0].description == "Run tests."
    assert plan.steps[3].description == "Run tests again."
