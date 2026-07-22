"""Secret-safe log and CLI redaction."""

import re

SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|authorization)(\s*[:=]\s*)([^\s,;]+)"
)


def redact(text: str) -> str:
    """Replace values following common secret labels without logging them."""
    return SECRET_PATTERN.sub(r"\1\2[REDACTED]", text)
