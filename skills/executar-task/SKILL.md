---
name: executar-task
description: Roteiro para trabalhar uma task do Jira do começo ao fim. Confere a branch, lê a task e os docs, move para Em Andamento, implementa com teste antes, verifica, comenta no Jira, move para Testes e entrega a mensagem de commit. Use quando o usuário pedir para começar, pegar, implementar, continuar ou fechar uma task (ex.: "vamos fazer a MS-61").
---

# Executar uma task

A task já nasce com as decisões tomadas (skill `jira-task`). Aqui é seguir o roteiro e parar só quando aparecer algo que a task não cobre.

## Antes de começar

1. **Uma task por vez.** Se outra task está em andamento nesta sessão, feche ou devolva antes de pegar a nova.
2. **Leia as regras do projeto:** o `CLAUDE.md` do projeto e os docs que ele aponta. Elas valem mais que esta skill. Por exemplo, é o projeto que diz se você pode commitar.
3. **Leia a task inteira:** descrição, comentários, links e as tasks de que ela depende. Se uma dependência não terminou, avise antes de começar.
4. **Confira com os docs e o código.** Se a task contradiz um dos dois, pare e mostre a contradição. Os docs vencem a task.
5. **Se faltar uma decisão**, a task devia ter trazido. Pergunte com as opções e a sua recomendação, registre a resposta como comentário na task, com a data, e só então continue. Nunca decida sozinho.
6. **Confira a branch** com `git branch --show-current`. O nome segue o projeto; o padrão é a chave da task (`MS-61`). Se não for a branch da task:
   - Se o projeto deixa você mexer no git, crie a partir de `develop`: `git switch -c MS-61 develop`.
   - Senão, peça ao usuário para criar ou trocar.
7. **Mova a task para Em Andamento.** Ache a transição pelo nome com `getTransitionsForJiraIssue`.

## Durante

- Faça o que está no escopo e nos critérios de aceite: nem mais, nem menos.
- Achou algo fora do escopo (bug, débito, melhoria)? Anote para o fim; não resolva junto.
- Código no padrão (skill `nestjs-padrao` no backend), com o teste antes (skill `test-driven-development`). Bug no caminho: skill `systematic-debugging`.
- Atualize o que a mudança afeta: README, `.env.example`, docs de arquitetura, `docs/DECISOES.md`.

## Para fechar

1. **Verifique** (skill `verification-before-completion`): lint, build, testes e o que os critérios de aceite pedem (Swagger, migration com run/revert, validação ponta a ponta). Confira cada critério de aceite e guarde a prova.
2. **Comente na task** com `addCommentToJiraIssue`:
   ```markdown
   **O que mudou:** <arquivos e comportamento>
   **Decisões:** <as tomadas durante a task, com data, ou "nenhuma além das da abertura">
   **Como validei:** <comandos e resultado: N testes passando, lint e build ok...>
   **Limites:** <o que ficou de fora e a task criada para isso>
   ```
3. **Mova para Testes.** Quem move para Concluído é o usuário.
4. **O que você anotou fora do escopo** vira task com a skill `jira-task`, com as decisões perguntadas antes, como sempre. Se o projeto tem `docs/PENDENCIAS_TECNICAS.md`, registre lá também.
5. **Commit.** Mensagem em Conventional Commits, em inglês, com a task no escopo:
   ```
   feat(MS-61): add forgot-password and reset-password screens

   <o quê e por quê, em 1 a 3 linhas>
   Validated with: <comandos>
   ```
   Se o projeto deixa você commitar e o usuário pediu, faça o commit na branch da task e abra o PR para `develop`. Senão, entregue só a mensagem.

## Nunca

- Começar a implementar sem uma task.
- Mover a task para Concluído.
- Commitar, dar push ou merge sem o projeto permitir e o usuário pedir.
- Mostrar o valor de um segredo (`.env`) em resposta, comentário ou log.
