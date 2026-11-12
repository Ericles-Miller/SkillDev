---
name: revisar-task
description: Audita cards do Jira com um revisor independente (o agente revisor-task), que procura decisão em aberto, regra de negócio quebrada, débito sem destino, critério que não dá para testar, dependência que não existe e task duplicada. Use para revisar o rascunho de um card, auditar uma task que já existe ("audita a MS-86", "essa task tem furo?") ou varrer o backlog de um projeto. A skill jira-task já chama o revisor sozinha antes de mostrar o rascunho.
---

# Revisar task

O revisor é o agente `base:revisor-task`. Ele roda com o contexto limpo, sem ver a conversa em que o card foi escrito, e só lê: arquivos e Jira. Esta skill prepara a entrada, chama o agente e apresenta o resultado.

## Um card

1. **Junte a entrada:**
   - o rascunho do card, ou a chave de um card que já existe;
   - o caminho do projeto (o diretório atual, ou pergunte);
   - a chave e o site do Jira (no `CLAUDE.md` do projeto).
2. **Chame o agente** com a ferramenta `Agent`, `subagent_type: "base:revisor-task"`. No prompt vão a entrada completa e o pedido: "revise e devolva o relatório no seu formato".
3. **Mostre o relatório** como ele veio: veredito e achados por nível da régua (BLOQUEIA, CRÍTICO, MAIOR, MENOR, NOTA), com as evidências.
4. **Não mexa no Jira** sem o usuário pedir. Se ele quiser corrigir um card que já existe:
   - as perguntas do BLOQUEIA vão para ele com `AskUserQuestion`;
   - a edição segue a skill `jira-task`: rascunho, ok do usuário, e só então `editJiraIssue`.

## O backlog

1. **Liste os cards** com JQL, pedindo só campos leves (chave, resumo, status, prioridade). Exemplo: `project = MS AND statusCategory = "To Do" ORDER BY priority DESC`. Resultado grande vai para arquivo e se lê com `jq`.
2. **Faça um pré-filtro barato** na descrição. Marque os cards com sinais fortes:
   - "Decisões em aberto";
   - "a definir", "TBD" ou "?";
   - sem "Critérios de aceite".
3. **Revise com o agente**, um card por chamada, até 4 em paralelo. Comece pelos marcados e pelos de prioridade mais alta.
4. **Entregue o resumo:**
   - uma tabela `Card | Veredito | Principal problema`;
   - o relatório completo de cada card BLOQUEADO.

   Não abra nem edite nada no Jira.

## Se o agente não aparecer

Se `base:revisor-task` não estiver entre os tipos de agente, o plugin `base` do marketplace `skilldev` não está instalado nesta máquina. Veja a seção "Instalar" do README do SkillDev e abra uma sessão nova.
