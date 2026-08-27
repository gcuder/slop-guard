import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const check = process.argv.includes("--check");

const bundles = [
  {
    source: join(root, "languages/typescript/src"),
    destination: join(root, "skills/install-slop-guard/assets/typescript"),
    extensions: [".ts"],
    skip: (name) => name.endsWith(".test.ts"),
  },
  {
    source: join(root, "languages/python/src/slop_guard"),
    destination: join(root, "skills/install-slop-guard/assets/python"),
    extensions: [".py"],
    skip: (name) => name.startsWith("test_"),
  },
];

function files(directory, bundle) {
  if (!existsSync(directory)) return [];
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) return entry.name === "__pycache__" ? [] : files(path, bundle);
    if (bundle.skip(entry.name)) return [];
    return bundle.extensions.includes(extname(entry.name)) ? [path] : [];
  });
}

// The scanner installs its own copy of the linter, pinned in languages.json. Those pins have to
// match what the pack itself builds against, or a scan and a local run disagree.
function checkScanPins() {
  const registry = JSON.parse(readFileSync(join(root, "skills/install-slop-guard/languages.json"), "utf8"));
  const manifest = JSON.parse(readFileSync(join(root, "languages/typescript/package.json"), "utf8"));
  const pinned = registry.languages.find((entry) => entry.id === "typescript")?.scan?.packages ?? {};
  const declared = { ...manifest.dependencies, ...manifest.devDependencies };
  for (const [name, version] of Object.entries(pinned)) {
    if (declared[name] !== version) {
      throw new Error(
        `languages.json pins ${name}@${version} for scanning, but languages/typescript/package.json declares ${declared[name] ?? "nothing"}.`,
      );
    }
  }
  console.log("Scan pins match the TypeScript pack.");
}

checkScanPins();

for (const bundle of bundles) {
  const label = relative(root, bundle.destination);
  if (check) {
    const expected = files(bundle.source, bundle).map((path) => relative(bundle.source, path)).sort();
    const actual = files(bundle.destination, bundle).map((path) => relative(bundle.destination, path)).sort();
    if (JSON.stringify(expected) !== JSON.stringify(actual)) {
      throw new Error(`${label} differs from its source; run \`pnpm sync:skill-assets\`.`);
    }
    for (const path of expected) {
      const from = readFileSync(join(bundle.source, path), "utf8");
      const to = readFileSync(join(bundle.destination, path), "utf8");
      if (from !== to) {
        throw new Error(`${join(label, path)} differs from its source; run \`pnpm sync:skill-assets\`.`);
      }
    }
    console.log(`${label} matches its source.`);
  } else {
    rmSync(bundle.destination, { recursive: true, force: true });
    mkdirSync(bundle.destination, { recursive: true });
    cpSync(bundle.source, bundle.destination, {
      recursive: true,
      filter: (path) => {
        const name = path.split("/").pop() ?? "";
        if (name === "__pycache__") return false;
        return !bundle.skip(name);
      },
    });
    console.log(`Synced ${label}.`);
  }
}
