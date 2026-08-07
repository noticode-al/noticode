import sys
from pathlib import Path

from packages.tools.terminal_tool import TerminalRequest, TerminalTool


def test_terminal_executes_allowed_command(tmp_path: Path) -> None:
    executable_name = Path(sys.executable).name

    tool = TerminalTool(
        tmp_path,
        allowed_commands={executable_name},
    )

    result = tool.execute(
        request=TerminalRequest(
            command=[
                sys.executable,
                "-c",
                "print('Noticode')",
            ]
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert result.output["returncode"] == 0
    assert result.output["stdout"].strip() == "Noticode"
    assert result.output["stderr"] == ""


def test_terminal_runs_inside_workspace(tmp_path: Path) -> None:
    executable_name = Path(sys.executable).name

    tool = TerminalTool(
        tmp_path,
        allowed_commands={executable_name},
    )

    result = tool.execute(
        request=TerminalRequest(
            command=[
                sys.executable,
                "-c",
                "import os; print(os.getcwd())",
            ]
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert Path(result.output["stdout"].strip()) == tmp_path.resolve()


def test_terminal_rejects_disallowed_command(tmp_path: Path) -> None:
    tool = TerminalTool(
        tmp_path,
        allowed_commands={"python"},
    )

    result = tool.execute(
        request=TerminalRequest(
            command=["dangerous-command"],
        )
    )

    assert result.success is False
    assert result.error == "Command is not allowed."


def test_terminal_validate_accepts_allowed_command(tmp_path: Path) -> None:
    executable_name = Path(sys.executable).name

    tool = TerminalTool(
        tmp_path,
        allowed_commands={executable_name},
    )

    request = TerminalRequest(
        command=[
            sys.executable,
            "--version",
        ]
    )

    assert tool.validate(request=request) is True


def test_terminal_validate_rejects_missing_request(tmp_path: Path) -> None:
    tool = TerminalTool(tmp_path)

    assert tool.validate() is False


def test_terminal_rejects_missing_request(tmp_path: Path) -> None:
    tool = TerminalTool(tmp_path)

    result = tool.execute()

    assert result.success is False
    assert result.error == "A valid TerminalRequest is required."


def test_terminal_reports_nonzero_exit_code(tmp_path: Path) -> None:
    executable_name = Path(sys.executable).name

    tool = TerminalTool(
        tmp_path,
        allowed_commands={executable_name},
    )

    result = tool.execute(
        request=TerminalRequest(
            command=[
                sys.executable,
                "-c",
                "import sys; print('failure', file=sys.stderr); sys.exit(2)",
            ]
        )
    )

    assert result.success is False
    assert isinstance(result.output, dict)
    assert result.output["returncode"] == 2
    assert "failure" in result.output["stderr"]
    assert result.error == "failure"


def test_terminal_command_timeout(tmp_path: Path) -> None:
    executable_name = Path(sys.executable).name

    tool = TerminalTool(
        tmp_path,
        allowed_commands={executable_name},
    )

    result = tool.execute(
        request=TerminalRequest(
            command=[
                sys.executable,
                "-c",
                "import time; time.sleep(2)",
            ],
            timeout_seconds=1,
        )
    )

    assert result.success is False
    assert result.error == "Command timed out after 1 seconds."
