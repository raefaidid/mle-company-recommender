# A dead company is not a recommendation

```gherkin
Feature: Catalogue

  Scenario: A struck-off company is stored and not recommended
    Given an empty catalogue
      And "SYN-000010" is stored as active with a vector
      And "SYN-000011" is stored as struck off with a vector near it
    When similar companies are requested for "SYN-000010"
    Then "SYN-000011" is not in the list
```
