from datetime import datetime, timezone

from fastapi.testclient import TestClient

from catalogue import Catalogue
from intake import Company
from panel import create_app


def _company(registration_number: str, name: str, industry: str, state: str) -> Company:
    return Company(
        registration_number=registration_number,
        company_name=name,
        industry=industry,
        state=state,
        source_updated_at=datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc),
        status="active",
    )


def test_portal_gets_card_fields_nearest_first(catalogue: Catalogue):
    catalogue.upsert(_company("SYN-000001", "Anchor Mills", "Manufacturing", "Selangor"), [1, 0])
    catalogue.upsert(_company("SYN-000002", "Near Mill", "Manufacturing", "Johor"), [0.9, 0.1])
    catalogue.upsert(_company("SYN-000003", "Far Haulage", "Logistics", "Sabah"), [0, 1])

    response = TestClient(create_app(catalogue)).get("/companies/SYN-000001/similar")

    assert response.status_code == 200
    companies = response.json()["companies"]
    assert companies[0]["registrationNumber"] == "SYN-000002"
    assert [company["registrationNumber"] for company in companies] == ["SYN-000002", "SYN-000003"]
    for company in companies:
        assert {"registrationNumber", "companyName", "industry", "state"} <= company.keys()
