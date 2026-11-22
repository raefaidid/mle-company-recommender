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
