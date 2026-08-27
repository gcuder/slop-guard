# slop-guard for TypeScript and JavaScript

An Oxlint plugin that rejects low-evidence TypeScript and JavaScript patterns, plus two opt-in
plugins: Effect architecture rules and the refactoring.guru code smells. It is meant to be vendored
into a repository and maintained there.

The [repository README](../../README.md) explains how the agent skill installs this pack, and
[`code-smells.md`](../../code-smells.md) maps the smell rules to the catalogue they come from.

## Manual local installation

Copy this pack's `src/` into the target repository, for example at `tools/oxlint/slop-guard/`, and install matching current versions of `oxlint` and `@oxlint/plugins`.

Register the copied entry point in `oxlint.config.ts`:

```ts
import { defineConfig } from "oxlint";

export default defineConfig({
  ignorePatterns: [
    ".agent/**",
    ".agents/**",
    ".claude/**",
    ".codex/**",
    ".continue/**",
    ".cursor/**",
    ".gemini/**",
    ".opencode/**",
    ".pi/**",
    ".roo/**",
    ".windsurf/**",
    "tools/oxlint/slop-guard/**",
  ],
  jsPlugins: [
    { name: "slop-guard", specifier: "./tools/oxlint/slop-guard/index.ts" },
  ],
  rules: {
    "slop-guard/no-chained-type-assertions": "error",
    "slop-guard/no-conditional-empty-object-spread": "error",
    "slop-guard/no-known-value-widening": "error",
    "slop-guard/no-module-mocking": "error",
    "slop-guard/no-object-parameters": "error",
    "slop-guard/no-reflect-apply": "error",
    "slop-guard/no-reflect-get": "error",
    "slop-guard/no-runtime-typeof": "error",
    "slop-guard/no-shape-in-symbol-names": "error",
    "slop-guard/no-unknown-parameters": "error",
    "slop-guard/no-unknown-returns": "error",
    "slop-guard/no-unknown-type-aliases": "error",
    "slop-guard/no-unsafe-dictionary-type": "error",
    "slop-guard/no-widen-then-assert": "error",
    "slop-guard/require-safety-comment-for-type-assertion": "error"
  }
});
```

The same `ignorePatterns`, `jsPlugins`, and rules work under `lint` in a Vite+ config. Merge the ignore patterns into Vite+'s `fmt.ignorePatterns` as well so `vp check` does not reformat installed agent assets or the vendored plugin. Preserve existing ignores and add any other project-local agent tooling directories detected in the repository; do not broadly ignore every dot-directory.

## Optional Effect rules

Effect-specific rules live in a separate plugin so projects that do not use Effect do not inherit Effect architecture policy. Register the Effect entry point only in repositories that use Effect:

```ts
export default defineConfig({
  jsPlugins: [
    { name: "slop-guard", specifier: "./tools/oxlint/slop-guard/index.ts" },
    {
      name: "slop-guard-effect",
      specifier: "./tools/oxlint/slop-guard/effect/index.ts"
    }
  ],
  rules: {
    "slop-guard-effect/no-service-constructor-imports": "error"
  }
});
```

## Code smell rules

The refactoring.guru code smells live in their own plugin, because they are threshold-based and noisier than the generic rules. Register it in any repository that wants them:

```ts
export default defineConfig({
  jsPlugins: [
    { name: "slop-guard", specifier: "./tools/oxlint/slop-guard/index.ts" },
    {
      name: "slop-guard-smells",
      specifier: "./tools/oxlint/slop-guard/smells/index.ts"
    }
  ],
  rules: {
    "slop-guard-smells/no-long-method": ["error", { maxStatements: 20 }],
    "slop-guard-smells/no-long-parameter-list": ["error", { maxParameters: 4 }],
    "slop-guard-smells/no-large-class": "error",
    "slop-guard-smells/no-primitive-obsession": "error",
    "slop-guard-smells/no-data-clumps": "error",
    "slop-guard-smells/no-refused-bequest": "error",
    "slop-guard-smells/no-type-code-switch": "error",
    "slop-guard-smells/no-temporary-field": "error",
    "slop-guard-smells/no-commented-out-code": "error",
    "slop-guard-smells/no-duplicate-code": "error",
    "slop-guard-smells/no-data-class": "error",
    "slop-guard-smells/no-unreachable-code": "error",
    "slop-guard-smells/no-lazy-class": "error",
    "slop-guard-smells/no-unused-parameter": "error",
    "slop-guard-smells/no-feature-envy": "error",
    "slop-guard-smells/no-inappropriate-intimacy": "error",
    "slop-guard-smells/no-message-chains": "error",
    "slop-guard-smells/no-middle-man": "error"
  }
});
```

The eighteen rules, with `no-inappropriate-intimacy` covering the TypeScript half of that smell:

- `no-commented-out-code` — code left behind as a comment.
- `no-data-class` — a class whose methods only store and return its own fields.
- `no-data-clumps` — the same group of parameters travelling between functions.
- `no-duplicate-code` — two functions with identical bodies.
- `no-feature-envy` — a method that reads another object's members far more than its own.
- `no-large-class` — more methods or fields than one job's worth.
- `no-lazy-class` — a class with no state and one method.
- `no-long-method` — a function longer than the statement budget.
- `no-long-parameter-list` — more parameters than a caller can keep straight.
- `no-message-chains` — a chain that walks several objects deep.
- `no-middle-man` — a class whose methods only forward to one of its fields.
- `no-primitive-obsession` — several parameters of the same primitive type.
- `no-refused-bequest` — a subclass that overrides an inherited method only to refuse it.
- `no-temporary-field` — a field first assigned outside the constructor.
- `no-type-code-switch` — branching on a type code where a type could decide.
- `no-unreachable-code` — statements after `return`, `raise`/`throw`, `break`, or `continue`.
- `no-unused-parameter` — a parameter the body never reads.
- `no-inappropriate-intimacy` — reading another object's underscore-prefixed members.

Every threshold is an option; `code-smells.md` lists the defaults, maps each rule to its catalogue entry, and says which five smells have no rule and why.

## Generic rules

- `no-chained-type-assertions` — rejects nested type assertions that fabricate evidence.
- `no-conditional-empty-object-spread` — rejects conditional spreads that use `{}` to omit fields.
- `no-known-value-widening` — rejects explicit broad target types that discard known value evidence.
- `no-module-mocking` — rejects Vitest and Jest module mocks in favor of real dependency seams.
- `no-object-parameters` — rejects the broad `object` type on function inputs.
- `no-reflect-apply` — rejects `Reflect.apply` in favor of typed function calls.
- `no-reflect-get` — rejects `Reflect.get` in favor of typed property access or boundary parsing.
- `no-runtime-typeof` — requires boundary parsing instead of ad hoc `typeof` narrowing.
- `no-shape-in-symbol-names` — rejects `shape` in symbol names.
- `no-unknown-parameters` — rejects `unknown` inputs except the explicit `cause` convention.
- `no-unknown-returns` — rejects function contracts that return `unknown` or `Promise<unknown>`.
- `no-unknown-type-aliases` — rejects aliases that merely conceal `unknown`.
- `no-unsafe-dictionary-type` — rejects dictionary value contracts based on `unknown`, `any`, `object`, `{}`, and semantic equivalents.
- `no-widen-then-assert` — rejects local flows that widen known values and later assert them back.
- `require-safety-comment-for-type-assertion` — requires each non-const assertion to document its checked invariant.

## Effect rules

- `no-service-constructor-imports` — rejects relative project imports of exported `make<CapabilityName>` constructors outside `*.test.*` and `*.spec.*` files. Runtime callers should import the owning Layer and yield the contextual service instead. Package imports and static constructors such as `WorkspaceName.make` are outside the rule.

## Violation examples

Each snippet below is rejected by the named rule.

### `no-chained-type-assertions`

```ts
const user = input as object as User;
```

### `no-conditional-empty-object-spread`

```ts
const options = {
  ...(timeout !== undefined ? { timeout } : {}),
};
```

### `no-known-value-widening`

```ts
const handlers: Record<string, Handler> = {
  start: startHandler,
};
```

This discards the known `start` key. Preserve inference or use `satisfies Record<string, Handler>` instead.

### `no-module-mocking`

```ts
vi.mock("./user-store");
```

### `no-object-parameters`

```ts
function save(value: object) {}
```

### `no-reflect-apply`

```ts
const value = Reflect.apply(operation, owner, args);
```

### `no-reflect-get`

```ts
const value = Reflect.get(owner, key);
```

### `no-runtime-typeof`

```ts
if (typeof input === "string") {
  useName(input);
}
```

Schema-free projects can permit `typeof` checks directly inside type predicate and
assertion functions while continuing to reject ad hoc checks elsewhere:

```json
{
  "slop-guard/no-runtime-typeof": [
    "error",
    { "allowInTypeGuards": true }
  ]
}
```

The option defaults to `false`.

### `no-shape-in-symbol-names`

```ts
interface UserShape {
  id: string;
}
```

### Effect: `no-service-constructor-imports`

```ts
import { makeIssueService } from "./issue-service.ts";
```

Import the owning Layer and yield `IssueService` instead. Focused `*.test.*` and `*.spec.*` files may import the constructor directly.

### `no-unknown-parameters`

```ts
function handle(input: unknown) {}
```

### `no-unknown-returns`

```ts
function loadUser(): unknown {
  return input;
}
```

### `no-unknown-type-aliases`

```ts
type ExternalValue = unknown;
```

### `no-unsafe-dictionary-type`

```ts
type Metadata = Record<string, unknown>;
type OtherMetadata = { [key: string]: object };
```

### `no-widen-then-assert`

```ts
const loaded: User = loadUser();
const stored: unknown = loaded;
const user = stored as User;
```

### `require-safety-comment-for-type-assertion`

```ts
const userId = value as UserId;
```

Add a specific justification immediately before a necessary assertion:

```ts
// SAFETY: parseUserId validated the identifier before branding it.
const userId = value as UserId;
```

## Development

```bash
pnpm install
./check.sh
```

`src/index.ts` is the generic plugin, `src/effect/index.ts` the Effect rules, and
`src/smells/index.ts` the code smells. `./check.sh` runs the lint, the rule tests, and the
typecheck.
