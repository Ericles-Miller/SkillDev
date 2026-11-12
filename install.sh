#!/usr/bin/env bash
# Liga o ~/.claude a este repositório: o CLAUDE.md global e os plugins do marketplace skilldev.
# Pode rodar de novo sem problema.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
# O backup fica fora de ~/.claude/skills: uma cópia antiga lá dentro seria lida como uma skill a mais.
BACKUP_DIR="$CLAUDE_DIR/backup-claude-config-$(date +%Y%m%d%H%M%S)"
# Valem em todo projeto. O plugin `front` é ligado só nos projetos com telas (skill iniciar-projeto).
USER_PLUGINS=(base nestjs)

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

echo "==> Limpeza do formato antigo"
# Antes dos plugins, cada skill e cada agente tinha um link próprio em ~/.claude. Se ficassem, cada skill
# apareceria duas vezes (com e sem o prefixo do plugin). As regras do hookify viraram hooks do plugin base.
for old in "$CLAUDE_DIR"/skills/* "$CLAUDE_DIR"/agents/* "$CLAUDE_DIR"/hookify; do
  [ -L "$old" ] || continue
  case "$(readlink "$old")" in
    "$REPO_DIR"/skills/* | "$REPO_DIR"/agents/* | "$REPO_DIR"/hookify) rm "$old" && echo "    removido: $old" ;;
  esac
done

echo "==> Marketplace skilldev (lido direto desta pasta: editar aqui vale na próxima sessão)"
current="$(claude plugin marketplace list --json | jq -r '.[] | select(.name == "skilldev") | .path // .repo // empty')"
if [ "$current" != "$REPO_DIR" ]; then
  [ -n "$current" ] && claude plugin marketplace remove skilldev
  claude plugin marketplace add "$REPO_DIR"
else
  echo "    já aponta para $REPO_DIR"
fi
for plugin in "${USER_PLUGINS[@]}"; do
  claude plugin install "$plugin@skilldev"
done

echo "==> Plugins de terceiros"
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
