# 0007. Commit só com o código igual ao que passou na verificação completa

- **Status:** Aceito em 2026-11-12

## Contexto

O portão de encerramento (ADR 0005) confere o lint e os testes ligados aos arquivos editados, mas não roda o build nem a suíte inteira e não garante que o que vai no commit é o que passou. Editar depois de verificar é o jeito mais comum de entregar código quebrado com "testes verdes" no relato.

## Decisão

- O `plugins/base/scripts/verificar.py` roda a verificação completa do projeto: os scripts `lint`, `build` e `test` do `package.json` (ou `flutter analyze` e `flutter test`). No fim, grava na pasta do git o resultado e a **impressão digital**: o hash da árvore com todos os arquivos (os do commit, os alterados e os novos não ignorados), calculado num índice temporário, sem mexer no índice real.
- A guarda de comandos barra `git commit` quando não houve verificação, quando a última falhou ou quando a impressão digital mudou. A mensagem diz o comando a rodar.
- Repositório sem `package.json` nem `pubspec.yaml` (docs, config) não é barrado. O projeto pode desligar com `SKILLDEV_PORTAO_COMMIT=off`.
- A verificação para no primeiro passo que falha.

## Consequências

- `git add` depois da verificação não muda a impressão digital; qualquer edição muda.
- Arquivo novo que não é ignorado entra na conta: arquivo de rascunho esquecido na pasta exige verificar de novo, ou entrar no `.gitignore`.
- Só os commits feitos pelo Claude passam pelo hook. Commit feito por você no terminal não é afetado.
