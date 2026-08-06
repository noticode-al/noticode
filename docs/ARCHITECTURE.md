# Noticode Architecture

## 1. Vision

Noticode is an autonomous software engineering platform designed to understand, plan, modify, test and improve software projects.

The platform must remain model-agnostic. Language models are interchangeable reasoning providers, while Noticode owns orchestration, tools, memory, security and execution.

---

## 2. Core Principles

- Understand before modifying.
- Plan before executing.
- Use tools instead of assumptions.
- Verify every important change.
- Keep humans in control of destructive actions.
- Record actions for auditability.
- Prefer reversible operations.
- Treat model output as untrusted input.

---

## 3. High-Level Architecture

```text
User Interface
      |
      v
API / CLI / Desktop
      |
      v
Agent Runtime
      |
      +--> Context Manager
      +--> Planner
      +--> Model Gateway
      +--> Tool Engine
      +--> Memory
      +--> Policy Engine
      +--> Task State
      |
      v
Execution Environment
      |
      +--> File System
      +--> Terminal
      +--> Git
      +--> Test Runner
      +--> Search / Indexer
      +--> Docker / Sandbox
4. Core Modules
4.1 Agent Runtime

The Agent Runtime coordinates the complete task lifecycle.

Responsibilities:

Receive user goals.
Create and update task state.
Request plans from the model.
Invoke approved tools.
Evaluate tool results.
Retry when necessary.
Stop on completion, failure or policy limits.
4.2 Planner

The Planner converts a user request into executable steps.

A plan contains:

Goal
Assumptions
Required context
Ordered steps
Verification strategy
Risk level
Completion criteria
4.3 Model Gateway

The Model Gateway provides a common interface for different language models.

Initial providers may include:

OpenAI-compatible APIs
Local Ollama models
Future third-party providers

The rest of the platform must not depend directly on a specific provider.

4.4 Tool Engine

The Tool Engine exposes controlled operations to the Agent Runtime.

Initial tools:

list_directory
read_file
write_file
replace_text
search_code
run_command
run_tests
git_status
git_diff
git_restore

Every tool must have:

Typed input
Typed output
Permission level
Timeout
Audit record
Error handling
4.5 Memory

Memory is divided into separate scopes:

Session memory
Task memory
Project memory
User preferences
Execution history

Memory must not silently override current project files or explicit user instructions.

4.6 Context Manager

The Context Manager selects the minimum relevant information for each model request.

Responsibilities:

Read project instructions.
Select related files.
Summarize previous steps.
Enforce context limits.
Avoid sending secrets.
Preserve source references.
4.7 Policy Engine

The Policy Engine decides whether an action is:

Allowed automatically
Allowed with user confirmation
Denied

Examples requiring confirmation:

File deletion
Package installation
Git commit or push
Database mutation
Service restart
Remote SSH execution

Destructive system operations must be denied by default.

4.8 Project Indexer

The Project Indexer builds a searchable representation of a repository.

Initial implementation:

File tree
Text search
Language detection
Symbol extraction
Ignore rules

Future implementation:

Tree-sitter parsing
Dependency graph
Semantic search
Vector retrieval
5. Agent Lifecycle
1. Receive goal
2. Validate scope
3. Inspect project
4. Create plan
5. Request approval when required
6. Execute one tool action
7. Observe result
8. Update task state
9. Verify progress
10. Repeat or finish
11. Produce final report

The agent must never claim success without verification evidence.

6. Task State

Every task must store:

Task ID
User goal
Current status
Plan
Completed steps
Pending steps
Tool calls
Errors
Modified files
Verification results
Final summary

Initial statuses:

pending
planning
awaiting_approval
executing
verifying
completed
failed
cancelled


7. Security Model

Noticode will use defense in depth.

Required controls
Non-root application user
Workspace path restrictions
Command allowlist and denylist
Execution timeouts
Output size limits
Secret redaction
Git-based rollback
Container sandboxing
Audit logs
Human approval gates

Model-generated commands must never be executed without validation.

8. Repository Strategy

Noticode begins as a monorepo.

apps/
  agent/
  api/
  cli/
  desktop/

packages/
  core/
  planner/
  tools/
  memory/
  models/
  security/
  indexer/

docs/
tests/
docker/
scripts/
configs/

Modules may be separated into independent repositories only after clear operational need appears.

9. Initial Technology Decisions
Language: Python 3.12+
API: FastAPI
Validation: Pydantic
CLI: Typer
Testing: Pytest
Database: SQLite initially
Cache / queue: Added only when required
Containers: Docker and Docker Compose
Source control: Git and GitHub
10. MVP Scope

The first usable alpha must:

Open a local project workspace.
Read and search project files.
Generate a step-by-step plan.
Modify files through controlled tools.
Run approved terminal commands.
Execute tests.
Inspect Git diff.
Retry after recoverable errors.
Produce a verified task report.

The alpha will not initially include:

Multi-user support
Autonomous deployment
Unrestricted remote execution
Model training
Complex multi-agent orchestration
11. Definition of Done

A task is complete only when:

The requested change exists.
Relevant tests or checks were executed.
Results were recorded.
Modified files are listed.
Remaining risks are disclosed.
The user receives a concise final report.


