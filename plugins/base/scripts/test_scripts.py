"""Testa o detectar_projeto.py contra um projeto falso.

O verificar.py é testado junto com o portão de commit, em plugins/base/hooks/test_hooks.py.

Uso: python3 -I -B plugins/base/scripts/test_scripts.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent
falhas = 0


def confere(nome, condicao, detalhe=''):
    global falhas
    falhas += not condicao
    print(f"{'OK ' if condicao else 'ERR'} {nome}" + ('' if condicao else f'  -> {detalhe}'))


def detectar(pasta, *extra):
    return subprocess.run([sys.executable, '-B', str(PASTA / 'detectar_projeto.py'), str(pasta), *extra],
                          capture_output=True, text=True)


def main():
    print('== detectar_projeto')
    with tempfile.TemporaryDirectory() as tmp:
        projeto = Path(tmp)
        scripts = {'lint': 'eslint .', 'build': 'nest build', 'test': 'jest', 'test:e2e': 'jest -c e2e', 'start:dev': 'nest start --watch', 'outro': 'x'}
        (projeto / 'package.json').write_text(json.dumps({'scripts': scripts}))
        (projeto / 'docker-compose.yml').write_text('services: {}\n')
        (projeto / '.github' / 'workflows').mkdir(parents=True)
        (projeto / '.github' / 'workflows' / 'ci.yml').write_text('jobs:\n  t:\n    steps:\n      - run: yarn install --frozen-lockfile\n      - run: yarn test\n      - run: |\n          echo bloco\n')
        (projeto / '.husky').mkdir()
        (projeto / '.husky' / 'pre-commit').write_text('#!/bin/sh\n. "$(dirname "$0")/_/husky.sh"\nyarn lint-staged\n')

        saida = detectar(projeto).stdout
        confere('lista os scripts conhecidos do package.json', all(f'`yarn {s}`' in saida for s in ('lint', 'build', 'test', 'test:e2e', 'start:dev')), saida)
        confere('não inventa script que não está no manifesto', '`yarn typecheck`' not in saida and 'outro' not in saida, saida)
        confere('lista os comandos do CI', '`yarn install --frozen-lockfile` (ci.yml)' in saida and '`yarn test` (ci.yml)' in saida, saida)
        confere('não lista o marcador de bloco do YAML como comando', '`|`' not in saida, saida)
        confere('lista o hook do Husky sem a linha de setup', 'pre-commit: `yarn lint-staged`' in saida, saida)
        confere('lista a infra local', '`docker compose up -d`' in saida, saida)

        claude_md = projeto / 'CLAUDE.md'
        claude_md.write_text('# Projeto\n\nTexto do usuário.\n')
        detectar(projeto, '--gravar', 'CLAUDE.md')
        primeira = claude_md.read_text()
        confere('acrescenta a seção sem apagar o resto', primeira.startswith('# Projeto\n\nTexto do usuário.') and '## Verificação' in primeira, primeira)
        scripts['typecheck'] = 'tsc --noEmit'
        (projeto / 'package.json').write_text(json.dumps({'scripts': scripts}))
        detectar(projeto, '--gravar', 'CLAUDE.md')
        segunda = claude_md.read_text()
        confere('rodar de novo troca a seção, sem duplicar', segunda.count('## Verificação') == 1 and '`yarn typecheck`' in segunda, segunda)
        confere('o texto do usuário continua lá', 'Texto do usuário.' in segunda)

    with tempfile.TemporaryDirectory() as tmp:
        saida = detectar(Path(tmp)).stdout
        confere('projeto sem manifesto diz que não há comando', 'Nenhum comando de verificação declarado' in saida, saida)

    print('OK' if not falhas else f'{falhas} falha(s)')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
