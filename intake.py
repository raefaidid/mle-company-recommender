import json
from dataclasses import dataclass
from datetime import datetime, timezone


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


def interpret(raw: bytes) -> Company | Rejection:
    message = json.loads(raw)
    if message is None:
        return Rejection("body was null")
    data = message["data"]
    source_updated_at = datetime.fromisoformat(message["updatedAt"]).astimezone(timezone.utc)
    return Company(
        registration_number=message["registrationNumber"],
        company_name=data["companyName"],
        industry=data["industry"],
        state=data["state"],
        source_updated_at=source_updated_at,
        status="active",
    )
