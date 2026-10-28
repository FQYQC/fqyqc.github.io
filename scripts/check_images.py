#!/usr/bin/env python3
"""Validate data/assets_optimized.json (web-sized post images from optimize_images.py).

Fails on malformed entries or keys that are not local /assets/local-assets/ paths; only reports
how many mapped images still lack a web-sized version.

Usage: check_images.py <project-root>
"""

import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: check_images.py <project-root>")
    root = Path(sys.argv[1])
    mapping = json.loads((root / "data" / "assets_mapping.json").read_text(encoding="utf-8"))
    optimized_file = root / "data" / "assets_optimized.json"
    optimized = json.loads(optimized_file.read_text(encoding="utf-8"))
    if not isinstance(optimized, dict):
        fail(f"{optimized_file} must be a JSON object")

    for key, entry in optimized.items():
        if key not in mapping and not key.startswith("/assets/local-assets/"):
            fail(f"{key} must be a local /assets/local-assets/ path used by a post")
        if not isinstance(entry, dict):
            fail(f"{key} must map to an object with avif, jpg, width and height")
        for field, suffix, required in (("avif", ".avif", True), ("jpg", ".jpg", False)):
            url = entry.get(field)
            if url is None and not required:
                continue  # optional JPEG fallback; browsers without AVIF get the original
            if not isinstance(url, str) or not url.startswith("https://") or not url.endswith(suffix):
                fail(f"{key} {field} must be an https:// URL ending in {suffix}")
        for field in ("width", "height"):
            if not isinstance(entry.get(field), int) or entry[field] <= 0:
                fail(f"{key} {field} must be a positive integer")

    pending = len(set(mapping) - set(optimized))
    if pending:
        print(f"note: {pending} of {len(mapping)} post image(s) have no web-sized version yet; "
              "run scripts/optimize_images.py build, upload optimized-images/, then link")


if __name__ == "__main__":
    main()
