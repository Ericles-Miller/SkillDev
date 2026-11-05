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
