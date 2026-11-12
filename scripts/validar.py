"""Valida o marketplace, os plugins, as skills, os agentes e os hooks do SkillDev.

Pega o que quebra em silêncio: nome de agente que mudou e ninguém atualizou a chamada, revisor que ganhou uma
ferramenta de escrita, regra crítica apagada do texto de uma skill, script de hook que não existe mais.

Uso: python3 -I -B scripts/validar.py
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MAX_LINHAS_AGENTE = 200  # agente maior que isso está carregando o que devia estar numa skill ou num script
AGENTES_SO_LEITURA = {'revisor-task', 'revisor-codigo', 'planejador'}
FERRAMENTAS_DE_ESCRITA = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit', 'Bash'}
ESCRITA_NO_JIRA = re.compile(r'__(create|edit|update|transition|add|delete)', re.IGNORECASE)
PREFIXOS_JIRA = ('mcp__claude_ai_Atlassian_Rovo__', 'mcp__1bf8bdd4-ea4f-4a42-b08c-4946ecfc0ebd__')
# Regras que, se sumirem do texto, mudam o comportamento sem ninguém perceber.
TRAVAS_DE_TEXTO = {
    'plugins/base/skills/regua-revisao/SKILL.md': ['BLOQUEIA', 'alguém precisa decidir', 'Veredito'],
    'plugins/base/skills/jira-task/SKILL.md': ['Definition of Ready', 'Dado / Quando / Então', 'Pré-mortem', 'Triagem antes de perguntar'],
    'plugins/base/skills/executar-task/SKILL.md': ['Prova por reversão', 'verificar.py', 'plano-v1'],
    'plugins/base/skills/planejar-task/SKILL.md': ['plano-v1'],
    'plugins/base/agents/planejador.md': ['plano-v1'],
}

erros = []


def erro(mensagem):
    erros.append(mensagem)
    print(f'ERR {mensagem}')


def frontmatter(arquivo: Path) -> dict:
    texto = arquivo.read_text(encoding='utf-8')
    if not texto.startswith('---\n'):
        return {}
    bloco = texto.split('---\n', 2)[1]
    dados, chave_lista = {}, None
    for linha in bloco.splitlines():
        item = re.match(r'\s+-\s+(.+)$', linha)
        if item and chave_lista:
            dados[chave_lista].append(item.group(1).strip())
            continue
        par = re.match(r'([\w-]+):\s*(.*)$', linha)
        if par:
            chave, valor = par.group(1), par.group(2).strip()
            if valor:
                dados[chave], chave_lista = valor, None
            else:
                dados[chave], chave_lista = [], chave
    return dados


def lista(valor) -> list:
    return valor if isinstance(valor, list) else [v.strip() for v in str(valor).split(',') if v.strip()]


def validar_marketplace() -> list:
    marketplace = json.loads((RAIZ / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    plugins = []
    for entrada in marketplace.get('plugins', []):
        pasta = (RAIZ / entrada['source']).resolve()
        manifesto = pasta / '.claude-plugin' / 'plugin.json'
        if not manifesto.exists():
            erro(f'plugin {entrada["name"]}: sem {manifesto.relative_to(RAIZ)}')
            continue
        nome = json.loads(manifesto.read_text(encoding='utf-8')).get('name')
        if nome != entrada['name']:
            erro(f'plugin {entrada["name"]}: o plugin.json diz "{nome}"')
        if (pasta / 'commands').exists():
            erro(f'plugin {nome}: pasta commands/ (formato antigo; use skills)')
        plugins.append((nome, pasta))
    return plugins


def validar_skills(nome_plugin: str, pasta: Path) -> None:
    for skill in sorted((pasta / 'skills').glob('*/SKILL.md')):
        dados = frontmatter(skill)
        if dados.get('name') != skill.parent.name:
            erro(f'{skill.relative_to(RAIZ)}: name "{dados.get("name")}" diferente da pasta')
        if not dados.get('description'):
            erro(f'{skill.relative_to(RAIZ)}: sem description')
        for alvo in re.findall(r'subagent_type:\s*"([\w-]+):([\w-]+)"', skill.read_text(encoding='utf-8')):
            if not (RAIZ / 'plugins' / alvo[0] / 'agents' / f'{alvo[1]}.md').exists():
                erro(f'{skill.relative_to(RAIZ)}: chama o agente {alvo[0]}:{alvo[1]}, que não existe')


def validar_agentes(nome_plugin: str, pasta: Path) -> None:
    for agente in sorted((pasta / 'agents').glob('*.md')):
        dados = frontmatter(agente)
        relativo = agente.relative_to(RAIZ)
        if dados.get('name') != agente.stem:
            erro(f'{relativo}: name "{dados.get("name")}" diferente do arquivo')
        if not dados.get('description'):
            erro(f'{relativo}: sem description')
        linhas = len(agente.read_text(encoding='utf-8').splitlines())
        if linhas > MAX_LINHAS_AGENTE:
            erro(f'{relativo}: {linhas} linhas (máximo {MAX_LINHAS_AGENTE})')
        ferramentas = lista(dados.get('tools', ''))
        if agente.stem in AGENTES_SO_LEITURA:
            for ferramenta in ferramentas:
                if ferramenta in FERRAMENTAS_DE_ESCRITA or ESCRITA_NO_JIRA.search(ferramenta):
                    erro(f'{relativo}: agente só leitura com a ferramenta de escrita {ferramenta}')
        jira = {f.split('__')[-1] for f in ferramentas if f.startswith(PREFIXOS_JIRA)}
        for nome_ferramenta in jira:
            for prefixo in PREFIXOS_JIRA:
                if prefixo + nome_ferramenta not in ferramentas:
                    erro(f'{relativo}: falta {prefixo}{nome_ferramenta} (a ferramenta precisa dos dois nomes, CLI e app)')
        for skill in lista(dados.get('skills', [])):
            plugin, _, nome = skill.partition(':')
            if not (RAIZ / 'plugins' / plugin / 'skills' / nome / 'SKILL.md').exists():
                erro(f'{relativo}: pré-carrega a skill {skill}, que não existe')


def validar_hooks(pasta: Path) -> None:
    arquivo = pasta / 'hooks' / 'hooks.json'
    if not arquivo.exists():
        return
    for grupos in json.loads(arquivo.read_text(encoding='utf-8'))['hooks'].values():
        for grupo in grupos:
            for hook in grupo['hooks']:
                for caminho in re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)', hook['command']):
                    if not (pasta / caminho).exists():
                        erro(f'{arquivo.relative_to(RAIZ)}: o hook chama {caminho}, que não existe')


def validar_travas() -> None:
    for caminho, trechos in TRAVAS_DE_TEXTO.items():
        texto = (RAIZ / caminho).read_text(encoding='utf-8')
        for trecho in trechos:
            if trecho not in texto:
                erro(f'{caminho}: sumiu o trecho obrigatório "{trecho}"')


def main() -> int:
    plugins = validar_marketplace()
    for nome, pasta in plugins:
        validar_skills(nome, pasta)
        validar_agentes(nome, pasta)
        validar_hooks(pasta)
    validar_travas()
    print(f'{len(plugins)} plugins conferidos: ' + ('OK' if not erros else f'{len(erros)} erro(s)'))
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main())
