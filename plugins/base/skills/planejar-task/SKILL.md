---
name: planejar-task
description: Gera o plano de implementação de uma task do Jira com o agente planejador (só leitura) e, com o ok do usuário, publica no Jira como comentário marcado "## Plano de implementação (plano-v1)". O plano liga cada critério a arquivos reais, diz o arquivo a espelhar e o teste que prova cada critério. Use antes de implementar uma task ("planeja a MS-61"); a skill executar-task chama esta skill quando a task não tem plano.
---

# Planejar task

O plano separa o "como" do "fazer". Você revisa o plano, que é barato, antes do código, que é caro. Quem implementa segue o plano em vez de replanejar em silêncio.

## Passo a passo

1. **Junte a entrada:** a chave da task, o caminho do projeto e o site do Jira (no `CLAUDE.md` do projeto).
2. **Veja se já existe plano:** procure nos comentários da task um que comece com `## Plano de implementação (plano-v1)`. Se existir e nada mudou na task depois dele, mostre esse plano em vez de gerar outro.
3. **Chame o agente** com `Agent`, `subagent_type: "base:planejador"`, passando a chave, o caminho do projeto e o pedido: "escreva o plano no seu formato".
4. **Perguntas em aberto:** se o plano voltar com "Pronto para implementar: não", leve as perguntas ao usuário com `AskUserQuestion` e chame o agente de novo com as respostas. São no máximo 2 rodadas; o que sobrar é decisão do usuário sobre o escopo, e a task volta para a skill `jira-task`.
5. **Mostre o plano** ao usuário e espere o ok. Comentar no Jira publica para quem acompanha a task.
6. **Publique** com `addCommentToJiraIssue`, com o plano inteiro, começando pelo marcador `## Plano de implementação (plano-v1)`, que é o que a `executar-task` procura.

## Regras

- Um plano por task. Plano novo substitui o antigo: o comentário mais recente com o marcador é o que vale.
- Se o usuário pedir mudança no plano, chame o agente de novo com o pedido; não edite o plano à mão para não perder a ancoragem no código.
