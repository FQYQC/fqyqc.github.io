#!/usr/bin/env python3
"""Validate a Chinese/English Hugo post pair without third-party packages."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "title",
    "date",
    "draft",
    "language",
    "description",
    "abstract",
    "categories",
    "tags",
)


@dataclass
class Post:
    path: Path
    metadata: dict[str, Any]
    body: str


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith(("[", "\"", "'")):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value.strip("\"'")
    return value


def read_post(path: Path) -> Post:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"cannot read {path}: {error}") from error

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: expected YAML front matter starting with ---")

    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as error:
        raise ValueError(f"{path}: front matter has no closing ---") from error

    metadata: dict[str, Any] = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not match:
            raise ValueError(f"{path}:{number}: unsupported front matter line: {line}")
        metadata[match.group(1)] = parse_scalar(match.group(2))

    return Post(path=path, metadata=metadata, body="\n".join(lines[end + 1 :]))


def post_stem(path: Path) -> tuple[str, str]:
    if path.name.endswith(".zh-cn.md"):
        return path.name[: -len(".zh-cn.md")], "zh-cn"
    if path.name.endswith(".en.md"):
        return path.name[: -len(".en.md")], "en"
    raise ValueError(f"{path}: expected a .zh-cn.md or .en.md filename")


def markdown_structure(body: str) -> dict[str, list[str]]:
    headings: list[str] = []
    images: list[str] = []
    links: list[str] = []
    fences: list[str] = []
    in_fence = False
    fence_marker = ""

    for line in body.splitlines():
        fence = re.match(r"^\s*(```+|~~~+)(.*)$", line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[0]
                fences.append(fence.group(2).strip())
            elif marker[0] == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue

        heading = re.match(r"^\s*(#{1,6})\s+", line)
        if heading:
            headings.append(str(len(heading.group(1))))

        images.extend(match.group(1).strip("<>") for match in re.finditer(r"!\[[^]]*\]\(([^)\s]+)", line))
        links.extend(match.group(1).strip("<>") for match in re.finditer(r"(?<!!)\[[^]]+\]\(([^)\s]+)", line))

    return {"headings": headings, "images": images, "links": links, "fences": fences}


def normalize_link(link: str) -> str:
    link = re.sub(r"^https?://(?:www\.)?ylqian\.com", "", link)
    link = re.sub(r"^/zh-cn(?=/|$)", "", link)
    if link.startswith("#"):
        return "#local-heading"
    return link


def content_links(post: Post, stem: str) -> list[str]:
    links = [normalize_link(link) for link in markdown_structure(post.body)["links"]]
    own_post_path = f"/posts/{stem.lower()}"
    return [link for link in links if link.rstrip("/") != own_post_path]


def validate(zh: Post, en: Post, release: bool) -> list[str]:
    errors: list[str] = []
    zh_stem = ""
    en_stem = ""

    try:
        zh_stem, zh_suffix = post_stem(zh.path)
        en_stem, en_suffix = post_stem(en.path)
        if zh_suffix != "zh-cn" or en_suffix != "en":
            errors.append("pass the .zh-cn.md file first and the .en.md file second")
        if zh_stem != en_stem:
            errors.append(f"filename stems differ: {zh_stem!r} != {en_stem!r}")
    except ValueError as error:
        errors.append(str(error))

    for post, expected_language in ((zh, "zh-cn"), (en, "en")):
        for field in REQUIRED_FIELDS:
            if field not in post.metadata:
                errors.append(f"{post.path}: missing front matter field {field!r}")
        if post.metadata.get("language") != expected_language:
            errors.append(
                f"{post.path}: language must be {expected_language!r}, "
                f"found {post.metadata.get('language')!r}"
            )
        if post.metadata.get("description") != post.metadata.get("abstract"):
            errors.append(f"{post.path}: description and abstract must match")
        for field in ("categories", "tags"):
            value = post.metadata.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{post.path}: {field} must be a non-empty inline list")
        if release:
            if post.metadata.get("draft") is not False:
                errors.append(f"{post.path}: draft must be false for release")
            for field in ("title", "date", "description", "abstract"):
                if not post.metadata.get(field):
                    errors.append(f"{post.path}: {field} must not be empty for release")

    for field in ("date", "draft"):
        if zh.metadata.get(field) != en.metadata.get(field):
            errors.append(
                f"front matter {field!r} differs: "
                f"{zh.metadata.get(field)!r} != {en.metadata.get(field)!r}"
            )

    zh_structure = markdown_structure(zh.body)
    en_structure = markdown_structure(en.body)
    if zh_structure["headings"] != en_structure["headings"]:
        errors.append("Markdown heading levels or order differ between translations")
    if zh_structure["images"] != en_structure["images"]:
        errors.append("Markdown image destinations or order differ between translations")
    if zh_structure["fences"] != en_structure["fences"]:
        errors.append("fenced code block languages or order differ between translations")

    zh_links = content_links(zh, zh_stem)
    en_links = content_links(en, en_stem)
    if zh_links != en_links:
        errors.append("Markdown link destinations or order differ between translations")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zh_cn", type=Path, help="Chinese .zh-cn.md post")
    parser.add_argument("en", type=Path, help="English .en.md post")
    parser.add_argument("--release", action="store_true", help="enforce publish-ready metadata")
    args = parser.parse_args()

    try:
        zh = read_post(args.zh_cn)
        en = read_post(args.en)
        errors = validate(zh, en, args.release)
    except ValueError as error:
        errors = [str(error)]

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"Post pair passed: {args.zh_cn} <-> {args.en}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
