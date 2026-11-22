import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

MALAYSIA = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class Company:
    registration_number: str
    company_name: str | None
    industry: str | None
    state: str | None
    source_updated_at: datetime
    status: str
    nature_of_business: str | None = None


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
    source_updated_at = _source_time(message["updatedAt"])
    if message["type"] == "company-struck-off":
        return Company(
            registration_number=message["registrationNumber"],
            company_name=None,
            industry=None,
            state=None,
            source_updated_at=source_updated_at,
            status="struck_off",
        )
    data = message["data"]
    return Company(
        registration_number=message["registrationNumber"],
        company_name=data["companyName"],
        industry=data["industry"],
        state=data["state"],
        source_updated_at=source_updated_at,
        status="active",
    )
