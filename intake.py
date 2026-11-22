import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

MALAYSIA = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class Company:
    registration_number: str
    company_name: str
    industry: str
    state: str
    source_updated_at: datetime
    status: str


@dataclass(frozen=True)
class Rejection:
    reason: str


def _source_time(updated_at: str) -> datetime:
    parsed = datetime.fromisoformat(updated_at)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=MALAYSIA)
    return parsed.astimezone(timezone.utc)


def interpret(raw: bytes) -> Company | Rejection:
    message = json.loads(raw)
    if message is None:
        return Rejection("body was null")
    data = message["data"]
    source_updated_at = _source_time(message["updatedAt"])
    return Company(
        registration_number=message["registrationNumber"],
        company_name=data["companyName"],
        industry=data["industry"],
        state=data["state"],
        source_updated_at=source_updated_at,
        status="active",
    )
