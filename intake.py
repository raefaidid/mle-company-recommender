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


def interpret(raw: bytes) -> Company:
    message = json.loads(raw)
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
