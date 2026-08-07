from pathlib import Path

from packages.tools.file_tool import FileTool


def test_file_tool_validates_workspace_path(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    assert tool.validate(path="README.md") is True


def test_file_tool_rejects_empty_path(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    assert tool.validate(path="") is False


def test_file_tool_rejects_path_outside_workspace(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation="read",
        path="../outside.txt",
    )

    assert result.success is False
    assert result.error == "Path is outside the allowed workspace."


def test_file_tool_writes_and_reads_file(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    write_result = tool.execute(
        operation="write",
        path="docs/example.txt",
        content="Noticode test content.",
    )

    read_result = tool.execute(
        operation="read",
        path="docs/example.txt",
    )

    assert write_result.success is True
    assert read_result.success is True
    assert read_result.output == "Noticode test content."


def test_file_tool_checks_file_existence(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    missing_result = tool.execute(
        operation="exists",
        path="missing.txt",
    )

    (tmp_path / "existing.txt").write_text(
        "content",
        encoding="utf-8",
    )

    existing_result = tool.execute(
        operation="exists",
        path="existing.txt",
    )

    assert missing_result.success is True
    assert missing_result.output is False
    assert existing_result.success is True
    assert existing_result.output is True


def test_file_tool_rejects_missing_file(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation="read",
        path="missing.txt",
    )

    assert result.success is False
    assert result.error == "File does not exist."


def test_file_tool_rejects_unknown_operation(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation="delete",
        path="example.txt",
    )

    assert result.success is False
    assert result.error == "Unsupported operation: delete"


def test_file_tool_creates_parent_directories(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation="write",
        path="nested/folder/example.txt",
        content="Created automatically.",
    )

    created_file = tmp_path / "nested" / "folder" / "example.txt"

    assert result.success is True
    assert created_file.exists()
    assert created_file.read_text(encoding="utf-8") == "Created automatically."
