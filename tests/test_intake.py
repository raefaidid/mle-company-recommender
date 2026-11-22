from datetime import datetime, timezone

from intake import Company, Rejection, interpret

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
    assert result.source_updated_at == datetime(2026, 8, 14, 8, 0, 33, tzinfo=timezone.utc)
