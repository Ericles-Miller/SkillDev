"""PostToolUse (Edit/Write/MultiEdit): lint do arquivo editado e avisos do padrão.

- Erro de lint sai com código 2: o Claude lê a saída e corrige na hora.
- Aviso (jest.mock num teste, console.log no código) vai como contexto, sem bloquear.
- Todo arquivo editado fica registrado na sessão, para o portão do Stop conferir depois.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from comum import EXTENSOES_JS, cortar, limpar_sessoes_antigas, raiz_do_projeto, registrar_edicao, rodar


def lint_js(arquivo: Path) -> str | None:
    raiz = raiz_do_projeto(arquivo, 'package.json')
    eslint = raiz / 'node_modules' / '.bin' / 'eslint' if raiz else None
    if not eslint or not eslint.exists():
        return None
    resultado = rodar([str(eslint), '--no-warn-ignored', str(arquivo)], raiz, timeout=90)
    # 1 = problema no código. 2 = erro de configuração do ESLint, que não vem da edição.
    return resultado.stdout + resultado.stderr if resultado.returncode == 1 else None


def lint_dart(arquivo: Path) -> str | None:
    raiz = raiz_do_projeto(arquivo, 'pubspec.yaml')
    dart = shutil.which('dart')
    if not raiz or not dart:
        return None
    resultado = rodar([dart, 'analyze', '--no-fatal-warnings', str(arquivo)], raiz, timeout=90)
    return resultado.stdout + resultado.stderr if resultado.returncode != 0 else None


def texto_escrito(entrada: dict) -> str:
    # Só o que o Claude acabou de escrever: um console.log antigo no arquivo não gera aviso a cada edição.
    dados = entrada.get('tool_input', {})
    if 'content' in dados:
        return dados['content']
    if 'new_string' in dados:
        return dados['new_string']
    return '\n'.join(edicao.get('new_string', '') for edicao in dados.get('edits', []))


def avisos(arquivo: Path, texto: str) -> list[str]:
    lista = []
    if arquivo.name.endswith('.spec.ts') and 'jest.mock(' in texto:
        lista.append(
            f'{arquivo.name}: `jest.mock` num teste. O padrão é um fake em memória com o mesmo contrato do real; '
            'mock só para algo externo e lento (rede, fila, SMTP), com um comentário dizendo por quê.'
        )
    eh_codigo_da_app = '/src/' in str(arquivo) and not arquivo.name.endswith('.spec.ts') and arquivo.name != 'main.ts'
    if eh_codigo_da_app and re.search(r'console\.(log|debug)\(', texto):
        lista.append(
            f'{arquivo.name}: `console.log` no código da aplicação. Use o logger da classe '
            '(`private readonly logger = new Logger(<Classe>.name)`), ou apague se era só para investigar.'
        )
    return lista


def main() -> int:
    entrada = json.load(sys.stdin)
    caminho = entrada.get('tool_input', {}).get('file_path')
    if not caminho:
        return 0
    registrar_edicao(entrada.get('session_id', 'sem-sessao'), caminho)
    limpar_sessoes_antigas()

    # Caminho real: com link simbólico no meio (no macOS, /var → /private/var), o ESLint acha que o arquivo
    # está fora do projeto e o ignora em silêncio.
    arquivo = Path(caminho).resolve()
    if os.environ.get('SKILLDEV_LINT_EDICAO') == 'off' or not arquivo.exists():
        return 0

    try:
        erro = lint_js(arquivo) if arquivo.suffix in EXTENSOES_JS else lint_dart(arquivo) if arquivo.suffix == '.dart' else None
    except subprocess.TimeoutExpired:
        erro = None
    lista_avisos = avisos(arquivo, texto_escrito(entrada))

    if erro:
        mensagem = f'O lint achou problemas em {arquivo.name}. Corrija antes de seguir:\n\n{cortar(erro)}'
        if lista_avisos:
            mensagem += '\n\nAvisos do padrão:\n- ' + '\n- '.join(lista_avisos)
        print(mensagem, file=sys.stderr)
        return 2
    if lista_avisos:
        contexto = 'Avisos do padrão:\n- ' + '\n- '.join(lista_avisos)
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': contexto}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
