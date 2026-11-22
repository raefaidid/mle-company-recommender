# A valid upsert becomes a company

```gherkin
Feature: Intake

  Scenario: A company upsert becomes a company record
    Given a company-upserted message for "SYN-001777"
      And the name is "Global Maju Packaging Sdn. Bhd."
      And the nature of business is "Production of rubber gloves for export"
      And the industry is "Manufacturing"
      And the state is "Negeri Sembilan"
      And updatedAt is "2026-08-14T09:00:00+08:00"
    When the message is interpreted
    Then the result is a company
      And the registration number is "SYN-001777"
      And the card fields are the name, industry, and state above
      And the source time is 2026-08-14 01:00:00 UTC
      And the status is active
```
