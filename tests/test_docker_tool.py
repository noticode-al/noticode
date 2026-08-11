from pathlib import Path
from unittest.mock import MagicMock, patch

from packages.tools.docker_tool import (
    DockerOperation,
    DockerRequest,
    DockerTool,
)


def test_docker_validate_accepts_valid_request(
    tmp_path: Path,
) -> None:
    tool = DockerTool(tmp_path)

    request = DockerRequest(
        operation=DockerOperation.PS,
    )

    assert tool.validate(request=request) is True


def test_docker_validate_rejects_missing_request(
    tmp_path: Path,
) -> None:
    tool = DockerTool(tmp_path)

    assert tool.validate() is False


def test_docker_rejects_missing_request(
    tmp_path: Path,
) -> None:
    tool = DockerTool(tmp_path)

    result = tool.execute()

    assert result.success is False
    assert result.error == "A valid DockerRequest is required."


@patch("packages.tools.docker_tool.subprocess.run")
def test_docker_ps(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "abc123\tubuntu\tUp 5 minutes\ttest\n"
    mock_run.return_value.stderr = ""

    tool = DockerTool(tmp_path)

    result = tool.execute(
        request=DockerRequest(
            operation=DockerOperation.PS,
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert result.output["returncode"] == 0
    assert "ubuntu" in result.output["stdout"]


@patch("packages.tools.docker_tool.subprocess.run")
def test_docker_images(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ubuntu\tlatest\tabc123\t80MB\n"
    mock_run.return_value.stderr = ""

    tool = DockerTool(tmp_path)

    result = tool.execute(
        request=DockerRequest(
            operation=DockerOperation.IMAGES,
        )
    )

    assert result.success is True
    assert isinstance(result.output, dict)
    assert "ubuntu" in result.output["stdout"]


@patch("packages.tools.docker_tool.subprocess.run")
def test_docker_reports_failure(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    mock_run.return_value.returncode = 1
    mock_run.return_value.stdout = ""
    mock_run.return_value.stderr = "Docker daemon unavailable"

    tool = DockerTool(tmp_path)

    result = tool.execute(
        request=DockerRequest(
            operation=DockerOperation.PS,
        )
    )

    assert result.success is False
    assert result.error == "Docker daemon unavailable"


@patch("packages.tools.docker_tool.subprocess.run")
def test_docker_uses_workspace_as_cwd(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = ""
    mock_run.return_value.stderr = ""

    tool = DockerTool(tmp_path)

    tool.execute(
        request=DockerRequest(
            operation=DockerOperation.COMPOSE_PS,
        )
    )

    assert mock_run.call_args.kwargs["cwd"] == tmp_path.resolve()
    assert mock_run.call_args.kwargs["shell"] is False
