#!/usr/bin/env node
// Detect which languages a repository contains and vendor the matching slop-guard rules.
// Mirrors scripts/install.py; both read languages.json through detect.mjs, so adding a language
// changes neither.
import { cpSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

import { detect, language as lookup, registry, skillRoot } from "./detect.mjs";

function parseArguments(argv) {
  const options = { language: null, target: null, force: false, mode: "install", json: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--language") options.language = argv[++index];
    else if (argument === "--target") options.target = argv[++index];
    else if (argument === "--force") options.force = true;
    else if (argument === "--detect") options.mode = "detect";
    else if (argument === "--list") options.mode = "list";
    else if (argument === "--json") options.json = true;
    else if (argument.startsWith("--")) throw new Error(`Unknown option ${argument}`);
    else options.target = argument;
  }
  return options;
}

function checkDestination(language, target, force) {
  const source = join(skillRoot, "assets", language.assets);
  if (!existsSync(source)) throw new Error(`This skill has no bundled assets for ${language.id}.`);
  if (existsSync(target) && !force) {
    throw new Error(
      `Refusing to overwrite ${target}. Re-run with --force only after reviewing the existing files.`,
    );
  }
}

function install(language, target) {
  const source = join(skillRoot, "assets", language.assets);
  mkdirSync(dirname(target), { recursive: true });
  cpSync(source, target, { recursive: true, force: true });
  return target;
}

function main() {
  const options = parseArguments(process.argv.slice(2));
  const root = process.cwd();

  if (options.mode === "list") {
    for (const language of registry.languages) {
      console.log(`${language.id}\t${language.name}\t${language.host}\t${language.reference}`);
    }
    return 0;
  }

  let chosen = detect(root);
  if (options.language) {
    chosen = [{ language: lookup(options.language), markers: [], sources: 0, detected: true }];
  }

  if (chosen.length === 0) {
    console.error("No supported language detected. Run with --list to see what this skill covers.");
    return 1;
  }

  if (options.mode === "detect") {
    const report = chosen.map((result) => ({
      id: result.language.id,
      name: result.language.name,
      reference: result.language.reference,
      target: result.language.target,
      markers: result.markers,
      sourceFiles: result.sources,
    }));
    if (options.json) console.log(JSON.stringify(report, null, 2));
    else {
      for (const entry of report) {
        const evidence = entry.markers.length > 0 ? entry.markers.join(", ") : `${entry.sourceFiles} source file(s)`;
        console.log(`${entry.id}\t${entry.name}\tdetected via ${evidence}\tread ${entry.reference}`);
      }
    }
    return 0;
  }

  if (options.target && chosen.length > 1) {
    throw new Error("--target applies to one language; pass --language as well.");
  }

  // Check every destination first so a conflict never leaves a half-installed repository.
  const planned = chosen.map((result) => ({
    language: result.language,
    target: resolve(root, options.target ?? result.language.target),
  }));
  for (const step of planned) checkDestination(step.language, step.target, options.force);

  for (const result of planned) {
    const target = result.target;
    install(result.language, target);
    console.log(`Copied the ${result.language.name} rules to ${target}`);
    console.log(`  entry point: ${join(target, result.language.entry)}`);
    console.log(`  next: follow ${join(skillRoot, result.language.reference)}`);
  }
  return 0;
}

try {
  process.exit(main());
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
