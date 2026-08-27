# Adding a language to slop-guard

Both installer runners are language-agnostic: they read `languages.json` and copy a directory. Adding a language means adding data and files, never editing `install.mjs` or `install.py`.

## What a language pack needs

1. **Canonical source in the repository.** Create `languages/<id>/`, next to `languages/typescript/` and `languages/python/`. The directory name is the language id used everywhere else, and the pack owns its source, its tooling configuration, and its dependency manifest; nothing about it belongs at the repository root. Write the rules against the host linter's own API, or as a standalone checker when the language has no plugin system worth using. A standalone checker must depend on nothing outside that language's standard library, because it is vendored into other people's repositories.

2. **Tests next to the source.** Mirror the existing valid/invalid harnesses: `RuleTester` for Oxlint rules, `RuleTestCase` for Python rules. Every rule needs both accepted and rejected snippets.

3. **A `check.sh`.** Add an executable `languages/<id>/check.sh` that changes to its own directory and runs the pack's lint, tests, and self-check. `node scripts/check.mjs` finds it by name, so the root runner needs no knowledge of the language.

4. **A sync bundle.** Add an entry to `bundles` in `scripts/sync-skill-assets.mjs` naming the canonical source, the destination under `skills/install-slop-guard/assets/<id>/`, the file extensions to copy, and a `skip` predicate for test files. `node scripts/sync-skill-assets.mjs` then copies it, and `--check` verifies the copy in CI. Keep the assets directory name equal to the language id.

5. **A registry entry** in `skills/install-slop-guard/languages.json`:

   ```json
   {
     "id": "rust",
     "name": "Rust",
     "assets": "rust",
     "target": "tools/slop-guard",
     "reference": "references/rust.md",
     "entry": "main.rs",
     "host": "standalone checker",
     "markers": ["Cargo.toml"],
     "extensions": [".rs"]
   }
   ```

   `markers` are files that prove the language is used, looked for at the repository root only. `extensions` are counted anywhere outside the shared `exclude` list. A language is detected when it has at least one marker or at least one source file. Keep `markers` to files that genuinely indicate ownership; a lockfile that any dependency could drop in does not qualify.

6. **A reference file** at `references/<id>.md`, following the shape of `typescript.md` and `python.md`: find the existing setup, install dependencies, register and configure, wire into the repository's checks, validate, list the rules, and say how to resolve findings honestly.

7. **A CI job** in `.github/workflows/ci.yml` with `working-directory: languages/<id>` that runs `./check.sh`, plus a section in the repository README.

## Keep the rules recognisably the same

A new language pack should enforce the same idea as the existing ones: a type or a name records evidence the program actually has. Before writing a rule, find its counterpart in the TypeScript or Python pack and keep the name parallel where the concept survives translation — `no-unknown-parameters` became `no-any-parameters`, and `require-safety-comment-for-type-assertion` became `require-safety-comment-for-cast`. Invent a new rule name only for a pattern the other packs have no equivalent of.

Diagnostic messages state what the code fails to prove and what to do instead. They do not scold, and they never suggest suppressing the rule.
