# Permanent junk is quarantined and acknowledged

```gherkin
Feature: Consumer

  Scenario Outline: Permanent junk is quarantined and acknowledged
    Given the raw body is <body>
    When the consumer handles the message
    Then no exception escapes
      And the message is acknowledged
      And the raw body is in quarantine
      And the reason says <reason>
      And no company is stored from that body

    Examples:
      | body | reason |
      | null | body was null |
      | { | invalid JSON |
      | {"type": "company-upserted", "updatedAt": "2026-08-14T09:20:07+08:00", "data": {"companyName": "No Reg Sdn. Bhd."}} | missing registration number |
      | {"type": "company-upserted", "registrationNumber": "SYN-000829", "data": {"companyName": "Unknown"}} | missing updatedAt |
      | {"type": "company-upserted", "registrationNumber": "SYN-000175", "updatedAt": "2026-08-14T09:17:46+08:00"} | data is not an object |
      | {"type": "company-upserted", "registrationNumber": "SYN-000737", "updatedAt": "2026-08-14T11:05:08+08:00", "data": "companyName=Foo; state=Perak"} | data is not an object |

  Scenario: An unparseable updatedAt fails loudly
    Given a company-upserted message for "SYN-000001"
      And updatedAt is "not a timestamp"
    When the consumer handles the message
    Then the consumer raises
      And nothing is written to quarantine

  Scenario: A store outage is not acknowledged and not quarantined
    Given a company-upserted message for "SYN-001777"
      And the catalogue cannot be reached
    When the consumer handles the message
    Then the message is not acknowledged
      And nothing is written to quarantine
```
