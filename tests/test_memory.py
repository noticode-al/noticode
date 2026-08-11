from packages.memory.memory import (
    MemoryScope,
    MemoryStore,
)


def test_memory_adds_entry() -> None:
    store = MemoryStore()

    entry = store.add(
        scope=MemoryScope.TASK,
        key="target_file",
        value="exchange.cpp",
    )

    assert store.count() == 1
    assert store.get(entry.id) is entry


def test_memory_finds_entries_by_scope() -> None:
    store = MemoryStore()

    store.add(
        scope=MemoryScope.TASK,
        key="task_value",
        value="A",
    )

    store.add(
        scope=MemoryScope.PROJECT,
        key="project_value",
        value="B",
    )

    results = store.find(scope=MemoryScope.TASK)

    assert len(results) == 1
    assert results[0].key == "task_value"


def test_memory_finds_entries_by_key() -> None:
    store = MemoryStore()

    store.add(
        scope=MemoryScope.TASK,
        key="language",
        value="Python",
    )

    store.add(
        scope=MemoryScope.PROJECT,
        key="language",
        value="C++",
    )

    results = store.find(key="language")

    assert len(results) == 2


def test_memory_finds_entries_by_scope_and_key() -> None:
    store = MemoryStore()

    store.add(
        scope=MemoryScope.TASK,
        key="language",
        value="Python",
    )

    store.add(
        scope=MemoryScope.PROJECT,
        key="language",
        value="C++",
    )

    results = store.find(
        scope=MemoryScope.PROJECT,
        key="language",
    )

    assert len(results) == 1
    assert results[0].value == "C++"


def test_memory_removes_entry() -> None:
    store = MemoryStore()

    entry = store.add(
        scope=MemoryScope.SESSION,
        key="temporary",
        value=True,
    )

    removed = store.remove(entry.id)

    assert removed is True
    assert store.get(entry.id) is None
    assert store.count() == 0


def test_memory_remove_returns_false_for_unknown_entry() -> None:
    store = MemoryStore()

    entry = store.add(
        scope=MemoryScope.USER,
        key="preference",
        value="dark",
    )

    store.remove(entry.id)

    assert store.remove(entry.id) is False


def test_memory_clear_removes_all_entries() -> None:
    store = MemoryStore()

    store.add(
        scope=MemoryScope.TASK,
        key="one",
        value=1,
    )

    store.add(
        scope=MemoryScope.PROJECT,
        key="two",
        value=2,
    )

    store.clear()

    assert store.count() == 0


def test_memory_stores_metadata() -> None:
    store = MemoryStore()

    entry = store.add(
        scope=MemoryScope.PROJECT,
        key="build_command",
        value="make -j4",
        metadata={
            "source": "README.md",
        },
    )

    assert entry.metadata["source"] == "README.md"
