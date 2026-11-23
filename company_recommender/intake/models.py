from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Company:
    registration_number: str
    company_name: str | None
    industry: str | None
    state: str | None
    source_updated_at: datetime
    status: str
    nature_of_business: str | None = None
    embedding_text: str | None = None


@dataclass(frozen=True)
class Rejection:
    reason: str
