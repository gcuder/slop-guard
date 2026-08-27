# slop-guard for Python

The rule pack is a standalone `ast` checker with no third-party dependencies, so it runs alongside Ruff, mypy, or pyright rather than replacing them. The installer copied it to `tools/slop_guard/` unless you passed another destination; adjust every path below to match where it landed.

## 1. Check the Python version and the existing checks

The checker needs Python 3.12 or newer. Read `requires-python` in `pyproject.toml` and report a mismatch instead of installing silently.

Identify how checks run today: `pyproject.toml` scripts, a `Makefile`, `tox.ini`, `noxfile.py`, `.pre-commit-config.yaml`, or a CI workflow.

## 2. Confirm the checker runs

To look without installing, `scripts/scan.py` in this skill runs these rules from the skill's own copy and writes nothing. Installing is what follows below.


```bash
python3 -m tools.slop_guard --list-rules
python3 -m tools.slop_guard src
```

Adjust the module path when the checker was copied elsewhere. Do not add the checker to a dependency list; it is vendored source, not a package to install.

## 3. Configure it

Merge this section into `pyproject.toml` rather than replacing the file:

```toml
[tool.slop-guard]
exclude = [
  ".agent", ".agents", ".claude", ".codex", ".continue", ".cursor",
  ".gemini", ".git", ".opencode", ".pi", ".roo", ".venv", ".windsurf",
  "__pycache__", "build", "dist", "node_modules", "venv", "tools",
]
```

Keep every existing exclusion. Add any other project-local agent tooling directories found in the repository, and exclude the vendored checker itself. Do not broadly exclude all dot-directories, because some repositories keep owned source in them.

All seventy-five rules run by default, and `select` and `ignore` accept both rule names and `group:<name>` tokens. Set `ignore` only for rules the user has decided against, and record why in a comment:

```toml
[tool.slop-guard]
ignore = ["no-runtime-isinstance"]

[tool.slop-guard.rules."no-runtime-isinstance"]
allow_in_type_guards = true

[tool.slop-guard.rules."no-any-parameters"]
allow_variadic_any = true

[tool.slop-guard.rules."no-forbidden-terms-in-symbol-names"]
terms = ["shape", "helper", "manager"]
```

## 4. Wire it into the existing checks

Use whichever mechanism the repository already has, and do not introduce a new task runner:

- With pre-commit, add a `repo: local` hook with `language: system` and `entry: python3 -m tools.slop_guard`.
- With a Makefile, tox, or nox, add a `slop-guard` step next to the lint step.
- In CI, add it to the job that already runs lint, before the test step.

The checker exits `1` when it reports a finding, so it needs no wrapper. `--format json` prints machine-readable findings, `--select` and `--ignore` take comma-separated rule names, and `--exit-zero` reports without failing the build.

## 5. Validate

Run the checker over owned source together with the repository's existing lint, typecheck, and tests.

## Rules

The checker ships 75 rules in seven groups, all of which run by default.

- **evidence** (15) — slop-guard's own position: a type or a name should record evidence the program has. `no-any-parameters`, `no-any-returns`, `no-any-type-aliases`, `no-chained-casts`, `no-conditional-empty-dict-spread`, `no-dynamic-attribute-access`, `no-forbidden-terms-in-symbol-names`, `no-known-value-widening`, `no-module-mocking`, `no-object-parameters`, `no-runtime-isinstance`, `no-silent-exception-swallow`, `no-unsafe-dictionary-type`, `no-widen-then-cast`, `require-safety-comment-for-cast`.
- **correctness** (20) — code that misbehaves at runtime: `no-bad-super-arguments`, `no-bare-except`, `no-builtin-shadowing`, `no-java-style-accessors`, `no-lambda-assignment`, `no-loop-else-without-break`, `no-method-without-receiver-use`, `no-mixed-indentation`, `no-mutable-default-argument`, `no-protected-member-access`, `no-return-value-in-init`, `no-tab-indentation`, `no-unreachable-except-clause`, `prefer-defaultdict`, `prefer-dict-get`, `prefer-explicit-unpacking`, `prefer-loop-else`, `prefer-setdefault`, `require-exit-signature`, `require-method-self`.
- **maintainability** (6) — `no-computed-attribute-names`, `no-global-statement`, `no-mixed-return-types`, `no-single-letter-names`, `no-wildcard-imports`, `require-with-for-open`.
- **readability** (15) — `no-camel-case-functions`, `no-comparison-to-bool`, `no-comparison-to-none`, `no-identity-comparison-to-literal`, `no-type-comparison`, `no-type-in-name`, `prefer-comprehension-over-map-filter`, `prefer-dict-comprehension`, `prefer-dict-items`, `prefer-eafp-for-files`, `prefer-enumerate`, `prefer-format-mapping`, `prefer-named-tuple`, `prefer-tuple-swap`, `prefer-zip`.
- **security** (1) — `no-exec`.
- **performance** (1) — `prefer-set-membership`.
- **smells** (17) — the refactoring.guru code smells: `no-commented-out-code`, `no-data-class`, `no-data-clumps`, `no-duplicate-code`, `no-feature-envy`, `no-large-class`, `no-lazy-class`, `no-long-method`, `no-long-parameter-list`, `no-message-chains`, `no-middle-man`, `no-primitive-obsession`, `no-refused-bequest`, `no-temporary-field`, `no-type-code-switch`, `no-unreachable-code`, `no-unused-parameter`. Every threshold is an option: `max_statements` (20), `max_parameters` (4), `max_methods` and `max_attributes` (10), `max_same_type` (2), `min_group` (3), `min_branches` (3), `min_statements` (3), `min_accesses` (5), `max_links` (3), `min_methods` (2). Read the repository's existing limits before accepting the defaults, and report the finding count per rule before the user commits to a threshold.

`python3 -m tools.slop_guard --list-rules` prints every rule with its group and, for the rules that come from the anti-patterns book, a link to the entry it enforces.

Rules that take options: `no-any-parameters` (`allow_variadic_any`), `no-runtime-isinstance` (`allow_in_type_guards`), `no-forbidden-terms-in-symbol-names` (`terms`), `no-single-letter-names` (`allow`), and every threshold rule in the smells group.

### Introducing the checker to an existing codebase

Seventy-five rules against code that has never seen them will produce a lot of findings at once. When the user wants a staged rollout, start with one group and add the rest as the findings are cleared:

```toml
[tool.slop-guard]
select = ["group:evidence", "group:correctness", "group:security"]  # add "group:smells" when the team is ready
```

Report the full count before narrowing, so the user chooses the scope rather than inheriting yours.

## Resolving findings

Parse at the boundary, name domain types, and use dataclasses or `TypedDict`. Do not silence rules, add `# type: ignore`, or replace a real type with `Any` to make the check pass.

Several rules overlap Ruff, which is expected and harmless: `no-bare-except` overlaps `E722`, `no-type-comparison` overlaps `E721`, `no-mutable-default-argument` overlaps `B006`, `no-lambda-assignment` overlaps `E731`, and `no-wildcard-imports` overlaps `F403`. Leave the Ruff rules enabled; slop-guard's messages say what to do instead, and the two tools disagree nowhere.

`languages/python/anti-patterns.md` in the slop-guard repository maps every entry in the general Python chapters of The Little Book of Python Anti-Patterns to the rule that enforces it, and says why three entries have none. The book's Django chapters and its Python 2 entries are out of scope: this pack stays framework-neutral, and it targets Python 3.12 and newer. `code-smells.md` does the same for the refactoring.guru catalogue that the smells group implements.

A smell finding is a place to look, not a defect. Raise a threshold when the team disagrees with the default, and turn a rule off rather than working around it.
