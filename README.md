# slop-guard

slop-guard reads your code and points out the places where it quietly hides a guess.

It is a **linter**: a program that reads code and reports problems, the way a spellchecker reads a document. Your editor probably runs one already. slop-guard adds a set of checks that ordinary linters do not make.

## The problem it catches

Code often says less than it could. A programmer, or an AI assistant writing code quickly, will label a piece of data "anything" rather than "a customer", because "anything" always compiles and never complains. Later, someone reads that line and cannot tell what is actually in there. The program still runs, so nothing warns anybody, and the guess sits in the code until it causes a bug.

slop-guard's rules look for exactly that shape:

- A function that accepts "anything" instead of naming what it needs.
- A claim that a value is a customer, with nothing in the code that ever checked.
- A name like `data` or `shape` that describes nothing about the thing it holds.
- A test that fakes the surrounding program, so it proves less than it appears to.

It also reports **code smells** — a well-known catalogue of shapes that make code harder to change, such as a function that has grown too long to follow, a list of parameters nobody can keep straight, or the same block of code copied into two places.

Every report says what the code fails to prove and what to do instead. None of them suggests turning the rule off.

## What you get

Two sets of checks, one per language:

| Language | Checks | Details |
| --- | --- | --- |
| TypeScript and JavaScript | 34 rules | [languages/typescript/README.md](languages/typescript/README.md) |
| Python | 75 rules | [languages/python/README.md](languages/python/README.md) |

Both carry the same code smell rules, under the same names. The two pages above list every rule with an example of the code it rejects.

The rules become yours once installed. slop-guard copies them into your project rather than adding a dependency you cannot see, so you can read them, change the limits, and delete the ones your team disagrees with. Nothing phones home, and nothing updates behind your back.

## Installing it

The easiest way is to let your AI coding assistant do it. slop-guard ships as a **skill**: a set of written instructions an assistant can follow. One command adds it to Claude Code, opencode, or Codex:

```bash
npx skills add gcuder/slop-guard
```

Then ask the assistant, in your own words. Two requests do different things:

- **"Run the slop check on this repository."** It scans and reports what the rules find, changing nothing. Nothing has to be installed in the project first, and both languages are covered. The first TypeScript scan on a machine downloads the linter into `~/.cache/slop-guard/`; after that it works offline.
- **"Set up slop-guard in this project."** It works out which languages you use, copies the right checks in, wires them into the checks your project already runs, and confirms the result. That wiring includes a commit hook when your project already manages one, so the checks run without anyone remembering to run them. It will not install a hook tool you do not already use; it asks first.

A scan is reversible and a setup is not, so if the request could mean either, the instructions tell the assistant to scan first and offer the setup afterwards.

To place the files yourself instead, copy the `skills/install-slop-guard/` folder into the directory your assistant reads:

| Assistant | Just this project | Every project |
| --- | --- | --- |
| [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) | `.claude/skills/install-slop-guard/` | `~/.claude/skills/` |
| [opencode](https://opencode.ai/docs/skills/) | `.opencode/skills/install-slop-guard/` | `~/.config/opencode/skills/` |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills/install-slop-guard/` | `~/.agents/skills/` |

opencode also reads `.claude/skills/`, so a Claude Code install already works there.

One caveat: after copying the checks, the instructions point the assistant at a setup guide for that language. Assistants differ in how reliably they follow that pointer. If the setup looks half-finished, name the guide in your next message — `references/python.md` or `references/typescript.md`.

## Doing it without an assistant

To scan, run either script from the project you want checked. Each one covers every language it finds:

```bash
node skills/install-slop-guard/scripts/scan.mjs src
python3 skills/install-slop-guard/scripts/scan.py src
```

They report and change nothing. Add `--language python` or `--language typescript` to check just one, and `--offline` to skip the one-time linter download.

To install, the copying is done by two more scripts that take the same options. Run whichever one your machine can:

```bash
node skills/install-slop-guard/scripts/install.mjs --detect   # say what it would install
node skills/install-slop-guard/scripts/install.mjs            # install it
```

```bash
python3 skills/install-slop-guard/scripts/install.py --detect
python3 skills/install-slop-guard/scripts/install.py
```

`--detect` looks for the signs of each language: a project file such as `package.json` or `pyproject.toml`, or any source file of that language. It reports what it found and changes nothing. Copying the files is all these scripts do; the setup that follows is on each language's page, linked in the table above.

## Where the rules come from

Some rules are slop-guard's own position on writing code that records what it knows. The rest come from two published catalogues, and two documents record which rule covers which entry, including the entries with no rule and the reason why:

- [`code-smells.md`](code-smells.md) — the [refactoring.guru code smells](https://refactoring.guru/refactoring/smells), for both languages. Five of the twenty-two have no rule: some can only be spotted from a project's history, and some need a judgement no program can make.
- [`languages/python/anti-patterns.md`](languages/python/anti-patterns.md) — [The Little Book of Python Anti-Patterns](https://docs.quantifiedcode.com/python-anti-patterns/index.html). Three entries have no rule: two describe Python 2, which this checker does not support, and one describes a mistake Python itself refuses to run.

Where a catalogue's advice has aged badly, the rule says so rather than repeating it.

---

## For contributors

### Repository layout

```
languages/
  python/          the Python checker: src/, tests/, pyproject.toml, check.sh, README.md
  typescript/      the Oxlint plugin: src/, tsconfig.json, package.json, check.sh, README.md
code-smells.md     the refactoring.guru catalogue, mapped to rules in both languages
scripts/
  check.mjs        runs every languages/*/check.sh, then verifies the skill's copies
  sync-skill-assets.mjs
skills/install-slop-guard/
  SKILL.md                      detect, then follow the guide for each detected language
  languages.json                markers, extensions, asset directory, and target path per language
  scripts/install.mjs           Node runner
  scripts/install.py            Python runner, same flags and same registry
  references/typescript.md      how to configure the Oxlint plugin
  references/python.md          how to configure the Python checker
  references/adding-a-language.md
  assets/typescript/            synced copy of languages/typescript/src/
  assets/python/                synced copy of languages/python/src/slop_guard/
```

Each language pack owns its own source, tests, tooling configuration, and `check.sh`. Nothing at the repository root is specific to one language: `scripts/check.mjs` discovers packs by looking for `languages/*/check.sh`, and the skill's two installer runners read `languages.json` rather than hard-coding any language. The directory name under `languages/` is the language id, and it matches the `assets` directory the skill installs from; keep those two names the same.

### Development

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

### Adding a language

Adding a language is data plus files, never a change to either runner or to `scripts/check.mjs`: create `languages/<id>/` with the rules, their tests, and a `check.sh`; add a bundle to `scripts/sync-skill-assets.mjs`; add an entry to `languages.json`; write `references/<id>.md`; and add a CI job. `skills/install-slop-guard/references/adding-a-language.md` covers each step and the conventions a new pack should keep.

## License

MIT
