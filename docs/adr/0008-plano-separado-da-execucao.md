# 0008. Plano separado da execução, publicado na task

- **Status:** Aceito em 2026-11-12

## Contexto

A `executar-task` planejava e implementava na mesma sessão. O usuário só via o resultado no código, que é a parte cara de revisar, e o plano mudava em silêncio no meio do caminho.

## Decisão

- O agente `planejador` (só leitura, Opus) escreve o plano no formato fixo `## Plano de implementação (plano-v1)`: cada critério ligado a uma mudança com caminho, passos com arquivos reais, o arquivo a espelhar para cada arquivo novo, o teste que prova cada critério, a lista "A provar" e as perguntas em aberto.
- A skill `planejar-task` chama o agente, leva as perguntas ao usuário, mostra o plano e, com o ok, publica como comentário na task.
- A `executar-task` procura o comentário mais recente com o marcador e segue o plano. Sem plano, roda a `planejar-task` antes, exceto em mudança trivial. Desviar do plano é decisão: pergunta ou fica registrado com o motivo.

## Consequências

- O usuário aprova em três pontos baratos: o card, o plano e o PR.
- Plano com pergunta em aberto não está pronto: a pergunta vai ao usuário antes do código.
- O agente não escreve no Jira; quem publica é a skill, depois do ok.
