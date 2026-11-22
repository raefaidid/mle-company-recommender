# The portal can render the panel

```gherkin
Feature: Panel

  Scenario: The portal gets card fields, nearest first
    Given the catalogue from the nearest-cards scenario
    When the portal requests GET /companies/SYN-000001/similar
    Then the status is 200
      And the body is an object with a companies list
      And the first registration number is "SYN-000002"
      And each company has registrationNumber, companyName, industry, and state
```
