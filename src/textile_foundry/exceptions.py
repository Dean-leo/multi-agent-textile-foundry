"""Domain-specific exceptions with safe, user-facing messages."""


class TextileFoundryError(Exception):
    """Base exception for expected application failures."""


class ConfigurationError(TextileFoundryError):
    """Raised when required safe configuration is missing or invalid."""


class DataValidationError(TextileFoundryError):
    """Raised when a local knowledge file is malformed."""


class DataNotFoundError(TextileFoundryError):
    """Raised when a required material, process, or cost is unavailable."""


class CompatibilityError(TextileFoundryError):
    """Raised when a proposed design violates deterministic rules."""


class ModelOutputError(TextileFoundryError):
    """Raised when model output cannot be validated."""


class ModelTimeoutError(TextileFoundryError):
    """Raised when the model times out after bounded attempts."""
