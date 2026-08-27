#!/usr/bin/env node
// Run every language pack's own checks, then verify the skill's bundled copies.
// Adding a language means adding languages/<id>/check.sh, not editing this file.
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const languages = readdirSync(join(root, "languages"), { withFileTypes: true })
  .filter((entry) => entry.isDirectory() && existsSync(join(root, "languages", entry.name, "check.sh")))
  .map((entry) => entry.name)
  .sort();

const failed = [];
for (const language of languages) {
  console.log(`\n== ${language} ==`);
  const result = spawnSync("sh", [join(root, "languages", language, "check.sh")], { stdio: "inherit" });
  if (result.status !== 0) failed.push(language);
}

console.log("\n== skill assets ==");
const assets = spawnSync(process.execPath, [join(root, "scripts/sync-skill-assets.mjs"), "--check"], {
  stdio: "inherit",
});
if (assets.status !== 0) failed.push("skill assets");

if (failed.length > 0) {
  console.error(`\nFailed: ${failed.join(", ")}`);
  process.exit(1);
}
console.log(`\nAll checks passed across ${languages.length} language pack(s).`);
