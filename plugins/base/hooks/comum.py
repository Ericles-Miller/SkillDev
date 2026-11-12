"""Funções compartilhadas pelos hooks do plugin base."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

EXTENSOES_JS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}
EXTENSOES_FONTE = EXTENSOES_JS | {'.dart'}
MAX_SAIDA = 4000  # caracteres de saída de ferramenta mandados ao Claude por bloco
DIAS_GUARDANDO_SESSAO = 7  # o registro de uma sessão antiga não serve para nada depois disso


def pasta_dados() -> Path:
    # CLAUDE_PLUGIN_DATA sobrevive às atualizações do plugin; sem ele (nos testes), fica em ~/.claude.
    pasta = Path(os.environ.get('CLAUDE_PLUGIN_DATA') or Path.home() / '.claude' / 'skilldev-hooks')
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def pasta_sessoes() -> Path:
    pasta = pasta_dados() / 'sessoes'
    pasta.mkdir(exist_ok=True)
    return pasta


def registrar_edicao(session_id: str, caminho: str) -> None:
    with (pasta_sessoes() / f'{session_id}.txt').open('a', encoding='utf-8') as registro:
        registro.write(caminho + '\n')


def editados_na_sessao(session_id: str) -> list[str]:
    registro = pasta_sessoes() / f'{session_id}.txt'
    if not registro.exists():
        return []
    return list(dict.fromkeys(linha for linha in registro.read_text(encoding='utf-8').splitlines() if linha))


def limpar_sessoes_antigas() -> None:
    limite = time.time() - DIAS_GUARDANDO_SESSAO * 86400
    for arquivo in pasta_sessoes().iterdir():
        if arquivo.stat().st_mtime < limite:
            arquivo.unlink(missing_ok=True)


def raiz_do_projeto(arquivo: Path, marcador: str) -> Path | None:
    for pasta in [arquivo.parent, *arquivo.parent.parents]:
        if (pasta / marcador).exists():
            return pasta
    return None


def rodar(comando: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    # Sem modo interativo e sem cores: os códigos de cor poluem a mensagem que o Claude lê.
    env = {**os.environ, 'CI': 'true', 'FORCE_COLOR': '0', 'NO_COLOR': '1'}
    return subprocess.run(comando, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)


def cortar(texto: str) -> str:
    texto = texto.strip()
    return texto if len(texto) <= MAX_SAIDA else '[...]\n' + texto[-MAX_SAIDA:]
