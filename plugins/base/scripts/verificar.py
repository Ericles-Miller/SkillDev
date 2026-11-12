"""Roda a verificação completa do projeto e grava a impressão digital do código verificado.

Uso: python3 -B verificar.py [pasta-do-projeto]

- Node: os scripts do package.json que existirem, nesta ordem: lint, build, test.
- Flutter: flutter analyze e flutter test.
- Grava em <pasta .git>/skilldev-verificacao.json o resultado de cada passo e a impressão digital: o hash da
  árvore com todos os arquivos (os do commit, os alterados e os novos não ignorados), calculado depois do
  último passo (o lint com --fix pode mudar arquivos).

O hook guarda_comandos.py recusa `git commit` se a última verificação falhou ou se o código mudou depois dela.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ARQUIVO_ESTADO = 'skilldev-verificacao.json'
TIMEOUT_POR_PASSO = 1800  # segundos; uma suíte grande de testes cabe com folga
MAX_SAIDA = 4000  # caracteres da saída de um passo que falhou


def git(args: list[str], cwd: Path, env: dict | None = None) -> str:
    resultado = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, check=True, env=env)
    return resultado.stdout.strip()


def raiz_git(pasta: Path) -> Path | None:
    try:
        return Path(git(['rev-parse', '--show-toplevel'], pasta)).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError, NotADirectoryError):
        return None


def pasta_do_projeto(pasta: Path, raiz: Path) -> Path:
    # Em repositório com o projeto numa subpasta, vale a pasta de onde se roda, se ela tiver o manifesto.
    for candidata in (pasta, raiz):
        if (candidata / 'package.json').exists() or (candidata / 'pubspec.yaml').exists():
            return candidata
    return raiz


def passos_do_projeto(projeto: Path) -> list[list[str]]:
    pacote = projeto / 'package.json'
    if pacote.exists():
        scripts = json.loads(pacote.read_text(encoding='utf-8')).get('scripts', {})
        return [['yarn', nome] for nome in ('lint', 'build', 'test') if nome in scripts]
    if (projeto / 'pubspec.yaml').exists():
        return [['flutter', 'analyze'], ['flutter', 'test']]
    return []


def impressao_digital(raiz: Path) -> str:
    # Índice temporário: a árvore inclui o que não está no stage e os arquivos novos, sem mexer no índice real.
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, 'GIT_INDEX_FILE': str(Path(tmp) / 'index')}
        try:
            git(['read-tree', 'HEAD'], raiz, env)
        except subprocess.CalledProcessError:
            pass  # repositório ainda sem commit
        git(['add', '-A'], raiz, env)
        return git(['write-tree'], raiz, env)


def arquivo_estado(raiz: Path) -> Path:
    return Path(git(['rev-parse', '--absolute-git-dir'], raiz)) / ARQUIVO_ESTADO


def ler_estado(raiz: Path) -> dict | None:
    arquivo = arquivo_estado(raiz)
    return json.loads(arquivo.read_text(encoding='utf-8')) if arquivo.exists() else None


def cortar(texto: str) -> str:
    texto = texto.strip()
    return texto if len(texto) <= MAX_SAIDA else '[...]\n' + texto[-MAX_SAIDA:]


def main() -> int:
    pasta = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
    raiz = raiz_git(pasta)
    if not raiz:
        print('Fora de um repositório git: não há o que verificar.')
        return 1
    projeto = pasta_do_projeto(pasta, raiz)
    passos = passos_do_projeto(projeto)
    if not passos:
        print('Nenhum passo de verificação encontrado (sem package.json com lint, build ou test, e sem pubspec.yaml).')
        return 1

    ambiente = {**os.environ, 'CI': 'true', 'FORCE_COLOR': '0', 'NO_COLOR': '1'}
    resultados = []
    ok = True
    for comando in passos:
        inicio = time.time()
        resultado = subprocess.run(comando, cwd=projeto, capture_output=True, text=True, timeout=TIMEOUT_POR_PASSO, env=ambiente)
        passou = resultado.returncode == 0
        resultados.append({'comando': ' '.join(comando), 'ok': passou, 'segundos': round(time.time() - inicio, 1)})
        print(f"{'OK ' if passou else 'ERR'} {' '.join(comando)} ({resultados[-1]['segundos']}s)")
        if not passou:
            print(cortar(resultado.stdout + resultado.stderr))
            ok = False
            break  # o primeiro passo que falha já reprova; os seguintes só gastariam tempo

    estado = {
        'ok': ok,
        'impressao': impressao_digital(raiz),
        'projeto': str(projeto),
        'passos': resultados,
        'quando': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    arquivo_estado(raiz).write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Verificação OK: impressão digital gravada; o commit está liberado.' if ok else 'Verificação falhou: o commit continua barrado.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
