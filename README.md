# claude-config

Minha configuração pessoal do Claude Code: as regras globais (`CLAUDE.md`) e as skills que valem em todos os projetos.

O `~/.claude` aponta para cá por symlink. Assim, toda mudança nas regras passa pelo git.

## Estrutura

```
claude-config/
├── CLAUDE.md                      → ~/.claude/CLAUDE.md (carregado em toda sessão)
├── install.sh                     cria os symlinks, instala os plugins e o language server
├── plugins.txt                    plugins do Claude Code instalados pelo install.sh
├── agents/                        → ~/.claude/agents/ (revisores independentes, só leitura)
│   ├── revisor-task.md            fiscal dos cards do Jira
│   └── revisor-codigo.md          fiscal do código: task, padrão, falhas, segurança, testes
├── scripts/verify-templates.sh    confere os templates do Nest num projeto descartável
├── hookify/                       → ~/.claude/hookify (regras a copiar para o .claude/ de cada projeto)
│   └── test_rules.py              testa cada regra contra comandos e edições de exemplo
└── skills/
    ├── nestjs-padrao/             → ~/.claude/skills/nestjs-padrao
    │   ├── SKILL.md               quando usar e checklist do padrão
    │   ├── references/padroes.md  o guia completo, com exemplos
    │   └── templates/             configs e arquivos iniciais de um projeto Nest
    │       └── opcional/          auth com JWT, paginação, env e docker-compose, com testes
    ├── jira-task/                 → ~/.claude/skills/jira-task
    │   ├── SKILL.md               passo a passo, prioridades e checklist do card
    │   └── references/modelos.md  modelos de descrição (tarefa, bug, tela, decisão, epic)
    ├── executar-task/             roteiro de uma task: branch, Jira, teste, verificação, commit
    ├── iniciar-projeto/           CLAUDE.md do projeto, log de decisões, pendências e .claude/
    │   └── templates/
    ├── telas-figma/               método de telas do calhas: Design System, Ficha, prompt do First Draft
    │   └── references/modelos.md  modelos dos docs, da Ficha, do prompt e da aprovação
    ├── figma-para-codigo/         implementa a partir do desenho do Figma, em web (Next) e mobile (Flutter)
    │   └── references/modelos.md  inventário, confronto, plano, mapa de tokens, checklist e conector
    ├── test-driven-development/   do Superpowers: teste antes do código
    ├── systematic-debugging/      do Superpowers: causa raiz antes da correção
    └── verification-before-completion/  do Superpowers: prova antes de dizer que terminou
```

- **`CLAUDE.md`**: regras curtas que valem sempre, em qualquer projeto.
- **Skill `nestjs-padrao`**: o Claude carrega quando a tarefa é NestJS/TypeScript. Também dá para chamar direto com `/nestjs-padrao`.
- **Skill `jira-task`**: o Claude carrega para abrir task, bug ou epic no Jira. Também dá para chamar direto com `/jira-task`. Toda decisão e todo débito técnico são definidos antes de criar o card. Ela usa quatro modelos de mercado:
  - **Pré-mortem:** antes de escrever, pergunta "por que esta task daria errado?" para achar as decisões e os riscos escondidos.
  - **ADR:** decisão grande ganha um registro próprio em `docs/decisoes/`.
  - **Critérios de aceite em Dado / Quando / Então**, com valores concretos. Cada critério vira um teste.
  - **Definition of Ready:** o portão final. O card só é criado se passar em todos os itens.
- **Skill `revisar-task` e agente `revisor-task`**: o fiscal dos cards. O agente roda com contexto limpo, sem ver a conversa em que o card foi escrito, e só tem ferramentas de leitura.
  - O que ele procura: decisão em aberto, regra de negócio quebrada (confere com os docs e o código), débito sem destino, critério que não dá para testar, dependência que não existe e task duplicada. Também faz um pré-mortem próprio.
  - O que ele devolve: BLOQUEIA, AJUSTAR e SUGESTÃO, cada item com a evidência.
  - Quando roda: a `jira-task` o chama sozinha antes de mostrar o rascunho. A skill também audita um card que já existe ou varre o backlog.
- **Skill `revisar-codigo` e agente `revisor-codigo`**: o fiscal do código, no mesmo modelo do fiscal de cards. O agente não tem terminal e só lê arquivos, a LSP e o Jira.
  - O que ele confere:
    - se cada critério Dado / Quando / Então da task tem código e teste;
    - o padrão do projeto (`nestjs-padrao` no backend, `figma-para-codigo` no front);
    - falhas e furos: `catch` que engole erro, `await` esquecido, corrida, transação;
    - segurança, qualidade dos testes e regras de negócio.
  - O que ele devolve: BLOQUEIA, AJUSTAR e SUGESTÃO, cada item com `arquivo:linha`, o cenário que quebra e a correção sugerida. Problema antigo fora do diff vira débito.
  - Quando roda: a `executar-task` o chama no fechamento da task. A skill também revisa uma branch, um PR, um módulo ou o repositório inteiro, e chama a `security-review` quando a mudança é sensível.
- **Skill `executar-task`**: o roteiro de uma task, do começo ao fim. Confere a branch, lê a task e os docs, move no Jira, implementa com teste antes, verifica, comenta na task e entrega a mensagem de commit.
- **Skill `iniciar-projeto`**: prepara um projeto, novo ou existente. Pergunta as regras (Jira, quem commita, branches, testes, cuidados) e cria o `CLAUDE.md` do projeto, o log de decisões, as pendências técnicas e o `.claude/`.

- **Skill `telas-figma`**: o método de telas do projeto calhas.
  - Uma vez por projeto: Design System Base, com o cabeçalho fixo do prompt, e os fluxos tirados do backend real.
  - Por tela: a Ficha no Jira, com os campos espelhando o DTO, e o prompt pronto para o Figma First Draft.
  - Depois do desenho: a aprovação com o `node-id` e a implementação lendo o Figma, com comparação visual.

- **Skill `figma-para-codigo`**: o caminho inverso, do desenho pronto para o código, em web (Next.js) e mobile (Flutter).
  - Uma vez por arquivo do Figma: inventário, confronto com os docs, o backend e o Design System, e um plano de front e back.
  - Por tela: implementação usando os tokens e componentes do projeto, com dado real e todos os estados, e comparação visual com os quadros.

O ciclo de uma task: `iniciar-projeto` (uma vez por projeto) → `jira-task` (abre a task já decidida) → `executar-task` (faz e fecha). Tela passa também pela `telas-figma` (do texto ao desenho) e pela `figma-para-codigo` (do desenho ao código).

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

As skills `nestjs-padrao` (projeto novo) e `iniciar-projeto` já fazem essa cópia.

| Regra | Ação | O que faz |
|---|---|---|
| `block-npm` | bloqueia | Barra `npm` como comando e mostra o equivalente em yarn. Deixa passar `npx`, `pnpm` e a palavra "npm" dentro de um texto, como uma mensagem de commit. |
| `block-push-protected` | bloqueia | Barra push para `main` ou `develop` e push com `--force`. Deixa passar o push da branch da task e o `--force-with-lease`. |
| `block-git-commit` | bloqueia, mas vem desligada | Barra `git commit`, `push` e `merge`. A skill `iniciar-projeto` liga essa regra nos projetos em que a IA não commita. |
| `warn-jest-mock` | avisa | `jest.mock` num `*.spec.ts`: o padrão é fake em memória. |
| `warn-console-log` | avisa | `console.log` ou `console.debug` em `src/`, fora de teste e do `main.ts`: o padrão é o `Logger` da classe. |

O hookify mostra o motivo do bloqueio para você, mas o Claude só vê "Blocked by hook". Por isso a regra também precisa estar escrita no `CLAUDE.md`.

## Testar as mudanças

Mudou um template do Nest ou uma regra do hookify? Rode o teste correspondente antes do commit:

```bash
./scripts/verify-templates.sh
```

```bash
python3 -I hookify/test_rules.py
```

O primeiro cria um projeto Nest descartável com os templates (base e opcionais) e roda prettier, ESLint, build, testes unitários e e2e. O segundo roda cada regra do hookify contra comandos e edições de exemplo. Toda regra nova precisa de casos no `CASES` do script.

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
