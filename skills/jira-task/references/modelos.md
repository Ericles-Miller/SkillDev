# Modelos de descrição

Os modelos foram tirados dos projetos MS (monitoramento de usina) e PC (calhas). Todos estão em markdown, porque o `createJiraIssue` recebe `contentFormat: "markdown"`.

O que mudou em relação a esses projetos: lá, algumas tasks nasciam com "Decisões em aberto" (MS-65, MS-86). Agora essa seção não existe. A decisão é tomada antes de abrir a task e entra em "Decisões", com a data.

## Tarefa

```markdown
**Contexto:** <por que a task existe: pedido do cliente, achado de auditoria, task de origem. De 2 a 4 linhas.>

**Prioridade:** <nível>. <motivo>

**Escopo**

* <o que entra, citando arquivos, endpoints e entidades>
* <...>

**Fora do escopo**

* <o que não entra> → <MS-XX, ou "decidido não fazer em DD/MM/AAAA">

**Decisões** (tomadas em DD/MM/AAAA)

1. **<tema>:** <o que foi decidido>. <o porquê, se não for óbvio>
2. <...>

**Débitos técnicos**

* <débito> → resolvido nesta task | virou MS-XX | aceito: <motivo> (DD/MM/AAAA)

**Critérios de aceite**

- [ ] <comportamento verificável, com o caso de erro>
- [ ] <regra de permissão: não vaza dado de outro usuário>
- [ ] Testes unitários (mínimo de 70% por método), lint e build passando.
- [ ] <conforme o caso: Swagger, migration com run/revert, validação ponta a ponta com backend e banco reais>

**Depende de:** MS-XX. **Bloqueia:** MS-YY.
**Ref:** `docs/<arquivo>.md` (seção "<nome>")
```

Quando não houver débito, escreva "Nenhum encontrado." A seção nunca some, para ficar claro que ela foi verificada.

## Bug

Formato da MS-99 e da PC-70.

```markdown
**Problema:** <o que o usuário vê ou o que está errado, em uma frase>

**Reprodução:** <passo a passo, ou a chamada com o corpo e a resposta>

**Causa:** <a causa encontrada, citando arquivo e linha>

**Prioridade:** <nível>. <motivo>

**Correção** (decidida em DD/MM/AAAA)

1. <mudança>
2. <...>

**Decisões** (tomadas em DD/MM/AAAA)

1. **<tema>:** <decisão>

**Débitos técnicos**

* <débito> → <destino>

**Critérios de aceite**

- [ ] A reprodução acima não acontece mais.
- [ ] Teste que falhava antes da correção e passa depois.
- [ ] Lint, build e testes passando.
```

Se a causa ainda não é conhecida, investigue antes seguindo a skill `systematic-debugging`. Se a investigação for longa, ela vira uma task própria (`<Área>: investigar <sintoma>`), e o bug de correção é aberto depois, com a causa.

## Tela (frontend)

Use o modelo de Tarefa e coloque uma Ficha de Tela por tela dentro do Escopo (formato da MS-61):

```markdown
**Ficha de Tela: <nome>** (`<rota>`, <pública | autenticada>)

* Endpoint(s): `<VERBO /rota>` `{ <corpo> }` → <status>
* Campos/dados: <lista>
* Entra de → vai para: <origem> → <destino em cada caso>
* Regra-chave: <as 1 a 3 regras que mais importam, com o tratamento de cada erro>
* Reusa: <componentes do Design System>
```

Os textos da tela também são decisão. Defina os textos principais (título, botão, mensagens de erro e de vazio) antes de abrir a task.

## Decisão

Formato da MS-32. Serve para registrar uma decisão grande que gera várias tasks, ou uma que depende de terceiro.

```markdown
**Decidido em DD/MM/AAAA:** <a decisão>, <a alternativa descartada e por quê>.

**Impacto:** <o que muda no projeto>

Plano completo em `docs/<arquivo>.md`. A implementação foi quebrada nas tasks MS-XX a MS-YY, nesta mesma Epic.
```

## Epic

Formato da MS-1 e da PC-87. Um parágrafo:

```markdown
<objetivo do bloco>. <fonte ou integração principal>. <o que bloqueia ou do que depende>. <o que fica fora, se houver>.

**Prioridade:** <nível>. <motivo>
```

## Exemplo: a MS-65 reescrita no padrão novo

A MS-65 original foi aberta com cinco "Decisões em aberto". No padrão novo, elas teriam sido perguntadas antes, e o card nasceria assim (as respostas são ilustrativas):

```markdown
**Contexto:** quarta task do foco em inversores. O cliente pediu alarmes classificados (A1 crítico, A2 importante, A3 informativo), no espírito da ISA-18.2. Entra na Fase 1, decidido em 24/09/2026 (`docs/arquitetura/08-inversores-fase1.md`).

**Prioridade:** Medium. Entrega da Fase 1, mas não bloqueia outras tasks de backend.

**Escopo**

* Entidade de alarme por inversor: tipo, classe, início, fim e a última leitura que o sustentou.
* Abertura e fechamento a partir das leituras e dos estados do coletor (MS-64), sem chamadas extras à Sungrow.
* Endpoints autenticados, só das usinas do usuário: alarmes ativos e histórico, com filtro por usina, inversor, classe e período.
* E-mail ao abrir um alarme A1 ou A2, pelo `EmailService` (MS-52). Uma falha no envio nunca derruba a coleta.

**Fora do escopo**

* Reconhecimento manual (ack) → MS-XX.

**Decisões** (tomadas em 24/09/2026)

1. **Classes:** A1 = todos os inversores da usina sem comunicação. A2 = inversor em falha. A3 = inversor isolado offline ou com potência limitada.
2. **Histerese:** o alarme abre depois de 2 leituras seguidas na condição e fecha depois de 2 leituras normais (20 min).
3. **E-mail:** só para o dono da usina, um por alarme aberto, sem resumo.
4. **Retenção:** 12 meses de histórico.

**Débitos técnicos**

* Não há falha real no histórico (561 leituras, todas online) → aceito: a validação usa leituras simuladas (24/09/2026).

**Critérios de aceite**

- [ ] O alarme abre e fecha conforme as regras, com histerese, testado com sequências simuladas.
- [ ] Ativos e histórico com filtros, sem vazar alarme de usina de outro usuário.
- [ ] O e-mail chega no Mailpit uma vez por alarme. Uma falha de SMTP não afeta a coleta.
- [ ] Migration com run/revert, testes unitários (mínimo de 70% por método), Swagger, lint e build passando.

**Depende de:** MS-64. **Bloqueia:** MS-68.
```
