# claude-config

Minha configuração pessoal do Claude Code: as regras globais (`CLAUDE.md`) e as skills que valem em todos os projetos.

O `~/.claude` aponta para cá por symlink. Assim, toda mudança nas regras passa pelo git.

## Estrutura

```
claude-config/
├── CLAUDE.md                      → ~/.claude/CLAUDE.md (carregado em toda sessão)
├── install.sh                     cria os symlinks em ~/.claude
└── skills/
    ├── nestjs-padrao/             → ~/.claude/skills/nestjs-padrao
    │   ├── SKILL.md               quando usar e checklist do padrão
    │   ├── references/padroes.md  o guia completo, com exemplos
    │   └── templates/             configs e arquivos iniciais de um projeto Nest
    └── jira-task/                 → ~/.claude/skills/jira-task
        ├── SKILL.md               passo a passo, prioridades e checklist do card
        └── references/modelos.md  modelos de descrição (tarefa, bug, tela, decisão, epic)
```

- **`CLAUDE.md`**: regras curtas que valem sempre, em qualquer projeto.
- **Skill `nestjs-padrao`**: o Claude carrega quando a tarefa é NestJS/TypeScript. Também dá para chamar direto com `/nestjs-padrao`.
- **Skill `jira-task`**: o Claude carrega para abrir task, bug ou epic no Jira. Também dá para chamar direto com `/jira-task`. Toda decisão e todo débito técnico são definidos antes de criar o card.

## Instalar

```bash
./install.sh
```

O script cria os symlinks. Se já existir um arquivo de verdade no lugar, ele é movido para `~/.claude/backup-claude-config-<data>/` antes. Pode rodar de novo sem problema.

## Mudar uma regra

1. Edite aqui mesmo, no VS Code. O symlink faz a mudança valer na próxima sessão do Claude.
2. Faça o commit: `git commit -am "docs: <o que mudou>"`.

Uma skill nova é uma pasta nova em `skills/` com um `SKILL.md`. Depois, rode o `./install.sh` de novo.

## Origem dos padrões

Os padrões foram extraídos de [Ericles-Miller/microsservice](https://github.com/Ericles-Miller/microsservice) (commit `888a298`), que segue o padrão do projeto calhas.
