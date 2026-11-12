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
- Antes de mexer, diga como vai provar que terminou. Diga também as suposições que fizer no caminho.
- Apague só o código morto que a sua mudança criou. Código morto antigo vira débito, não limpeza de carona.
- Feature ou correção: o teste vem antes do código (skill `test-driven-development`).
- Bug, teste falhando ou comportamento estranho: ache a causa raiz antes de propor a correção (skill `systematic-debugging`).
- Tela de frontend: siga a skill `telas-figma`. A Ficha e o prompt do Figma vêm antes, e o desenho aprovado antes do código.
- Implementar a partir de um desenho do Figma, em web ou mobile: siga a skill `figma-para-codigo`.
- Revisar código (a branch de uma task, um PR, um módulo): siga a skill `revisar-codigo`. No fechamento de uma task, a revisão é obrigatória.

## Antes de dizer que terminou

- Siga a skill `verification-before-completion`: rode o lint, o build e os testes do projeto e mostre o resultado.

## Jira

- Para abrir task, bug ou epic, siga a skill `jira-task`.
- Nenhuma task é aberta com decisão ou débito técnico em aberto: tudo é definido comigo antes de criar o card.
- Para trabalhar numa task, do começo ao fim, siga a skill `executar-task`.

## Projeto

- Projeto novo, ou projeto sem `CLAUDE.md` próprio: proponha a skill `iniciar-projeto` antes de começar.

## Git

- Conventional Commits em inglês, com a tarefa no escopo quando houver: `feat(REC-48): ...`.
- Uma branch por tarefa. PR para `develop`, depois de `develop` para `main`.
- Commit só depois da verificação completa (`verificar.py`, da skill `executar-task`). Nos projetos com `package.json` ou `pubspec.yaml`, o hook barra o commit se o código mudou depois dela.
