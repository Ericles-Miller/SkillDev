---
name: block-npm
enabled: true
event: bash
pattern: (^|[;&|(\n]\s*)npm(\s|$)
action: block
---

🛑 **npm bloqueado: neste projeto é só yarn.**

Troque o comando pelo equivalente em yarn:
- `npm install` → `yarn`
- `npm install <pacote>` → `yarn add <pacote>` (`-D` para dev)
- `npm run <script>` → `yarn <script>`
- `npm install -g <pacote>` → `yarn global add <pacote>`
