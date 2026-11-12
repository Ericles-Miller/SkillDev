---
name: executar-task
description: Roteiro para trabalhar uma task do Jira do começo ao fim. Confere a branch, lê a task, os docs e o plano (ou gera um com a planejar-task), move para Em Andamento, implementa com teste antes, faz a prova por reversão, roda a verificação completa, passa pela revisão de código independente, comenta no Jira, move para Testes e faz ou entrega o commit. Use quando o usuário pedir para começar, pegar, implementar, continuar ou fechar uma task (ex.: "vamos fazer a MS-61").
---

# Executar uma task

A task já nasce com as decisões tomadas (skill `jira-task`). Aqui é seguir o roteiro e parar só quando aparecer algo que a task não cobre.

## Antes de começar

1. **Uma task por vez.** Se outra task está em andamento nesta sessão, feche ou devolva antes de pegar a nova.
2. **Leia as regras do projeto:** o `CLAUDE.md` do projeto e os docs que ele aponta. Elas valem mais que esta skill. Por exemplo, é o projeto que diz se você pode commitar.
3. **Leia a task inteira:** descrição, comentários, links e as tasks de que ela depende. Se uma dependência não terminou, avise antes de começar.
4. **Confira com os docs e o código.** Se a task contradiz um dos dois, pare e mostre a contradição. Os docs vencem a task.
5. **Se faltar uma decisão**, a task devia ter trazido. Pergunte com as opções e a sua recomendação, registre a resposta como comentário na task, com a data, e só então continue. Se a decisão for grande, ela também vira um ADR (skill `jira-task`). Nunca decida sozinho.
6. **Confira a branch** com `git branch --show-current`. O nome segue o projeto; o padrão é a chave da task (`MS-61`). Se não for a branch da task:
   - Se o projeto deixa você mexer no git, crie a partir de `develop`: `git switch -c MS-61 develop`.
   - Senão, peça ao usuário para criar ou trocar.
7. **Plano.** Procure nos comentários da task o mais recente que começa com `## Plano de implementação (plano-v1)`.
   - **Com plano:** siga-o. Comentário de pessoa mais novo que o plano pode mudar o escopo: leia antes.
   - **Sem plano:** rode a skill `planejar-task` antes de implementar. Só a task trivial (um arquivo, mudança mecânica) segue sem plano, e você diz isso ao usuário.
   - **Plano com perguntas em aberto** não está pronto: as perguntas vão para o usuário antes do código.
8. **Mova a task para Em Andamento.** Ache a transição pelo nome com `getTransitionsForJiraIssue`.

## Durante

- **Siga o plano.** Desviar dele é decisão: se o desvio muda o resultado, pergunte; se não muda, registre o motivo no comentário final.
- **Antes da primeira edição**, escreva como vai provar que terminou: os comandos e os testes que mostram cada critério funcionando. O plano de teste do plano é o ponto de partida.
- Faça o que está no escopo e nos critérios de aceite: nem mais, nem menos. Cada critério Dado / Quando / Então vira um teste, escrito antes do código.
- **Lista "a provar":** cada lógica fácil de errar (regex, parser, guard, condição, limite, conta com fronteira) entra numa lista, com o teste que a cobre. Ela é usada na prova por reversão, no fechamento.
- **Narre as suposições** que fizer no caminho; elas vão para o comentário final.
- **Apague só o código morto que a sua mudança criou.** Código morto antigo vira débito.
- Achou algo fora do escopo (bug, débito, melhoria)? Anote para o fim; não resolva junto.
- Código no padrão (skill `nestjs-padrao` no backend), com o teste antes (skill `test-driven-development`). Bug no caminho: skill `systematic-debugging`.
- Tela: só a partir do desenho aprovado, com o `node-id` registrado na task. Siga a skill `figma-para-codigo`.
- Atualize o que a mudança afeta: README, `.env.example`, docs de arquitetura, `docs/DECISOES.md`. Se mudou o `package.json`, o CI ou o Husky, gere de novo a seção "Verificação" do `CLAUDE.md` com o `scripts/detectar_projeto.py` do plugin `base`.

## Para fechar

1. **Prova por reversão.** Para cada item da lista "a provar":
   - desfaça só aquele trecho de produção (edite de volta, ou use `git stash push -p` para escolher o pedaço);
   - rode o teste que o cobre e confira que ele **falha pela asserção esperada** (falha por erro de setup ou por timeout não conta);
   - restaure o trecho e rode de novo, até ficar verde.

   O teste que continua verde com o trecho desfeito não prova nada: corrija o teste. O que não deu para provar vai para "Não verificado", com o motivo.
2. **Verifique** (skill `verification-before-completion`):
   - Rode a verificação completa com o `scripts/verificar.py` do plugin `base` (duas pastas acima desta skill). Ele roda o lint, o build e os testes do projeto e grava a impressão digital do código verificado; o hook só deixa commitar esse mesmo código.
   - Confira também o que os critérios de aceite pedem além disso (Swagger, migration com run/revert, validação ponta a ponta), e guarde a prova de cada critério.
   - Depois de qualquer edição, a verificação precisa rodar de novo.
3. **Revisão de código** (skill `revisar-codigo`), com a task e o diff da branch:
   - **BLOQUEIA:** é decisão do usuário. Leve a pergunta do revisor, aplique a resposta e peça nova revisão.
   - **CRÍTICO e MAIOR:** corrija com teste antes e peça nova revisão. São no máximo 2 rodadas; o que sobrar vai para o usuário decidir.
   - **MENOR:** corrija o que está no escopo. O resto vira débito (passo 6).
   - **NOTA:** registre no comentário, se valer.
   - **"Fora do diff":** vira débito (passo 6).
   - **Segurança:** mudança em autenticação, permissões, pagamento, upload ou segredos também passa pela skill `security-review`.
   - **Depois de qualquer correção**, verifique de novo (passo 2).
4. **Comente na task** com `addCommentToJiraIssue`:
   ```markdown
   **O que mudou:** <arquivos e comportamento>
   **Decisões:** <as tomadas durante a task, com data, ou "nenhuma além das da abertura">
   **Como validei:** <comandos e resultado: N testes passando, lint e build ok...>
   **Prova por reversão:** <cada trecho da lista "a provar" e o teste que falhou com ele desfeito>
   **Não verificado:** <arquivo:linha e o motivo, ou "tudo provado">
   **Suposições:** <as que você fez no caminho, ou "nenhuma">
   **Revisão de código:** <veredito do revisor e o que foi corrigido>
   **Limites:** <o que ficou de fora e a task criada para isso>
   ```
5. **Mova para Testes.** Quem move para Concluído é o usuário.
6. **O que você anotou fora do escopo** vira task com a skill `jira-task`, com as decisões perguntadas antes, como sempre. Isso inclui os débitos da revisão de código. Se o projeto tem `docs/PENDENCIAS_TECNICAS.md`, registre lá também.
7. **Commit.** Mensagem em Conventional Commits, em inglês, com a task no escopo:
   ```
   feat(MS-61): add forgot-password and reset-password screens

   <o quê e por quê, em 1 a 3 linhas>
   Validated with: <comandos>
   ```
   Se o projeto deixa você commitar e o usuário pediu, faça o commit na branch da task e abra o PR para `develop`. O hook barra o commit se a última verificação falhou ou se o código mudou depois dela: nesse caso, rode o `verificar.py` de novo. Senão, entregue só a mensagem.

## Nunca

- Começar a implementar sem uma task.
- Mover a task para Concluído.
- Commitar, dar push ou merge sem o projeto permitir e o usuário pedir.
- Mostrar o valor de um segredo (`.env`) em resposta, comentário ou log.
