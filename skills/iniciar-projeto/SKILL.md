---
name: iniciar-projeto
description: Prepara um projeto para trabalhar no meu padrão com o Claude. Cria o CLAUDE.md do projeto (Jira, git, fonte de verdade, testes, cuidados), o log de decisões, o doc de pendências técnicas e a pasta .claude/ (regras do hookify e permissões). Use ao criar um projeto novo, ao adotar o padrão num projeto que já existe, ou quando o projeto não tem CLAUDE.md.
---

# Iniciar um projeto

Cada projeto tem as suas regras: quem pode commitar, qual o board do Jira, onde ficam os docs. Elas são decididas aqui, uma vez, e ficam escritas no `CLAUDE.md` do projeto. As skills `jira-task` e `executar-task` leem esse arquivo.

## Passo a passo

1. **Olhe o que já existe:** `CLAUDE.md`, `docs/`, `.claude/`, README. Num projeto que já existe, não sobrescreva nada.
   - Se já há um log de decisões ou um doc de pendências com outro nome (ex.: `DIRETRIZES_DE_TRABALHO.md`), aponte para ele no `CLAUDE.md` em vez de criar outro.
   - Se já existe um `CLAUDE.md`, mostre o que falta nele e acrescente só isso.
2. **Pergunte as regras do projeto** com `AskUserQuestion`, trazendo a sua recomendação:
   - **Jira:** site, chave do projeto e Epics. Pode não ter Jira.
   - **Git:** você pode commitar? As opções são "nunca: só entrega a mensagem" ou "na branch da task, quando eu pedir". Push e PR seguem a mesma resposta.
   - **Branches:** a base (padrão `develop`) e o nome (padrão a chave da task, `MS-61`).
   - **Fonte de verdade:** quais docs mandam no escopo (padrão `docs/`).
   - **Testes:** a cobertura mínima (padrão 70% por método nos services, controllers, DTOs e validators).
   - **Cuidados:** dado real de cliente, contas que não podem ser apagadas, APIs com limite de chamada, segredos.
3. **Copie os modelos** de [templates/](templates/) e preencha. Eles têm outro nome no template para o Claude não carregá-los como configuração de verdade:
   - `CLAUDE.template.md` → `CLAUDE.md` na raiz do projeto. Apague as linhas que não valem, como a opção de git que não foi escolhida.
   - `docs/DECISOES.md` e `docs/PENDENCIAS_TECNICAS.md`. Registre as respostas do passo 2 como as primeiras decisões.
   - `settings.json` → `.claude/settings.json`: libera sem perguntar `yarn lint`, `yarn build`, `yarn test` e os comandos de git que só leem.
4. **Regras do hookify:** `mkdir -p .claude && cp ~/.claude/hookify/*.local.md .claude/`.
   - Se você não pode commitar, mude `enabled: false` para `enabled: true` em `.claude/hookify.block-git-commit.local.md`.
5. **Mostre ao usuário** o que foi criado e o que ainda falta preencher.

## Regras

- O `CLAUDE.md` do projeto é curto: as regras e onde está cada coisa. O detalhe fica nos docs.
- Nada de segredo no `CLAUDE.md` nem nos docs: só o nome das variáveis.
- Toda decisão nova do projeto entra em `docs/DECISOES.md`, com a data e onde foi tomada.
