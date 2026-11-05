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
├── common/         correlation/, dtos/ compartilhados
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

- As exceções do Nest são lançadas direto, sem classes próprias nem filtro.
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

## Decisões pendentes

Divergências encontradas no repositório de origem. Ao lado de cada uma, a proposta para o padrão.

1. **Tratamento de erro.** `lojista` e `ledger` lançam as exceções do Nest direto (decisão do REC-41). `pagamentos` usa classes próprias (`extends Error`, com `this.name = X.name`) e um `@Catch` filter para traduzir em HTTP.
   **Proposta:** o primeiro estilo é o padrão. Classes próprias só para erro de infra que atravessa camadas (repository e gateway).
2. **Os tsconfigs não são iguais.** O de `liquidacao` não tem `strictPropertyInitialization: false` e o de `repasse` não tem `types`.
   **Proposta:** o modelo é o tsconfig de `pagamentos`.
3. **Mensagem fora do molde:** `'charge not found!'` em `pagamentos`.
   **Proposta:** seguir sempre `<Entidade> ${id} not found`.
4. **Sem regra de ordem de imports nem de máximo de linhas.**
   **Proposta:** continuar sem regra, a menos que se decida outra coisa (ex.: `max-lines: 300`).
