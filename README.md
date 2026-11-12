# claude-config (marketplace SkillDev)

Minha configuração do Claude Code: as regras globais (`CLAUDE.md`) e um **marketplace de plugins** com as skills e os agentes que uso em todo projeto.

O repositório é um marketplace (`skilldev`) com três plugins:

| Plugin | Onde vale | O que traz |
|---|---|---|
| `base` | Todo projeto | `jira-task`, `planejar-task`, `executar-task`, `revisar-task`, `revisar-codigo`, `regua-revisao`, `iniciar-projeto`, as três skills do Superpowers, os agentes `revisor-task`, `revisor-codigo` e `planejador`, os hooks e os scripts de verificação |
| `nestjs` | Todo projeto | `nestjs-padrao`, com os templates de projeto |
| `front` | Só nos projetos com telas | `telas-figma` e `figma-para-codigo` |

Dentro do plugin, cada skill e cada agente ganham o prefixo do plugin: `base:jira-task`, `base:revisor-codigo`, `nestjs:nestjs-padrao`, `front:telas-figma`.

## Estrutura

```
claude-config/
├── .claude-plugin/marketplace.json   o marketplace skilldev e a lista dos plugins
├── CLAUDE.md                         → ~/.claude/CLAUDE.md (carregado em toda sessão)
├── install.sh                        liga tudo nesta máquina
├── plugins.txt                       plugins de terceiros (typescript-lsp)
├── .github/workflows/                CI: validador e testes em todo PR; templates do Nest quando mudam
├── scripts/
│   ├── validar.py                    confere marketplace, plugins, skills, agentes, hooks e regras obrigatórias
│   └── verify-templates.sh           confere os templates do Nest num projeto descartável
├── docs/adr/                         por que cada regra existe (decisões do SkillDev)
└── plugins/
    ├── base/
    │   ├── .claude-plugin/plugin.json
    │   ├── hooks/
    │   │   ├── hooks.json            liga os três hooks abaixo
    │   │   ├── guarda_comandos.py    PreToolUse: barra npm, push protegido e (se o projeto pedir) commit
    │   │   ├── lint_edicao.py        PostToolUse: lint de cada arquivo editado e avisos do padrão
    │   │   ├── portao_stop.py        Stop: não deixa encerrar com lint ou teste quebrado no que foi editado
    │   │   └── test_hooks.py         testa os hooks (e o portão de commit) contra projetos falsos
    │   ├── scripts/
    │   │   ├── verificar.py          verificação completa (lint, build, testes) + impressão digital do código
    │   │   ├── detectar_projeto.py   gera a seção "Verificação" do CLAUDE.md a partir dos manifestos
    │   │   └── test_scripts.py       testa o detectar_projeto.py
    │   ├── agents/
    │   │   ├── revisor-task.md       fiscal dos cards do Jira (só leitura)
    │   │   ├── revisor-codigo.md     fiscal do código: task, padrão, falhas, segurança, testes (só leitura)
    │   │   └── planejador.md         escreve o plano de implementação ancorado no código (só leitura)
    │   └── skills/
    │       ├── jira-task/            abre task: pré-mortem, ADR, critérios Dado/Quando/Então, Definition of Ready
    │       ├── revisar-task/         chama o revisor de cards (um card ou o backlog)
    │       ├── planejar-task/        gera o plano com o planejador e publica na task (plano-v1)
    │       ├── executar-task/        roteiro da task: plano, teste, prova por reversão, verificação, revisão, commit
    │       ├── revisar-codigo/       chama o revisor de código (branch, PR, módulo ou repositório)
    │       ├── regua-revisao/        régua de severidade dos dois revisores (BLOQUEIA = decisão humana)
    │       ├── iniciar-projeto/      CLAUDE.md do projeto, decisões, ADRs, pendências, .claude/ e plugins
    │       ├── test-driven-development/         do Superpowers: teste antes do código
    │       ├── systematic-debugging/            do Superpowers: causa raiz antes da correção
    │       └── verification-before-completion/  do Superpowers: prova antes de dizer que terminou
    ├── nestjs/
    │   ├── .claude-plugin/plugin.json
    │   └── skills/nestjs-padrao/     checklist, guia (references/padroes.md) e templates (com opcionais)
    └── front/
        ├── .claude-plugin/plugin.json
        └── skills/
            ├── telas-figma/          do texto ao desenho: Design System, Ficha, prompt do First Draft
            └── figma-para-codigo/    do desenho ao código, em web (Next) e mobile (Flutter)
```

## As skills e os agentes

- **`CLAUDE.md`**: regras curtas que valem sempre, em qualquer projeto.
- **`nestjs:nestjs-padrao`**: o Claude carrega quando a tarefa é NestJS/TypeScript.
- **`base:jira-task`**: abre task, bug ou epic no Jira. Toda decisão e todo débito técnico são definidos antes de criar o card. Ela usa quatro modelos de mercado:
  - **Pré-mortem:** antes de escrever, pergunta "por que esta task daria errado?" para achar as decisões e os riscos escondidos.
  - **ADR:** decisão grande ganha um registro próprio em `docs/decisoes/`.
  - **Critérios de aceite em Dado / Quando / Então**, com valores concretos. Cada critério vira um teste.
  - **Definition of Ready:** o portão final. O card só é criado se passar em todos os itens.
- **`base:revisar-task` e o agente `base:revisor-task`**: o fiscal dos cards. O agente roda com contexto limpo, sem ver a conversa em que o card foi escrito, e só tem ferramentas de leitura.
  - O que ele procura: decisão em aberto, regra de negócio quebrada (confere com os docs e o código), débito sem destino, critério que não dá para testar, dependência que não existe e task duplicada. Também faz um pré-mortem próprio.
  - O que ele devolve: o veredito e os achados pela régua de revisão (BLOQUEIA, CRÍTICO, MAIOR, MENOR, NOTA), cada item com a evidência.
  - Quando roda: a `jira-task` o chama sozinha antes de mostrar o rascunho. A skill também audita um card que já existe ou varre o backlog.
- **`base:revisar-codigo` e o agente `base:revisor-codigo`**: o fiscal do código, no mesmo modelo. O agente não tem terminal e só lê arquivos, a LSP e o Jira.
  - O que ele confere: se cada critério da task tem código e teste; o padrão do projeto; falhas e furos; segurança; a qualidade dos testes; as regras de negócio.
  - O que ele devolve: o veredito e os achados pela régua de revisão, cada item com `arquivo:linha`, o cenário que quebra e a correção sugerida. Problema antigo fora do diff vira débito.
  - Quando roda: a `executar-task` o chama no fechamento da task. A skill também revisa uma branch, um PR, um módulo ou o repositório inteiro, e chama a `security-review` quando a mudança é sensível.
- **`base:planejar-task` e o agente `base:planejador`**: o plano antes do código. O agente (só leitura) liga cada critério a arquivos reais, diz o arquivo a espelhar e o teste que prova cada critério. Com o seu ok, o plano vira um comentário marcado na task (`## Plano de implementação (plano-v1)`), que a `executar-task` segue.
- **`base:executar-task`**: o roteiro de uma task, do começo ao fim. Lê a task e o plano (ou gera um), move no Jira, implementa com teste antes, faz a prova por reversão, roda a verificação completa (`verificar.py`), passa pela revisão de código, comenta na task e faz ou entrega o commit.
- **`base:iniciar-projeto`**: prepara um projeto, novo ou existente. Pergunta as regras (Jira, quem commita, branches, testes, cuidados, se tem telas) e cria o `CLAUDE.md` do projeto, o log de decisões, os ADRs, as pendências técnicas e o `.claude/`. Liga o plugin `front` quando o projeto tem telas.
- **`front:telas-figma`**: o método de telas do projeto calhas.
  - Uma vez por projeto: Design System Base, com o cabeçalho fixo do prompt, e os fluxos tirados do backend real.
  - Por tela: a Ficha no Jira, com os campos espelhando o DTO, e o prompt pronto para o Figma First Draft.
  - Depois do desenho: a aprovação com o `node-id`, e a implementação pela `figma-para-codigo`.
- **`front:figma-para-codigo`**: do desenho pronto para o código, em web (Next.js) e mobile (Flutter).
  - Uma vez por arquivo do Figma: inventário, confronto com os docs, o backend e o Design System, e um plano de front e back.
  - Por tela: implementação usando os tokens e componentes do projeto, com dado real e todos os estados, e comparação visual com os quadros.

O ciclo de uma task: `iniciar-projeto` (uma vez por projeto) → `jira-task` (abre a task já decidida, com o revisor de cards) → `executar-task` (faz e fecha, com o revisor de código). Tela passa também pela `telas-figma` (do texto ao desenho) e pela `figma-para-codigo` (do desenho ao código).

- **`base:regua-revisao`**: a régua de severidade dos dois revisores e de quem trata o relatório. BLOQUEIA só quando alguém precisa decidir; CRÍTICO e MAIOR o agente corrige; MENOR vira correção no escopo ou débito; NOTA é opcional. O veredito é calculado pela maior severidade.

## Onde cada coisa fica

A regra que guia este repositório está no [ADR 0001](docs/adr/0001-onde-cada-coisa-fica.md): o que precisa ser garantido vai para hook, o que é determinístico vai para script (os dois com teste), o que é fato de um projeto vai para o `CLAUDE.md` dele, o que é padrão vira skill, o que pede julgamento independente vira agente com ferramentas limitadas, e o porquê de cada regra vai para um ADR. Antes de mudar uma regra, leia o ADR dela em [`docs/adr/`](docs/adr/README.md).

## Instalar

**Nesta máquina** (onde o repositório é editado):

```bash
./install.sh
```

O script:
- Liga o `CLAUDE.md` global por symlink. Se já existir um arquivo de verdade no lugar, ele vai antes para `~/.claude/backup-claude-config-<data>/`.
- Remove os links do formato antigo, em que cada skill, cada agente e as regras do hookify tinham um link próprio em `~/.claude`.
- Registra o marketplace `skilldev` apontando para esta pasta e instala os plugins `base` e `nestjs` no usuário. O marketplace é lido direto da pasta, então editar aqui vale na próxima sessão, sem reinstalar.
- Instala os plugins de terceiros de `plugins.txt`: o `typescript-lsp`, com o qual o Claude vê os erros de tipo e navega pelo código TypeScript.
- Instala com yarn o `typescript-language-server`, que o `typescript-lsp` usa. A versão fica fixa em 5.3.0, porque a 6.x pede Node 22.22 ou mais novo.
- Pode rodar de novo sem problema.

**Em outra máquina, ou para outra pessoa**, sem clonar o repositório:

```bash
claude plugin marketplace add Ericles-Miller/SkillDev
```

```bash
claude plugin install base@skilldev
```

```bash
claude plugin install nestjs@skilldev
```

**Num projeto com telas:**

```bash
claude plugin install front@skilldev --scope project
```

O `--scope project` grava o plugin no `.claude/settings.json` do projeto (`enabledPlugins`), que vai para o git. Quem abrir o projeto vê que ele precisa do plugin `front`.

## Hooks

O plugin `base` traz três hooks, que valem em todo projeto onde ele está ligado. Quando um hook bloqueia, o Claude lê o motivo e se corrige sozinho.

| Hook | Evento | O que faz |
|---|---|---|
| `guarda_comandos.py` | Antes de cada comando no terminal | Barra `npm` como comando e diz o equivalente em yarn; deixa passar `npx`, `pnpm` e a palavra "npm" dentro de um texto. Barra push para `main` ou `develop` e push com `--force`; deixa passar o push da branch da task e o `--force-with-lease`. Barra `git commit`, `push` e `merge` nos projetos que pedem isso. Barra `git commit` sem a verificação completa verde ou com o código diferente do verificado. |
| `lint_edicao.py` | Depois de cada edição de arquivo | Roda o ESLint do projeto (ou o `dart analyze`) só no arquivo editado. Erro volta na hora para o Claude corrigir. Avisa, sem bloquear, de `jest.mock` num teste e de `console.log` no código da aplicação. |
| `portao_stop.py` | Quando o Claude vai encerrar | Roda o ESLint e os testes do Jest ligados aos arquivos que o Claude editou nesta sessão e que ainda não foram commitados (no Flutter, o `dart analyze`). Se algo falha, o Claude não encerra e recebe a saída. |

O portão do Stop foi pensado para não atrapalhar:
- Ele não confere o trabalho em andamento que você deixou no projeto, só o que o próprio Claude editou.
- Estado já aprovado não roda de novo.
- Se o Claude tentar encerrar duas vezes sem mudar nada, ele deixa encerrar e avisa você, em vez de prender o Claude num laço.

**Ajuste por projeto**, no `env` do `.claude/settings.json` do projeto:

| Variável | Efeito |
|---|---|
| `"SKILLDEV_SEM_COMMIT": "1"` | Barra `git commit`, `push` e `merge` (projetos em que a IA não commita). |
| `"SKILLDEV_LINT_EDICAO": "off"` | Desliga o lint a cada edição. |
| `"SKILLDEV_PORTAO": "off"` | Desliga o portão do Stop. |
| `"SKILLDEV_PORTAO_COMMIT": "off"` | Desliga o portão de commit. |

## Testar as mudanças

Mudou um template do Nest, um hook ou um manifesto? Rode o teste correspondente antes do commit:

```bash
./scripts/verify-templates.sh
```

```bash
python3 -I -B plugins/base/hooks/test_hooks.py
```

```bash
python3 -I -B plugins/base/scripts/test_scripts.py
```

```bash
python3 -I -B scripts/validar.py
```

```bash
claude plugin validate --strict . && for p in plugins/*; do claude plugin validate --strict "$p"; done
```

- O primeiro cria um projeto Nest descartável com os templates (base e opcionais) e roda prettier, ESLint, build, testes unitários e e2e.
- O segundo roda os três hooks contra um projeto falso, em que o ESLint e o Jest falham quando o arquivo tem uma marca. Toda regra nova precisa de casos no script.
- O terceiro testa o gerador da seção "Verificação" do `CLAUDE.md`.
- O quarto confere o marketplace, os plugins, as skills, os agentes (nenhum revisor com ferramenta de escrita, cada agente chamado existe), os hooks e as regras obrigatórias no texto das skills.
- O último valida o marketplace e os três plugins com o próprio Claude Code.

O workflow `CI` do GitHub roda o validador e os testes dos hooks e dos scripts em todo PR e em todo push na `main`. O workflow `Templates do Nest` roda o `verify-templates.sh` quando os templates mudam.

## Skills de terceiros

`test-driven-development`, `systematic-debugging` e `verification-before-completion` são cópias do [obra/superpowers](https://github.com/obra/superpowers) (commit `22f0b46`, licença MIT, que vai junto em cada pasta). O texto original foi mantido em inglês, para facilitar a comparação com versões novas. Os únicos ajustes:
- `npm` virou `yarn`.
- `*.test.ts` virou `*.spec.ts`.
- As referências `superpowers:<skill>` perderam o prefixo.

Para atualizar, compare com a versão nova do Superpowers e refaça esses três ajustes.

## Mudar uma regra

1. Edite aqui mesmo, no VS Code. Nesta máquina, a mudança vale na próxima sessão do Claude (ou depois de `/reload-plugins`).
2. Rode os testes da seção anterior que se aplicam.
3. Faça o commit: `git commit -am "docs: <o que mudou>"`.
4. Para as outras máquinas, suba a versão no `plugin.json` do plugin alterado. Quem usa o marketplace pelo GitHub atualiza com `claude plugin marketplace update skilldev` e `claude plugin update <plugin>@skilldev`.

Uma skill nova é uma pasta nova em `plugins/<plugin>/skills/` com um `SKILL.md`. Um agente novo é um arquivo em `plugins/<plugin>/agents/`. Um plugin novo é uma pasta em `plugins/` com o `.claude-plugin/plugin.json`, mais uma entrada no `.claude-plugin/marketplace.json`.

## Origem dos padrões

Os padrões foram extraídos de [Ericles-Miller/microsservice](https://github.com/Ericles-Miller/microsservice) (commit `888a298`), que segue o padrão do projeto calhas.
