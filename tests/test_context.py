from pathlib import Path

import pytest

from packages.core.context import ContextBundle, ContextManager


def test_context_bundle_adds_items_by_priority() -> None:
    bundle = ContextBundle()

    bundle.add_item(
        source="low.txt",
        content="low",
        priority=200,
    )

    bundle.add_item(
        source="high.txt",
        content="high",
        priority=10,
    )

    assert bundle.items[0].source == "high.txt"
    assert bundle.items[1].source == "low.txt"


def test_context_bundle_counts_characters() -> None:
    bundle = ContextBundle()

    bundle.add_item(
        source="a.txt",
        content="abc",
    )

    bundle.add_item(
        source="b.txt",
        content="12345",
    )

    assert bundle.total_characters() == 8


def test_context_manager_reads_selected_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text(
        "Noticode",
        encoding="utf-8",
    )

    manager = ContextManager(tmp_path)

    bundle = manager.build_from_files(["a.txt"])

    assert len(bundle.items) == 1
    assert bundle.items[0].source == "a.txt"
    assert bundle.items[0].content == "Noticode"


def test_context_manager_skips_missing_files(tmp_path: Path) -> None:
    manager = ContextManager(tmp_path)

    bundle = manager.build_from_files(["missing.txt"])

    assert bundle.items == []


def test_context_manager_skips_binary_files(tmp_path: Path) -> None:
    (tmp_path / "binary.dat").write_bytes(
        b"\xff\xfe\x00\x00",
    )

    manager = ContextManager(tmp_path)

    bundle = manager.build_from_files(["binary.dat"])

    assert bundle.items == []


def test_context_manager_respects_character_limit(
    tmp_path: Path,
) -> None:
    (tmp_path / "large.txt").write_text(
        "abcdefghij",
        encoding="utf-8",
    )

    manager = ContextManager(
        tmp_path,
        max_characters=5,
    )

    bundle = manager.build_from_files(["large.txt"])

    assert len(bundle.items) == 1
    assert bundle.items[0].content == "abcde"
    assert bundle.total_characters() == 5


def test_context_manager_rejects_path_outside_workspace(
    tmp_path: Path,
) -> None:
    manager = ContextManager(tmp_path)

    with pytest.raises(
        ValueError,
        match="Path is outside the allowed workspace.",
    ):
        manager.build_from_files(["../outside.txt"])
