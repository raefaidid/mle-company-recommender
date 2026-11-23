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
    embedding_text: str | None = None


@dataclass(frozen=True)
class Rejection:
    reason: str


def _description(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def _fallback_text(industry: object, state: object) -> str | None:
    parts = []
    if isinstance(industry, str) and industry.strip():
        parts.append(" ".join(industry.split()))
    if isinstance(state, str) and state.strip():
        parts.append(" ".join(state.split()).title())
    return " in ".join(parts) if parts else None


def _source_time(updated_at: str | int) -> datetime:
    if isinstance(updated_at, int):
        return datetime.fromtimestamp(updated_at / 1000, timezone.utc)
    parsed = datetime.fromisoformat(updated_at)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=MALAYSIA)
    return parsed.astimezone(timezone.utc)


def interpret(raw: bytes) -> Company | Rejection:
    try:
        message = json.loads(raw)
    except json.JSONDecodeError:
        return Rejection("invalid JSON")
    if message is None:
        return Rejection("body was null")
    if not isinstance(message, dict):
        return Rejection("body is not an object")
    if "registrationNumber" not in message:
        return Rejection("missing registration number")
    if "updatedAt" not in message:
        return Rejection("missing updatedAt")
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
    data = message.get("data")
    if not isinstance(data, dict):
        return Rejection("data is not an object")
    industry = data.get("industry")
    state = data.get("state")
    description = _description(data.get("natureOfBusiness"))
    return Company(
        registration_number=message["registrationNumber"],
        company_name=data["companyName"],
        industry=industry,
        state=state,
        source_updated_at=source_updated_at,
        status="active",
        nature_of_business=description,
        embedding_text=description or _fallback_text(industry, state),
    )
