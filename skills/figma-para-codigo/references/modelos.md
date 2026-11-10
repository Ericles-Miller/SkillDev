# Modelos

Tirados do projeto da usina, onde o caminho inverso aconteceu de verdade:
- O designer desenhou as telas de autenticação e de usinas no Figma, e elas foram implementadas a partir do desenho (MS-71, MS-72).
- Os protótipos do Figma Make foram analisados e viraram um plano de front e back (`solar-monitor-web/docs/front/10-PROTOTIPOS_FIGMA_A_B.md` e `11-PLANO_FRONT_E_BACK_PROTOTIPO_B.md`).
- As regras de "Figma para código" estão no `09-FLUXO_FIGMA.md`, seções 5 a 7.

## 1. Inventário do arquivo

Vai no início do `docs/front/PLANO_<desenho>.md`:

```markdown
## Inventário — <nome do arquivo> (lido pelo Figma MCP em DD/MM/AAAA)

Arquivo: <link> · Tipo: Design | Make · Aprovado: sim (DD/MM/AAAA) | não (referência)

| Fluxo | Tela | Variante | Tema | Estado | Quadro | node-id |
|---|---|---|---|---|---|---|
| Auth | Login | Mobile | Claro | padrão | Tela/Auth/Login/Mobile | 108:210 |

**Variáveis:** <coleções e modos, ex.: Cores (Claro, Escuro), Espaço, Raio>
**Componentes da biblioteca:** <Button (variantes), Card, Input...>
**Dados de demonstração no desenho:** <o que é fictício e não pode ir para o código>
```

## 2. Confronto

```markdown
## Cobertura dos docs
| O que os docs exigem | Onde está no desenho | Situação |
|---|---|---|
| <regra ou tela do doc> | <quadro> | coberto · falta · contradiz (os docs vencem) |

## Backend: de onde vem cada dado
### Já existe (só falta o front consumir)
- <dado> → `<VERBO /rota>` (`<campo do DTO>`)
### Dá para calcular no front
- <dado> → <cálculo a partir de quê>
### Falta no backend (viável)
- <dado> → <endpoint ou campo novo> → task B<n>
### Não existe em lugar nenhum
- <dado> → sai da tela | decisão do usuário

## Design System
| Variável do Figma | Token no código | Claro | Escuro | Situação |
|---|---|---|---|---|
| `primary` | `--primary` / `colorScheme.primary` | #267355 | #72c39b | igual · valor diferente · sem token |

## Componentes
| Componente do Figma | Componente no código | Situação |
|---|---|---|
| Button / primary / md | `ui/Button` (`variant="primary" size="md"`) | existe · falta (criar no Design System) |
```

## 3. Plano de ação

```markdown
## Backend
### B1. <título> (<CHAVE>-XX ou "sem task")
<o que muda, por quê, critério de pronto>

## Frontend
### F1. <título> (<CHAVE>-XX ou "sem task")
<telas, componentes, dependências de B<n>>

## Decisões pendentes (usuário)
1. <pergunta, opções e recomendação>

## Fora deste plano
- <o que foi discutido e ficou de fora, e por quê>

## Tasks do Jira em relação a este plano
- **Perderam o sentido (candidatas a fechar):** <CHAVE>-XX
- **A premissa contradiz o plano (reescrever):** <CHAVE>-XX
- **Sem conflito:** <CHAVE>-XX
- **Itens do plano sem task:** B<n>, F<n>
```

## 4. Mapa de tokens

Quando o Figma e o código usam os mesmos nomes, o mapeamento é mecânico. É o que a usina fez: variável `primary` no Figma = token `--primary` no CSS, com os modos Claro e Escuro.

| Figma | Web (Next + Tailwind) | Mobile (Flutter) |
|---|---|---|
| Variável de cor `primary` | `--primary` em `globals.css` → `bg-primary` | `Theme.of(context).colorScheme.primary` |
| Modo `Claro` / `Escuro` | `:root` e `[data-theme=dark]` (ou `prefers-color-scheme`) | `theme` e `darkTheme` do `MaterialApp` |
| Estilo de texto `title` | utilitário de texto do projeto (ex.: `text-title`) | `textTheme.titleLarge` |
| Espaço 16 | escala do projeto (ex.: `p-4`) | constante de espaço do Design System (ex.: `Spacing.md`) |
| Raio 16 (cartão) | `rounded-card` / token do projeto | `shape` do `CardTheme` |
| Componente `Button` | `src/components/ui/Button` | widget do Design System (ex.: `AppButton`) |

Valor do Figma sem linha nesta tabela é uma pergunta, não um `#hex` no código.

## 5. Checklist por tela

- [ ] Quadros aprovados (`node-id` de cada variante, tema e estado) na task.
- [ ] Os dados vêm do endpoint e do DTO reais; nenhum dado de demonstração.
- [ ] Só tokens e componentes do Design System. A busca de cor solta voltou vazia.
- [ ] Todos os estados do desenho implementados, com os textos do desenho.
- [ ] Responsivo (web até 320 px; mobile nos breakpoints) e nos dois temas, se houver.
- [ ] Contraste, foco visível, rótulo em texto e alvo de toque conferidos.
- [ ] Comparação lado a lado com cada quadro; divergências registradas.
- [ ] Lint, build e testes passando (web: Playwright; mobile: `flutter analyze`, `flutter test` e golden).

## 6. Fechamento da tela

Acrescente ao comentário de fechamento da skill `executar-task`:

```markdown
**Comparação com o desenho:** <estados comparados, em cada variante e tema>
**Divergências do desenho:** <o que mudou e por quê, ou "nenhuma">
**Novo no Design System:** <token ou componente criado com aprovação, ou "nada">
```

## 7. Conector (Figma MCP)

- **Arquivo Design** (`figma.com/design/<fileKey>/...?node-id=1-2`):
  - `get_metadata` sem `nodeId` lista as páginas.
  - `get_design_context` e `get_screenshot` pedem o `node-id` do quadro, e `1-2` vira `1:2`.
  - As variáveis vêm do `get_variable_defs`.
- **Arquivo Make** (`figma.com/make/<fileKey>/...`):
  - `get_design_context` com `nodeId` = `0:1` devolve a lista dos arquivos-fonte do protótipo (React/HTML, CSS, imagens).
  - Cada arquivo se lê pela leitura de recurso MCP (`file://figma/make/source/<fileKey>/<caminho>`).
  - `get_metadata` e `get_screenshot` não funcionam em arquivo Make.
  - O código do Make é referência de comportamento, não código para copiar.
- **Licença:** o limite de chamadas do MCP vale por pessoa e por seat. Um seat View ou Collab faz poucas chamadas por mês; o uso real pede seat Dev ou Full num plano pago. Reconfirme os limites, porque eles mudam.
- **Sem conector:** peça o link e as imagens exportadas de cada quadro (variantes, temas e estados) e pergunte as medidas que ficarem em dúvida. O resultado é menos fiel; registre isso na task.
- **Segredo:** o token de acesso do Figma nunca vai para chat, doc, comentário de Jira ou commit.
