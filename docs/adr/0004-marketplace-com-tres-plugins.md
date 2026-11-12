# 0004. Marketplace com três plugins, lido direto da pasta nesta máquina

- **Status:** Aceito em 2026-11-12

## Contexto

Até então, cada skill era um link em `~/.claude/skills` e valia igual em todo projeto. Não dava para um projeto escolher o que usa, nem levar o padrão para outra máquina ou para o CI sem clonar o repositório e rodar um script.

## Decisão

O repositório é um marketplace (`skilldev`) com três plugins:
- `base`: vale em todo projeto (fluxo de task, revisores, hooks).
- `nestjs`: padrão NestJS. Também vale em todo projeto, por ser a stack principal.
- `front`: telas. É ligado só no projeto que tem telas (`--scope project`, gravado no `.claude/settings.json` do projeto).

Nesta máquina, o marketplace aponta para a pasta do repositório. O Claude Code lê os plugins direto dela, então a edição vale na próxima sessão sem reinstalar. Em outra máquina, o marketplace vem do GitHub.

## Consequências

- Skills e agentes ganham o prefixo do plugin (`base:jira-task`, `base:revisor-task`). As chamadas de agente usam o nome com prefixo.
- Agente não pode depender de caminho fixo de arquivo: carrega as skills pelo frontmatter (`skills:`) ou pela ferramenta `Skill`.
- O `install.sh` registra o marketplace, instala `base` e `nestjs` e remove os links do formato antigo.
