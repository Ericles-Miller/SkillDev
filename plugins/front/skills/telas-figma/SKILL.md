---
name: telas-figma
description: Método para especificar, desenhar e implementar telas com o Figma First Draft, o mesmo do projeto calhas. Cobre o Design System Base, o mapa de fluxos tirado do backend real, a Ficha de Tela no Jira com os campos espelhando o DTO, o prompt pronto para o First Draft (mobile e web), a aprovação do desenho e a implementação lendo o Figma. Use quando o desenho ainda não existe: para planejar as telas de um módulo, abrir a task de uma tela ou escrever o prompt do Figma. Se o desenho já existe (designer, protótipo), use a skill figma-para-codigo.
---

# Telas com Figma First Draft

Tela gerada no Figma a partir de uma ideia vaga sai com layout genérico, campo inventado e cara diferente das outras telas. Por isso toda tela passa por três camadas, sempre nesta ordem:

```
Camada 1                  Camada 2                  Camada 3
Design System Base   →    Ficha de Tela        →    Prompt do First Draft
(uma vez por projeto)     (uma por tela, no Jira)   (dentro da Ficha, pronto para colar)
```

Os modelos de cada documento, com exemplos reais, estão em [references/modelos.md](references/modelos.md).

## Quem faz o quê

| Quem | Faz |
|---|---|
| Claude | Mapeia os fluxos, escreve a Ficha e os prompts, implementa a partir do desenho aprovado e compara a tela com ele. Não desenha nem decide o visual. |
| Quem opera o Figma | Cola o prompt no First Draft, ajusta os quadros e entrega o link. |
| Usuário | Decide o Design System e aprova cada desenho antes de virar código. |

## Uma vez por projeto, antes da primeira tela

1. **Design System Base** (`docs/front/DESIGN_SYSTEM_BASE.md`): cor, fonte, temas, grid, breakpoints, componentes base, tamanho dos frames e o **cabeçalho fixo do prompt**.
   - São decisões do usuário. Mostre opções reais lado a lado, como a página "Paleta e Tipografia" do calhas, e registre a escolha com a data.
   - Depois de decidido, não se reabre por tela.
2. **Fluxo Mestre** (`docs/front/FLUXO_MESTRE.md`): para onde cada papel vai depois do login e o que muda no menu de cada um.
   - Tire isso dos guards e decorators de papel do código, não do doc de requisitos. No calhas, o doc de papéis tinha um papel que o código não tinha.
3. **Um fluxo por módulo** (`docs/front/FLUXO_<MODULO>.md`), antes de qualquer tela do módulo: as telas, o endpoint e os campos de cada uma, de onde vem e para onde vai, e as regras de negócio. Sempre lido do backend real: controllers, DTOs e enums.
4. **Pendências técnicas** (`docs/PENDENCIAS_TECNICAS.md`, o da skill `iniciar-projeto`): toda falha de backend achada no mapeamento, como endpoint que falta, validação que falta ou código que contradiz o Swagger. Tela que depende de uma pendência aberta fica bloqueada até a task de backend ser entregue.

## Por tela

1. **Confira o terreno.** O módulo já tem fluxo mapeado? Alguma pendência aberta bloqueia esta tela? Se bloqueia, a task de backend vem primeiro.
2. **Escreva a Ficha de Tela** e abra a task com a skill `jira-task`.
   - Os campos da tela espelham o DTO do backend: nome, tipo, obrigatoriedade e aninhamento.
   - Textos, estados e papéis são decisões: são perguntados antes de abrir a task, como toda decisão.
3. **Escreva os prompts**, um para Mobile e um para Web, na fórmula fixa e começando pelo cabeçalho do Design System. Eles vão na própria Ficha, prontos para colar.
4. **Desenho.** Quem opera o Figma cola o prompt no First Draft, revisa com a checklist da Ficha e ajusta à mão.
   - Um fluxo com muitas etapas ou condições difíceis de descrever pode ser validado antes no Figma Make. A versão oficial sai do First Draft, porque o Make tende a ignorar os componentes do design system.
5. **Aprovação.** O usuário aprova, e a task recebe um comentário com o link do arquivo e o `node-id` de cada quadro aprovado. **Desenho sem aprovação registrada não vira código.**
6. **Implementação e verificação:** siga a skill `figma-para-codigo`, seção "Por tela", junto com a `executar-task`. Ela cobre:
   - a leitura dos quadros aprovados pelo Figma MCP;
   - o uso dos tokens e componentes do projeto, nunca de valores copiados do Figma;
   - as regras de web e de Flutter;
   - a comparação visual com os quadros.

   O endpoint e o DTO consumidos são os da Ficha.

## Regras

- Não desenhe no Figma pelo conector (`use_figma`, `generate_figma_design`, skill `figma:figma-use`). No método, quem desenha é o First Draft, operado por uma pessoa; o conector serve para ler o desenho aprovado. Se pedirem para "desenhar a tela", entregue a Ficha e o prompt.
- Não invente campo. Se a tela precisa de um campo que o DTO não tem, é uma pendência de backend, não uma liberdade de design.
- Cada tela tem duas variantes, Mobile e Web. Tablet só ganha desenho próprio quando a tela muda de forma (uma lista que vira lista + detalhe lado a lado), não só de tamanho.
- Nenhuma cor ou fonte solta na tela: tudo vem do tema central.
- Os textos da interface são os reais, no idioma do produto, e já vão no prompt.
- Regra de papel ambígua não se resolve na tela. Se não está clara, é a Ficha que está incompleta: pergunte.

## Checklist da Ficha

- [ ] O módulo tem fluxo mapeado, e nenhuma pendência aberta bloqueia a tela.
- [ ] Objetivo, fluxo de navegação, variantes, estados, papéis, regras e textos preenchidos.
- [ ] A tabela de campos espelha o DTO, com o endpoint.
- [ ] Há um prompt para Mobile e um para Web, os dois começando pelo cabeçalho do Design System.
- [ ] A checklist de colagem traz o tamanho e o nome dos frames.
- [ ] Nenhuma decisão em aberto.
