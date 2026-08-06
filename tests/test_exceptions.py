from packages.core.exceptions import (
    ConfigurationError,
    MemoryError,
    ModelError,
    NoticodeError,
    PermissionDeniedError,
    PlannerError,
    RuntimeError,
    TaskNotFoundError,
    ToolError,
    ValidationError,
)


def test_all_exceptions_inherit_from_noticode_error() -> None:
    exceptions = [
        RuntimeError,
        PlannerError,
        ToolError,
        MemoryError,
        ModelError,
        ConfigurationError,
        ValidationError,
        PermissionDeniedError,
        TaskNotFoundError,
    ]

    for exception in exceptions:
        assert issubclass(exception, NoticodeError)
