---
name: install-slop-guard
description: Install and configure slop-guard lint rules in a local repository, in whatever languages that repository uses. Detects TypeScript, JavaScript, and Python automatically and applies the matching rule pack. Use whenever a user asks to add slop-guard, add anti-slop or anti-pattern lint rules, copy the slop-guard plugin or checker, configure opinionated lint rules, or migrate an existing local slop-guard setup.
---

# Install slop-guard

Detect which languages the current repository contains, vendor the matching rule pack for each one, and integrate each pack with the checks the repository already runs. The user does not choose a language; this skill works it out. Preserve unrelated work and adapt to the project's existing tooling.

## Procedure

1. Inspect the repository before changing it:
   - Read its agent instructions.
   - Check `git status` and preserve unrelated changes.
   - Check whether slop-guard files, rules, or configuration already exist. Do not overwrite them without reviewing the diff.

2. Detect the languages. Run from the target repository, using whichever runtime the machine has:

   ```bash
   node <skill-directory>/scripts/install.mjs --detect
   # or
   python3 <skill-directory>/scripts/install.py --detect
   ```

   Both runners read the same `languages.json` and print one line per detected language: its id, the evidence that found it, and the reference file to follow. `--list` prints every language this skill supports, whether or not the repository uses it.

   Treat the output as a starting point, not a verdict. A repository with one stray script in a second language does not need that language's rule pack. Confirm the detected set against what the repository actually builds and tests, and say what you concluded.

3. Copy the rule packs. With no arguments the installer vendors every detected language:

   ```bash
   node <skill-directory>/scripts/install.mjs
   ```

   Pass `--language <id>` to install one language, and `--target <path>` with it when the repository has an established tooling layout. The installer refuses to replace an existing destination; only use `--force` after backing up and reviewing existing files.

4. For each installed language, read its reference file under `<skill-directory>/references/` and follow it. The reference holds that language's dependency requirements, configuration format, rule list, and validation commands:

   - TypeScript and JavaScript — `references/typescript.md`
   - Python — `references/python.md`

   Read only the references for the languages you installed. Do not apply one language's configuration advice to another.

5. Run the repository's own checks for each language after configuring it. If findings appear in owned project source, report them and fix them only when the user asked for migration or cleanup. Never silence a rule, weaken its severity, add an unchecked cast or assertion, or launder a type to make a check pass.

6. Review the final diff and clearly report, per language:
   - copied path,
   - dependencies installed, if any,
   - configuration changed,
   - checks run and any remaining findings.

   Also report any language you detected but deliberately skipped, and why.

## Migration guidance

When replacing an older local copy, compare its rules and diagnostics before overwriting. Keep project-specific rules in their own plugin or module rather than editing the vendored ones, so the next sync stays a clean copy. Resolve findings by parsing values at the boundary and naming domain types, not by widening annotations.

## Adding a language

This skill is a router over `languages.json`; neither runner has language-specific code. To cover a new language, see `references/adding-a-language.md`.
