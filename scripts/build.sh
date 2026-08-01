#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

EXPECTED_HUGO_VERSION="$(tr -d '[:space:]' < .hugo-version)"

if ! command -v hugo >/dev/null 2>&1; then
  echo "error: Hugo is not installed (expected v${EXPECTED_HUGO_VERSION} extended)." >&2
  exit 1
fi

HUGO_VERSION_OUTPUT="$(hugo version)"
case "$HUGO_VERSION_OUTPUT" in
  "hugo v${EXPECTED_HUGO_VERSION}"*) ;;
  *)
    echo "error: expected Hugo v${EXPECTED_HUGO_VERSION}, found: ${HUGO_VERSION_OUTPUT}" >&2
    exit 1
    ;;
esac

case "$HUGO_VERSION_OUTPUT" in
  *extended*) ;;
  *)
    echo "error: the Hugo extended edition is required." >&2
    exit 1
    ;;
esac

while IFS= read -r SUBMODULE_STATUS; do
  case "$SUBMODULE_STATUS" in
    -*)
      echo "error: a Git submodule is not initialized; run: git submodule update --init --recursive" >&2
      exit 1
      ;;
    +*)
      echo "error: a Git submodule is not at the commit recorded by this repository." >&2
      exit 1
      ;;
    U*)
      echo "error: a Git submodule has unresolved merge conflicts." >&2
      exit 1
      ;;
  esac
done < <(git submodule status --recursive)

exec hugo \
  --gc \
  --minify \
  --panicOnWarning \
  --noBuildLock \
  "$@"
