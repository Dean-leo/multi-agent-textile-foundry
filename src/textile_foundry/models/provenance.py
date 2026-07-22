"""Source provenance model shared by future repositories."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class SourceReference(BaseModel):
    """Minimal source metadata required for traceable records."""

    model_config = ConfigDict(frozen=True)

    source_id: str
    title: str
    publisher: str
    source_url: str | None
    retrieved_at: date
    license_or_terms: str
    data_scope: str
    confidence_level: str
    is_mock: bool
    notes: str
