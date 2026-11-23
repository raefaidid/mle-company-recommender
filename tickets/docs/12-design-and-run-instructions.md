# Design record and run instructions

```gherkin
Feature: Documentation

  Scenario: The README starts the whole pipeline
    Given a clean checkout
      And `just up` has started Postgres and RabbitMQ
    When I run `just publish`, `just consume`, and `just serve`
    Then the feed is stored and embedded
      And `GET /companies/SYN-001777/similar` returns cards

  Scenario: The design record explains the choices
    Given the repository
    Then `DESIGN.md` covers the embedding choice, latest-wins, junk handling,
      and the plan for 10x the volume
```
