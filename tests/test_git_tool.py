import subprocess
from pathlib import Path

from packages.tools.git_tool import (
    GitOperation,
    GitRequest,
    GitTool,
)


def initialize_repository(path: Path) -> None:
    """Create a temporary Git repository for testing."""

    subprocess.run(
        ["git", "init"],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            "noticode@example.com",
        ],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.name",
            "Noticode Test",
        ],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )


def create_initial_commit(path: Path) -> None:
    """Create an initial commit in a test repository."""

    test_file = path / "example.txt"
    test_file.write_text(
        "Noticode\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", "example.txt"],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Initial commit",
        ],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )


def test_git_status(tmp_path: Path) -> None:
    initialize_repository(tmp_path)

    tool = GitTool(tmp_path)

    result = tool.execute(
        request=GitRequest(
            operation=GitOperation.STATUS,
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert result.output["returncode"] == 0


def test_git_branch(tmp_path: Path) -> None:
    initialize_repository(tmp_path)
    create_initial_commit(tmp_path)

    tool = GitTool(tmp_path)

    result = tool.execute(
        request=GitRequest(
            operation=GitOperation.BRANCH,
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert result.output["stdout"].strip() in {
        "master",
        "main",
    }


def test_git_diff(tmp_path: Path) -> None:
    initialize_repository(tmp_path)
    create_initial_commit(tmp_path)

    test_file = tmp_path / "example.txt"
    test_file.write_text(
        "Noticode changed\n",
        encoding="utf-8",
    )

    tool = GitTool(tmp_path)

    result = tool.execute(
        request=GitRequest(
            operation=GitOperation.DIFF,
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert "Noticode changed" in result.output["stdout"]


def test_git_log(tmp_path: Path) -> None:
    initialize_repository(tmp_path)
    create_initial_commit(tmp_path)

    tool = GitTool(tmp_path)

    result = tool.execute(
        request=GitRequest(
            operation=GitOperation.LOG,
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert "Initial commit" in result.output["stdout"]


def test_git_rejects_non_repository(tmp_path: Path) -> None:
    tool = GitTool(tmp_path)

    result = tool.execute(
        request=GitRequest(
            operation=GitOperation.STATUS,
        )
    )

    assert result.success is False
    assert result.error == "Workspace is not a Git repository."


def test_git_rejects_missing_request(tmp_path: Path) -> None:
    initialize_repository(tmp_path)

    tool = GitTool(tmp_path)

    result = tool.execute()

    assert result.success is False
    assert result.error == "A valid GitRequest is required."


def test_git_validate_accepts_repository(tmp_path: Path) -> None:
    initialize_repository(tmp_path)

    tool = GitTool(tmp_path)

    request = GitRequest(
        operation=GitOperation.STATUS,
    )

    assert tool.validate(request=request) is True


def test_git_validate_rejects_non_repository(
    tmp_path: Path,
) -> None:
    tool = GitTool(tmp_path)

    request = GitRequest(
        operation=GitOperation.STATUS,
    )

    assert tool.validate(request=request) is False
