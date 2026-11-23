from datetime import datetime, timezone

import pytest

from catalogue import Catalogue
from consumer import Ack, Consumer, Retry
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
    stored = Catalogue(DSN, schema=SCHEMA)
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
    first = catalogue.get("SYN-000099")
    assert first is not None
    assert isinstance(consumer.handle(older), Ack)
    stored = catalogue.get("SYN-000099")
    assert stored is not None
    assert stored.company_name == "New Name"
    assert stored.created_at == first.created_at
    assert stored.updated_at == first.updated_at


def test_arrival_time_is_kept_and_update_time_moves(consumer: Consumer, catalogue: Catalogue):
    older = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000123", '
        b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": "First Name", '
        b'"natureOfBusiness": "Retail of stationery", "state": "Perak", "industry": "Retail"}}'
    )
    newer = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000123", '
        b'"updatedAt": "2026-08-14T10:00:00+08:00", "data": {"companyName": "Second Name", '
        b'"natureOfBusiness": "Retail of stationery", "state": "Perak", "industry": "Retail"}}'
    )

    assert isinstance(consumer.handle(older), Ack)
    arrived = catalogue.get("SYN-000123")
    assert arrived is not None
    assert arrived.created_at == arrived.updated_at

    assert isinstance(consumer.handle(newer), Ack)
    updated = catalogue.get("SYN-000123")
    assert updated is not None
    assert updated.created_at == arrived.created_at
    assert updated.updated_at >= arrived.updated_at


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


@pytest.mark.parametrize(
    ("raw", "reason", "registration"),
    [
        (b"null", "body was null", None),
        (b"{", "invalid JSON", None),
        (
            b'{"type": "company-upserted", "updatedAt": "2026-08-14T09:20:07+08:00", '
            b'"data": {"companyName": "No Reg Sdn. Bhd."}}',
            "missing registration number",
            None,
        ),
        (
            b'{"type": "company-upserted", "registrationNumber": "SYN-000829", '
            b'"data": {"companyName": "Unknown"}}',
            "missing updatedAt",
            "SYN-000829",
        ),
        (
            b'{"type": "company-upserted", "registrationNumber": "SYN-000175", '
            b'"updatedAt": "2026-08-14T09:17:46+08:00"}',
            "data is not an object",
            "SYN-000175",
        ),
        (
            b'{"type": "company-upserted", "registrationNumber": "SYN-000737", '
            b'"updatedAt": "2026-08-14T11:05:08+08:00", '
            b'"data": "companyName=Foo; state=Perak"}',
            "data is not an object",
            "SYN-000737",
        ),
    ],
)
def test_permanent_junk_is_quarantined_and_acknowledged(
    consumer: Consumer,
    catalogue: Catalogue,
    quarantine: Quarantine,
    raw: bytes,
    reason: str,
    registration: str | None,
):
    decision = consumer.handle(raw)

    assert isinstance(decision, Ack)
    records = quarantine.matching(raw)
    assert [record.reason for record in records] == [reason]
    if registration is not None:
        assert catalogue.get(registration) is None


def test_store_outage_is_not_acknowledged_and_not_quarantined(
    consumer: Consumer,
    catalogue: Catalogue,
    quarantine: Quarantine,
):
    catalogue.close()

    decision = consumer.handle(DESCRIBED)

    assert isinstance(decision, Retry)
    assert quarantine.all() == []


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
