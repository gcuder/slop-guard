---
name: install-slop-guard
description: Scan a repository for slop, anti-patterns, and code smells, or install and configure the slop-guard lint rules that find them. Detects TypeScript, JavaScript, and Python automatically. Use whenever a user asks to run a slop check, scan or review code for AI slop, anti-patterns, or code smells, add slop-guard, add anti-pattern lint rules, copy the slop-guard plugin or checker, configure opinionated lint rules, or migrate an existing local slop-guard setup.
---

# slop-guard

Two jobs live here, and they are different requests:

- **Scan** — report what the rules find, and change nothing. Follow "Scanning" below.
- **Install** — vendor the rules into the repository and wire them into its checks. Follow "Installing" below.

Read the request before choosing. "Run the slop check", "scan this repo", "what would slop-guard find here", and "review this for anti-patterns" are scans. "Add slop-guard", "set this up", and "configure the rules" are installs. When the wording could mean either, scan first and offer the install with the finding count in hand: a scan is reversible and an install is not.

## Scanning

A scan needs nothing in the target repository. The rules run from this skill, and both languages are covered.

1. Run the scanner from the repository you are checking, with whichever runtime the machine has:

   ```bash
   node <skill-directory>/scripts/scan.mjs src
   # or
   python3 <skill-directory>/scripts/scan.py src
   ```

   Either runner scans every language it detects and hands the one it cannot run itself to the other runtime, so both cover TypeScript, JavaScript, and Python. Pass paths to narrow the scan; with none it scans the working directory. `--language typescript` or `--language python` restricts it to one pack.

   The Python rules run immediately. The TypeScript rules are an Oxlint plugin, so the first scan on a machine installs the linter into `~/.cache/slop-guard/` and reuses it afterwards: that first run needs `npm` and network access, and later runs need neither. `--offline` skips the preparation and reports TypeScript as not scanned rather than reaching for the network.

   Flags the Python checker understands pass straight through: `--select` and `--ignore` take rule names and `group:<name>` tokens, `--format json` prints machine-readable findings, and `--list-rules` prints every rule with its group and source.

2. Report the findings grouped by rule, most frequent first, with the count for each and one example location. Name the rule that would silence a whole group before the user asks. Do not paste hundreds of lines; a repository seeing these rules for the first time will produce many findings, and the shape of them matters more than the list.

3. State plainly what the scan did not cover: any language the runner reported as unscanned, and any path excluded by the repository's `[tool.slop-guard]` configuration. Never report a clean result for a language that was never checked.

4. Offer the next step rather than taking it: fixing findings, installing the rules so they run in CI, or narrowing the selection to one group. Do not edit files during a scan, and do not install anything into the repository.

## Installing

Detect which languages the current repository contains, vendor the matching rule pack for each one, and integrate each pack with the checks the repository already runs. The user does not choose a language; this skill works it out. Preserve unrelated work and adapt to the project's existing tooling.

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
