#!/usr/bin/env python3
"""Validate data/friends.toml and its rendered friend pages in a Hugo build.

Usage: check_friends.py <project-root> <public-dir>
"""

import sys
import tomllib
from pathlib import Path

PAGES = ("friends/index.html", "zh-cn/friends/index.html")
LANGS = ("en", "zh-cn")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 3:
        fail("usage: check_friends.py <project-root> <public-dir>")
    root, public = Path(sys.argv[1]), Path(sys.argv[2])

    data_file = root / "data" / "friends.toml"
    with data_file.open("rb") as handle:
        friends = tomllib.load(handle).get("friends")
    if not isinstance(friends, list) or not friends:
        fail(f"{data_file} must define at least one [[friends]] entry")

    seen = set()
    for index, friend in enumerate(friends, start=1):
        name, url = friend.get("name"), friend.get("url")
        if not isinstance(name, str) or not name.strip():
            fail(f"friend #{index} in {data_file} has no name")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            fail(f"friend {name!r} needs an http:// or https:// url")
        if url in seen:
            fail(f"friend url {url} is listed more than once")
        seen.add(url)
        icon = friend.get("icon")
        if icon is not None:
            if not isinstance(icon, str) or not icon.startswith("/"):
                fail(f"friend {name!r} icon must be a site path under static/, such as /images/friends/x.png")
            if not (root / "static" / icon.lstrip("/")).is_file():
                fail(f"friend {name!r} icon file is missing: static{icon}")
            if not (public / icon.lstrip("/")).is_file():
                fail(f"friend {name!r} icon was not copied into the build: {icon}")
        description = friend.get("description", {})
        if not isinstance(description, dict) or set(description) - set(LANGS):
            fail(f"friend {name!r} description may only contain {', '.join(LANGS)}")

    for page in PAGES:
        path = public / page
        if not path.is_file():
            fail(f"friend page was not generated: {page}")
        html = path.read_text(encoding="utf-8")
        missing = [url for url in seen if url not in html]
        if missing:
            fail(f"{page} is missing friend links: {', '.join(missing)}")


if __name__ == "__main__":
    main()
