# A strike-off is a status, not a card

```gherkin
Feature: Intake

  Scenario: A strike-off names the company and nothing else
    Given a company-struck-off message for "SYN-001748"
      And updatedAt is "2026-08-14T16:00:33+08:00"
    When the message is interpreted
    Then the result is a company
      And the status is struck off
      And there is no name, industry, state, or description
      And the source time is 2026-08-14 08:00:33 UTC
```
