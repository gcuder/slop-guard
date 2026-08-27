# Repository guidance

- `languages/<id>/` holds one self-contained rule pack: its source, tests, tooling configuration, and a `check.sh` that runs its checks. `languages/typescript/` is the Oxlint plugin; `languages/python/` is the standalone `ast` checker.
- Nothing at the repository root may be specific to one language. `scripts/check.mjs` discovers packs by looking for `languages/*/check.sh`, and `skills/install-slop-guard/` routes over `languages.json`; adding a language means adding data and files. See `skills/install-slop-guard/references/adding-a-language.md`.
- The directory name under `languages/` is the language id and matches the `assets` directory name the skill installs from. Keep them the same.
- Keep rules generic and suitable for reuse across repositories. Do not add application-specific names, paths, or exceptions.
- Use Oxlint's ESTree API on the TypeScript side and the standard library `ast` module on the Python side. Do not add another production parser, and keep vendored checkers free of third-party dependencies.
- Python rules live in `languages/python/src/slop_guard/rules/<group>/`, one rule per module, and every rule declares its `group`. A rule taken from an external catalogue also declares `reference`, the URL of the entry it enforces, and `languages/python/anti-patterns.md` records the mapping. Add a group by creating the package and listing it in `rules/__init__.py`; put it in `OPT_IN_GROUPS` when it only applies to one framework. The Python pack itself stays framework-neutral.
- The code smell rules are the same set in both languages, under the same names; `code-smells.md` is the shared map. A change to one language's smell rule needs the matching change in the other.
- Two rules must never report the same code. When a new rule overlaps an existing one, narrow the existing rule and say in both descriptions which one owns the case.
- Add focused RuleTester or `RuleTestCase` coverage for semantic rule changes.
- Run `node scripts/sync-skill-assets.mjs` after changing production source.
- Run `node scripts/check.mjs` before committing.
