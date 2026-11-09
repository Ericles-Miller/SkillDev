# Regras globais

Valem em todo projeto. Se o CLAUDE.md do projeto disser outra coisa, vale o do projeto.

## Conversa

- Fale comigo em português.

## Código

- Em NestJS ou backend TypeScript, siga a skill `nestjs-padrao`: projeto novo, módulo, entidade, DTO, service, controller, teste ou revisão.
- Código, nomes, logs, mensagens de erro e Swagger em inglês. Comentários e documentação em português.
- O comentário explica o porquê (decisão, risco, tarefa), nunca o quê.
- Só `yarn`, nunca `npm`.
- Dinheiro sempre em centavos inteiros (`amountCents`), nunca float.
- Se o projeto existente usa um padrão diferente, siga o do projeto e me avise da diferença, em vez de reescrever.
- Feature ou correção: o teste vem antes do código (skill `test-driven-development`).
- Bug, teste falhando ou comportamento estranho: ache a causa raiz antes de propor a correção (skill `systematic-debugging`).

## Antes de dizer que terminou

- Siga a skill `verification-before-completion`: rode o lint, o build e os testes do projeto e mostre o resultado.

## Jira

- Para abrir task, bug ou epic, siga a skill `jira-task`.
- Nenhuma task é aberta com decisão ou débito técnico em aberto: tudo é definido comigo antes de criar o card.

## Git

- Conventional Commits em inglês, com a tarefa no escopo quando houver: `feat(REC-48): ...`.
- Uma branch por tarefa. PR para `develop`, depois de `develop` para `main`.
