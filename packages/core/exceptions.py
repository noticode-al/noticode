"""
Custom exceptions used throughout the Noticode platform.
"""


class NoticodeError(Exception):
    """Base exception for all Noticode errors."""


class RuntimeError(NoticodeError):
    """Raised when the runtime fails."""


class PlannerError(NoticodeError):
    """Raised when planning fails."""


class ToolError(NoticodeError):
    """Raised when a tool execution fails."""


class MemoryError(NoticodeError):
    """Raised when the memory engine fails."""


class ModelError(NoticodeError):
    """Raised when the language model fails."""


class ConfigurationError(NoticodeError):
    """Raised when configuration is invalid."""


class ValidationError(NoticodeError):
    """Raised when validation fails."""


class PermissionDeniedError(NoticodeError):
    """Raised when an operation is not allowed."""


class TaskNotFoundError(NoticodeError):
    """Raised when a task cannot be found."""
