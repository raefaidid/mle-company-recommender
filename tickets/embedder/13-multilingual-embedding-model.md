# Multilingual embedding model

```gherkin
Feature: Embeddings

  Scenario: A Malay description is close to its English translation
    Given the Malay description "Pengeluaran sarung tangan getah untuk eksport"
      And the English description "Production of rubber gloves for export"
      And an unrelated description "Tuition centre for primary and secondary students"
    When all three are embedded
    Then the Malay and English vectors are closer than the Malay and unrelated vectors
      And the embedding is 384 dimensions
```
