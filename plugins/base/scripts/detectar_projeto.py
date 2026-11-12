"""Monta a seção "Verificação" do CLAUDE.md do projeto a partir dos manifestos reais.

Uso:
  python3 -B detectar_projeto.py [pasta]                    imprime a seção
  python3 -B detectar_projeto.py [pasta] --gravar CLAUDE.md  troca a seção no arquivo (ou acrescenta no fim)

Lê o package.json (scripts), o pubspec.yaml, os workflows do GitHub Actions, os hooks do Husky e o
docker-compose. Nenhum comando entra na seção sem estar declarado num desses arquivos.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

INICIO = '<!-- skilldev:verificacao:inicio (gerado por detectar_projeto.py; para mudar, rode o script de novo) -->'
FIM = '<!-- skilldev:verificacao:fim -->'
SCRIPTS_CONHECIDOS = [
    ('lint', 'Lint'),
    ('typecheck', 'Typecheck'),
    ('build', 'Build'),
    ('test', 'Testes'),
    ('test:e2e', 'Testes e2e'),
    ('test:cov', 'Cobertura'),
    ('format', 'Formatação'),
    ('start:dev', 'Rodar em desenvolvimento'),
]


def comandos_do_ci(pasta: Path) -> list[tuple[str, str]]:
    comandos = []
    for workflow in sorted((pasta / '.github' / 'workflows').glob('*.y*ml')):
        for linha in workflow.read_text(encoding='utf-8').splitlines():
            achado = re.match(r'\s*-?\s*run:\s*(.+)$', linha)
            if achado and achado.group(1).strip() not in ('|', '>'):
                comandos.append((workflow.name, achado.group(1).strip()))
    return comandos


def hooks_do_husky(pasta: Path) -> list[tuple[str, str]]:
    hooks = []
    pasta_husky = pasta / '.husky'
    for nome in ('pre-commit', 'commit-msg', 'pre-push'):
        arquivo = pasta_husky / nome
        if arquivo.exists():
            linhas = [l.strip() for l in arquivo.read_text(encoding='utf-8').splitlines()]
            uteis = [l for l in linhas if l and not l.startswith('#') and 'husky.sh' not in l]
            hooks.append((nome, '; '.join(uteis)))
    return hooks


def montar_secao(pasta: Path) -> str:
    linhas = [INICIO, '## Verificação', '']
    pacote = pasta / 'package.json'
    if pacote.exists():
        scripts = json.loads(pacote.read_text(encoding='utf-8')).get('scripts', {})
        for nome, rotulo in SCRIPTS_CONHECIDOS:
            if nome in scripts:
                linhas.append(f'- {rotulo}: `yarn {nome}`')
    if (pasta / 'pubspec.yaml').exists():
        linhas += ['- Análise: `flutter analyze`', '- Testes: `flutter test`']
    if any((pasta / nome).exists() for nome in ('docker-compose.yml', 'docker-compose.yaml', 'compose.yml')):
        linhas.append('- Infra local: `docker compose up -d`')
    ci = comandos_do_ci(pasta)
    if ci:
        linhas += ['', 'O CI roda:']
        linhas += [f'- `{comando}` ({workflow})' for workflow, comando in ci]
    husky = hooks_do_husky(pasta)
    if husky:
        linhas += ['', 'Hooks do git (Husky):']
        linhas += [f'- {nome}: `{comando}`' for nome, comando in husky]
    if len(linhas) == 3:
        linhas.append('Nenhum comando de verificação declarado nos manifestos.')
    linhas += ['', FIM]
    return '\n'.join(linhas)


def gravar(arquivo: Path, secao: str) -> None:
    texto = arquivo.read_text(encoding='utf-8') if arquivo.exists() else ''
    if INICIO in texto and FIM in texto:
        antes, resto = texto.split(INICIO, 1)
        depois = resto.split(FIM, 1)[1]
        texto = antes + secao + depois
    else:
        texto = texto.rstrip() + ('\n\n' if texto.strip() else '') + secao + '\n'
    arquivo.write_text(texto, encoding='utf-8')


def main() -> int:
    argumentos = sys.argv[1:]
    destino = None
    if '--gravar' in argumentos:
        indice = argumentos.index('--gravar')
        destino = Path(argumentos[indice + 1])
        argumentos = argumentos[:indice] + argumentos[indice + 2:]
    pasta = Path(argumentos[0] if argumentos else '.').resolve()
    secao = montar_secao(pasta)
    if destino:
        gravar(destino if destino.is_absolute() else pasta / destino, secao)
        print(f'Seção "Verificação" gravada em {destino}.')
    else:
        print(secao)
    return 0


if __name__ == '__main__':
    sys.exit(main())
