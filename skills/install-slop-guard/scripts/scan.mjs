#!/usr/bin/env node
// Scan a repository with the bundled rules, changing nothing in it.
// Mirrors scripts/scan.py: either runner scans every detected language, delegating the one it
// cannot run itself to the other runtime.
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join, resolve } from "node:path";

import { detect, language, registry, skillRoot } from "./detect.mjs";

const CACHE = join(process.env.SLOP_GUARD_CACHE ?? join(homedir(), ".cache", "slop-guard"), "typescript");

function parseArguments(argv) {
  const options = { language: null, paths: [], passthrough: [], offline: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--language") options.language = argv[++index];
    else if (argument === "--offline") options.offline = true;
    else if (argument.startsWith("--")) options.passthrough.push(argument);
    else options.paths.push(argument);
  }
  if (options.paths.length === 0) options.paths.push(".");
  return options;
}

function ruleNames(pluginSource) {
  // The plugin lists its rules as `"rule-name": someRule,` inside eslintCompatPlugin.
  return [...readFileSync(pluginSource, "utf8").matchAll(/^\s*"([a-z0-9-]+)":\s*\w+Rule,/gmu)].map(
    (match) => match[1],
  );
}

/** Install the linter once into a cache directory, beside a copy of the rules it loads. */
function prepareCache(scan, offline) {
  const stamp = join(CACHE, "installed.json");
  const wanted = JSON.stringify(scan.packages);
  if (existsSync(stamp) && readFileSync(stamp, "utf8") === wanted) return true;
  if (offline) return false;

  mkdirSync(CACHE, { recursive: true });
  writeFileSync(
    join(CACHE, "package.json"),
    `${JSON.stringify({ name: "slop-guard-scan", private: true, type: "module", dependencies: scan.packages }, null, 2)}\n`,
  );
  console.error(`Preparing the TypeScript linter in ${CACHE} (first run only)...`);
  const install = spawnSync("npm", ["install", "--silent", "--no-audit", "--no-fund"], {
    cwd: CACHE,
    stdio: ["ignore", "ignore", "inherit"],
  });
  if (install.status !== 0) return false;
  rmSync(join(CACHE, "plugin"), { recursive: true, force: true });
  cpSync(join(skillRoot, "assets", "typescript"), join(CACHE, "plugin"), { recursive: true });
  writeFileSync(stamp, wanted);
  return true;
}

function usesPackage(root, name) {
  const manifest = join(root, "package.json");
  if (!existsSync(manifest)) return false;
  try {
    const parsed = JSON.parse(readFileSync(manifest, "utf8"));
    return Boolean(parsed.dependencies?.[name] ?? parsed.devDependencies?.[name]);
  } catch {
    return false;
  }
}

function scanTypescript(paths, passthrough, offline) {
  const entry = language("typescript");
  const scan = entry.scan;
  if (!prepareCache(scan, offline)) {
    console.error(
      "Could not prepare the TypeScript linter. It needs `npm` and, on the first run, network access.",
    );
    return 2;
  }

  const active = scan.plugins.filter(
    (plugin) => plugin.requires === undefined || usesPackage(process.cwd(), plugin.requires),
  );
  const rules = {};
  for (const plugin of active) {
    for (const rule of ruleNames(join(CACHE, "plugin", plugin.entry))) {
      rules[`${plugin.name}/${rule}`] = "error";
    }
  }
  const config = {
    // A scan reports slop-guard's rules. The project's own linter owns everything else.
    categories: { correctness: "off", perf: "off", style: "off", suspicious: "off", pedantic: "off", restriction: "off" },
    ignorePatterns: registry.exclude.map((name) => `${name}/**`),
    jsPlugins: active.map((plugin) => ({
      name: plugin.name,
      specifier: join(CACHE, "plugin", plugin.entry),
    })),
    rules,
  };

  const directory = mkdtempSync(join(tmpdir(), "slop-guard-"));
  const configPath = join(directory, "oxlintrc.json");
  writeFileSync(configPath, JSON.stringify(config, null, 2));
  const result = spawnSync(join(CACHE, "node_modules", ".bin", "oxlint"), [
    "--config",
    configPath,
    ...passthrough,
    ...paths,
  ], { stdio: "inherit" });
  rmSync(directory, { recursive: true, force: true });
  console.error(`Checked TypeScript and JavaScript with ${Object.keys(rules).length} rule(s).`);
  return result.status ?? 2;
}

function scanPython(paths, passthrough) {
  const runner = spawnSync("python3", [join(skillRoot, "scripts", "scan.py"), "--language", "python", ...passthrough, ...paths], {
    stdio: "inherit",
  });
  if (runner.error !== undefined && runner.error !== null) {
    console.error("Could not run the Python checker: python3 is not on PATH.");
    return 2;
  }
  return runner.status ?? 2;
}

function main() {
  const options = parseArguments(process.argv.slice(2));
  const root = resolve(process.cwd());
  const chosen = options.language
    ? [language(options.language)]
    : detect(root).map((result) => result.language);

  if (chosen.length === 0) {
    console.error("No supported language detected here. Run install.mjs --list to see what this skill covers.");
    return 1;
  }

  let status = 0;
  for (const entry of chosen) {
    // The other runner prints the header when it delegates one language to this one.
    if (options.language === null) console.error(`\n== ${entry.name} ==`);
    const code =
      entry.id === "typescript"
        ? scanTypescript(options.paths, options.passthrough, options.offline)
        : scanPython(options.paths, options.passthrough);
    if (code > status) status = code;
  }
  return status;
}

try {
  process.exit(main());
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(2);
}
