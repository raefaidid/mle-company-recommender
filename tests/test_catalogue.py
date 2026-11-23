from datetime import datetime, timezone

from catalogue import Catalogue
from intake import Company


def _vector(*values: float) -> list[float]:
    return [*values, *([0.0] * (384 - len(values)))]


def _company(
    registration_number: str,
    name: str,
    industry: str,
    state: str,
    status: str = "active",
) -> Company:
    return Company(
        registration_number=registration_number,
        company_name=name,
        industry=industry,
        state=state,
        source_updated_at=datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc),
        status=status,
    )


def test_similar_companies_are_the_nearest_stored_cards(catalogue: Catalogue):
    catalogue.upsert(_company("SYN-000001", "Anchor Mills", "Manufacturing", "Selangor"), _vector(1, 0))
    catalogue.upsert(_company("SYN-000002", "Near Mill", "Manufacturing", "Johor"), _vector(0.9, 0.1))
    catalogue.upsert(_company("SYN-000003", "Far Haulage", "Logistics", "Sabah"), _vector(0, 1))

    cards = catalogue.similar("SYN-000001")

    assert [card.registration_number for card in cards] == ["SYN-000002", "SYN-000003"]
    assert [(card.company_name, card.industry, card.state) for card in cards] == [
        ("Near Mill", "Manufacturing", "Johor"),
        ("Far Haulage", "Logistics", "Sabah"),
    ]
    assert len(cards) <= 4


def test_struck_off_company_is_stored_and_not_recommended(catalogue: Catalogue):
    catalogue.upsert(_company("SYN-000010", "Still Trading", "Retail", "Perak"), _vector(1, 0))
    catalogue.upsert(
        _company("SYN-000011", "Gone Shop", "Retail", "Perak", status="struck_off"),
        _vector(0.9, 0.1),
    )
    catalogue.upsert(_company("SYN-000012", "Other Shop", "Retail", "Kedah"), _vector(0, 1))

    cards = catalogue.similar("SYN-000010")

    assert [card.registration_number for card in cards] == ["SYN-000012"]
    assert "SYN-000011" not in [card.registration_number for card in cards]
