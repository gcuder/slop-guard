# slop-guard for TypeScript and JavaScript

The rule pack is an Oxlint plugin. The installer copied it to `tools/oxlint/slop-guard/` unless you passed another destination; adjust every path below to match where it landed.

## 1. Find the lint setup

Identify the package manager from `packageManager` and lockfiles. Find the Oxlint configuration (`oxlint.config.*`, `.oxlintrc*`, or a Vite+ config). Do not replace the package manager or rewrite unrelated dependency ranges.

## 2. Install dependencies

To look without installing, `scripts/scan.mjs` in this skill runs these rules against a repository using a cached copy of the linter under `~/.cache/slop-guard/`, and writes nothing into the project. Installing is what follows below.


Install current compatible versions rather than trusting versions remembered by the agent:

- Query `npm view oxlint version` and `npm view @oxlint/plugins version`.
- Install the same current version of both packages with the repository's package manager.
- `oxlint` is a development dependency. The copied source imports `@oxlint/plugins`, so install it as a development dependency for a local-only plugin.

## 3. Register the plugin

For `oxlint.config.ts` or `.oxlintrc.json`, merge these fields with the existing configuration:

```ts
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
```

Keep every existing ignore. Adjust the final pattern when the plugin was copied elsewhere. Inspect the repository for other project-local agent tooling directories and add them rather than linting installed skills, hooks, or generated agent configuration as application source. Do not broadly ignore all dot-directories, because some repositories keep owned source or checks in them.

For Vite+, add these fields to `lint.ignorePatterns` and `lint.jsPlugins`. Also merge the same patterns into `fmt.ignorePatterns` so `vp check` does not reformat installed agent assets or the vendored plugin. Merge existing entries instead of replacing them.

## 4. Enable the rules

```json
{
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
```

`no-runtime-typeof` takes `{ "allowInTypeGuards": true }` for projects without a parsing layer; it defaults to `false`.

## 5. Optional Effect rules

If the repository declares `effect` in a package manifest, or the user explicitly requests Effect rules, also register the opt-in Effect plugin:

```ts
jsPlugins: [
  {
    name: "slop-guard-effect",
    specifier: "./tools/oxlint/slop-guard/effect/index.ts",
  },
],
rules: {
  "slop-guard-effect/no-service-constructor-imports": "error",
},
```

Merge these entries with the generic plugin configuration rather than replacing it. Do not enable the Effect plugin merely because Effect appears transitively in a lockfile; require a direct package-manifest dependency or an explicit user request. The rule covers relative project imports. Report package-alias imports as a current limitation rather than pretending they are enforced.

## 6. Optional code smell rules

The refactoring.guru code smells live in a second opt-in plugin, `slop-guard-smells`. They are threshold-based and noisier than the generic rules, so register them when the user asks for smell checks, or when the repository already runs a complexity or size limit that these would replace:

```ts
jsPlugins: [
  {
    name: "slop-guard-smells",
    specifier: "./tools/oxlint/slop-guard/smells/index.ts",
  },
],
rules: {
  "slop-guard-smells/no-commented-out-code": "error",
  "slop-guard-smells/no-data-class": "error",
  "slop-guard-smells/no-data-clumps": "error",
  "slop-guard-smells/no-duplicate-code": "error",
  "slop-guard-smells/no-feature-envy": "error",
  "slop-guard-smells/no-inappropriate-intimacy": "error",
  "slop-guard-smells/no-large-class": "error",
  "slop-guard-smells/no-lazy-class": "error",
  "slop-guard-smells/no-long-method": "error",
  "slop-guard-smells/no-long-parameter-list": "error",
  "slop-guard-smells/no-message-chains": "error",
  "slop-guard-smells/no-middle-man": "error",
  "slop-guard-smells/no-primitive-obsession": "error",
  "slop-guard-smells/no-refused-bequest": "error",
  "slop-guard-smells/no-temporary-field": "error",
  "slop-guard-smells/no-type-code-switch": "error",
  "slop-guard-smells/no-unreachable-code": "error",
  "slop-guard-smells/no-unused-parameter": "error",
},
```

Each threshold rule takes an options object: `maxStatements` (20), `maxParameters` (4), `maxMethods` and `maxFields` (10), `maxSameType` (2), `minGroup` (3), `minBranches` (3), `minStatements` (3), `minAccesses` (5), `maxLinks` (3), `minMethods` (2). Read the repository's existing limits before accepting the defaults, and set the numbers to what the team already agrees on. Report the finding count per rule before the user commits to a threshold.

## 7. Validate

Run the repository's lint command and typecheck. For Vite+, run the repository's full `vp check` command after adding both lint and format ignores.

## Rules

- `no-chained-type-assertions` — nested type assertions that fabricate evidence.
- `no-conditional-empty-object-spread` — conditional spreads that use `{}` to omit fields.
- `no-known-value-widening` — explicit broad target types that discard known value evidence.
- `no-module-mocking` — Vitest and Jest module mocks, in favor of real dependency seams.
- `no-object-parameters` — the broad `object` type on function inputs.
- `no-reflect-apply` — `Reflect.apply`, in favor of typed function calls.
- `no-reflect-get` — `Reflect.get`, in favor of typed property access or boundary parsing.
- `no-runtime-typeof` — ad hoc `typeof` narrowing instead of boundary parsing.
- `no-shape-in-symbol-names` — `shape` in symbol names.
- `no-unknown-parameters` — `unknown` inputs, except the explicit `cause` convention.
- `no-unknown-returns` — contracts that return `unknown` or `Promise<unknown>`.
- `no-unknown-type-aliases` — aliases that merely conceal `unknown`.
- `no-unsafe-dictionary-type` — dictionary value contracts based on `unknown`, `any`, `object`, `{}`, and semantic equivalents.
- `no-widen-then-assert` — local flows that widen known values and later assert them back.
- `require-safety-comment-for-type-assertion` — each non-const assertion must document its checked invariant.

## Resolving findings

Prefer inference, `as const`, `satisfies`, named owner contracts, and boundary parsing. The default plugin is intentionally generic; framework-specific policy belongs in an explicit opt-in group such as `slop-guard-effect`, and the code smells belong in `slop-guard-smells`.

A smell finding is a place to look, not a defect. Raise a threshold when the team disagrees with the default, and turn a rule off rather than working around it. `code-smells.md` in the slop-guard repository maps each rule to its catalogue entry and names the five smells no rule covers.
