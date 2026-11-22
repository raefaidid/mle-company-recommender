# A naive timestamp is Malaysia time

```gherkin
Feature: Intake

  Scenario: A timestamp with no offset is read as +08:00
    Given a company-upserted message for "SYN-000521"
      And updatedAt is "2026-08-14T09:06:19"
    When the message is interpreted
    Then the source time is 2026-08-14 01:06:19 UTC
```
