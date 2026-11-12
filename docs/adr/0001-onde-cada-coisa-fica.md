# 0001. Onde cada coisa fica

- **Status:** Aceito em 2026-11-12

## Contexto

Regra escrita só no prompt depende de o agente lembrar dela. Quanto mais regras no texto, mais longo o prompt e menor a chance de cada uma ser seguida. Os problemas que mais importam (entregar com teste quebrado, usar npm, empurrar para `main`) são justamente falhas de lembrar uma instrução.

## Decisão

Cada coisa vai para o lugar que a garante melhor:

| Natureza | Vai para | Exemplo |
|---|---|---|
| Precisa ser garantido | Hook, com teste | `guarda_comandos.py`, `portao_stop.py` |
| Determinístico e repetível | Script, com teste | `scripts/verify-templates.sh` |
| Regra de comportamento que vale sempre | `CLAUDE.md` global, curto | idioma, yarn, dinheiro em centavos |
| Fato de um projeto | `CLAUDE.md` do projeto ou `.claude/rules/` | comandos, layout, regra de uma pasta |
| Padrão de uma stack ou de um processo | Skill | `nestjs-padrao`, `jira-task` |
| Papel com julgamento independente | Agente, com ferramentas limitadas no frontmatter | `revisor-task`, `revisor-codigo` |
| Por que uma regra existe | ADR | esta pasta |

Quando aparece um problema, a primeira pergunta é: cabe num script ou num hook? Só depois se mexe no texto de uma skill.

## Consequências

- O texto das skills e dos agentes fica com o mínimo: o processo e o julgamento.
- Garantia que vira hook ou script precisa de teste (`test_hooks.py`, `verify-templates.sh`).
- Restrição de agente vai no frontmatter (`tools`, `skills`, `maxTurns`), não em "não faça X" no prompt.
