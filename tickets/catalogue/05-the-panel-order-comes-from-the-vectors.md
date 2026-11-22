# The panel order comes from the vectors

```gherkin
Feature: Catalogue

  Scenario: Similar companies are the nearest stored cards
    Given an empty catalogue
      And "SYN-000001" is stored with name "Anchor Mills" and vector [1, 0]
      And "SYN-000002" is stored with name "Near Mill" and vector [0.9, 0.1]
      And "SYN-000003" is stored with name "Far Haulage" and vector [0, 1]
    When similar companies are requested for "SYN-000001"
    Then the registration numbers are "SYN-000002" then "SYN-000003"
      And "SYN-000001" is not in the list
      And each card has a name, industry, and state
      And there are at most 4 cards
```
