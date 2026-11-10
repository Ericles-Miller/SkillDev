"""Testa as regras do hookify contra comandos e edições de exemplo.

Cada regra roda sozinha, num projeto falso, pelo mesmo script que o plugin usa (hooks/pretooluse.py).
Regra com `enabled: false` é ligada só aqui, para poder ser testada.

Uso: python3 -I hookify/test_rules.py   (HOOKIFY_ROOT aponta para outro lugar do plugin, se precisar)
"""
import json
import os
import subprocess
import sys
import tempfile

RULES_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.environ.get(
    'HOOKIFY_ROOT',
    os.path.expanduser('~/.claude/plugins/marketplaces/claude-plugins-official/plugins/hookify'),
)


def bash(command):
    return {'tool_name': 'Bash', 'tool_input': {'command': command}}


def write(file_path, content):
    return {'tool_name': 'Write', 'tool_input': {'file_path': file_path, 'content': content}}


def edit(file_path, new_string):
    return {'tool_name': 'Edit', 'tool_input': {'file_path': file_path, 'old_string': 'x', 'new_string': new_string}}


CASES = {
    'hookify.block-npm.local.md': [
        (bash('npm install'), 'deny'),
        (bash('cd api && npm run build'), 'deny'),
        (bash('npm'), 'deny'),
        (bash('yarn lint\nnpm test'), 'deny'),
        (bash('(npm ci)'), 'deny'),
        (bash('yarn test'), 'allow'),
        (bash('pnpm i'), 'allow'),
        (bash('npx tsc --noEmit'), 'allow'),
        (bash('yarn global add typescript'), 'allow'),
        (bash("git commit -m 'chore: drop npm lockfile'"), 'allow'),
        (bash('cat package-lock.json'), 'allow'),
    ],
    'hookify.block-push-protected.local.md': [
        (bash('git push origin main'), 'deny'),
        (bash('git push origin develop'), 'deny'),
        (bash('git push origin HEAD:main'), 'deny'),
        (bash('git push --force'), 'deny'),
        (bash('git push -f origin MS-61'), 'deny'),
        (bash('git push -u origin MS-61'), 'allow'),
        (bash('git push --force-with-lease origin MS-61'), 'allow'),
        (bash('git push origin feature/main-menu'), 'allow'),
        (bash('git checkout main && git pull'), 'allow'),
    ],
    'hookify.block-git-commit.local.md': [
        (bash("git commit -m 'feat(MS-61): add screens'"), 'deny'),
        (bash('git add . && git commit -m wip'), 'deny'),
        (bash('git -C api commit -m wip'), 'deny'),
        (bash('git merge develop'), 'deny'),
        (bash('git push -u origin MS-61'), 'deny'),
        (bash('git status'), 'allow'),
        (bash('git log --oneline -5'), 'allow'),
        (bash('git diff HEAD'), 'allow'),
        (bash("echo 'run git commit later'"), 'allow'),
    ],
    'hookify.warn-jest-mock.local.md': [
        (write('/p/src/charges/charges.service.spec.ts', "jest.mock('./charges.repository');"), 'warn'),
        (edit('/p/src/charges/charges.service.spec.ts', "jest.mock('axios');"), 'warn'),
        (write('/p/src/charges/charges.service.spec.ts', 'const repository = new InMemoryChargesRepository();'), 'allow'),
        (write('/p/src/charges/charges.service.ts', '// jest.mock( não vale fora de teste'), 'allow'),
    ],
    'hookify.warn-console-log.local.md': [
        (write('/p/src/charges/charges.service.ts', "console.log('charge', charge);"), 'warn'),
        (edit('/p/src/charges/charges.service.ts', 'console.debug(payload);'), 'warn'),
        (write('/p/src/main.ts', "await app.listen(3000, () => console.log('running'));"), 'allow'),
        (write('/p/src/charges/charges.service.spec.ts', 'console.log(result);'), 'allow'),
        (write('/p/scripts/seed.ts', "console.log('seeded');"), 'allow'),
        (write('/p/src/charges/charges.service.ts', "this.logger.log('charge created');"), 'allow'),
    ],
}


def run_hook(project_dir, case):
    payload = json.dumps({'hook_event_name': 'PreToolUse', **case})
    proc = subprocess.run(
        ['python3', os.path.join(PLUGIN_ROOT, 'hooks', 'pretooluse.py')],
        input=payload,
        capture_output=True,
        text=True,
        cwd=project_dir,
        env={**os.environ, 'CLAUDE_PLUGIN_ROOT': PLUGIN_ROOT},
    )
    out = json.loads(proc.stdout or '{}')
    if out.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny':
        return 'deny'
    if 'Hookify' in out.get('systemMessage', '') and 'error' in out.get('systemMessage', ''):
        return 'error: ' + out['systemMessage']
    return 'warn' if out.get('systemMessage') else 'allow'


def main():
    missing = sorted(set(f for f in os.listdir(RULES_DIR) if f.endswith('.local.md')) - set(CASES))
    if missing:
        print('Regra sem casos de teste: ' + ', '.join(missing))
        return 1

    failures = 0
    for rule_file, cases in CASES.items():
        print(f'== {rule_file}')
        with tempfile.TemporaryDirectory() as project_dir:
            os.makedirs(os.path.join(project_dir, '.claude'))
            with open(os.path.join(RULES_DIR, rule_file), encoding='utf-8') as source:
                rule = source.read().replace('enabled: false', 'enabled: true', 1)
            with open(os.path.join(project_dir, '.claude', rule_file), 'w', encoding='utf-8') as target:
                target.write(rule)

            for case, expected in cases:
                got = run_hook(project_dir, case)
                ok = got == expected
                failures += not ok
                subject = case['tool_input'].get('command') or case['tool_input']['file_path']
                print(f"  {'OK ' if ok else 'ERR'} {subject!r:60} → {got}" + ('' if ok else f' (esperado: {expected})'))

    print('OK' if not failures else f'{failures} falha(s)')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
