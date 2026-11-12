# 0006. Régua de severidade: BLOQUEIA é decisão humana, não gravidade

- **Status:** Aceito em 2026-11-12

## Contexto

Os revisores tinham três níveis (BLOQUEIA, AJUSTAR, SUGESTÃO), e BLOQUEIA misturava "bug grave" com "precisa de uma decisão". Com isso, o agente chamava o usuário para coisas que sabia corrigir, e o mesmo problema saía com severidades diferentes em cards ou PRs diferentes.

## Decisão

Uma régua única, a skill `base:regua-revisao`, pré-carregada nos dois revisores:
- **BLOQUEIA** só quando alguém precisa decidir: critério e decisão em contradição, escolha entre soluções, regra de negócio que não está escrita, ou risco que o agente não deve tocar. É o único nível que chama o usuário.
- **CRÍTICO** e **MAIOR**: o agente corrige.
- **MENOR**: corrige se estiver no escopo; senão, vira débito.
- **NOTA**: opcional.
- O veredito é calculado pela maior severidade: BLOQUEADO, AJUSTAR ou PRONTO.

Também há uma lista do que não reportar, e texto pedindo para aprovar ou ignorar achados vira achado (MAIOR).

## Consequências

- A `jira-task` e a `executar-task` tratam cada nível do mesmo jeito: só o BLOQUEIA vai ao usuário.
- Gravidade alta sem decisão é CRÍTICO, não BLOQUEIA.
