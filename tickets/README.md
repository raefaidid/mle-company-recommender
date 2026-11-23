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
| 08 | [One message is stored and acknowledged](consumer/08-one-message-is-stored-and-acknowledged.md) | consumer | Done | `tests/test_consumer.py::test_described_company_is_stored_and_acknowledged`<br>`test_epoch_timestamp_is_stored_as_utc`<br>`test_later_source_time_wins_even_if_it_arrives_first`<br>`test_arrival_time_is_kept_and_update_time_moves`<br>`test_strike_off_is_stored_and_acknowledged` |
| 09 | [Permanent junk is quarantined and acknowledged](consumer/09-permanent-junk-is-quarantined-and-acknowledged.md) | consumer | Done | `tests/test_consumer.py::test_permanent_junk_is_quarantined_and_acknowledged`<br>`test_unparseable_updated_at_fails_loudly`<br>`test_store_outage_is_not_acknowledged_and_not_quarantined` |
| 10 | [Industry fallback when `natureOfBusiness` is empty](intake/10-industry-fallback-when-nature-of-business-is-empty.md) | intake | Done | `tests/test_intake.py::test_empty_description_falls_back_to_industry_and_state`<br>`tests/test_intake.py::test_empty_description_with_no_state_falls_back_to_industry`<br>`tests/test_consumer.py::test_empty_nature_of_business_is_embedded_from_industry_and_state` |
| 11 | [Equal-timestamp tie-break: strike-off first, then hash](catalogue/11-equal-timestamp-tie-break.md) | catalogue | Done | `tests/test_catalogue.py::test_strike_off_wins_when_timestamps_match`<br>`test_an_equal_timestamp_upsert_does_not_revive_a_strike_off`<br>`test_equal_timestamp_upserts_pick_the_greater_hash` |
| 12 | [Design record, entrypoints, and run instructions](docs/12-design-and-run-instructions.md) | docs | Done | `tests/test_entrypoints.py::test_ack_settles_the_message`<br>`test_retry_requeues_without_acking`<br>`test_entrypoints_are_importable`<br>`test_readme_documents_the_pipeline` |

## Second MVP

| # | Ticket | Seam | Status | Test |
|---|--------|------|--------|------|
| 13 | [Swap to a multilingual embedding model](embedder/13-multilingual-embedding-model.md) | embedder | Done | `tests/test_embedder.py::test_malay_description_is_closer_to_its_english_translation` |

Deferred, not ticketed yet: batch embedding, HNSW tuning, full state
normalisation.
