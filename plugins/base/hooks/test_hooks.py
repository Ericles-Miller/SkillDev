"""Testa os hooks do plugin base contra um projeto falso.

O ESLint e o Jest do projeto falso são scripts: falham quando o arquivo tem ERRO_LINT ou ERRO_TESTE. Assim dá
para testar a lógica dos hooks sem instalar nada. O teste com as ferramentas reais é feito à parte.

Uso: python3 -I -B plugins/base/hooks/test_hooks.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PASTA_HOOKS = Path(__file__).resolve().parent
PASTA_SCRIPTS = PASTA_HOOKS.parent / 'scripts'
FORA_DE_REPOSITORIO = tempfile.gettempdir()  # cwd dos casos que não envolvem o portão de commit

# Como o ESLint de verdade, ignora em silêncio o arquivo cujo caminho não começa pela pasta do projeto.
ESLINT_FALSO = """#!/bin/sh
for f in "$@"; do case "$f" in "$PWD"/*) if grep -q ERRO_LINT "$f" 2>/dev/null; then echo "$f: erro de lint"; exit 1; fi;; esac; done
exit 0
"""
JEST_FALSO = """#!/bin/sh
echo chamado >> "$JEST_CALLS"
for f in "$@"; do case "$f" in -*) ;; *) if grep -q ERRO_TESTE "$f" 2>/dev/null; then echo "FAIL $f"; exit 1; fi;; esac; done
exit 0
"""

falhas = 0


def confere(nome, condicao, detalhe=''):
    global falhas
    falhas += not condicao
    print(f"{'OK ' if condicao else 'ERR'} {nome}" + ('' if condicao else f'  -> {detalhe}'))


def hook(script, entrada, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    return subprocess.run(
        [sys.executable, '-B', str(PASTA_HOOKS / script)], input=json.dumps(entrada),
        capture_output=True, text=True, env=env,
    )


def bash(comando, env_extra=None, cwd=FORA_DE_REPOSITORIO):
    entrada = {'tool_name': 'Bash', 'cwd': cwd, 'tool_input': {'command': comando}}
    return hook('guarda_comandos.py', entrada, env_extra).returncode


def testar_guarda():
    print('== guarda_comandos')
    bloqueia = ['npm install', 'cd api && npm run build', 'npm', 'yarn lint\nnpm test', '(npm ci)',
                'git push origin main', 'git push origin develop', 'git push origin HEAD:main', 'git push --force',
                'git push -f origin MS-61', 'git -c user.name=t push origin main', 'git --no-pager push --force',
                'git -C api push origin develop']
    passa = ['yarn test', 'pnpm i', 'npx tsc --noEmit', "git commit -m 'chore: drop npm lockfile'",
             'git push -u origin MS-61', 'git push --force-with-lease origin MS-61', 'git push origin feature/main-menu',
             'git commit -m wip', 'git merge develop']
    for comando in bloqueia:
        confere(f'bloqueia {comando!r}', bash(comando) == 2)
    for comando in passa:
        confere(f'deixa passar {comando!r}', bash(comando) == 0)
    sem_commit = {'SKILLDEV_SEM_COMMIT': '1'}
    for comando in ['git commit -m wip', 'git add . && git commit -m x', 'git -C api commit -m x', 'git merge develop',
                    'git -c user.name=t -c user.email=t@t commit -m x', 'git --no-pager merge develop']:
        confere(f'sem commit: bloqueia {comando!r}', bash(comando, sem_commit) == 2)
    for comando in ['git status', 'git log --oneline', "echo 'git commit depois'"]:
        confere(f'sem commit: deixa passar {comando!r}', bash(comando, sem_commit) == 0)
    resultado = hook('guarda_comandos.py', {'tool_name': 'Bash', 'tool_input': {'command': 'npm i'}})
    confere('o motivo vai no stderr', 'yarn' in resultado.stderr, resultado.stderr)


def montar_projeto(raiz):
    (raiz / 'src').mkdir(parents=True)
    (raiz / 'package.json').write_text('{"name": "falso"}')
    bin_dir = raiz / 'node_modules' / '.bin'
    bin_dir.mkdir(parents=True)
    for nome, conteudo in [('eslint', ESLINT_FALSO), ('jest', JEST_FALSO)]:
        (bin_dir / nome).write_text(conteudo)
        (bin_dir / nome).chmod(0o755)
    (raiz / '.gitignore').write_text('node_modules/\n')
    for comando in (['git', 'init', '-q'], ['git', 'add', '.'], ['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'init']):
        subprocess.run(comando, cwd=raiz, check=True)


def escrever(raiz, sessao, relativo, conteudo, env):
    arquivo = raiz / relativo
    arquivo.write_text(conteudo)
    return hook('lint_edicao.py', {'session_id': sessao, 'tool_name': 'Write',
                                    'tool_input': {'file_path': str(arquivo), 'content': conteudo}}, env)


def testar_lint(raiz, env):
    print('== lint_edicao')
    r = escrever(raiz, 's1', 'src/limpo.ts', 'export const x = 1;\n', env)
    confere('arquivo limpo passa em silêncio', r.returncode == 0 and not r.stdout.strip(), r.stdout + r.stderr)
    r = escrever(raiz, 's1', 'src/sujo.ts', 'ERRO_LINT\n', env)
    confere('erro de lint sai com 2 e mostra a saída', r.returncode == 2 and 'erro de lint' in r.stderr, r.stderr)
    atalho = raiz.parent / 'atalho'
    atalho.symlink_to(raiz)
    r = escrever(atalho, 's1', 'src/pelo-atalho.ts', 'ERRO_LINT\n', env)
    confere('erro de lint é pego também por caminho com link simbólico', r.returncode == 2, r.stderr)
    r = escrever(raiz, 's1', 'src/x.spec.ts', "jest.mock('./x');\n", env)
    contexto = json.loads(r.stdout or '{}').get('hookSpecificOutput', {}).get('additionalContext', '')
    confere('jest.mock vira aviso, sem bloquear', r.returncode == 0 and 'jest.mock' in contexto, r.stdout)
    arquivo = raiz / 'src' / 'servico.ts'
    arquivo.write_text('console.log(1);\n')
    r = hook('lint_edicao.py', {'session_id': 's1', 'tool_name': 'Edit',
                                 'tool_input': {'file_path': str(arquivo), 'old_string': 'a', 'new_string': 'console.log(1);'}}, env)
    confere('console.log em src vira aviso', 'console.log' in r.stdout, r.stdout)
    r = escrever(raiz, 's1', 'src/main.ts', "console.log('rodando');\n", env)
    confere('console.log no main.ts não gera aviso', not r.stdout.strip(), r.stdout)
    r = escrever(raiz, 's1', 'src/desligado.ts', 'ERRO_LINT\n', {**env, 'SKILLDEV_LINT_EDICAO': 'off'})
    confere('SKILLDEV_LINT_EDICAO=off não bloqueia', r.returncode == 0, r.stderr)
    registro = Path(env['CLAUDE_PLUGIN_DATA']) / 'sessoes' / 's1.txt'
    confere('as edições ficam registradas na sessão', registro.exists() and 'desligado.ts' in registro.read_text())


def chamadas_jest(env):
    arquivo = Path(env['JEST_CALLS'])
    return len(arquivo.read_text().splitlines()) if arquivo.exists() else 0


def parar(sessao, env, ativo=False):
    return hook('portao_stop.py', {'session_id': sessao, 'hook_event_name': 'Stop', 'stop_hook_active': ativo}, env)


def testar_portao(raiz, env):
    print('== portao_stop')
    confere('sessão sem edição encerra', parar('s2', env).returncode == 0)
    escrever(raiz, 's2', 'src/ok.ts', 'export const ok = true;\n', env)
    antes = chamadas_jest(env)
    r = parar('s2', env)
    confere('edição limpa encerra e roda os testes', r.returncode == 0 and chamadas_jest(env) == antes + 1, r.stderr)
    r = parar('s2', env)
    confere('estado já aprovado não roda de novo', r.returncode == 0 and chamadas_jest(env) == antes + 1)
    escrever(raiz, 's2', 'src/quebrado.ts', 'ERRO_TESTE\n', env)
    r = parar('s2', env)
    confere('teste quebrado bloqueia com o motivo', r.returncode == 2 and 'Jest' in r.stderr, r.stderr)
    r = parar('s2', env, ativo=True)
    confere('mesmo estado de novo: encerra e avisa o usuário', r.returncode == 0 and 'systemMessage' in r.stdout, r.stdout)
    escrever(raiz, 's2', 'src/quebrado.ts', 'export const consertado = true;\n', env)
    confere('depois de corrigir, encerra', parar('s2', env).returncode == 0)
    (raiz / 'src' / 'do-usuario.ts').write_text('ERRO_LINT\n')
    confere('trabalho do usuário (não editado pelo Claude) não trava', parar('s2', env).returncode == 0)
    subprocess.run(['git', 'add', '-A'], cwd=raiz, check=True)
    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'x'], cwd=raiz, check=True)
    antes = chamadas_jest(env)
    escrever(raiz, 's3', 'src/ok.ts', 'export const ok = true;\n', env)  # mesmo conteúdo do commit: nada pendente
    r = parar('s3', env)
    confere('arquivo igual ao commit não é conferido', r.returncode == 0 and chamadas_jest(env) == antes)
    escrever(raiz, 's4', 'src/novo.ts', 'ERRO_TESTE\n', env)
    confere('SKILLDEV_PORTAO=off encerra', parar('s4', {**env, 'SKILLDEV_PORTAO': 'off'}).returncode == 0)


def git(raiz, *args):
    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=raiz, check=True, capture_output=True)


def testar_portao_commit(tmp):
    print('== portão de commit (impressão digital)')
    raiz = Path(tmp) / 'app'
    raiz.mkdir()
    teste = "node -e \"process.exit(require('fs').existsSync('QUEBRADO') ? 1 : 0)\""
    scripts = {'lint': 'node -e 0', 'build': 'node -e 0', 'test': teste}
    (raiz / 'package.json').write_text(json.dumps({'name': 'app', 'private': True, 'scripts': scripts}))
    (raiz / 'index.js').write_text('module.exports = 1;\n')
    git(raiz, 'init', '-q')
    git(raiz, 'add', '.')
    git(raiz, 'commit', '-qm', 'init')

    def commit(env_extra=None):
        entrada = {'tool_name': 'Bash', 'cwd': str(raiz), 'tool_input': {'command': 'git commit -m "feat: x"'}}
        return hook('guarda_comandos.py', entrada, env_extra)

    def verificar():
        return subprocess.run([sys.executable, '-B', str(PASTA_SCRIPTS / 'verificar.py'), str(raiz)], capture_output=True, text=True)

    r = commit()
    confere('sem verificação: commit barrado, dizendo o que rodar', r.returncode == 2 and 'verificar.py' in r.stderr, r.stderr)
    com_opcoes = {'tool_name': 'Bash', 'cwd': str(raiz), 'tool_input': {'command': 'git -c user.name=t -c user.email=t@t commit -m x'}}
    confere('opções do git antes do commit não escapam do portão', hook('guarda_comandos.py', com_opcoes).returncode == 2)
    pela_pasta_de_cima = {'tool_name': 'Bash', 'cwd': str(raiz.parent), 'tool_input': {'command': 'git -C app commit -m x'}}
    confere('git -C <pasta> confere o repositório da pasta', hook('guarda_comandos.py', pela_pasta_de_cima).returncode == 2)
    v = verificar()
    confere('verificação verde', v.returncode == 0, v.stdout + v.stderr)
    confere('código igual ao verificado: commit liberado', commit().returncode == 0)
    git(raiz, 'add', '-A')
    confere('git add depois da verificação não muda nada', commit().returncode == 0)
    (raiz / 'index.js').write_text('module.exports = 2;\n')
    r = commit()
    confere('código mudou depois da verificação: commit barrado', r.returncode == 2 and 'mudou' in r.stderr, r.stderr)
    confere('SKILLDEV_PORTAO_COMMIT=off libera', commit({'SKILLDEV_PORTAO_COMMIT': 'off'}).returncode == 0)
    (raiz / 'QUEBRADO').write_text('x')
    v = verificar()
    confere('teste quebrado: verificação falha', v.returncode == 1, v.stdout)
    r = commit()
    confere('verificação reprovada: commit barrado', r.returncode == 2 and 'falhou' in r.stderr, r.stderr)
    (raiz / 'QUEBRADO').unlink()
    sem_manifesto = Path(tmp) / 'docs'
    sem_manifesto.mkdir()
    git(sem_manifesto, 'init', '-q')
    (sem_manifesto / 'README.md').write_text('# docs\n')
    confere('repositório sem package.json: commit liberado', bash('git commit -m x', cwd=str(sem_manifesto)) == 0)


def main():
    testar_guarda()
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp) / 'projeto'
        montar_projeto(raiz)
        env = {'CLAUDE_PLUGIN_DATA': str(Path(tmp) / 'dados'), 'JEST_CALLS': str(Path(tmp) / 'jest-calls.txt')}
        testar_lint(raiz, env)
        testar_portao(raiz, env)
        testar_portao_commit(tmp)
    print('OK' if not falhas else f'{falhas} falha(s)')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
