"""Stop: não deixa o Claude encerrar com lint ou teste quebrado nos arquivos que ele editou nesta sessão.

- Só confere o que o próprio Claude editou (registro do lint_edicao.py) e que ainda está diferente do último
  commit. O trabalho em andamento do usuário nunca trava o Claude.
- Estado já aprovado não é conferido de novo. Estado que já bloqueou uma vez e não mudou deixa o Claude
  encerrar e avisa o usuário, para não virar laço.
- Falha sai com código 2: o Claude lê o motivo e continua trabalhando.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from comum import EXTENSOES_FONTE, EXTENSOES_JS, cortar, editados_na_sessao, pasta_sessoes, raiz_do_projeto, rodar

TIMEOUT_POR_COMANDO = 240  # segundos; o hook inteiro tem 600


def alterado_desde_o_commit(arquivo: Path) -> bool:
    try:
        resultado = subprocess.run(
            ['git', 'status', '--porcelain', '--', arquivo.name],
            cwd=arquivo.parent, capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return True
    # Fora de um repositório git não dá para saber: confere do mesmo jeito.
    return resultado.returncode != 0 or bool(resultado.stdout.strip())


def impressao(arquivos: list[Path]) -> str:
    partes = []
    for arquivo in sorted(arquivos):
        estado = arquivo.stat()
        partes.append(f'{arquivo}:{estado.st_mtime_ns}:{estado.st_size}')
    return hashlib.sha256('\n'.join(partes).encode()).hexdigest()


def verificar_node(raiz: Path, arquivos: list[Path]) -> list[str]:
    falhas = []
    bin_dir = raiz / 'node_modules' / '.bin'
    js = [str(arquivo) for arquivo in arquivos if arquivo.suffix in EXTENSOES_JS]
    if js and (bin_dir / 'eslint').exists():
        resultado = rodar([str(bin_dir / 'eslint'), '--no-warn-ignored', *js], raiz, TIMEOUT_POR_COMANDO)
        if resultado.returncode == 1:
            falhas.append(f'== ESLint ({raiz}) ==\n{cortar(resultado.stdout + resultado.stderr)}')
    if js and (bin_dir / 'jest').exists():
        comando = [str(bin_dir / 'jest'), '--findRelatedTests', *js, '--passWithNoTests']
        resultado = rodar(comando, raiz, TIMEOUT_POR_COMANDO)
        if resultado.returncode != 0:
            falhas.append(f'== Jest, testes ligados aos arquivos editados ({raiz}) ==\n{cortar(resultado.stdout + resultado.stderr)}')
    return falhas


def verificar_dart(raiz: Path, arquivos: list[Path]) -> list[str]:
    dart = shutil.which('dart')
    if not dart:
        return []
    resultado = rodar([dart, 'analyze', '--no-fatal-warnings', *map(str, arquivos)], raiz, TIMEOUT_POR_COMANDO)
    return [f'== dart analyze ({raiz}) ==\n{cortar(resultado.stdout + resultado.stderr)}'] if resultado.returncode != 0 else []


def verificar(arquivos: list[Path]) -> list[str]:
    por_projeto: dict[tuple[str, Path], list[Path]] = defaultdict(list)
    for arquivo in arquivos:
        marcador = 'pubspec.yaml' if arquivo.suffix == '.dart' else 'package.json'
        raiz = raiz_do_projeto(arquivo, marcador)
        if raiz:
            por_projeto[(marcador, raiz)].append(arquivo)
    falhas = []
    for (marcador, raiz), do_projeto in por_projeto.items():
        falhas += verificar_dart(raiz, do_projeto) if marcador == 'pubspec.yaml' else verificar_node(raiz, do_projeto)
    return falhas


def main() -> int:
    entrada = json.load(sys.stdin)
    if os.environ.get('SKILLDEV_PORTAO') == 'off':
        return 0
    sessao = entrada.get('session_id', 'sem-sessao')
    # Caminho real, pelo mesmo motivo do lint_edicao.py: com link simbólico, o ESLint ignora o arquivo.
    editados = list(dict.fromkeys(Path(caminho).resolve() for caminho in editados_na_sessao(sessao)))
    pendentes = [
        arquivo for arquivo in editados
        if arquivo.suffix in EXTENSOES_FONTE and arquivo.exists() and alterado_desde_o_commit(arquivo)
    ]
    if not pendentes:
        return 0

    arquivo_estado = pasta_sessoes() / f'{sessao}.estado.json'
    estado = json.loads(arquivo_estado.read_text()) if arquivo_estado.exists() else {}
    atual = impressao(pendentes)
    if estado.get('aprovado') == atual:
        return 0
    if entrada.get('stop_hook_active') and estado.get('reprovado') == atual:
        aviso = (
            'Portão do SkillDev: a verificação dos arquivos editados nesta sessão continua falhando, '
            'e o Claude encerrou sem corrigir. Confira antes de aceitar o trabalho.'
        )
        print(json.dumps({'systemMessage': aviso}))
        return 0

    try:
        falhas = verificar(pendentes)
    except subprocess.TimeoutExpired as erro:
        print(json.dumps({'systemMessage': f'Portão do SkillDev: a verificação demorou demais e foi pulada ({erro.cmd[0]}).'}))
        return 0

    if falhas:
        estado['reprovado'] = atual
        arquivo_estado.write_text(json.dumps(estado))
        print(
            'Portão do SkillDev: a verificação dos arquivos que você editou nesta sessão falhou. Corrija antes de '
            'encerrar. Se a falha não vem da sua mudança, diga isso ao usuário em vez de mexer no que não é seu.\n\n'
            + '\n\n'.join(falhas),
            file=sys.stderr,
        )
        return 2
    estado['aprovado'] = atual
    arquivo_estado.write_text(json.dumps(estado))
    return 0


if __name__ == '__main__':
    sys.exit(main())
