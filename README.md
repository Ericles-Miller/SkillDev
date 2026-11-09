# claude-config

Minha configuração pessoal do Claude Code: as regras globais (`CLAUDE.md`) e as skills que valem em todos os projetos.

O `~/.claude` aponta para cá por symlink. Assim, toda mudança nas regras passa pelo git.

## Estrutura

```
claude-config/
├── CLAUDE.md                      → ~/.claude/CLAUDE.md (carregado em toda sessão)
├── install.sh                     cria os symlinks, instala os plugins e o language server
├── plugins.txt                    plugins do Claude Code instalados pelo install.sh
├── hookify/                       → ~/.claude/hookify (regras a copiar para o .claude/ de cada projeto)
└── skills/
    ├── nestjs-padrao/             → ~/.claude/skills/nestjs-padrao
    │   ├── SKILL.md               quando usar e checklist do padrão
    │   ├── references/padroes.md  o guia completo, com exemplos
    │   └── templates/             configs e arquivos iniciais de um projeto Nest
    ├── jira-task/                 → ~/.claude/skills/jira-task
    │   ├── SKILL.md               passo a passo, prioridades e checklist do card
    │   └── references/modelos.md  modelos de descrição (tarefa, bug, tela, decisão, epic)
    ├── test-driven-development/   do Superpowers: teste antes do código
    ├── systematic-debugging/      do Superpowers: causa raiz antes da correção
    └── verification-before-completion/  do Superpowers: prova antes de dizer que terminou
```

- **`CLAUDE.md`**: regras curtas que valem sempre, em qualquer projeto.
- **Skill `nestjs-padrao`**: o Claude carrega quando a tarefa é NestJS/TypeScript. Também dá para chamar direto com `/nestjs-padrao`.
- **Skill `jira-task`**: o Claude carrega para abrir task, bug ou epic no Jira. Também dá para chamar direto com `/jira-task`. Toda decisão e todo débito técnico são definidos antes de criar o card.

## Instalar

```bash
./install.sh
```

O script faz quatro coisas:
- Cria os symlinks. Se já existir um arquivo de verdade no lugar, ele é movido para `~/.claude/backup-claude-config-<data>/` antes.
- Instala os plugins de `plugins.txt`: `typescript-lsp` (o Claude passa a ver os erros de tipo e a navegar pelo código TypeScript) e `hookify` (transforma regra em bloqueio).
- Instala com yarn o `typescript-language-server`, que o `typescript-lsp` usa. A versão fica fixa em 5.3.0, porque a 6.x pede Node 22.22 ou mais novo.
- Pode rodar de novo sem problema.

## Hookify

As regras do hookify valem por projeto: o plugin só lê os arquivos `.claude/hookify.*.local.md` do projeto aberto. Para ligar as regras num projeto que já existe:

```bash
mkdir -p .claude && cp ~/.claude/hookify/*.local.md .claude/
```

Projeto novo criado pela skill `nestjs-padrao` já recebe as regras.

| Regra | O que faz |
|---|---|
| `block-npm` | Barra `npm` como comando e mostra o equivalente em yarn. Deixa passar `npx`, `pnpm` e a palavra "npm" dentro de um texto, como uma mensagem de commit. |

## Skills de terceiros

`test-driven-development`, `systematic-debugging` e `verification-before-completion` são cópias do [obra/superpowers](https://github.com/obra/superpowers) (commit `22f0b46`, licença MIT, que vai junto em cada pasta). O texto original foi mantido em inglês, para facilitar a comparação com versões novas. Os únicos ajustes:
- `npm` virou `yarn`.
- `*.test.ts` virou `*.spec.ts`.
- As referências `superpowers:<skill>` perderam o prefixo.

Para atualizar, compare com a versão nova do Superpowers e refaça esses três ajustes.

## Mudar uma regra

1. Edite aqui mesmo, no VS Code. O symlink faz a mudança valer na próxima sessão do Claude.
2. Faça o commit: `git commit -am "docs: <o que mudou>"`.

Uma skill nova é uma pasta nova em `skills/` com um `SKILL.md`. Depois, rode o `./install.sh` de novo.

## Origem dos padrões

Os padrões foram extraídos de [Ericles-Miller/microsservice](https://github.com/Ericles-Miller/microsservice) (commit `888a298`), que segue o padrão do projeto calhas.
