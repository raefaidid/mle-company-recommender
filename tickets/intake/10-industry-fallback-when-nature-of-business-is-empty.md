# Industry fallback when natureOfBusiness is empty

```gherkin
Feature: Intake

  Scenario: An empty nature of business falls back to industry and state
    Given a company-upserted message for "SYN-000200"
      And the name is "No Description Sdn. Bhd."
      And the nature of business is empty
      And the industry is "Retail"
      And the state is "kedah"
    When the consumer handles the message
    Then the message is acknowledged
      And the company is stored
      And it is embedded from "Retail in Kedah"

  Scenario: A missing state falls back to the industry alone
    Given a company-upserted message for "SYN-000201"
      And the nature of business is empty
      And the industry is "Retail"
      And the state is missing
    When the consumer handles the message
    Then the message is acknowledged
      And the company is stored
      And it is embedded from "Retail"
```
