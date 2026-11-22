from datetime import datetime, timezone

import pytest
from psycopg import connect

from catalogue import Catalogue
from intake import Company

DSN = "postgresql://postgres:postgres@localhost:5432/companies"


def _company(registration_number: str, name: str, industry: str, state: str) -> Company:
    return Company(
        registration_number=registration_number,
        company_name=name,
        industry=industry,
        state=state,
        source_updated_at=datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc),
        status="active",
    )


@pytest.fixture
def catalogue():
    schema = "test_catalogue"
    stored = Catalogue(DSN, schema=schema)
    yield stored
    stored.close()
    with connect(DSN, autocommit=True) as conn:
        conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")


def test_similar_companies_are_the_nearest_stored_cards(catalogue: Catalogue):
    catalogue.upsert(_company("SYN-000001", "Anchor Mills", "Manufacturing", "Selangor"), [1, 0])
    catalogue.upsert(_company("SYN-000002", "Near Mill", "Manufacturing", "Johor"), [0.9, 0.1])
    catalogue.upsert(_company("SYN-000003", "Far Haulage", "Logistics", "Sabah"), [0, 1])

    cards = catalogue.similar("SYN-000001")

    assert [card.registration_number for card in cards] == ["SYN-000002", "SYN-000003"]
    assert [(card.company_name, card.industry, card.state) for card in cards] == [
        ("Near Mill", "Manufacturing", "Johor"),
        ("Far Haulage", "Logistics", "Sabah"),
    ]
    assert len(cards) <= 4
