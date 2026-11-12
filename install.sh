#!/usr/bin/env bash
# Liga o ~/.claude a este repositório por symlink. Pode rodar de novo sem problema.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
# O backup fica fora de ~/.claude/skills: uma cópia antiga lá dentro seria lida como uma skill a mais.
BACKUP_DIR="$CLAUDE_DIR/backup-claude-config-$(date +%Y%m%d%H%M%S)"

# Faz backup do que já existe (se não for symlink) e cria o link para o repo.
link() {
  local src="$REPO_DIR/$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    mkdir -p "$BACKUP_DIR"
    mv "$dst" "$BACKUP_DIR/"
    echo "    backup: $BACKUP_DIR/$(basename "$dst")"
  fi
  ln -sfn "$src" "$dst"
  echo "    $dst -> $src"
}

echo "==> CLAUDE.md global"
link CLAUDE.md "$CLAUDE_DIR/CLAUDE.md"

echo "==> Skills"
for skill in "$REPO_DIR"/skills/*/; do
  name="$(basename "$skill")"
  link "skills/$name" "$CLAUDE_DIR/skills/$name"
done

echo "==> Agentes"
for agent in "$REPO_DIR"/agents/*.md; do
  name="$(basename "$agent")"
  link "agents/$name" "$CLAUDE_DIR/agents/$name"
done

echo "==> Regras do hookify (copiadas para o .claude/ de cada projeto)"
link hookify "$CLAUDE_DIR/hookify"

echo "==> Plugins"
# Instalar um plugin que já está instalado não muda nada.
while read -r plugin; do
  [ -n "$plugin" ] && claude plugin install "$plugin"
done < "$REPO_DIR/plugins.txt"

echo "==> TypeScript language server (usado pelo typescript-lsp)"
# A 6.x pede Node >= 22.22; a 5.3.0 roda no Node 22.19 desta máquina.
# O --prefix põe o binário na pasta do Node ativo, que está no PATH (o ~/.yarn/bin não está).
if command -v typescript-language-server >/dev/null; then
  echo "    já instalado: $(typescript-language-server --version)"
else
  yarn global add typescript-language-server@5.3.0 typescript@5.7 --prefix "$(dirname "$(dirname "$(command -v node)")")"
fi
