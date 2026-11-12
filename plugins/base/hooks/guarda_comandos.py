"""PreToolUse (Bash): barra comandos que quebram as regras do padrão.

Sai com código 2 e o motivo no stderr: o Claude Code cancela o comando e o Claude lê o motivo.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PASTA_SCRIPTS = Path(__file__).resolve().parent.parent / 'scripts'
sys.path.insert(0, str(PASTA_SCRIPTS))
import verificar  # noqa: E402  (precisa do caminho acima)

# Comando no começo da linha ou depois de um separador de shell; "npm" dentro de um texto passa.
INICIO_DE_COMANDO = r'(^|[;&|(\n]\s*)'
# Opções globais do git antes do subcomando (`git -c user.name=x commit`, `git -C api push`, `git --no-pager ...`):
# sem isso, qualquer uma delas escapava das regras.
GIT = r'git(\s+(-[cC]\s+\S+|--[\w-]+(=\S+)?|-[a-zA-Z]))*\s+'

REGRAS = [
    {
        'padrao': re.compile(INICIO_DE_COMANDO + r'npm(\s|$)'),
        'ativa': lambda: True,
        'motivo': (
            'npm bloqueado: o padrão é só yarn. Troque pelo equivalente: '
            '`npm install` → `yarn`; `npm install <pacote>` → `yarn add <pacote>` (`-D` para dev); '
            '`npm run <script>` → `yarn <script>`; `npm install -g <pacote>` → `yarn global add <pacote>`.'
        ),
    },
    {
        'padrao': re.compile(
            GIT + r'push\b[^;&|\n]*(\s(main|develop)(\s|$)|:(main|develop)(\s|$)|\s(--force|-f)(\s|=|$))'
        ),
        'ativa': lambda: True,
        'motivo': (
            'Push bloqueado: `main` e `develop` só recebem código por Pull Request, e `--force` reescreve o '
            'histórico de quem já baixou a branch. Faça push da branch da task e abra o PR para `develop`; '
            'depois de um rebase na branch da task, use `--force-with-lease`.'
        ),
    },
    {
        'padrao': re.compile(INICIO_DE_COMANDO + GIT + r'(commit|push|merge)\b'),
        # Ligada pelo projeto, no .claude/settings.json: "env": {"SKILLDEV_SEM_COMMIT": "1"}.
        'ativa': lambda: os.environ.get('SKILLDEV_SEM_COMMIT') == '1',
        'motivo': (
            'Neste projeto você não faz commit, push nem merge (veja o CLAUDE.md do projeto). '
            'No fim da task, entregue a mensagem de commit sugerida e deixe o commit com o usuário.'
        ),
    },
]

COMMIT = re.compile(INICIO_DE_COMANDO + GIT + r'commit\b')


def motivo_commit_sem_verificacao(entrada: dict, comando: str) -> str | None:
    """Commit só com a verificação completa verde e com o código igual ao que foi verificado."""
    if os.environ.get('SKILLDEV_PORTAO_COMMIT') == 'off':
        return None
    pasta = Path(entrada.get('cwd') or os.getcwd())
    # `git -C <pasta> commit` commita em outro repositório: é esse que precisa estar verificado.
    outra_pasta = re.search(r'\bgit\b[^;&|\n]*?\s-C\s+(\S+)', comando)
    if outra_pasta:
        pasta = (pasta / outra_pasta.group(1).strip('\'"')).resolve()
    raiz = verificar.raiz_git(pasta)
    if not raiz:
        return None
    # Repositório sem verificação definida (docs, config) não é barrado.
    if not verificar.passos_do_projeto(verificar.pasta_do_projeto(pasta, raiz)):
        return None
    comando = f'python3 -B "{PASTA_SCRIPTS / "verificar.py"}"'
    try:
        estado = verificar.ler_estado(raiz)
        if not estado:
            return f'Commit barrado: ainda não houve a verificação completa deste código. Rode `{comando}` e só depois faça o commit.'
        if not estado.get('ok'):
            return f'Commit barrado: a última verificação falhou. Corrija e rode `{comando}` de novo.'
        if estado.get('impressao') != verificar.impressao_digital(raiz):
            return (
                'Commit barrado: o código mudou depois da última verificação, então o que iria no commit não é o '
                f'que passou. Rode `{comando}` de novo.'
            )
    except (subprocess.CalledProcessError, OSError, ValueError):
        return None  # falha do próprio portão não trava o trabalho
    return None


def main() -> int:
    entrada = json.load(sys.stdin)
    comando = entrada.get('tool_input', {}).get('command', '')
    for regra in REGRAS:
        if regra['ativa']() and regra['padrao'].search(comando):
            print(regra['motivo'], file=sys.stderr)
            return 2
    if COMMIT.search(comando):
        motivo = motivo_commit_sem_verificacao(entrada, comando)
        if motivo:
            print(motivo, file=sys.stderr)
            return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
