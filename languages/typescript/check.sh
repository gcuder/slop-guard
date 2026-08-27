#!/bin/sh
# Every language pack exposes its checks here, so the root runner needs no per-language knowledge.
set -e
cd "$(dirname "$0")"
if command -v pnpm >/dev/null 2>&1; then
  pnpm check
else
  npx --no-install oxlint src
  for test in src/rules/*.test.ts src/effect/rules/*.test.ts src/smells/rules/*.test.ts; do
    npx --no-install tsx "$test"
  done
  npx --no-install tsc --noEmit
fi
