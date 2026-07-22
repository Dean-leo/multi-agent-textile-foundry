"""SQLAlchemy declarative base and timestamp helpers."""

from datetime import UTC, datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return an aware UTC timestamp for database defaults and tests."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Shared declarative base."""


class TimestampMixin:
    """Application-managed timestamps used by every mutable record."""

    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now, nullable=False)
