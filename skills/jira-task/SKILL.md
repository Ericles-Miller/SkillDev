---
name: jira-task
description: Abre tasks, bugs e epics no Jira no meu padrão (o mesmo dos projetos MS e PC). O card sai com título "<Área>: <o quê>", prioridade com motivo, labels, Epic pai e uma descrição com contexto, escopo, decisões tomadas, débitos técnicos, critérios de aceite e dependências. Use para criar, escrever ou quebrar uma task, bug ou epic no Jira, ou para transformar um pedido, achado ou débito técnico em card. A task só é aberta depois de todas as decisões e débitos técnicos estarem definidos.
---

# Task no Jira

**Regra principal:** nenhuma task é aberta com decisão em aberto. Toda decisão e todo débito técnico são resolvidos com o usuário antes de o card ser criado, e ficam escritos nele. Assim, quem implementa não precisa voltar para perguntar definição.

Os modelos de descrição, com exemplos, estão em [references/modelos.md](references/modelos.md).

## Passo a passo

1. **Descubra o projeto.** O site, a chave (`MS`, `PC`...) e as Epics vêm do CLAUDE.md ou dos docs do projeto. Se não estiverem lá, rode `getAccessibleAtlassianResources` e pergunte a chave.
2. **Leia antes de escrever.** Busque no Jira (JQL) tasks parecidas, para não duplicar, e também a Epic certa e as dependências. Leia os docs e o código que a task vai tocar. Resultado grande de busca vai para arquivo: extraia com `jq`.
3. **Levante as decisões.** Liste tudo o que quem for implementar teria que decidir (veja "O que conta como decisão"). Para cada uma, traga de 2 a 3 opções e a sua recomendação.
4. **Levante os débitos técnicos.** Liste o que a task encontra, cria ou deixa para depois (veja "Débito técnico").
5. **Pergunte tudo** com `AskUserQuestion`. Cabem até 4 perguntas por chamada, então repita até acabar. Não crie nada enquanto houver pergunta sem resposta.
6. **Mostre o rascunho** (título, tipo, Epic, prioridade, labels e descrição) e espere o ok. Criar um card publica no Jira.
7. **Crie** com `createJiraIssue`:
   - `contentFormat: "markdown"`.
   - `parent` = a Epic.
   - `priority` e `labels` em `additional_fields`.

   Depois, ligue as dependências com `createIssueLink`, tipo `Blocks` (`inwardIssue` = quem bloqueia).
8. **Registre.** Se o projeto tem um log de decisões ou um doc de pendências técnicas, atualize com a data e a chave da task. Devolva o link do card.

### Se uma decisão não pode ser tomada agora

Se ela depende de terceiro (cliente, credencial, fornecedor), a task não é aberta. Abra antes uma task `Decisão: <tema>` (como a MS-32) ou uma de investigação (como a MS-73). A task principal só nasce depois da resposta.

## O que conta como decisão

- **Regra de negócio e números:** limites, validades, prazos, quantidades, arredondamento, fuso.
- **Erro:** status HTTP, mensagem, o que acontece quando um serviço de fora falha.
- **Contrato:** rotas, campos, nomes, formato da resposta, paginação, filtros.
- **Escolha técnica:** biblioteca, provedor, onde guardar, síncrono ou fila, migration.
- **Permissão:** quem pode fazer e o que cada um enxerga.
- **Escopo:** o que fica fora e para onde vai.
- **Tela:** textos, estados de vazio, erro e carregamento, de onde vem e para onde vai.

Se algo já está decidido nos docs do projeto, cite o doc em vez de perguntar de novo.

## Débito técnico

Procure nestes lugares:
- TODO e FIXME no código que a task toca.
- Testes que faltam.
- O doc de pendências técnicas do projeto.
- Atalhos que a própria task vai criar, como uma decisão provisória.

Todo débito encontrado sai com um destino:
- **Resolvido aqui:** entra no escopo e nos critérios de aceite.
- **Vira outra task:** é criada junto e ligada por link (a MS-86 saiu da MS-66).
- **Aceito:** o card registra o motivo e a data ("Sem testes automatizados no front: dívida P10, aceita em 23/09/2026").

## Prioridade

Toda task sai com o campo de prioridade preenchido e com a linha `**Prioridade:** <nível>. <motivo>` na descrição.

| Prioridade | Quando | Exemplos |
|---|---|---|
| Highest | Bloqueia outras tasks ou a entrega. Falha de segurança crítica. | MS-8 credenciais da API, MS-13 modelagem do banco, PC-70 escalonamento de privilégio |
| High | Entrega principal da fase, que o cliente vê. Bug sério que não bloqueia. | MS-17 leitura atual do inversor, MS-61 esqueci a senha, PC-85 máquina de estados da OS |
| Medium | Trabalho normal da fase. É o padrão. | MS-65 alarmes, MS-98 log de requisições |
| Low | Pode ficar para o fim da fase ou depois. Testes extras. Backlog adiado. | MS-74 pontos extras do inversor, PC-81 documentação da empresa, PC-96 testes de integração |
| Lowest | Fase futura, opcional ou exploratório. | MS-80 Live Data via MQTT |

A Epic também recebe prioridade, pela importância do bloco inteiro.

## Formato do card

- **Título** em português: `<Área>: <o que entrega>`.
  - A área é `Backend`, `Frontend`, `Infra (Terraform)`, `Frontend (Figma)` ou `Backend + Frontend`.
  - Bug: `<Área>: fix — <o que estava errado>`.
  - Decisão: `Decisão: <tema>`.
- **Tipo:** `Tarefa`, `Bug`, `Epic` ou `Subtarefa` (os nomes do Jira em português).
- **Labels** em minúsculas, com hífen: a área (`backend`, `frontend`, `infra`), o domínio (`auth`, `payments`) e a fase (`fase1`), quando houver. Use `blocked` se a task depende de terceiro.
- **Epic:** toda task tem pai. Uma task de mais de ~3 dias vira várias tasks na mesma Epic (a MS-32 virou as MS-36 a MS-40).
- **Descrição:** as seções vêm na ordem do modelo. Não existe seção "Decisões em aberto".

## Checklist antes de criar

- [ ] Nenhuma decisão em aberto, e cada uma está com data.
- [ ] Todo débito tem destino: resolvido aqui, outra task ou aceito com motivo.
- [ ] A prioridade está no campo e na descrição, com o motivo.
- [ ] Epic, labels e dependências (Depende de / Bloqueia) preenchidos.
- [ ] O que fica fora do escopo está escrito.
- [ ] Os critérios de aceite são verificáveis e incluem testes (no backend, mínimo de 70% por método), lint e build.
- [ ] O usuário aprovou o rascunho.
