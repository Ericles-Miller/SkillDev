# 0005. Hooks nativos no lugar do hookify

- **Status:** Aceito em 2026-11-12

## Contexto

As regras do hookify só valiam nos projetos para onde eram copiadas. Quando uma regra bloqueava, o Claude via só "Blocked by hook", sem o motivo. E "rode lint e testes antes de terminar" era só instrução.

## Decisão

O plugin `base` traz três hooks em Python, com testes (`plugins/base/hooks/test_hooks.py`):
- **Guarda de comandos** (PreToolUse, Bash): barra npm, push em `main`/`develop` ou com `--force`, e, se o projeto pedir (`SKILLDEV_SEM_COMMIT=1`), commit, push e merge. Sai com código 2 e o motivo no stderr, que o Claude lê.
- **Lint a cada edição** (PostToolUse): ESLint (ou `dart analyze`) só no arquivo editado, mais avisos de `jest.mock` e `console.log`.
- **Portão de encerramento** (Stop): ESLint e os testes do Jest ligados aos arquivos que o Claude editou nesta sessão e ainda não commitou.

O portão não confere o trabalho em andamento do usuário, não repete um estado já aprovado e, se o Claude tentar encerrar duas vezes sem mudar nada, deixa encerrar e avisa o usuário.

## Consequências

- Os hooks valem em todo projeto onde o plugin está ligado, sem copiar nada.
- O teste real achou um bug, já corrigido: com link simbólico no caminho (no macOS, `/var` → `/private/var`), o ESLint ignorava o arquivo. Os hooks resolvem o caminho real.
- **Limitação declarada:** o portão confere os testes ligados aos arquivos, não o build nem o typecheck completo, e não garante que o commit é igual ao que passou.

**Emenda de 2026-11-12:** a limitação acima foi resolvida pelo portão de commit (ADR 0007).
