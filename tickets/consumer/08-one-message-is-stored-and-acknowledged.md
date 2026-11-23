# One message is stored and acknowledged

```gherkin
Feature: Consumer

  Scenario: A described company is stored and acknowledged
    Given a company-upserted message for "SYN-001777"
      And the name is "Global Maju Packaging Sdn. Bhd."
      And the nature of business is "Production of rubber gloves for export"
      And the industry is "Manufacturing"
      And the state is "Negeri Sembilan"
      And updatedAt is "2026-08-14T09:00:00+08:00"
    When the consumer handles the message
    Then the message is acknowledged
      And the company is stored as active
      And the stored name, industry, and state are the fields above
      And the embedding is 384 dimensions of that nature of business
      And the source time is 2026-08-14 01:00:00 UTC

  Scenario: An epoch timestamp is stored as UTC
    Given a company-upserted message for "SYN-000842"
      And the nature of business is "Pembangunan perisian perakaunan"
      And updatedAt is 1786671038000
    When the consumer handles the message
    Then the message is acknowledged
      And the company is stored
      And the source time is 2026-08-14 01:30:38 UTC
      And the message is not quarantined

  Scenario: The later source time wins, even if it arrives first
    Given a company-upserted message for "SYN-000099" named "New Name" at "2026-08-14T10:00:00+08:00"
      And a company-upserted message for "SYN-000099" named "Old Name" at "2026-08-14T09:00:00+08:00"
    When the consumer handles the newer message and then the older message
    Then both messages are acknowledged
      And the stored name is "New Name"

  Scenario: The arrival time is kept when a newer message updates the company
    Given a company-upserted message for "SYN-000123" at "2026-08-14T09:00:00+08:00"
      And a company-upserted message for "SYN-000123" at "2026-08-14T10:00:00+08:00"
    When the consumer handles the older message and then the newer message
    Then both messages are acknowledged
      And the arrival time is the time of the first message
      And the update time is not earlier than the arrival time

  Scenario: A company with no description is stored and not embedded
    Given a company-upserted message for "SYN-000200"
      And the name is "No Description Sdn. Bhd."
      And the nature of business is empty
    When the consumer handles the message
    Then the message is acknowledged
      And the company is stored
      And it has no embedding

  Scenario: A strike-off is stored and acknowledged
    Given a company-struck-off message for "SYN-001748"
      And updatedAt is "2026-08-14T16:00:33+08:00"
    When the consumer handles the message
    Then the message is acknowledged
      And the company is stored as struck off
      And it is not returned as a similar company
```
