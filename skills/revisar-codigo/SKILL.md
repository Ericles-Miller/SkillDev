---
name: revisar-codigo
description: Revisa código com um revisor independente (o agente revisor-codigo). Ele procura critério da task sem código ou sem teste, quebra do padrão do projeto, bugs e furos de robustez, segurança, testes fracos e regra de negócio contradita. Use para revisar a branch de uma task, um PR, um módulo ou o repositório inteiro ("revisa meu código", "tem furo nessa branch?"). A skill executar-task já chama o revisor sozinha no fechamento da task.
---

# Revisar código

O revisor é o agente `revisor-codigo`. Ele roda com o contexto limpo, sem ver a conversa em que o código foi escrito, e só lê: arquivos, LSP e Jira. Ele não tem terminal, então esta skill monta a entrada (o diff vem do git aqui na sessão principal), chama o agente e apresenta o resultado.

## Passo a passo

1. **Defina o escopo:**
   - **Branch da task:** `git diff --stat develop...HEAD` e `git diff --name-only develop...HEAD`. A base é a do projeto, que por padrão é `develop`.
   - **PR:** faça `git fetch` e o diff da branch do PR contra a base dele.
   - **Módulo ou pasta:** a lista de arquivos da pasta.
   - **Repositório inteiro:** uma revisão por área (cada módulo do backend, o front, a infra).
2. **Ache a task.** A chave vem do nome da branch (`MS-61`) ou do pedido. Se não houver task, a revisão segue sem o bloco de critérios.
3. **Divida se for grande.** Diff com mais de ~40 arquivos ou ~2.000 linhas vira uma revisão por área: backend por módulo, front e testes. São até 4 agentes em paralelo, todos com a mesma task.
4. **Chame o agente** com `Agent`, `subagent_type: "revisor-codigo"`. O prompt leva:
   - a chave da task e o site do Jira, ou os critérios em texto;
   - o caminho do projeto e a branch base;
   - a lista de arquivos alterados e o `--stat`;
   - o diff completo, se tiver até ~1.500 linhas. Acima disso, vão só os arquivos, e o agente os lê inteiros.
5. **Mostre o relatório.** Com várias revisões, junte numa só: uma única tabela de critérios e os achados agrupados por severidade.
6. **Segurança:** se a mudança toca autenticação, permissões, pagamento, upload ou segredos, rode também a skill `security-review`.

## Correções

- **Revisão avulsa:** não altere o código sem o usuário pedir.
- **Dentro da `executar-task`:** siga o passo "Revisão de código" dela.
- **Em qualquer caso:**
  - toda correção de BLOQUEIA vem com um teste que falha antes e passa depois (skill `test-driven-development`);
  - o que estiver em "Fora do diff" vira débito pela skill `jira-task`.

## Se o agente não aparecer

Se `revisor-codigo` não estiver entre os tipos de agente, o `install.sh` do claude-config não rodou nesta máquina. Rode `~/Documents/GitHub/claude-config/install.sh` e abra uma sessão nova.
