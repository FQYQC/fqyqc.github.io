#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/fqyqc-hugo-check.XXXXXX")"

cleanup() {
  rm -rf -- "$BUILD_ROOT"
}
trap cleanup EXIT

"$PROJECT_ROOT/scripts/build.sh" \
  --destination "$BUILD_ROOT/public" \
  --cacheDir "$BUILD_ROOT/cache"

echo "Hugo production build passed."
