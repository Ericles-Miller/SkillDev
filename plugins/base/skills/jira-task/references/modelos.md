# Modelos de descrição

Os modelos foram tirados dos projetos MS (monitoramento de usina) e PC (calhas). Todos estão em markdown, porque o `createJiraIssue` recebe `contentFormat: "markdown"`.

O que mudou em relação a esses projetos:
- **Sem "Decisões em aberto".** Lá, algumas tasks nasciam com essa seção (MS-65, MS-86). Agora a decisão é tomada antes de abrir a task e entra em "Decisões", com a data. A decisão grande também ganha um ADR.
- **Seção "Riscos".** Traz o que o pré-mortem achou, cada risco com a sua mitigação.
- **Critérios de aceite em Dado / Quando / Então**, com valores concretos. Cada critério vira um teste.

## Tarefa

```markdown
**Contexto:** <por que a task existe: pedido do cliente, achado de auditoria, task de origem. De 2 a 4 linhas.>

**Prioridade:** <nível>. <motivo>

**Escopo**

* <o que entra, citando arquivos, endpoints e entidades>
* <...>

**Arquivos**

* Criar: `<caminho>` (espelhando `<arquivo real parecido>`)
* Modificar: `<caminho>`: <o que muda>

**Fora do escopo**

* <o que não entra> → <MS-XX, ou "decidido não fazer em DD/MM/AAAA">

**Decisões** (tomadas em DD/MM/AAAA)

1. **<tema>:** <o que foi decidido>. <o porquê, se não for óbvio>
2. **<tema>:** <decisão grande, em uma linha>. Ver ADR `docs/decisoes/NNNN-<titulo>.md`.

**Premissas assumidas** (só se houver; aprovadas pelo usuário no rascunho)

* Assumimos <X> porque <Y>.

**A conferir** (só se houver; fato sem fonte que não muda a implementação)

* <fato>: confere <quem>, em <onde>.

**Efeitos fora do código**

* <cliente afetado, dado a corrigir, dinheiro, outro time> → <dono ou task>

**Outros usuários de `<recurso>`** (só quando a task cria ou muda fila, lock, tabela ou estado compartilhado)

* <serviço ou módulo>: <como usa>; <o que muda para ele>.

**Débitos técnicos**

* <débito> → resolvido nesta task | virou MS-XX | aceito: <motivo> (DD/MM/AAAA)

**Riscos** (do pré-mortem)

* <o que pode dar errado> → <mitigação, que também está nos critérios de aceite>

**Critérios de aceite**

- [ ] **Dado** <situação inicial>, **quando** <ação>, **então** <resultado concreto: status, mensagem, dado gravado>.
- [ ] **Dado** <situação de erro>, **quando** <ação>, **então** <resposta de erro concreta>.
- [ ] **Dado** um usuário sem permissão, **quando** <ação>, **então** <404 ou 403, e nada muda>.
- [ ] Testes unitários (mínimo de 70% por método), lint e build passando.
- [ ] <conforme o caso: Swagger, migration com run/revert, validação ponta a ponta com backend e banco reais>

**Depende de:** MS-XX. **Bloqueia:** MS-YY.
**Ref:** `docs/<arquivo>.md` (seção "<nome>")
```

Quando não houver débito, escreva "Nenhum encontrado." Quando o pré-mortem não achar risco, escreva "Nenhum encontrado no pré-mortem." Quando não houver efeito fora do código, escreva "Nenhum." Essas seções nunca somem, para ficar claro que foram verificadas. "Premissas assumidas", "A conferir" e "Outros usuários" só aparecem quando têm item.

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

- [ ] **Dado** <a situação da reprodução>, **quando** <a ação>, **então** <o comportamento correto, concreto>.
- [ ] Teste de regressão que falhava antes da correção e passa depois.
- [ ] Lint, build e testes passando.
```

Se a causa ainda não é conhecida, investigue antes seguindo a skill `systematic-debugging`. Se a investigação for longa, ela vira uma task própria (`<Área>: investigar <sintoma>`), e o bug de correção é aberto depois, com a causa.

## Tela (frontend)

A task de tela usa a Ficha de Tela da skill `telas-figma` (veja o `references/modelos.md` dela). A Ficha traz:
- O título `Tela: <Nome> — Mobile + Web`.
- Os campos espelhando o DTO do backend.
- Os textos decididos.
- Os prompts do Figma First Draft e a checklist de colagem.

As regras desta skill continuam valendo: prioridade com motivo, e decisões e débitos fechados antes de abrir a task.

## Decisão

Formato da MS-32. Serve para registrar uma decisão grande que gera várias tasks, ou uma que depende de terceiro.

```markdown
**Decidido em DD/MM/AAAA:** <a decisão>, <a alternativa descartada e por quê>.

**Impacto:** <o que muda no projeto>

Registro completo no ADR `docs/decisoes/NNNN-<titulo>.md`. A implementação foi quebrada nas tasks MS-XX a MS-YY, nesta mesma Epic.
```

## ADR (Architecture Decision Record)

Arquivo `docs/decisoes/NNNN-<titulo-em-kebab>.md`, no repositório do projeto. O NNNN segue a numeração dos ADRs que já existem (`0001`, `0002`...).

```markdown
# NNNN. <Título da decisão, em uma frase>

- **Status:** Proposto | Aceito em DD/MM/AAAA | Substituído pelo NNNN
- **Task:** <CHAVE>-XX
- **Substitui:** <NNNN, se for o caso>

## Contexto

<O problema e o que está em jogo: requisito, restrição, prazo, custo, o que os docs diziam. Por que a decisão precisou ser tomada agora.>

## Opções

1. **<Opção A>:** <como seria>. A favor: <...>. Contra: <...>.
2. **<Opção B>:** <como seria>. A favor: <...>. Contra: <...>.

## Decisão

<A opção escolhida e o motivo principal.>

## Consequências

- <O que fica mais fácil.>
- <O que fica mais difícil, ou passa a ser obrigatório para as próximas tasks.>
- <A premissa que, se mudar, obriga a rever esta decisão.>
```

## Epic

Formato da MS-1 e da PC-87. Um parágrafo:

```markdown
<objetivo do bloco>. <fonte ou integração principal>. <o que bloqueia ou do que depende>. <o que fica fora, se houver>.

**Prioridade:** <nível>. <motivo>
```

## Exemplo: a MS-65 reescrita no padrão novo

A MS-65 original foi aberta com cinco "Decisões em aberto". No padrão novo, elas teriam sido perguntadas antes, o pré-mortem teria achado os riscos, e o card nasceria assim (as respostas são ilustrativas):

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

**Riscos** (do pré-mortem)

* Uma leitura que oscila abre e fecha o alarme a cada coleta, enchendo a caixa de e-mail → histerese de 2 leituras (decisão 2) e um e-mail por alarme (decisão 3).
* O SMTP fora do ar trava a coleta → o envio roda fora da coleta, e a falha só vira log.
* Um usuário vê alarme da usina de outro → o filtro pelo dono vai na própria consulta, com 404.

**Critérios de aceite**

- [ ] **Dado** um inversor em falha em 2 leituras seguidas, **quando** a coleta roda, **então** abre um alarme A2 com o início na primeira dessas leituras.
- [ ] **Dado** um alarme A2 aberto, **quando** chegam 2 leituras normais seguidas, **então** o alarme fecha com o fim na primeira leitura normal.
- [ ] **Dado** um inversor que alterna falha e normal a cada leitura, **quando** a coleta roda 6 vezes, **então** nenhum alarme abre.
- [ ] **Dado** o SMTP fora do ar, **quando** um alarme A1 abre, **então** a coleta segue normal e o erro aparece no log.
- [ ] **Dado** um usuário sem acesso à usina X, **quando** chama `GET /alarms?plantId=X`, **então** recebe 404.
- [ ] Migration com run/revert, testes unitários (mínimo de 70% por método), Swagger, lint e build passando.

**Depende de:** MS-64. **Bloqueia:** MS-68.
```
