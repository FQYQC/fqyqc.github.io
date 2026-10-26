#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/fqyqc-hugo-check.XXXXXX")"

cleanup() {
  rm -rf -- "$BUILD_ROOT"
}
trap cleanup EXIT

# 根据文章的 featured 标记刷新参考用的 docs/featured.md（首页本身直接读取标记）
python3 -I "$PROJECT_ROOT/scripts/sync_featured.py" "$PROJECT_ROOT"

"$PROJECT_ROOT/scripts/build.sh" \
  --destination "$BUILD_ROOT/public" \
  --cacheDir "$BUILD_ROOT/cache"

for SEARCH_INDEX in \
  "$BUILD_ROOT/public/index.json" \
  "$BUILD_ROOT/public/zh-cn/index.json"; do
  if [[ ! -s "$SEARCH_INDEX" ]] || ! grep -q '"objectID"' "$SEARCH_INDEX"; then
    echo "error: local search index is missing or empty: ${SEARCH_INDEX}" >&2
    exit 1
  fi
  if grep -q '"/thecove/' "$SEARCH_INDEX"; then
    echo "error: protected Cove content leaked into the search index: ${SEARCH_INDEX}" >&2
    exit 1
  fi
done

python3 -I "$PROJECT_ROOT/scripts/check_friends.py" "$PROJECT_ROOT" "$BUILD_ROOT/public"

# 校验网站更新日志；有比最新一条更新更晚的 [Lot.]/[Str.] 提交时只提醒，不失败
python3 -I "$PROJECT_ROOT/scripts/check_updates.py" "$PROJECT_ROOT"
for UPDATES_PAGE in "$BUILD_ROOT/public/updates/index.html" "$BUILD_ROOT/public/zh-cn/updates/index.html"; do
  if ! grep -q 'site-update-version' "$UPDATES_PAGE"; then
    echo "error: site updates page was not generated: ${UPDATES_PAGE#$BUILD_ROOT/public/}" >&2
    exit 1
  fi
done

echo "Hugo production build passed."
