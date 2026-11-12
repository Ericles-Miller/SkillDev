# 0003. Revisores independentes, só leitura, para card e para código

- **Status:** Aceito em 2026-11-12

## Contexto

Quem escreve um card ou um código e depois revisa o próprio trabalho tende a confirmar o que fez. As ferramentas prontas (`/code-review`, `/security-review`) não conhecem o padrão nem as regras de negócio de cada projeto.

## Decisão

Dois agentes, cada um rodando com o contexto limpo, sem ver a conversa que produziu o trabalho:
- `revisor-task` confere o rascunho do card: Definition of Ready, texto vago, arquivos e fatos citados, regras contra os docs e o código, Jira e um pré-mortem próprio.
- `revisor-codigo` confere o diff: cada critério com código e teste, o padrão da stack, falhas, segurança, testes e regras.

Os dois só leem. A restrição fica no frontmatter (`tools` com uma lista só de leitura, sem terminal), e não no texto do prompt. As ferramentas do Jira aparecem com os nomes das duas superfícies (CLI e app desktop). Os dois rodam em Opus, porque o trabalho é de julgamento.

## Consequências

- A `jira-task` chama o `revisor-task` antes de mostrar o rascunho; a `executar-task` chama o `revisor-codigo` no fechamento.
- Quem roda lint, build e testes é a sessão principal. O revisor lê o código e não executa nada.
- Testado em 2026-11-12: na MS-86, o revisor de cards achou seis furos com evidência no código; na MS-77, o de código achou oito problemas reais.
