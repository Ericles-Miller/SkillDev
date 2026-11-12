---
name: iniciar-projeto
description: Prepara um projeto para trabalhar no meu padrão com o Claude. Cria o CLAUDE.md do projeto (Jira, git, fonte de verdade, testes, cuidados), o log de decisões, o doc de pendências técnicas e a pasta .claude/ (permissões, plugins e o ajuste dos hooks). Use ao criar um projeto novo, ao adotar o padrão num projeto que já existe, ou quando o projeto não tem CLAUDE.md.
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
   - **Telas:** o projeto tem frontend ou app? Se tiver, o plugin `front` é ligado no projeto (passo 4).
3. **Copie os modelos** de [templates/](templates/) e preencha. Eles têm outro nome no template para o Claude não carregá-los como configuração de verdade:
   - `CLAUDE.template.md` → `CLAUDE.md` na raiz do projeto. Apague as linhas que não valem, como a opção de git que não foi escolhida.
   - A seção "Verificação" do `CLAUDE.md` não se escreve à mão: rode o `scripts/detectar_projeto.py` do plugin `base` (duas pastas acima desta skill) com `--gravar CLAUDE.md`. Ele lê o `package.json`, o CI e o Husky, e nenhum comando entra sem estar declarado neles.
   - `docs/DECISOES.md` e `docs/PENDENCIAS_TECNICAS.md`. Registre as respostas do passo 2 como as primeiras decisões.
   - `docs/decisoes/`: a pasta dos ADRs. Ponha nela um `0000-modelo.md` com o modelo de ADR da skill `base:jira-task` (seção "ADR" do `references/modelos.md` dela).
   - `settings.json` → `.claude/settings.json`: libera sem perguntar `yarn lint`, `yarn build`, `yarn test` e os comandos de git que só leem.
4. **Plugins do SkillDev.** Os plugins `base` e `nestjs` valem em todo projeto, instalados no usuário. O que depende do projeto é ligado só nele, e fica registrado no `.claude/settings.json` (`enabledPlugins`):
   - Projeto com telas: `claude plugin install front@skilldev --scope project`.
   - Confira com `claude plugin list` e mostre ao usuário o que ficou ligado.
5. **Hooks.** Os hooks do plugin `base` já valem em todo projeto: barram npm e push protegido, rodam o lint a cada edição, não deixam encerrar com lint ou teste quebrado e só deixam commitar depois da verificação completa (`scripts/verificar.py`, com o código igual ao verificado). O projeto só ajusta, no `env` do `.claude/settings.json`:
   - Se você não pode commitar: `"SKILLDEV_SEM_COMMIT": "1"` (barra `git commit`, `push` e `merge`).
   - Se o lint ou os testes do projeto forem lentos demais para rodar a cada edição ou a cada encerramento, decida com o usuário: `"SKILLDEV_LINT_EDICAO": "off"` ou `"SKILLDEV_PORTAO": "off"`, e registre a decisão em `docs/DECISOES.md`.
6. **Mostre ao usuário** o que foi criado e o que ainda falta preencher.

## Regras

- O `CLAUDE.md` do projeto é curto: as regras e onde está cada coisa. O detalhe fica nos docs.
- Nada de segredo no `CLAUDE.md` nem nos docs: só o nome das variáveis.
- Toda decisão nova do projeto entra em `docs/DECISOES.md`, com a data e onde foi tomada.
