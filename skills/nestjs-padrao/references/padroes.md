# Padrões de desenvolvimento NestJS

Guia extraído do [microsservice](https://github.com/Ericles-Miller/microsservice) (commit `888a298`), que segue o padrão do projeto calhas. Os exemplos vêm dos serviços `lojista`, `pagamentos`, `ledger` e `repasse`.

## Stack

- NestJS 11, TypeScript 5.7, Node 22.
- **Só `yarn`** (nunca `npm`).
- Jest 30 com ts-jest, Swagger (`@nestjs/swagger`), class-validator e class-transformer.
- Banco: TypeORM (Postgres) ou AWS SDK v3 (DynamoDB, SQS, SNS). Em ambiente local, LocalStack e Postgres via `docker compose`.
- Cada serviço tem `Dockerfile`, `.env.example`, `README.md`, `GET /health` e Swagger em `/docs`.
- A porta vem de `PORT`, com um valor padrão por serviço.
- `ConfigModule.forRoot({ isGlobal: true })`. O correlation id por requisição usa `nestjs-cls`, montado como middleware.

## Estrutura de pastas

Uma pasta por feature:

```
src/
├── main.ts · app.module.ts · health.controller.ts
├── aws/            aws.module.ts + <svc>/<svc>.config.ts + aws-<svc>.service.ts
├── database/       database.module.ts, data-source.ts, migrations/, *.definition.ts
├── auth/           auth.module.ts, token.service.ts, guards/, decorators/, enums/, interfaces/
├── common/         correlation/, dtos/ compartilhados (paginação)
├── config/         env-reader.ts e utilitários de configuração
├── utils/validators/
├── scripts/        criação de tabela, ferramentas de linha de comando
└── <feature>/
    ├── <feature>.module.ts · <feature>.controller.ts · <feature>.service.ts · <feature>.constants.ts
    ├── dtos/ · entities/ · enums/ · interfaces/ · types/
    ├── repositories/   <x>.repository.ts · <x>.keys.ts · <x>.mapper.ts
    └── exceptions/ · filters/ · pipes/ · guards/ · decorators/ · gateways/ · consumers/   (só quando precisa)
test/               *.e2e-spec.ts, jest-e2e.json
```

Tudo que é AWS fica em `src/aws/`, com uma pasta por serviço AWS: `<svc>.config.ts` monta o client e `aws-<svc>.service.ts` é o que o app injeta. Quem usa importa o `AwsModule`.

## Nomes

| O quê | Regra | Exemplo |
|---|---|---|
| Interface | prefixo `I` | `IPspGateway`, `IChargeItem` |
| Enum | prefixo `E`; chave em `UPPER_SNAKE`, valor em minúsculas (snake_case) | `EPayoutAction.MARK_PAID = 'mark_paid'` |
| Type | sem prefixo | `IdempotentCreateResult` |
| DTO | `<Ação><Entidade>RequestDto` / `<Entidade>ResponseDto` | `CreateChargeRequestDto`, `ChargeResponseDto` |
| Entidade | sem prefixo nem sufixo, no singular | `Charge`, `Merchant`, `Entry` |
| Module, service, controller, repository | no plural | `ChargesService`, `charges.repository.ts` |
| Keys e mapper | no singular | `ChargeKeys`, `ChargeMapper` |
| Arquivo | kebab-case com o tipo no nome, **nunca** com `I`/`E` | `charge-status.enum.ts`, `charge-item.interface.ts`, `create-charge-request.dto.ts`, `idempotent-create-result.type.ts` |
| Constante | `UPPER_SNAKE` em `<feature>.constants.ts`, com comentário da unidade | `CHARGE_EXPIRATION_MINUTES = 30; // quanto tempo o pagador tem para pagar` |
| Token de injeção | `Symbol` (interfaces somem na compilação) | `PSP_GATEWAY = Symbol('PSP_GATEWAY')` |
| Coluna do banco | snake_case com `name` explícito | `@Column({ name: 'split_bps', type: 'int' })` |
| Constraint | nomeada, com prefixo | `uq_merchants_email`, `ck_merchants_status`, `ix_entries_transaction_id`, `fk_entries_reverses_entry` |

**Idioma:** código, logs, mensagens de erro, valores de enum e Swagger em **inglês**. Comentários e documentação em **português**.

## Entidades

A entidade é um modelo rico: a regra de negócio mora nela, não no service.

- Transições de estado são métodos da entidade (`approve()`, `reject(reason)`, `submitForReview()`, `deactivate()`), com helpers privados `ensureActive()`, `ensureTransition()` e `transition()`.
- Tudo é conferido **antes** de mudar o estado: um erro nunca deixa a entidade num estado falso.
- Com TypeORM, o construtor recebe o DTO de request como `input?` opcional, porque o TypeORM instancia sem argumentos: `constructor(input?: RegisterMerchantRequestDto) { if (!input) return; ... }`.
- Campos imutáveis são `readonly`. Há fábricas estáticas para os casos especiais (`Entry.reversalOf(original)`, `Payout.split(amountCents, splitBps)`).
- **Dinheiro sempre em centavos inteiros** (`amountCents`). Percentual em **basis points** (`splitBps`, 10000 = 100%). Arredondamento explícito e documentado (ex.: `Math.floor` para a parte do lojista).
- Datas: string ISO 8601 UTC no DynamoDB, `timestamptz` no Postgres.
- Com DynamoDB, a entidade não sabe nada do banco: os prefixos de chave ficam em `<x>.keys.ts` (único lugar que os conhece) e o `<x>.mapper.ts` converte com **lista explícita de campos**, para um atributo novo não vazar por acidente.
- Uma máquina de estados vira tabela: `Record<EAction, { from: EStatus[]; to: EStatus }>` + `canApply(action, status)`.
- As CHECKs do banco são repetidas em `@Check` na entidade. As migrations são escritas à mão.
- Campos sensíveis levam `@Exclude({ toPlainOnly: true })`.

## DTOs

- Todo campo tem class-validator e `@ApiProperty` com `description`, `example` e os limites (`minimum`, `maximum`, `maxLength`, `required: false`).
- O DTO de update deriva do de criação: `PartialType(OmitType(RegisterMerchantRequestDto, ['document']))`, importado de `@nestjs/swagger`.
- O `ValidationPipe` global é registrado como `APP_PIPE` no `AppModule` (e não no `main.ts`), para valer também nos testes: `new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true })`.
- Existe um `ErrorResponseDto` (`statusCode`, `error`, `message: string | string[]`) para documentar os erros no Swagger.
- Validador customizado fica em `utils/validators/` (ex.: `@IsCnpj()`).

## Controllers

- São finos: só repassam ao service (`return await this.service.register(dto);`).
- Swagger completo em toda rota: `@ApiTags`, `@ApiOperation` com `summary` e `description`, `@ApiParam` com `schema` (`format: 'uuid'`, `example`) e um `@ApiResponse` para cada status possível (400/404/409/422/500).
- Ids passam por `ParseUUIDPipe`.
- Ações que mudam estado são `POST /:id/<verbo>` (`/submit`, `/approve`, `/reject`, `/deactivate`) com `@HttpCode(200)`.

## Services

- `@Injectable()`, injeção no construtor com `private readonly`.
- Logger por classe: `private readonly logger = new Logger(MerchantsService.name);`.
- Dependência externa entra por interface + token: `@Inject(PSP_GATEWAY) private readonly psp: IPspGateway`, com `import type` na interface.
- Métodos públicos primeiro, helpers privados depois (`ensureMerchantCanCharge`, `buildCharge`).
- Toda escrita abre uma transação com `queryRunner`. Ao ler para alterar, usa `lock: { mode: 'pessimistic_write' }`. Uma leitura simples usa o repository.
- Duplicidade: o service consulta antes (`existsBy`) para dar uma mensagem clara, e o UNIQUE do banco segura dois pedidos simultâneos. O erro `23505` é traduzido pelo nome da constraint.
- O evento de outbox é gravado **na mesma transação**, depois do `save` e antes do `commit`.

### Tratamento de erro (try/catch)

```ts
async approve(id: string): Promise<Merchant> {
  const queryRunner = this.dataSource.createQueryRunner();
  await queryRunner.connect();
  await queryRunner.startTransaction();

  try {
    const merchant = await queryRunner.manager.findOne(Merchant, {
      where: { id },
      lock: { mode: 'pessimistic_write' },
    });
    if (!merchant) throw new NotFoundException(`Merchant ${id} not found`);

    merchant.approve();
    await queryRunner.manager.save(merchant);
    await this.outboxEventService.create(queryRunner.manager, EEventType.MERCHANT_APPROVED, merchant);

    await queryRunner.commitTransaction();
    return merchant;
  } catch (error) {
    await queryRunner.rollbackTransaction();

    if (error instanceof NotFoundException || error instanceof ConflictException) throw error;

    this.logger.error('Unexpected error approving merchant', error instanceof Error ? error.stack : String(error));
    throw new InternalServerErrorException('Unexpected server error approving merchant');
  } finally {
    await queryRunner.release();
  }
}
```

- As exceções do Nest são lançadas direto, sem classes próprias nem filtro. Classe própria (`extends Error`, com `this.name = X.name`) só para erro de infra que atravessa camadas, lançada por repository ou gateway.
- No `catch`, os erros HTTP que **aquela ação** lança de propósito são relançados, listados um a um com `instanceof`. O resto vira 500, com o erro original no log.
- Status usados:

| Status | Quando |
|---|---|
| 400 Bad Request | validação do DTO, registro duplicado |
| 403 Forbidden | o chamador não pode fazer a ação (ex.: lojista não aprovado) |
| 404 Not Found | o recurso não existe |
| 409 Conflict | o estado atual não permite a ação |
| 422 Unprocessable Entity | os dados não atendem a regra de negócio |
| 500 Internal Server Error | qualquer erro inesperado |

- Moldes de mensagem:
  - `Merchant ${id} not found`
  - `Cannot ${action} merchant ${id}: status is ${status}, expected ${from}`
  - `Invalid data for merchant ${id}: pixKey is required to submit for review`
  - `Unexpected server error <verbo>ing <entidade>`
- Nos repositories (DynamoDB), o `catch` pega só o erro específico de infra e traduz. O resto é relançado:

```ts
} catch (error) {
  if (error instanceof ConditionalCheckFailedException) throw new ChargeAlreadyExistsException(charge.id);

  throw error;
}
```

## Autenticação e autorização

O modelo é o backend da usina (MS-36 a MS-40), feito depois das auditorias do calhas, que acharam rotas sem guard e acesso a recurso de outro usuário (PC-70, PC-73, PC-77). Os arquivos prontos, com testes, estão em `templates/opcional/src/auth/`.

- **Guard global que nega por padrão.** O `JwtAuthGuard` é registrado como `APP_GUARD`: rota nova nasce protegida, e só `@Public()` a libera (health, login, refresh, links de e-mail). No calhas o guard era por rota, e um controller inteiro ficou público (PC-73).
- **Sem passport.** O guard lê o `Bearer`, valida com o `TokenService` e põe `{ id, email, role }` em `request.user`. O controller recebe com `@CurrentUser()`.
- **Papéis:** `@RequireRoles(ERole.ADMIN)` com o `RolesGuard`, o segundo `APP_GUARD`. Sem o decorator, qualquer usuário autenticado passa; com papel errado, 403. O papel vai dentro do access token, então uma troca de papel só vale no próximo token (até 15 min).
- **Dono do recurso:** filtre pelo dono na própria consulta (`where: { id, userId }`) e responda 404 quando não achar. É 404 e não 403 para não revelar que o recurso existe. O id do dono vem sempre do `@CurrentUser()`, nunca do body ou da query.
- **Tokens:**
  - Access token de 15 min e refresh de 7 dias, com segredos diferentes, de 32 caracteres ou mais, conferidos na subida do app.
  - O refresh leva um `jti` aleatório, e o banco guarda só o hash SHA-256 dele. Não bcrypt: ele só olha os primeiros 72 bytes, e o começo de dois JWTs é quase igual.
  - O refresh gira a cada uso: o hash novo só é gravado se o antigo ainda for o atual. Se não for, é reuso de um token já trocado: apague o hash e recuse, tratando como vazamento.
  - Logout apaga o hash do refresh. Com token inválido, responde do mesmo jeito, sem erro.
  - Link de e-mail (confirmar conta, redefinir senha): token opaco de 32 bytes aleatórios, de uso único e com validade. Só o hash vai para o banco.
- **Login:**
  - Senha com `bcryptjs`.
  - E-mail inexistente também passa pelo `compare` (com um hash falso), para o tempo de resposta não denunciar quem tem cadastro.
  - Credencial errada → 401 `Invalid credentials`, sem dizer qual dos dois errou. Conta não confirmada → 403, só para quem acertou a senha.
  - "Esqueci a senha" responde igual, exista a conta ou não.
- `@Exclude({ toPlainOnly: true })` em senha e hashes. O `ClassSerializerInterceptor` global, que faz o `@Exclude` funcionar, já está no template do `app.module.ts`.
- Rota pública sensível (esqueci a senha, reenviar confirmação) tem limite por IP com `@nestjs/throttler`, aplicado com `@UseGuards` só nela. Atrás de um balanceador, ligue o `trust proxy`, senão todos os clientes dividem o IP do balanceador.
- Swagger: `.addBearerAuth()` no `main.ts` e `@ApiBearerAuth()` nos controllers protegidos.

## Paginação e filtros

Os arquivos prontos estão em `templates/opcional/src/common/`.

- `PaginationRequestDto`: `page` a partir de 1 e `limit` de 1 a 100, com padrão 10. O teto evita que uma listagem carregue a tabela inteira (o do calhas não tinha).
- O filtro é `List<Entidade>RequestDto extends PaginationRequestDto`, recebido com `@Query()`. Todo campo é opcional, com class-validator e `@ApiPropertyOptional`.
- A resposta é `PaginatedResponseDto<T>` (`data`, `total`, `page`, `limit`, `totalPages`), montada com `PaginatedResponseDto.of(data, total, pagination)`. Para o Swagger, cada listagem declara `<Entidade>PageResponseDto` estendendo a classe e redeclarando `data` com `@ApiProperty({ type: [<Entidade>ResponseDto] })`.
- A consulta usa `findAndCount` com `skip: (page - 1) * limit` e `take: limit`, e sempre com ordem explícita (`order: { createdAt: 'DESC' }`). Sem ordem, a mesma página pode mudar entre duas chamadas.

## Variáveis de ambiente

- Toda variável nova entra no `.env.example` com um comentário: para que serve, o formato e se é obrigatória.
- Obrigatória que falta derruba o app na subida, com mensagem clara, em vez de falhar no primeiro uso. Use o `createEnvReader(configService)` de `templates/opcional/src/config/env-reader.ts`: `env.required('MAIL_HOST', 'to send emails')`. Vazio ou só com espaços conta como ausente.
- Segredo nunca tem valor padrão no código.
- Valor do `.env` nunca aparece em log, resposta, comentário de Jira ou doc: só o nome.

## Infra local

`templates/opcional/docker-compose.yml` traz:
- Postgres com healthcheck: `docker compose up -d db`.
- LocalStack no profile `aws` e Mailpit (SMTP falso, caixa de entrada em `localhost:8025`) no profile `mail`.

As portas ficam presas ao `127.0.0.1`.

## Estilo de código

- **Prettier:** `singleQuote`, `trailingComma: "all"`, `printWidth: 120` (até 120 caracteres por linha). Indentação de 2 espaços e ponto e vírgula (os padrões do Prettier).
- Cláusula de guarda é um `if` de uma linha, sem chaves, com saída antecipada (`if (!merchant) throw new NotFoundException(...)`). Uma linha em branco separa a guarda do resto.
- Os comentários explicam o **porquê** (decisões, concorrência, número da tarefa), nunca o quê:
  `// Consultar ANTES de chamar o PSP: uma repetição não pode gerar um segundo PIX.`
- Os arquivos são pequenos: o maior tem 265 linhas. Não há regra de máximo de linhas.
- `main.ts` termina com `void bootstrap();`, por causa do `no-floating-promises`.

## ESLint (`eslint.config.mjs`, flat config)

```js
export default tseslint.config(
  { ignores: ['eslint.config.mjs'] },
  eslint.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  eslintPluginPrettierRecommended,
  {
    languageOptions: {
      globals: { ...globals.node, ...globals.jest },
      sourceType: 'commonjs',
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
  },
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-floating-promises': 'warn',
      '@typescript-eslint/no-unsafe-argument': 'warn',
    },
  },
);
```

## tsconfig

- `module`/`moduleResolution: "nodenext"`, `target: "ES2023"`, `emitDecoratorMetadata` e `experimentalDecorators` ligados.
- `strictNullChecks: true`.
- **Relaxados de propósito:**
  - `strictPropertyInitialization: false`: campos de DTO e entidade não precisam de inicializador.
  - `noImplicitAny: false`
  - `strictBindCallApply: false`
  - `noFallthroughCasesInSwitch: false`
- Demais opções: `skipLibCheck`, `incremental`, `removeComments`, `sourceMap`, `declaration`, `esModuleInterop`, `isolatedModules`, `types: ["node", "jest"]`.
- O `tsconfig.build.json` estende o principal e exclui `node_modules`, `test`, `dist` e `**/*spec.ts`.

## Testes

| Arquivo | Tipo | Onde roda |
|---|---|---|
| `*.spec.ts` | unitário, ao lado do arquivo testado | `yarn test` |
| `*.test.spec.ts` | integração contra LocalStack ou Postgres reais; usa ids únicos e apaga o que criou | `yarn test` (com a infra no ar) |
| `test/*.e2e-spec.ts` | e2e da API | `yarn test:e2e` |

- Fakes em memória com o mesmo contrato do real (`InMemoryChargesRepository`), em vez de `jest.mock`. O fake simula falhas e corridas (`failNextWriteWith`, `competingRequest`).
- O `describe` do teste de integração leva o sufixo: `describe('ChargesRepository (integration)', ...)`.

## Git

- Conventional Commits em inglês, com a tarefa no escopo: `feat(REC-48): payouts table, merchant replica and payout model in repasse`.
- Uma branch por tarefa (`REC-48`), PR para `develop` e depois PR de `develop` para `main`.

## Decisões sobre as divergências (2026-11-05)

O repositório de origem tinha divergências entre os serviços. Ficou decidido assim:

1. **Tratamento de erro.** `lojista` e `ledger` lançam as exceções do Nest direto (decisão do REC-41). `pagamentos` usa classes próprias (`extends Error`, com `this.name = X.name`) e um `@Catch` filter para traduzir em HTTP.
   **Decidido:** o primeiro estilo é o padrão. Classes próprias só para erro de infra que atravessa camadas (repository e gateway).
2. **Os tsconfigs não eram iguais.** O de `liquidacao` não tinha `strictPropertyInitialization: false` e o de `repasse` não tinha `types`.
   **Decidido:** o modelo é o tsconfig de `pagamentos` (`templates/tsconfig.json`).
3. **Mensagem fora do molde:** `'charge not found!'` em `pagamentos`.
   **Decidido:** seguir sempre `<Entidade> ${id} not found`.
4. **Ordem de imports e máximo de linhas.**
   **Decidido:** sem regra por enquanto. Se mudar, a regra entra no `templates/eslint.config.mjs` (ex.: `max-lines: 300`).

## Decisões sobre auth, paginação e env (2026-11-09)

A usina e o calhas resolviam estas partes de jeitos diferentes. São recomendações aplicadas a pedido do Ericles; confirmar na revisão.

5. **Autenticação.** O calhas usa passport e um guard por rota; a usina usa um guard global que nega por padrão, sem passport.
   **Recomendado:** o da usina. O guard por rota deixou um controller inteiro público no calhas (PC-73).
6. **Dono do recurso.** O calhas usa um guard que compara o `companyId` da query com o do usuário; a usina filtra pelo dono na consulta e responde 404.
   **Recomendado:** o da usina. O id na query é fácil de esquecer ou de trocar (PC-77).
7. **Paginação.** Só o calhas tinha.
   **Recomendado:** a do calhas, com teto de 100 itens e os nomes deste padrão (`PaginationRequestDto`).
8. **Log de requisição com dados mascarados (MS-98).** A task foi aberta, mas nunca implementada.
   **Fica de fora** até existir uma implementação validada.
