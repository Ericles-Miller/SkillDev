# claude-config

Minha configuração pessoal do Claude Code: as regras globais (`CLAUDE.md`) e as skills que valem em todos os projetos.

O `~/.claude` aponta para cá por symlink. Assim, toda mudança nas regras passa pelo git.

## Estrutura

```
claude-config/
├── CLAUDE.md                      → ~/.claude/CLAUDE.md            (a fazer)
├── install.sh                     cria os symlinks em ~/.claude    (a fazer)
└── skills/
    └── nestjs-padrao/             → ~/.claude/skills/nestjs-padrao
        ├── SKILL.md               quando e como aplicar o padrão   (a fazer)
        ├── references/padroes.md  o guia completo dos padrões
        └── templates/             eslint, prettier, tsconfig        (a fazer)
```

## Origem dos padrões

Os padrões foram extraídos de [Ericles-Miller/microsservice](https://github.com/Ericles-Miller/microsservice) (commit `888a298`), que segue o padrão do projeto calhas.
