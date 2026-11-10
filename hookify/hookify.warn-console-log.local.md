---
name: warn-console-log
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: /src/(?!.*\.spec\.ts$)(?!main\.ts$).*\.ts$
  - field: content
    operator: regex_match
    pattern: console\.(log|debug)\(
---

🪵 **`console.log` no código da aplicação.**

Use o logger da classe: `private readonly logger = new Logger(<Classe>.name)`. Se era só para investigar, apague antes de terminar.
