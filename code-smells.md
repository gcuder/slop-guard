# Coverage of the refactoring.guru code smells

Every smell in the [refactoring.guru catalogue](https://refactoring.guru/refactoring/smells), and the rule that reports it in each language. Seventeen of the twenty-two have rules; the five that do not are listed at the end with the reason.

The rules live in one selectable unit per language: the `smells` group in the Python checker, which runs by default, and the `slop-guard-smells` Oxlint plugin, which you register alongside the generic plugin. Rule names match across the two languages.

## Bloaters

| Smell | Rule | Threshold |
| --- | --- | --- |
| Long Method | `no-long-method` | `max_statements` / `maxStatements`, default 20 |
| Large Class | `no-large-class` | `max_methods` / `maxMethods`, default 10; `max_attributes` / `maxFields`, default 10 |
| Primitive Obsession | `no-primitive-obsession` | `max_same_type` / `maxSameType`, default 2 |
| Long Parameter List | `no-long-parameter-list` | `max_parameters` / `maxParameters`, default 4 |
| Data Clumps | `no-data-clumps` | `min_group` / `minGroup`, default 3 |

## Object-Orientation Abusers

| Smell | Rule | Threshold |
| --- | --- | --- |
| Alternative Classes with Different Interfaces | **no rule** — see below | |
| Refused Bequest | `no-refused-bequest` | |
| Switch Statements | `no-type-code-switch` | `min_branches` / `minBranches`, default 3 |
| Temporary Field | `no-temporary-field` | |

## Change Preventers

| Smell | Rule |
| --- | --- |
| Divergent Change | **no rule** — see below |
| Shotgun Surgery | **no rule** — see below |
| Parallel Inheritance Hierarchies | **no rule** — see below |

## Dispensables

| Smell | Rule | Threshold |
| --- | --- | --- |
| Comments | `no-commented-out-code` | |
| Duplicate Code | `no-duplicate-code` | `min_statements` / `minStatements`, default 3 |
| Data Class | `no-data-class` | |
| Dead Code | `no-unreachable-code` | |
| Lazy Class | `no-lazy-class` | |
| Speculative Generality | `no-unused-parameter` | |

## Couplers

| Smell | Rule | Threshold |
| --- | --- | --- |
| Feature Envy | `no-feature-envy` | `min_accesses` / `minAccesses`, default 5 |
| Inappropriate Intimacy | `no-inappropriate-intimacy` (TypeScript); `no-protected-member-access` in the Python correctness group | |
| Incomplete Library Class | **no rule** — see below | |
| Message Chains | `no-message-chains` | `max_links` / `maxLinks`, default 3; a chain rooted at `self`/`this` counts |
| Middle Man | `no-middle-man` | `min_methods` / `minMethods`, default 2 |

## Where a rule covers part of a smell

Three smells are broader than any single check, so the rule takes the slice a parser can see and the name says which slice:

- **Comments** covers commented-out code. A comment that explains what confusing code does is a judgement call about the prose, which a linter cannot make; a comment that is switched-off code is recognisable, and the history already keeps it.
- **Speculative Generality** covers parameters nobody reads. Abstractions built for a future that never arrived usually need the whole codebase, and often the roadmap, to identify; an argument every caller passes and the body ignores is visible in one function.
- **Dead Code** covers statements after `return`, `raise`/`throw`, `break`, or `continue`. Unused modules and exports need whole-program reachability, which a per-file checker does not have. Your bundler or `ruff`/`ts-prune` covers that half.

## The five smells with no rule

- **Alternative Classes with Different Interfaces** needs to judge that two classes do the same job under different names. Same-named methods with different signatures are not evidence of it, and a rule built on that would report ordinary unrelated code.
- **Divergent Change** and **Shotgun Surgery** are both defined by how a file changes over time: one class edited for many reasons, or one reason spreading edits across many files. The evidence is in version control history, not in the syntax tree.
- **Parallel Inheritance Hierarchies** needs the class graph of the whole program, across files, to see that adding a subclass in one hierarchy forces one in another.
- **Incomplete Library Class** is about a third-party class you cannot change. Recognising it means knowing which imports are yours and what you wish they did.

Reporting on any of these from a single parsed file would mean guessing, and a guess in a lint rule is a false positive someone has to argue with.

## Thresholds are opinions

Every threshold above is a default, not a finding. Twenty statements is not the point at which a function becomes wrong; it is where this project asks you to look. Set the numbers to what your team already agrees on, and treat a rule you constantly override as a rule to turn off rather than one to work around.

`no-feature-envy` in particular is a heuristic that reads the shape of a method, not its meaning. It is right about application code and wrong about code that walks a foreign tree, which is why slop-guard's own Python checker disables it for itself, with the reason recorded in `languages/python/pyproject.toml`.
