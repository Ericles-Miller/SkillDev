---
name: block-push-protected
enabled: true
event: bash
pattern: git\s+push\b[^;&|\n]*(\s(main|develop)(\s|$)|:(main|develop)(\s|$)|\s(--force|-f)(\s|=|$))
action: block
---

🛑 **Push bloqueado.**

`main` e `develop` só recebem código por Pull Request, e `--force` reescreve o histórico de quem já baixou a branch.
- Faça push da branch da task (`git push -u origin <CHAVE>-12`) e abra o PR para `develop`.
- Depois de um rebase na branch da task, use `--force-with-lease`.
