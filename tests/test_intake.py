import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from company_recommender.intake.models import Company, Rejection
from company_recommender.intake.parser import _source_time, interpret

FEED = Path(__file__).resolve().parent.parent / "data" / "feed.jsonl"

UPSERT = (
    b'{"type": "company-upserted", "registrationNumber": "SYN-001777", '
    b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": '
    b'"Global Maju Packaging Sdn. Bhd.", "natureOfBusiness": '
    b'"Production of rubber gloves for export", "state": "Negeri Sembilan", '
    b'"industry": "Manufacturing"}}'
)


def test_company_upsert_becomes_a_company_record():
    result = interpret(UPSERT)

    assert isinstance(result, Company)
    assert result.registration_number == "SYN-001777"
    assert result.company_name == "Global Maju Packaging Sdn. Bhd."
    assert result.industry == "Manufacturing"
    assert result.state == "Negeri Sembilan"
    assert result.source_updated_at == datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)
    assert result.status == "active"
    assert result.embedding_text == "Production of rubber gloves for export"


def test_null_message_is_rejected_without_raising():
    result = interpret(b"null")

    assert isinstance(result, Rejection)
    assert "null" in result.reason.lower()


def test_timestamp_with_no_offset_is_read_as_malaysia_time():
    raw = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000521", '
        b'"updatedAt": "2026-08-14T09:06:19", "data": {"companyName": '
        b'"Everbright Indah Education Sdn. Bhd.", "natureOfBusiness": '
        b'"Tuition centre for primary and secondary students", "state": "perak", '
        b'"industry": "Education"}}'
    )

    result = interpret(raw)

    assert isinstance(result, Company)
    assert result.source_updated_at == datetime(2026, 8, 14, 1, 6, 19, tzinfo=timezone.utc)


def test_every_updated_at_in_the_feed_parses():
    unparsable = []
    for line in FEED.read_text(encoding="utf-8").splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict) or "updatedAt" not in message:
            continue
        try:
            _source_time(message["updatedAt"])
        except Exception as error:
            unparsable.append((message.get("registrationNumber"), message["updatedAt"], error))

    assert unparsable == []


def test_unparseable_updated_at_raises():
    raw = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000001", '
        b'"updatedAt": "not a timestamp", "data": {"companyName": "Broken Time"}}'
    )

    with pytest.raises(ValueError):
        interpret(raw)


def test_null_updated_at_raises():
    raw = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000001", '
        b'"updatedAt": null, "data": {"companyName": "Broken Time"}}'
    )

    with pytest.raises(TypeError):
        interpret(raw)


def test_empty_description_falls_back_to_industry_and_state():
    raw = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000200", '
        b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": '
        b'"No Description Sdn. Bhd.", "natureOfBusiness": "", "state": "kedah", '
        b'"industry": "Retail"}}'
    )

    result = interpret(raw)

    assert isinstance(result, Company)
    assert result.nature_of_business is None
    assert result.embedding_text == "Retail in Kedah"


def test_empty_description_with_no_state_falls_back_to_industry():
    raw = (
        b'{"type": "company-upserted", "registrationNumber": "SYN-000201", '
        b'"updatedAt": "2026-08-14T09:00:00+08:00", "data": {"companyName": '
        b'"No State Sdn. Bhd.", "natureOfBusiness": "", "industry": "Retail"}}'
    )

    result = interpret(raw)

    assert isinstance(result, Company)
    assert result.nature_of_business is None
    assert result.embedding_text == "Retail"


def test_strike_off_names_the_company_and_nothing_else():
    raw = (
        b'{"type": "company-struck-off", "registrationNumber": "SYN-001748", '
        b'"updatedAt": "2026-08-14T16:00:33+08:00"}'
    )

    result = interpret(raw)

    assert isinstance(result, Company)
    assert result.registration_number == "SYN-001748"
    assert result.status == "struck_off"
    assert result.company_name is None
    assert result.industry is None
    assert result.state is None
    assert result.nature_of_business is None
    assert result.embedding_text is None
    assert result.source_updated_at == datetime(2026, 8, 14, 8, 0, 33, tzinfo=timezone.utc)
