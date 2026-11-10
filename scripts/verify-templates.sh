#!/usr/bin/env bash
# Confere os templates do nestjs-padrao num projeto Nest descartável: lint, prettier, build e testes.
# Uso: ./scripts/verify-templates.sh   (precisa do nest CLI 11 e de rede para o `yarn add`)
set -euo pipefail

command -v nest >/dev/null || { echo "Instale o nest CLI: yarn global add @nestjs/cli@11"; exit 1; }

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES="$REPO_DIR/skills/nestjs-padrao/templates"
WORK_DIR="$(mktemp -d)"
# KEEP=1 mantém o projeto descartável para investigar uma falha.
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$WORK_DIR"' EXIT

echo "==> nest new (em $WORK_DIR)"
cd "$WORK_DIR"
nest new app --package-manager yarn --skip-git --skip-install >/dev/null
cd app
rm -f src/app.controller.ts src/app.controller.spec.ts src/app.service.ts

echo "==> templates base + opcional"
cp -R "$TEMPLATES/." .
mv gitignore .gitignore
cp -R opcional/src/. src/
rm -rf opcional

echo "==> yarn"
yarn install --silent
yarn add --silent @nestjs/config@^4 @nestjs/swagger@^11 class-validator class-transformer @nestjs/jwt@^11

# Prettier antes e ESLint sem --fix (o `yarn lint` do Nest corrige sozinho e esconderia erro de formatação do template).
echo "==> prettier";     yarn --silent prettier --check 'src/**/*.ts' 'test/**/*.ts'
echo "==> eslint";       yarn --silent eslint '{src,test}/**/*.ts'
echo "==> build";        yarn --silent build
echo "==> test";         yarn --silent test 2>&1 | tail -5
echo "==> test:e2e";     yarn --silent test:e2e 2>&1 | tail -5
echo "==> OK"
