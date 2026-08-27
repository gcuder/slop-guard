// Language detection shared by the installer and the scanner.
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
export const registry = JSON.parse(readFileSync(join(skillRoot, "languages.json"), "utf8"));

const FILE_LIMIT = 20000;

function sourceExtensions(root, excluded) {
  const found = [];
  const queue = [root];
  while (queue.length > 0 && found.length < FILE_LIMIT) {
    const directory = queue.shift();
    let entries;
    try {
      entries = readdirSync(directory, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (!excluded.has(entry.name)) queue.push(join(directory, entry.name));
      } else if (found.length < FILE_LIMIT) {
        found.push(extname(entry.name));
      }
    }
  }
  return found;
}

/** Report which registered languages a directory appears to contain, most source files first. */
export function detect(root) {
  const excluded = new Set(registry.exclude);
  const extensions = sourceExtensions(root, excluded);
  return registry.languages
    .map((language) => {
      const markers = language.markers.filter((marker) => existsSync(join(root, marker)));
      const sources = extensions.filter((extension) => language.extensions.includes(extension)).length;
      return { language, markers, sources, detected: markers.length > 0 || sources > 0 };
    })
    .filter((result) => result.detected)
    .sort((left, right) => right.sources - left.sources);
}

/** Look up one language by its id, or throw with the ids this skill knows. */
export function language(id) {
  const found = registry.languages.find((entry) => entry.id === id);
  if (found === undefined) {
    const known = registry.languages.map((entry) => entry.id).join(", ");
    throw new Error(`Unknown language ${id}. This skill supports: ${known}.`);
  }
  return found;
}
