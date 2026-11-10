# <Projeto>

<O que é o projeto, para quem e em que fase está, em 2 linhas.>

## Jira

- Site `<site>.atlassian.net`, projeto **<CHAVE>**.
- Epics: <CHAVE-1 Nome>, <CHAVE-2 Nome>.
- Para abrir task, siga a skill `jira-task`. Para trabalhar numa task, siga a skill `executar-task`.
- Uma task por vez. Quem move para Concluído sou eu.

## Fonte de verdade

- Os docs em `docs/` vencem a descrição da task e a memória de quem pediu. Se discordarem, pare e me avise.
- Decisões: `docs/DECISOES.md`. Débitos e pendências: `docs/PENDENCIAS_TECNICAS.md`.
- Decisão que não está nos docs: pare e pergunte, dizendo que está fora do que foi documentado.

## Git

- Uma branch por task, com a chave da task no nome (`<CHAVE>-12`), saindo de `develop`. PR para `develop`; `main` só recebe PR de `develop`.
- <Opção A> Não faça commit, push nem merge, em nenhuma branch: no fim da task, entregue a mensagem de commit sugerida.
- <Opção B> Pode commitar na branch da task quando eu pedir. Push e PR também só quando eu pedir. Nunca em `main` ou `develop`.

## Testes

- Mínimo de 70% de cobertura por método nos services, controllers, DTOs e validators. Entidade sem lógica fica de fora.

## Cuidados

- <Dado real de cliente, conta que não pode ser apagada, API com limite de chamada.>
- Nunca mostre valores do `.env`: só os nomes.

## Como rodar

- `docker compose up -d db`, `yarn start:dev` e `curl localhost:<porta>/health`.
