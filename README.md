# slop-guard

Opinionated lint rules that reject low-evidence and low-signal code in TypeScript, JavaScript, and Python.

This project is meant to be vendored, not treated as a fixed dependency. Copy the rules into your repository, read them, and change them to match your team's standards. The bundled agent skill handles the initial copy and configuration; after that, the vendored files are yours to maintain and make your own.

One skill covers every language. There is a rule pack per language, and the skill works out which ones a repository needs:

| Pack | What it is | Rules | Reference |
| --- | --- | --- | --- |
| **TypeScript and JavaScript** | an Oxlint plugin, plus two opt-in plugins | 15 generic, 1 Effect, 18 code smells | [languages/typescript/README.md](languages/typescript/README.md) |
| **Python** | a standalone `ast` checker with no third-party dependencies, running alongside Ruff, mypy, or pyright | 75 in seven groups | [languages/python/README.md](languages/python/README.md) |

Each pack README covers installing it by hand, configuring it, every rule it carries, and an example of what each rule rejects.

Both packs carry the same code smell rules under the same names. Two documents map the rules to the catalogues they come from:

- [`code-smells.md`](code-smells.md) — the refactoring.guru code smells, for both languages, including the five with no rule and why.
- [`languages/python/anti-patterns.md`](languages/python/anti-patterns.md) — The Little Book of Python Anti-Patterns, including the three entries with no rule and why.

Every pack enforces the same idea: a type or a name should record evidence the program actually has. Parse values where they enter the program, name what they are, and keep that name.

## Install with an agent skill

```bash
npx skills add gcuder/slop-guard
```

Then ask your coding agent to install or configure slop-guard in the current repository. You do not name a language. The skill detects which languages the repository uses, vendors the matching rule packs, reads each pack's own reference for how to configure it, wires it into the checks the repository already runs, and validates the result. A repository with both TypeScript and Python gets both packs in one pass.

Detection reads `skills/install-slop-guard/languages.json`: a language counts as present when a marker file such as `package.json` or `pyproject.toml` sits at the repository root, or when the tree holds at least one source file with that language's extension. You can drive the installer yourself:

```bash
node skills/install-slop-guard/scripts/install.mjs --detect   # what would be installed
node skills/install-slop-guard/scripts/install.mjs --list     # every supported language
node skills/install-slop-guard/scripts/install.mjs            # install every detected pack
node skills/install-slop-guard/scripts/install.mjs --language python --target tools/slop_guard
```

There is an identical `scripts/install.py` for machines without Node, and neither runner needs the other's runtime.

## Repository layout

```
languages/
  python/          canonical Python checker: src/, tests/, pyproject.toml, check.sh, README.md
  typescript/      canonical Oxlint plugin: src/, tsconfig.json, package.json, check.sh, README.md
code-smells.md     the refactoring.guru catalogue, mapped to rules in both languages
scripts/
  check.mjs        runs every languages/*/check.sh, then verifies the skill's copies
  sync-skill-assets.mjs
skills/install-slop-guard/
  SKILL.md                      detect, then follow the reference for each detected language
  languages.json                markers, extensions, asset directory, and target path per language
  scripts/install.mjs           Node runner
  scripts/install.py            Python runner, same flags and same registry
  references/typescript.md      how to configure the Oxlint plugin
  references/python.md          how to configure the Python checker
  references/adding-a-language.md
  assets/typescript/            synced copy of languages/typescript/src/
  assets/python/                synced copy of languages/python/src/slop_guard/
```

Each pack documents itself: [languages/typescript/README.md](languages/typescript/README.md) and [languages/python/README.md](languages/python/README.md) carry the install steps, configuration, rule list, and examples for their language, and [languages/python/anti-patterns.md](languages/python/anti-patterns.md) sits with the pack whose catalogue it maps.

Each language pack owns its own source, tests, tooling configuration, and `check.sh`. Nothing at the repository root is specific to one language: `scripts/check.mjs` discovers packs by looking for `languages/*/check.sh`, and the skill's two installer runners read `languages.json` rather than hard-coding any language.

The directory name under `languages/` is the language id, and it matches the `assets` directory the skill installs from. Keep those two names the same.

## Development

Run everything:

```bash
node scripts/check.mjs
```

That runs each pack's own checks and then verifies the skill's bundled copies. To work on one pack, use its directory directly:

```bash
cd languages/typescript && pnpm install && ./check.sh
cd languages/python && ./check.sh
```

The Python pack needs no installation step. `languages/typescript/src/` and `languages/python/src/slop_guard/` are canonical; after changing production source, run `node scripts/sync-skill-assets.mjs`, and CI checks that the skill's bundled copies remain identical.

The Python checker disables four of its own rules on its own source, and `languages/python/pyproject.toml` records why for each: it walks Python's `ast`, a closed union that `isinstance` genuinely discriminates and whose nodes its methods necessarily read more than their own object, and it carries per-rule options straight from TOML, where the value type is open by definition. Application code should not copy those exemptions.

## Adding a language

Adding a language is data plus files, never a change to either runner or to `scripts/check.mjs`: create `languages/<id>/` with the rules, their tests, and a `check.sh`; add a bundle to `scripts/sync-skill-assets.mjs`; add an entry to `languages.json`; write `references/<id>.md`; and add a CI job. `skills/install-slop-guard/references/adding-a-language.md` covers each step and the conventions a new pack should keep.


## License

MIT
