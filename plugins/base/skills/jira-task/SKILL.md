---
name: jira-task
description: Abre tasks, bugs e epics no Jira no meu padrão (o mesmo dos projetos MS e PC). O card sai com título "<Área>: <o quê>", prioridade com motivo, labels, Epic pai e uma descrição com contexto, escopo, decisões tomadas (as grandes em ADR), débitos técnicos, riscos do pré-mortem, critérios de aceite em Dado/Quando/Então e dependências. A task só é criada quando passa na Definition of Ready. Use para criar, escrever ou quebrar uma task, bug ou epic no Jira, ou para transformar um pedido, achado ou débito técnico em card.
---

# Task no Jira

**Regra principal:** nenhuma task é aberta com decisão em aberto. Toda decisão e todo débito técnico são resolvidos com o usuário antes de o card ser criado, e ficam escritos nele. Assim, quem implementa não precisa voltar para perguntar definição.

Os modelos de descrição, com exemplos, estão em [references/modelos.md](references/modelos.md).

## Passo a passo

1. **Descubra o projeto.** O site, a chave (`MS`, `PC`...) e as Epics vêm do CLAUDE.md ou dos docs do projeto. Se não estiverem lá, rode `getAccessibleAtlassianResources` e pergunte a chave.
2. **Leia antes de escrever.** Busque no Jira (JQL) tasks parecidas, para não duplicar, e também a Epic certa e as dependências. Leia os docs e o código que a task vai tocar. Resultado grande de busca vai para arquivo: extraia com `jq`.
3. **Levante o que está em aberto**, de três jeitos:
   - **Decisões:** tudo o que quem for implementar teria que decidir (veja "O que conta como decisão"). Para cada uma, traga de 2 a 3 opções e a sua recomendação.
   - **Débitos técnicos:** o que a task encontra, cria ou deixa para depois (veja "Débito técnico").
   - **Pré-mortem:** os motivos pelos quais a task daria errado (veja "Pré-mortem").
4. **Pergunte tudo** com `AskUserQuestion`. Cabem até 4 perguntas por chamada, então repita até acabar. Não crie nada enquanto houver pergunta sem resposta.
5. **Decisão grande vira ADR** (veja "Decisão grande: ADR"). As pequenas ficam só no card.
6. **Monte o rascunho** no modelo, com os critérios de aceite em Dado / Quando / Então (veja "Critérios de aceite").
7. **Peça a revisão independente** ao agente `base:revisor-task`, como descrito na skill `revisar-task`. Passe o rascunho, o caminho do projeto e a chave do projeto no Jira.
   - **BLOQUEIA:** vira pergunta ao usuário. Corrija o rascunho com a resposta e peça nova revisão. São no máximo 2 rodadas; o que sobrar vai para o usuário decidir.
   - **CRÍTICO e MAIOR:** corrija no rascunho, sem perguntar.
   - **MENOR:** corrija se for barato; senão, mostre junto com o rascunho.
   - **NOTA:** mostre junto com o rascunho, e o usuário decide.
8. **Confira a Definition of Ready.** Se um item não passa, resolva antes ou não abra a task.
9. **Mostre o rascunho** (título, tipo, Epic, prioridade, labels, descrição, o ADR, se houver, e o veredito do revisor) e espere o ok. Criar um card publica no Jira.
10. **Crie** com `createJiraIssue`:
   - `contentFormat: "markdown"`.
   - `parent` = a Epic.
   - `priority` e `labels` em `additional_fields`.

   Depois, ligue as dependências com `createIssueLink`, tipo `Blocks` (`inwardIssue` = quem bloqueia). Se houver ADR, grave o arquivo com status "Aceito" e a chave do card.
11. **Registre.** Se o projeto tem um log de decisões ou um doc de pendências técnicas, atualize com a data e a chave da task. Devolva o link do card.

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

### Triagem antes de perguntar

Vira pergunta só o que passa nos três testes:
1. A resposta muda o que o cliente ou a operação veem.
2. Nada nos docs, no código ou nas tasks indica a resposta.
3. Duas respostas razoáveis levam a resultados diferentes.

Fora disso, assuma a opção segura e reversível e escreva em **"Premissas assumidas"** ("Assumimos X porque Y"). O usuário vê e aprova as premissas junto com o rascunho, então nada fica decidido em segredo.

Dúvida de **fato** (um número de produção, o comportamento de um serviço de fora) não é decisão: vai para **"A conferir"**, com quem confere. Se a resposta mudaria a implementação, ela não pode ficar em "A conferir": vira dependência ou task de investigação.

### Como perguntar

- Uma decisão por pergunta, começando pela situação em linguagem comum.
- Exemplo concreto quando a pergunta for abstrata.
- De 2 a 4 opções, cada uma descrevendo o resultado (não a técnica).
- A recomendada vem primeiro, com o porquê.

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

## Pré-mortem

Antes de escrever o card, imagine que a task foi entregue e deu errado, ou travou no meio. Liste os motivos prováveis. Estas perguntas ajudam:
- **Dado e acesso:** que dado, conta de teste, credencial ou ambiente pode não existir na hora? Que limite de API pode estourar?
- **Borda:** que caso quebra a regra? Vazio, duplicado, dois pedidos ao mesmo tempo, fuso, arredondamento, volume grande.
- **Serviço de fora:** o que acontece se ele falhar, demorar ou responder diferente do documentado? Na PC-75, uma falha ao publicar no SQS deixava a OS órfã no banco.
- **Permissão:** quem não pode ver ou fazer isso, e como isso é garantido?
- **Quem já usa:** o que quebra no contrato, nos dados existentes (migration) ou no front?

Cada motivo sai do pré-mortem com um destino:
- **Decisão:** pergunte ao usuário, junto com as outras.
- **Risco com mitigação:** vai para a seção "Riscos" do card. A mitigação também vira critério de aceite.
- **Fora do escopo:** escrito no card, com a task para onde foi.
- **Débito:** segue a seção "Débito técnico".

## Decisão grande: ADR

Uma decisão vale além desta task quando trata de:
- arquitetura;
- provedor ou biblioteca;
- modelo de dados;
- um padrão que outras tasks vão seguir;
- qualquer coisa cara de desfazer.

Essa decisão vira um ADR (Architecture Decision Record):
- **Arquivo:** `docs/decisoes/NNNN-<titulo-em-kebab>.md`, com numeração sequencial, no modelo do `references/modelos.md`.
- **Status:** "Proposto" no rascunho, "Aceito" quando o usuário aprova.
- **Mudança de ideia:** o ADR aceito não se edita. Um ADR novo o substitui ("Substitui o 0003"), e o antigo passa a "Substituído pelo 0007".
- **Onde aparece:** o card cita o ADR na seção "Decisões", e o `docs/DECISOES.md` do projeto ganha uma linha apontando para ele.
- **Git:** o arquivo entra no repositório pela regra de commit do projeto.

A decisão que só vale para esta task fica só no card. Um caso que teria virado ADR: a MS-32, autenticação própria com JWT em vez de Supabase ou Firebase.

## Critérios de aceite

Cada comportamento vira um critério no formato Dado / Quando / Então, com valores concretos:

```markdown
- [ ] **Dado** um usuário dono de uma usina, **quando** chama `DELETE /power-plants/:id` com o id da usina de outra pessoa, **então** recebe 404 e nada muda no banco.
```

- Um critério para o caminho feliz, um para cada erro e um para cada regra de permissão.
- Valores concretos: status, mensagem, número, prazo. Nunca "funciona corretamente".
- Cada critério vira um teste (skill `test-driven-development`): unitário, de integração ou e2e.
- Os itens técnicos continuam como itens simples no fim da lista: testes com 70% por método, lint, build, Swagger e migration com run/revert.

## Definition of Ready

A task só é criada, e só entra em *A fazer*, quando passa em todos os itens:

- [ ] **Contexto:** dá para entender por que a task existe sem perguntar a ninguém.
- [ ] **Decisões:** nenhuma em aberto. Cada uma tem data, e as grandes têm ADR.
- [ ] **Débitos e riscos:** todo débito tem destino, e todo motivo do pré-mortem virou decisão, risco com mitigação, fora do escopo ou débito.
- [ ] **Arquivos:** cada arquivo em "Modificar" existe, cada um em "Criar" ainda não existe, e cada arquivo novo cita o arquivo real que espelha.
- [ ] **Efeitos fora do código** (cliente afetado, dado a corrigir, dinheiro, outro time) têm dono ou task, e recurso compartilhado lista os outros usuários dele.
- [ ] **Premissas e fatos:** as premissas assumidas estão escritas, e nada em "A conferir" muda a implementação.
- [ ] **Critérios de aceite** em Dado / Quando / Então, com valores concretos, mais os itens de teste, lint e build.
- [ ] **Dependências** entregues, ou ligadas por `Blocks` e planejadas para antes desta.
- [ ] **Acessos e dados de teste** existem (credencial, conta de teste, ambiente). O que falta vira dependência.
- [ ] **Tamanho:** cabe em até ~3 dias. Se passar, quebre em tasks na mesma Epic.
- [ ] **Card completo:** prioridade no campo e na descrição, com o motivo; Epic, labels e fora do escopo preenchidos.
- [ ] **Revisão:** o `base:revisor-task` não deixou nenhum BLOQUEIA sem resposta.
- [ ] **Aprovação:** o usuário aprovou o rascunho.

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
  - Tela: `Tela: <Nome> — Mobile + Web`, com a Ficha de Tela da skill `telas-figma`.
- **Tipo:** `Tarefa`, `Bug`, `Epic` ou `Subtarefa` (os nomes do Jira em português).
- **Labels** em minúsculas, com hífen: a área (`backend`, `frontend`, `infra`), o domínio (`auth`, `payments`) e a fase (`fase1`), quando houver. Use `blocked` se a task depende de terceiro.
- **Epic:** toda task tem pai. Uma task de mais de ~3 dias vira várias tasks na mesma Epic (a MS-32 virou as MS-36 a MS-40).
- **Descrição:** as seções vêm na ordem do modelo. Não existe seção "Decisões em aberto".
