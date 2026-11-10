---
name: nestjs-padrao
description: Padrão pessoal de desenvolvimento NestJS/TypeScript. Cobre estrutura por feature, prefixos I/E, DTOs Request/Response, entidade rica, try/catch com exceções do Nest, Swagger completo e as configs de ESLint, Prettier e tsconfig. Use ao criar um projeto, módulo, entidade, DTO, enum, interface, controller, service, repository ou teste em NestJS/TypeScript, e ao revisar se um código segue o padrão.
---

# Padrão NestJS

O guia completo, com exemplos reais, está em [references/padroes.md](references/padroes.md). Antes de escrever um tipo de arquivo, leia a seção dele no guia (ex.: "Services" antes de criar um service).

## Projeto existente

Se o projeto já segue um padrão diferente deste, siga o do projeto e aponte a diferença ao usuário. Não reescreva código que funciona só para encaixar no padrão.

## Projeto novo

1. `nest new <nome> --package-manager yarn --skip-git`
2. Apague `src/app.controller.ts`, `src/app.controller.spec.ts` e `src/app.service.ts`.
3. Copie os arquivos de [templates/](templates/) por cima dos gerados:
   - Raiz: `eslint.config.mjs`, `.prettierrc`, `tsconfig.json`, `tsconfig.build.json`, `nest-cli.json`, `Dockerfile`, `.dockerignore` e `.env.example`.
   - `gitignore` vira `.gitignore`. No template ele não tem o ponto, para não valer dentro do repositório da skill.
   - `src/`: `main.ts`, `app.module.ts`, `health.controller.ts`, `health.controller.spec.ts`.
   - `test/`: `app.e2e-spec.ts`, `jest-e2e.json`.
   - `.claude/`: as regras do hookify de `~/.claude/hookify/` (a `block-npm` barra o `npm`).
   - De `templates/opcional/`, só o que o projeto usa, no mesmo caminho: `src/auth/` (login com JWT), `src/common/` (paginação), `src/config/env-reader.ts` e `docker-compose.yml`. Com `src/auth/`, marque o `HealthController` com `@Public()`.
4. No `main.ts`, troque `<project>`, `<service>` e `<what the service does>`. Ajuste a porta padrão no `main.ts` e no `.env.example`.
5. `yarn add @nestjs/config@^4 @nestjs/swagger@^11 class-validator class-transformer`
   - Com Postgres: `yarn add @nestjs/typeorm@^11 typeorm pg`.
   - Com login: `yarn add @nestjs/jwt@^11 bcryptjs`, e `@nestjs/throttler` se houver rota pública sensível (esqueci a senha).
   - Fique no `@nestjs/config` ^4 e no `@nestjs/typeorm` ^11: as versões seguintes são só ESM e quebram o Jest (decisão do REC-41).
   - Fique no `@nestjs/swagger` ^11: a 12 exige Nest 12, e o `nest new` 11 cria um projeto Nest 11.
6. Escreva o README: como subir a infra, `yarn start:dev` e `curl localhost:<porta>/health`.
7. Confira: `yarn lint`, `yarn build`, `yarn test` e `yarn test:e2e`.

Os geradores `nest g` seguem os nomes do Nest (`dto/`, `create-x.dto.ts`), não os deste padrão. Se usar, renomeie para `dtos/` e `<Ação><Entidade>RequestDto`.

## Checklist

**Nomes**
- Interface com `I` (`IPspGateway`), enum com `E` (`EChargeStatus`) e type sem prefixo.
- DTO: `<Ação><Entidade>RequestDto` / `<Entidade>ResponseDto`. Entidade no singular, sem sufixo.
- Arquivo em kebab-case com o tipo no nome e nunca com `I`/`E` (`charge-status.enum.ts`).
- Module, service, controller e repository no plural (`ChargesService`).
- Constantes em `UPPER_SNAKE` no `<feature>.constants.ts`. Token de injeção é um `Symbol`.
- Código, logs, erros e Swagger em inglês. Comentários em português, explicando o porquê.

**Entidade**
- Regra de negócio e transição de estado ficam na entidade, conferidas antes de mudar o estado.
- Campos imutáveis `readonly`. Com TypeORM, o construtor recebe `input?: <Request>Dto`.
- Dinheiro em centavos inteiros (`amountCents`), percentual em basis points (`splitBps`).
- Colunas em snake_case com `name` explícito. Constraints nomeadas (`uq_`, `ck_`, `ix_`, `fk_`).

**DTO**
- Cada campo tem class-validator e `@ApiProperty` com `description`, `example` e limites.
- Update = `PartialType(OmitType(...))` de `@nestjs/swagger`.

**Controller**
- Fino: `return await this.service.x(dto);`.
- Swagger completo: `@ApiTags`, `@ApiOperation`, `@ApiParam` e um `@ApiResponse` por status.
- `ParseUUIDPipe` nos ids. Ação que muda estado: `POST /:id/<verbo>` com `@HttpCode(200)`.

**Service**
- `private readonly logger = new Logger(<Classe>.name)`.
- Escrita em transação com `queryRunner`, e `pessimistic_write` ao ler para alterar.
- `try/catch/finally`: relança, com `instanceof`, os erros HTTP que a ação lança de propósito. O resto vira `InternalServerErrorException('Unexpected server error <verbo>ing <entidade>')`, com `logger.error(..., error.stack)`.
- Exceções do Nest direto: 400 duplicado/validação, 403, 404, 409 estado, 422 regra de negócio.
- Mensagens: `<Entidade> ${id} not found`, `Cannot <ação> <entidade> ${id}: <motivo>`.

**Autenticação e listagem**
- Guard de JWT global, que nega por padrão. Rota pública só com `@Public()`.
- Papel com `@RequireRoles(...)`. Dono do recurso filtrado na própria consulta (`where: { id, userId }`), com 404 quando não é dele.
- Listagem: `List<Entidade>RequestDto extends PaginationRequestDto`, resposta `PaginatedResponseDto` e ordem explícita.
- Variável de ambiente obrigatória derruba o app na subida se faltar, e entra no `.env.example` com comentário.

**Teste**
- Teste antes do código, visto falhando primeiro (skill `test-driven-development`).
- `*.spec.ts` unitário ao lado do arquivo. `*.test.spec.ts` integração com a infra real. `test/*.e2e-spec.ts` e2e.
- Fake em memória com o mesmo contrato, em vez de `jest.mock`.

**Estilo**
- Prettier com 120 colunas, aspas simples e vírgula no final.
- Cláusula de guarda é um `if` de uma linha, sem chaves.
