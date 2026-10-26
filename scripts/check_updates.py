#!/usr/bin/env python3
"""Validate data/updates.toml and remind when site changes lack an update entry.

Errors (exit 1): malformed releases, or zh/en note lists of different lengths.
Warning only: a layout or structure commit ([Lot.] / [Str.]) is newer than the
latest release date, i.e. a site change probably has no entry yet.

Usage: check_updates.py <project-root>
"""

import datetime
import subprocess
import sys
import tomllib
from pathlib import Path

SITE_PREFIXES = ("[Lot.]", "[Str.]")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    data_file = root / "data" / "updates.toml"
    with data_file.open("rb") as handle:
        releases = tomllib.load(handle).get("releases")
    if not isinstance(releases, list) or not releases:
        fail(f"{data_file} must define at least one [[releases]] entry")

    latest = None
    for index, release in enumerate(releases, start=1):
        version, date = release.get("version"), release.get("date")
        zh, en = release.get("zh"), release.get("en")
        label = version or f"#{index}"
        if not isinstance(version, str) or not version.strip():
            fail(f"release #{index} has no version")
        if not isinstance(date, datetime.date):
            fail(f"release {label} needs a date like 2026-10-25 (unquoted)")
        if not isinstance(zh, list) or not isinstance(en, list) or not zh:
            fail(f"release {label} needs non-empty zh and en lists")
        if len(zh) != len(en):
            fail(f"release {label} has {len(zh)} zh notes but {len(en)} en notes")
        latest = date if latest is None or date > latest else latest

    try:
        log = subprocess.run(
            ["git", "-C", str(root), "log", "--no-merges", "--format=%cs %s", "-n", "200"],
            capture_output=True, text=True, check=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return

    newer = []
    for line in log:
        day, _, subject = line.partition(" ")
        if not subject.startswith(SITE_PREFIXES):
            continue
        try:
            when = datetime.date.fromisoformat(day)
        except ValueError:
            continue
        if when > latest:
            newer.append(f"  {day} {subject}")
    if newer:
        print(
            "warning: these site changes are newer than the latest entry in data/updates.toml "
            f"({latest}); consider adding them:\n" + "\n".join(newer),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
