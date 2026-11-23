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


def _strike_off(registration_number: str) -> Company:
    return Company(
        registration_number=registration_number,
        company_name=None,
        industry=None,
        state=None,
        source_updated_at=datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc),
        status="struck_off",
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


def test_strike_off_wins_when_timestamps_match(catalogue: Catalogue):
    catalogue.upsert(_company("SYN-000020", "Still Trading", "Retail", "Perak"), _vector(1, 0), "a")
    catalogue.upsert(_strike_off("SYN-000020"), None, "b")

    stored = catalogue.get("SYN-000020")
    assert stored is not None
    assert stored.status == "struck_off"
    assert stored.company_name is None


def test_an_equal_timestamp_upsert_does_not_revive_a_strike_off(catalogue: Catalogue):
    catalogue.upsert(_strike_off("SYN-000021"), None, "b")
    catalogue.upsert(_company("SYN-000021", "Back Again", "Retail", "Perak"), _vector(1, 0), "a")

    stored = catalogue.get("SYN-000021")
    assert stored is not None
    assert stored.status == "struck_off"


def test_equal_timestamp_upserts_pick_the_greater_hash(catalogue: Catalogue):
    catalogue.upsert(_company("SYN-000022", "From A", "Retail", "Perak"), _vector(1, 0), "a")
    catalogue.upsert(_company("SYN-000022", "From B", "Retail", "Perak"), _vector(1, 0), "b")
    catalogue.upsert(_company("SYN-000023", "From B", "Retail", "Perak"), _vector(1, 0), "b")
    catalogue.upsert(_company("SYN-000023", "From A", "Retail", "Perak"), _vector(1, 0), "a")

    first = catalogue.get("SYN-000022")
    second = catalogue.get("SYN-000023")
    assert first is not None
    assert second is not None
    assert first.company_name == "From B"
    assert second.company_name == "From B"
