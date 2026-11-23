# Equal-timestamp tie-break

```gherkin
Feature: Catalogue

  Scenario: A strike-off wins when the timestamps match
    Given a company is active at "2026-08-14T09:00:00+08:00"
      And a strike-off for the same company is at "2026-08-14T09:00:00+08:00"
    When both messages are stored, in either order
    Then the stored company is struck off

  Scenario: Two upserts at the same timestamp pick the greater message hash
    Given two upserts for the same company at "2026-08-14T09:00:00+08:00"
      And the message hashes are "a" and "b"
    When both messages are stored, in either order
    Then the stored company is the one with hash "b"
```
