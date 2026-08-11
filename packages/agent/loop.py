from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from packages.agent.agent import AgentStatus
from packages.agent.decision import AgentAction, AgentDecision
from packages.agent.parser import AgentDecisionParseError, AgentDecisionParser
from packages.models.gateway import (
    ModelGateway,
    ModelMessage,
    ModelRequest,
)
from packages.tools.registry import ToolRegistry
from packages.tools.result import ToolResult


class AgentLoopRun(BaseModel):
    """Runtime state of an AI-driven agent loop."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    goal: str = Field(min_length=3, max_length=10_000)
    status: AgentStatus = AgentStatus.CREATED
    iterations: int = 0
    decisions: list[AgentDecision] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    messages: list[ModelMessage] = Field(default_factory=list)
    final_message: str | None = None
    error: str | None = None


class AIAgentLoop:
    """Drive model decisions, tool execution and observations."""

    SYSTEM_PROMPT = """
You are the reasoning engine of Noticode.

You must respond with exactly one JSON object and no additional text.

Available actions:

1. Tool action:
{
  "action": "tool",
  "tool_name": "<tool-name>",
  "arguments": {}
}

2. Finish action:
{
  "action": "finish",
  "message": "<final answer>"
}

Use tools when information or execution is required.
Never claim that an action succeeded without observing its tool result.
""".strip()

    def __init__(
        self,
        model_gateway: ModelGateway,
        tool_registry: ToolRegistry,
        parser: AgentDecisionParser | None = None,
        max_iterations: int = 20,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1.")

        self._model_gateway = model_gateway
        self._tool_registry = tool_registry
        self._parser = parser or AgentDecisionParser()
        self._max_iterations = max_iterations

    async def run(self, goal: str) -> AgentLoopRun:
        """Execute the autonomous reasoning loop for a user goal."""

        run = AgentLoopRun(
            goal=goal,
            status=AgentStatus.RUNNING,
            messages=[
                ModelMessage(
                    role="system",
                    content=self.SYSTEM_PROMPT,
                ),
                ModelMessage(
                    role="user",
                    content=goal,
                ),
            ],
        )

        while run.iterations < self._max_iterations:
            run.iterations += 1

            try:
                response = await self._model_gateway.generate(
                    ModelRequest(
                        messages=list(run.messages),
                        temperature=0.0,
                    )
                )
            except Exception as exc:
                return self._fail_run(
                    run,
                    f"Model request failed: {exc}",
                )

            try:
                decision = self._parser.parse(response)
            except AgentDecisionParseError as exc:
                return self._fail_run(
                    run,
                    f"Model decision could not be parsed: {exc}",
                )

            run.decisions.append(decision)

            run.messages.append(
                ModelMessage(
                    role="assistant",
                    content=decision.model_dump_json(),
                )
            )

            if decision.action is AgentAction.FINISH:
                run.status = AgentStatus.COMPLETED
                run.final_message = decision.message

                return run

            if decision.action is AgentAction.TOOL:
                tool_result = self._execute_tool(decision)

                run.tool_results.append(tool_result)

                run.messages.append(
                    ModelMessage(
                        role="tool",
                        content=tool_result.model_dump_json(),
                    )
                )

                continue

        return self._fail_run(
            run,
            f"Maximum iteration limit reached: {self._max_iterations}.",
        )

    def _execute_tool(
        self,
        decision: AgentDecision,
    ) -> ToolResult:
        """Execute the tool requested by a model decision."""

        if decision.tool_name is None:
            return ToolResult(
                success=False,
                error="Tool decision does not contain a tool name.",
            )

        try:
            tool = self._tool_registry.get(decision.tool_name)
        except KeyError:
            return ToolResult(
                success=False,
                error=f"Tool is not registered: {decision.tool_name}",
            )

        arguments: dict[str, Any] = decision.arguments

        try:
            if not tool.validate(**arguments):
                return ToolResult(
                    success=False,
                    error=f"Tool arguments are invalid: {decision.tool_name}",
                )

            raw_result = tool.execute(**arguments)

        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Tool execution raised an exception: {exc}",
            )

        if not isinstance(raw_result, ToolResult):
            return ToolResult(
                success=False,
                error=(f"Tool returned an invalid result type: {type(raw_result).__name__}"),
            )

        return raw_result

    def _fail_run(
        self,
        run: AgentLoopRun,
        error: str,
    ) -> AgentLoopRun:
        """Mark an agent loop run as failed."""

        run.status = AgentStatus.FAILED
        run.error = error

        return run
