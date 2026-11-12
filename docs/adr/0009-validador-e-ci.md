# 0009. Validador e CI do próprio SkillDev

- **Status:** Aceito em 2026-11-12

## Contexto

Com três plugins, agentes, hooks e scripts, uma mudança pequena quebra outra parte em silêncio: um agente renomeado e a chamada esquecida, um revisor que ganha uma ferramenta de escrita, uma regra crítica apagada do texto de uma skill. Nada disso aparece até alguém usar.

## Decisão

- `scripts/validar.py` confere:
  - o marketplace e os manifestos;
  - o nome e a descrição de cada skill e de cada agente;
  - o tamanho máximo de agente (200 linhas);
  - que os agentes só leitura não têm ferramenta de escrita;
  - que cada ferramenta do Jira tem os dois nomes (CLI e app);
  - que cada `subagent_type` e cada skill pré-carregada existem;
  - que os scripts chamados pelos hooks existem;
  - que trechos obrigatórios continuam no texto das skills principais.
- O workflow `CI` roda o validador, os testes dos hooks e os testes dos scripts em todo PR e em todo push na `main`. O workflow `Templates do Nest` roda o `verify-templates.sh` quando os templates mudam.
- O validador foi testado estragando uma cópia de três jeitos; ele pegou os três.

## Consequências

- Regra nova que precisa ser garantida ganha uma trava no validador ou um teste.
- Os workflows só rodam no GitHub depois do push; nesta máquina, rodam os mesmos comandos à mão.
- Ainda não há eval de comportamento dos agentes (`claude plugin eval`); fica como próximo passo.
