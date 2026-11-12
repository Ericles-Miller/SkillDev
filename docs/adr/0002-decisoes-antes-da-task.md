# 0002. Nenhuma task é aberta com decisão ou débito em aberto

- **Status:** Aceito em 2026-11-06. Emendas em 2026-11-12.

## Contexto

Nos projetos MS e PC, várias tasks nasciam com "Decisões em aberto" (MS-65, MS-86). Quem implementava parava no meio para perguntar, ou decidia sozinho e errava.

## Decisão

A skill `jira-task` só cria o card depois de levantar e resolver com o usuário as decisões, os débitos técnicos e os riscos. As decisões ficam escritas no card, com data.

**Emendas de 2026-11-12:**
- Pré-mortem ("por que esta task daria errado?"), critérios em Dado / Quando / Então, ADR para decisão grande e Definition of Ready como portão final.
- Triagem antes de perguntar: só vira pergunta o que muda o resultado para o cliente e tem duas respostas razoáveis. O resto vira premissa segura, escrita no card e aprovada no rascunho. Fato sem fonte vai para "A conferir".
- O card cita os arquivos (Criar e Modificar), os efeitos fora do código com dono e os outros usuários de um recurso compartilhado.
- O `revisor-task` confere o rascunho antes de ele chegar ao usuário (ADR 0003).

## Consequências

- Abrir um card leva mais tempo; implementar leva menos e volta menos.
- Decisão que depende de terceiro vira uma task "Decisão:" ou de investigação antes da task principal.
