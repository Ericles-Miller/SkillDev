---
name: warn-jest-mock
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.spec\.ts$
  - field: content
    operator: regex_match
    pattern: jest\.mock\(
---

🧪 **`jest.mock` num teste.**

O padrão é um fake em memória com o mesmo contrato do real (ex.: `InMemoryChargesRepository`), não `jest.mock`. Mock só para algo externo e lento (rede, fila, SMTP), com um comentário dizendo por quê.
