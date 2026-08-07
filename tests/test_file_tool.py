from pathlib import Path

from packages.tools.file_tool import FileOperation, FileTool


def test_file_tool_validates_workspace_path(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    assert tool.validate(path="README.md") is True


def test_file_tool_rejects_empty_path(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    assert tool.validate(path="") is False


def test_file_tool_rejects_path_outside_workspace(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation=FileOperation.READ,
        path="../outside.txt",
    )

    assert result.success is False
    assert result.error == "Path is outside the allowed workspace."


def test_file_tool_writes_file(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation=FileOperation.WRITE,
        path="docs/example.txt",
        content="Noticode test content.",
    )

    output = result.output

    assert result.success is True
    assert isinstance(output, dict)
    assert output["bytes_written"] == 22
    assert output["size"] == 22
    assert output["encoding"] == "utf-8"


def test_file_tool_reads_file(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    target_file = tmp_path / "README.md"
    target_file.write_text(
        "Noticode",
        encoding="utf-8",
    )

    result = tool.execute(
        operation=FileOperation.READ,
        path="README.md",
    )

    output = result.output

    assert result.success is True
    assert isinstance(output, dict)
    assert output["content"] == "Noticode"
    assert output["size"] == 8
    assert output["encoding"] == "utf-8"


def test_file_tool_checks_file_existence(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    missing_result = tool.execute(
        operation=FileOperation.EXISTS,
        path="missing.txt",
    )

    existing_file = tmp_path / "existing.txt"
    existing_file.write_text(
        "content",
        encoding="utf-8",
    )

    existing_result = tool.execute(
        operation=FileOperation.EXISTS,
        path="existing.txt",
    )

    assert missing_result.success is True
    assert missing_result.output is False
    assert existing_result.success is True
    assert existing_result.output is True


def test_file_tool_rejects_missing_file(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation=FileOperation.READ,
        path="missing.txt",
    )

    assert result.success is False
    assert result.error == "File does not exist."


def test_file_tool_rejects_directory_read(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    directory = tmp_path / "docs"
    directory.mkdir()

    result = tool.execute(
        operation=FileOperation.READ,
        path="docs",
    )

    assert result.success is False
    assert result.error == "Path is not a file."


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
        operation=FileOperation.WRITE,
        path="nested/folder/example.txt",
        content="Created automatically.",
    )

    created_file = tmp_path / "nested" / "folder" / "example.txt"

    assert result.success is True
    assert created_file.exists()
    assert created_file.read_text(encoding="utf-8") == "Created automatically."


def test_file_tool_rejects_non_utf8_file(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    binary_file = tmp_path / "binary.dat"
    binary_file.write_bytes(b"\xff\xfe\x00\x00")

    result = tool.execute(
        operation=FileOperation.READ,
        path="binary.dat",
    )

    assert result.success is False
    assert result.error == "File is not valid UTF-8 text."


def test_file_tool_rejects_invalid_content_type(tmp_path: Path) -> None:
    tool = FileTool(tmp_path)

    result = tool.execute(
        operation=FileOperation.WRITE,
        path="example.txt",
        content=123,
    )

    assert result.success is False
    assert result.error == "Content must be a string."
