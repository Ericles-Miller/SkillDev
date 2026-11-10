---
name: block-git-commit
enabled: false
event: bash
pattern: (^|[;&|(\n]\s*)git\s+(-C\s+\S+\s+)?(commit|push|merge)\b
action: block
---

🛑 **Neste projeto você não faz commit, push nem merge** (ver o `CLAUDE.md` do projeto).

No fim da task, entregue a mensagem de commit sugerida e deixe que o usuário faça o commit.
