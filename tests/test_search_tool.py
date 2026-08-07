from pathlib import Path

from packages.tools.search_tool import SearchRequest, SearchTool


def test_search_finds_text(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text(
        "hello world",
        encoding="utf-8",
    )

    tool = SearchTool(tmp_path)

    result = tool.execute(
        request=SearchRequest(query="hello"),
    )

    assert result.success is True
    assert isinstance(result.output, list)
    assert len(result.output) == 1

    match = result.output[0]

    assert match["file"] == "a.txt"
    assert match["line"] == 1
    assert match["text"] == "hello world"


def test_search_is_case_insensitive_by_default(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text(
        "Hello Noticode",
        encoding="utf-8",
    )

    tool = SearchTool(tmp_path)

    result = tool.execute(
        request=SearchRequest(query="hello"),
    )

    assert result.success is True
    assert isinstance(result.output, list)
    assert len(result.output) == 1


def test_search_can_be_case_sensitive(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text(
        "Hello Noticode",
        encoding="utf-8",
    )

    tool = SearchTool(tmp_path)

    result = tool.execute(
        request=SearchRequest(
            query="hello",
            case_sensitive=True,
        ),
    )

    assert result.success is True
    assert result.output == []


def test_search_returns_empty_list_when_no_match_exists(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.txt").write_text(
        "Nothing here",
        encoding="utf-8",
    )

    tool = SearchTool(tmp_path)

    result = tool.execute(
        request=SearchRequest(query="CharacterManager"),
    )

    assert result.success is True
    assert result.output == []


def test_search_respects_max_results(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text(
        "Noticode\nNoticode\nNoticode\n",
        encoding="utf-8",
    )

    tool = SearchTool(tmp_path)

    result = tool.execute(
        request=SearchRequest(
            query="Noticode",
            max_results=2,
        ),
    )

    assert result.success is True
    assert isinstance(result.output, list)
    assert len(result.output) == 2


def test_search_skips_non_utf8_files(tmp_path: Path) -> None:
    (tmp_path / "binary.dat").write_bytes(b"\xff\xfe\x00\x00")

    tool = SearchTool(tmp_path)

    result = tool.execute(
        request=SearchRequest(query="Noticode"),
    )

    assert result.success is True
    assert result.output == []


def test_search_rejects_missing_request(tmp_path: Path) -> None:
    tool = SearchTool(tmp_path)

    result = tool.execute()

    assert result.success is False
    assert result.error == "A valid SearchRequest is required."


def test_search_validate_accepts_valid_request(tmp_path: Path) -> None:
    tool = SearchTool(tmp_path)

    request = SearchRequest(query="Noticode")

    assert tool.validate(request=request) is True


def test_search_validate_rejects_missing_request(tmp_path: Path) -> None:
    tool = SearchTool(tmp_path)

    assert tool.validate() is False
