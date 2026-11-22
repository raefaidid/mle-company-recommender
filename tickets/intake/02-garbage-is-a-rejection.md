# Garbage is a rejection

```gherkin
Feature: Intake

  Scenario: A null message is rejected without raising
    Given the raw body is the bytes for JSON null
    When the message is interpreted
    Then the result is a rejection
      And the reason says the body was null
      And no exception escapes
```
