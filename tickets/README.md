# Tickets

## MVP

| # | Ticket | Seam | Status | Test |
|---|--------|------|--------|------|
| 01 | [A valid upsert becomes a company](intake/01-a-valid-upsert-becomes-a-company.md) | intake | Done | `tests/test_intake.py::test_company_upsert_becomes_a_company_record` |
| 02 | [Garbage is a rejection](intake/02-garbage-is-a-rejection.md) | intake | Done | `tests/test_intake.py::test_null_message_is_rejected_without_raising` |
| 03 | [A naive timestamp is Malaysia time](intake/03-a-naive-timestamp-is-malaysia-time.md) | intake | Done | `tests/test_intake.py::test_timestamp_with_no_offset_is_read_as_malaysia_time` |
| 04 | [A strike-off is a status, not a card](intake/04-a-strike-off-is-a-status-not-a-card.md) | intake | Done | `tests/test_intake.py::test_strike_off_names_the_company_and_nothing_else` |
| 05 | [The panel order comes from the vectors](catalogue/05-the-panel-order-comes-from-the-vectors.md) | catalogue | Done | `tests/test_catalogue.py::test_similar_companies_are_the_nearest_stored_cards` |
| 06 | [A dead company is not a recommendation](catalogue/06-a-dead-company-is-not-a-recommendation.md) | catalogue | Done | `tests/test_catalogue.py::test_struck_off_company_is_stored_and_not_recommended` |
| 07 | [The portal can render the panel](panel/07-the-portal-can-render-the-panel.md) | panel | Done | `tests/test_panel.py::test_portal_gets_card_fields_nearest_first` |

## Next

Rows here have no ticket file yet. Add the file when the ticket is picked up.

| # | Ticket | Seam | Status |
|---|--------|------|--------|
| 08 | Consumer: one message, interpret, embed, upsert, ack | consumer | Next |
| 09 | Quarantine permanent junk instead of retrying it | consumer | Backlog |
| 10 | Industry fallback when `natureOfBusiness` is empty | intake | Backlog |
| 11 | Equal-timestamp tie-break: strike-off first, then hash | catalogue | Backlog |
| 12 | `DESIGN.md` and README run instructions | docs | Backlog |

Deferred, not ticketed yet: batch embedding, HNSW tuning, Malay evaluation,
state normalisation.
