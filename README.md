# slop-guard

[![skills.sh](https://skills.sh/b/gcuder/slop-guard)](https://skills.sh/gcuder/slop-guard)

Opinionated lint rules that reject low-evidence code, published anti-patterns, and known code smells in TypeScript, JavaScript, and Python.

The rules look for code that claims less than it could: a value typed as "anything" rather than named, an assertion nothing checked, a function too long to follow, the same block copied twice. Each finding says what the code fails to prove and what to do instead, and none of them suggests turning the rule off.

This project is meant to be vendored, not treated as a fixed dependency. Copy the rules into your repository, read them, and change them to match your team's standards. The bundled agent skill handles the initial copy and configuration; after that, the vendored files are yours to maintain and make your own.

## Install with an agent skill

```bash
npx skills add gcuder/slop-guard
```

One skill covers every language, and it works for Claude Code, opencode, and Codex. To place it by hand, copy `skills/install-slop-guard/` into the directory your agent reads:

| Agent | This project | Every project |
| --- | --- | --- |
| [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) | `.claude/skills/install-slop-guard/` | `~/.claude/skills/` |
| [opencode](https://opencode.ai/docs/skills/) | `.opencode/skills/install-slop-guard/` | `~/.config/opencode/skills/` |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills/install-slop-guard/` | `~/.agents/skills/` |

opencode also reads `.claude/skills/`, so a Claude Code install already works there.

## Prompting the agent

You never name a language; the skill detects what the repository uses.

```
set up slop-guard in this project
```

Copies the rules for every detected language, merges them into the existing lint configuration, wires them into the repository's check command, its CI job, and its commit hook when it already manages one, then runs the checks and reports what it changed.

```
run the slop check on this repository
```

Scans and reports, writing nothing. Nothing has to be installed first. The first TypeScript scan on a machine downloads the linter into `~/.cache/slop-guard/`; later scans work offline.

```
run the slop check on src and fix what it finds, without weakening any types or disabling rules
```

Scans, then fixes. The second clause matters: the messages refuse to suggest suppression, but an agent under pressure may still reach for a wider type.

```
scan this repo with the slop-guard code smell rules only
```

Narrows to one group. Any rule name or `group:<name>` works — `evidence`, `correctness`, `readability`, `maintainability`, `security`, `performance`, `smells`.

## Scan without installing

Either runner scans every language it detects, and neither needs the other's runtime:

```bash
node skills/install-slop-guard/scripts/scan.mjs src
python3 skills/install-slop-guard/scripts/scan.py src
```

Add `--language python`, `--select group:smells`, `--format json`, or `--offline` to skip the one-time linter download.

## Manual local installation

```bash
node skills/install-slop-guard/scripts/install.mjs --detect   # what it would install
node skills/install-slop-guard/scripts/install.mjs            # install every detected pack
```

There is an identical `scripts/install.py`. Copying is all either runner does; the configuration that follows is documented per language:

- [languages/typescript/README.md](languages/typescript/README.md) — the Oxlint config, the opt-in Effect and code smell plugins, and every rule with an example.
- [languages/python/README.md](languages/python/README.md) — the `[tool.slop-guard]` config, the seven rule groups, and every rule with an example.

## Rules

| Pack | What it is | Rules |
| --- | --- | --- |
| TypeScript and JavaScript | an Oxlint plugin, plus opt-in Effect and code smell plugins | 15 generic, 1 Effect, 18 smells |
| Python | a standalone `ast` checker with no third-party dependencies | 75 in seven groups |

Both packs carry the same code smell rules under the same names. Two documents map every rule to the catalogue it enforces, including the entries with no rule and why:

- [`code-smells.md`](code-smells.md) — the [refactoring.guru code smells](https://refactoring.guru/refactoring/smells), for both languages.
- [`languages/python/anti-patterns.md`](languages/python/anti-patterns.md) — [The Little Book of Python Anti-Patterns](https://docs.quantifiedcode.com/python-anti-patterns/index.html).

## Repository layout

```
languages/
  python/          the Python checker: src/, tests/, pyproject.toml, check.sh, README.md
  typescript/      the Oxlint plugin: src/, tsconfig.json, package.json, check.sh, README.md
code-smells.md     the refactoring.guru catalogue, mapped to rules in both languages
scripts/
  check.mjs        runs every languages/*/check.sh, then verifies the skill's copies
  sync-skill-assets.mjs
skills/install-slop-guard/
  SKILL.md                      scan or install, depending on what was asked
  languages.json                markers, extensions, target paths, and scan pins per language
  scripts/detect.mjs|.py        language detection, shared by both runners
  scripts/install.mjs|.py       copy the rules into a repository
  scripts/scan.mjs|.py          run the rules without copying anything
  references/                   how to configure each language, and how to add one
  assets/                       synced copies of both packs
```

Each language pack owns its source, tests, tooling configuration, and `check.sh`. Nothing at the repository root is specific to one language: `scripts/check.mjs` finds packs by looking for `languages/*/check.sh`, and the skill's runners read `languages.json`.

## Development

```bash
node scripts/check.mjs
```

That runs each pack's own checks and verifies the skill's bundled copies. To work on one pack, use its directory:

```bash
cd languages/typescript && pnpm install && ./check.sh
cd languages/python && ./check.sh
```

`languages/typescript/src/` and `languages/python/src/slop_guard/` are canonical; after changing production source, run `node scripts/sync-skill-assets.mjs`, and CI checks that the skill's copies stay identical.

The Python checker disables four of its own rules on its own source, and `languages/python/pyproject.toml` records why for each: it walks Python's `ast`, a closed union that `isinstance` genuinely discriminates and whose nodes its methods necessarily read more than their own object, and it carries per-rule options straight from TOML, where the value type is open by definition. Application code should not copy those exemptions.

## Adding a language

Adding a language is data plus files, never a change to either runner or to `scripts/check.mjs`: create `languages/<id>/` with the rules, their tests, and a `check.sh`; add a bundle to `scripts/sync-skill-assets.mjs`; add an entry to `languages.json`; write `references/<id>.md`; and add a CI job. `skills/install-slop-guard/references/adding-a-language.md` covers each step.

## License

MIT
