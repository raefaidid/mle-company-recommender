from datetime import datetime, timezone

import pytest

from catalogue import Catalogue
from consumer import Ack, Consumer
from embedder import FastEmbedder
from quarantine import Quarantine

DSN = "postgresql://postgres:postgres@localhost:5432/companies"
SCHEMA = "test_consumer"

DESCRIBED = (
    b'{"type": "company-upserted", "registrationNumber": "SYN-001777", '
    b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": '
    b'"Global Maju Packaging Sdn. Bhd.", "natureOfBusiness": '
    b'"Production of rubber gloves for export", "state": "Negeri Sembilan", '
    b'"industry": "Manufacturing"}}'
)


@pytest.fixture(scope="module")
def embedder():
    return FastEmbedder()


@pytest.fixture
def catalogue():
    stored = Catalogue(DSN, schema=SCHEMA, dimensions=384)
    yield stored
    stored.close()
    import psycopg

    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")


@pytest.fixture
def quarantine():
    store = Quarantine(DSN, schema=SCHEMA)
    yield store
    store.close()


@pytest.fixture
def consumer(catalogue: Catalogue, embedder: FastEmbedder, quarantine: Quarantine):
    return Consumer(catalogue, embedder, quarantine)


def test_described_company_is_stored_and_acknowledged(
    consumer: Consumer, catalogue: Catalogue
):
    decision = consumer.handle(DESCRIBED)

    assert isinstance(decision, Ack)
    stored = catalogue.get("SYN-001777")
    assert stored is not None
    assert stored.status == "active"
    assert stored.company_name == "Global Maju Packaging Sdn. Bhd."
    assert stored.industry == "Manufacturing"
    assert stored.state == "Negeri Sembilan"
    assert stored.source_updated_at == datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)
    assert stored.embedding is not None
    assert len(stored.embedding) == 384

    twin = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-009999", '
        b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": '
        b'"Different Name Sdn. Bhd.", "natureOfBusiness": '
        b'"Production of rubber gloves for export", "state": "Johor", '
        b'"industry": "Retail"}}'
    )
    assert isinstance(consumer.handle(twin), Ack)
    twin_stored = catalogue.get("SYN-009999")
    assert twin_stored is not None
    assert twin_stored.embedding == stored.embedding


def test_epoch_timestamp_is_stored_as_utc(
    consumer: Consumer, catalogue: Catalogue, quarantine: Quarantine
):
    raw = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000842", '
        b'"updatedAt": 1786671038000, "data": {"companyName": '
        b'"Everbright Teguh Solutions PLT", "natureOfBusiness": '
        b'"Pembangunan perisian perakaunan", "state": "Selangor", '
        b'"industry": "Technology"}}'
    )

    decision = consumer.handle(raw)

    assert isinstance(decision, Ack)
    stored = catalogue.get("SYN-000842")
    assert stored is not None
    assert stored.source_updated_at == datetime(2026, 8, 14, 1, 30, 38, tzinfo=timezone.utc)
    assert quarantine.matching(raw) == []


def test_later_source_time_wins_even_if_it_arrives_first(consumer: Consumer, catalogue: Catalogue):
    newer = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000099", '
        b'"updatedAt": "2026-08-14T10:00:00+08:00", "data": {"companyName": "New Name", '
        b'"natureOfBusiness": "Retail of stationery", "state": "Perak", "industry": "Retail"}}'
    )
    older = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000099", '
        b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": "Old Name", '
        b'"natureOfBusiness": "Retail of stationery", "state": "Perak", "industry": "Retail"}}'
    )

    assert isinstance(consumer.handle(newer), Ack)
    assert isinstance(consumer.handle(older), Ack)
    stored = catalogue.get("SYN-000099")
    assert stored is not None
    assert stored.company_name == "New Name"


def test_company_with_no_description_is_stored_and_not_embedded(
    consumer: Consumer, catalogue: Catalogue
):
    raw = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000200", '
        b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": '
        b'"No Description Sdn. Bhd.", "natureOfBusiness": "", "state": "Kedah", '
        b'"industry": "Retail"}}'
    )

    decision = consumer.handle(raw)

    assert isinstance(decision, Ack)
    stored = catalogue.get("SYN-000200")
    assert stored is not None
    assert stored.company_name == "No Description Sdn. Bhd."
    assert stored.embedding is None


def test_strike_off_is_stored_and_acknowledged(consumer: Consumer, catalogue: Catalogue):
    strike_off = (
        b'{"type": "company-struck-off", "registrationNumber": "SYN-001748", '
        b'"updatedAt": "2026-08-14T16:00:33+08:00"}'
    )
    neighbour = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000010", '
        b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": "Still Trading", '
        b'"natureOfBusiness": "Retail of mobile phones", "state": "Perak", "industry": "Retail"}}'
    )

    assert isinstance(consumer.handle(strike_off), Ack)
    assert isinstance(consumer.handle(neighbour), Ack)

    stored = catalogue.get("SYN-001748")
    assert stored is not None
    assert stored.status == "struck_off"
    assert stored.company_name is None
    cards = catalogue.similar("SYN-000010")
    assert "SYN-001748" not in [card.registration_number for card in cards]
