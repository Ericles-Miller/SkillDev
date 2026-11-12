---
name: figma-para-codigo
description: Implementa telas em código a partir de um desenho do Figma que já existe (feito por designer, protótipo do Figma Make ou aprovado pelo método telas-figma), em mobile (Flutter) e web (Next.js/React). Cobre o inventário do arquivo, o confronto do desenho com os docs, o backend e o Design System, o plano de front e back, a implementação usando os tokens e componentes do projeto (nunca valores copiados do Figma) e a comparação visual com os quadros. Use quando o designer entregar o Figma, quando pedirem para implementar, seguir, analisar ou portar um desenho, protótipo ou link do Figma, ou para saber por onde começar com um Figma pronto.
---

# Do Figma para o código

O Figma é a intenção; o Design System do código é a implementação; o backend real é o contrato dos dados. O desenho diz como a tela deve parecer. Ele não decide cor solta, campo que o backend não tem, nem dado de demonstração.

Os modelos de inventário, confronto, plano, mapa de tokens e fechamento estão em [references/modelos.md](references/modelos.md).

## Ler o Figma

- Tudo passa pelo Figma MCP. Comece com `create_session` usando o `fileKey` do link.
- Antes de qualquer `get_design_context`, carregue a skill `figma:figma-design-to-code` e siga as regras dela:
  - Peça o screenshot junto. Ele é o alvo visual, nunca um asset da tela.
  - Resposta "sparse": peça os nós filhos.
  - Assets: baixe exatamente os do desenho.
- Arquivo Design (`figma.com/design/...`) e arquivo Make (`figma.com/make/...`) se leem de jeitos diferentes. Veja a seção "Conector" dos modelos.
- Só leia. Não escreva no Figma (`use_figma`, `generate_figma_design`): quem desenha é o designer ou o First Draft.

## Uma vez por arquivo do Figma, antes da primeira tela

1. **Inventário:** liste páginas e quadros (`get_metadata`) e monte a tabela de telas, variantes (mobile e web), temas e estados, com o `node-id` de cada quadro. Liste também as variáveis (`get_variable_defs`) e os componentes da biblioteca.
2. **Confronto:**
   - **Docs do projeto:** o que o desenho cobre, o que falta e o que contradiz. Os docs vencem o desenho, e cada contradição vira uma pergunta ao usuário.
   - **Backend:** cada dado da tela cai num de quatro grupos:
     - já existe;
     - dá para calcular no front;
     - falta no backend, mas é viável;
     - não existe em lugar nenhum: sai da tela, ou o usuário decide o que fazer.
   - **Design System:** cada variável do Figma ganha o token de código correspondente. O ideal é o mesmo nome. Variável sem token, ou valor diferente, é uma decisão: adotar no código ou tratar como desvio do desenho.
   - **Componentes:** cada componente do Figma ganha o componente de código correspondente. O que falta é criado primeiro no Design System.
3. **Plano** (`docs/front/PLANO_<desenho>.md`):
   - Tasks de backend (B1, B2...) e de frontend (F1, F2...).
   - Decisões pendentes e o que fica de fora.
   - O efeito nas tasks que já existem no Jira: as que perderam o sentido, as que contradizem o plano, as que seguem sem conflito e os itens que ainda não têm task.
   - As decisões são perguntadas antes de abrir as tasks, com a skill `jira-task`.

Um protótipo que ainda não foi aprovado é referência, não especificação. Ele serve para o inventário e o confronto, mas não vira código.

## Por tela

1. **Task e aprovação.** A task (aberta com a `jira-task` e trabalhada com a `executar-task`) traz o link e o `node-id` dos quadros aprovados: cada variante, tema e estado. Sem aprovação registrada, pergunte antes de implementar.
2. **Leia os quadros** de todas as variantes, temas e estados, seguindo a `figma:figma-design-to-code`. Se o quadro tiver animação, siga também a skill `figma:figma-implement-motion`.
3. **Implemente:**
   - **Tokens, não valores.** Cor, fonte, espaço e raio saem dos tokens do projeto. Valor do Figma sem token correspondente: pergunte. Se for aprovado, o token entra primeiro no Design System (código e doc, nos dois temas) e só depois na tela.
   - **Componentes do Design System primeiro.** O que faltar vira componente do Design System, com aprovação. Nunca um componente de uso único escondido dentro da tela.
   - **Layout nativo** (flex/grid na web, Row/Column/LayoutBuilder no Flutter). Nada de posição absoluta copiada do Figma, salvo quando o desenho só existe assim.
   - **Dados reais** do endpoint e do DTO da task. Dado de demonstração do protótipo nunca vai para o código.
   - **Todos os estados** desenhados (padrão, carregando, vazio, erro, desabilitado, sucesso), com os textos do desenho no idioma do produto.
   - **Responsivo e acessível:**
     - Web: até 320 px sem rolagem horizontal.
     - Mobile: os breakpoints do Design System.
     - Contraste de 4,5:1 ou mais, foco visível, estado sempre com rótulo em texto (nunca só cor) e alvo de toque de 48dp ou mais.
4. **Siga as regras da stack** (seções abaixo).
5. **Compare com o desenho:** o screenshot de cada estado, em cada variante e tema, lado a lado com o quadro do mesmo estado.
   - Divergência só se ficar registrada na task, com o motivo: limite técnico, contraste, regra do backend ou conflito com os docs.
   - Divergência grande: pare e pergunte antes de seguir.
6. **Feche** com o comentário da `executar-task`, mais o bloco de comparação dos modelos.

## Web (Next.js / React)

- Os tokens ficam no CSS global (ex.: `globals.css` com `@theme`), com claro e escuro. Os componentes ficam em `src/components/ui/`.
- **Nenhuma cor solta na tela.** O tema escuro vem dos tokens, não do `dark:` do Tailwind. Esta busca tem que voltar vazia:
  ```bash
  grep -rnE "#[0-9a-fA-F]{3,8}\b|rgba?\(|zinc-|slate-|gray-|black/|white/|red-[0-9]|green-[0-9]|blue-[0-9]|amber-|emerald-|dark:" src --include='*.tsx' --include='*.ts'
  ```
- **Verificação:**
  - `yarn lint` e `yarn build`.
  - Playwright contra o backend real, com screenshot de cada estado no claro e no escuro, no desktop e em 320 px.
  - O Playwright e os scripts ficam fora do repositório.

## Mobile (Flutter)

- O tema é central: um `ThemeData` com Material 3, o `ColorScheme` do Design System (ex.: `ColorScheme.fromSeed`) e o `TextTheme` com a fonte do projeto. O tema escuro sai do mesmo lugar.
- **Na tela, só `Theme.of(context).colorScheme` e `textTheme`.** Nada de `Color(0x...)`, `Colors.*` ou `TextStyle` montado à mão. Esta busca, fora do arquivo de tema, tem que voltar vazia:
  ```bash
  grep -rnE "Color\(0x|Colors\.[a-z]|fontSize:|fontFamily:" lib --include='*.dart' | grep -v -E "theme/|Colors\.transparent"
  ```
- Os widgets reutilizáveis do Design System ficam numa pasta própria (ex.: `lib/core/widgets/`), e as telas os compõem.
- Breakpoints do Design System com `LayoutBuilder` ou `MediaQuery`: Compact, Medium e Expanded. A variante Web do desenho é a Expanded.
- **Verificação:**
  - `flutter analyze` e `flutter test`, com widget test de cada estado.
  - Comparação visual por golden test (`matchesGoldenFile`) ou por screenshot no simulador. Use o simulador iOS pelo controle do simulador quando ele estiver disponível.

## Nunca

- Copiar cor, fonte ou medida do Figma para o código.
- Levar dado de demonstração do protótipo para o código.
- Implementar um desenho sem aprovação registrada.
- Deixar o desenho vencer os docs ou o contrato do backend sem perguntar.
- Escrever no Figma.
