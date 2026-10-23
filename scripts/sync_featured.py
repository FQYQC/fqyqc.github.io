#!/usr/bin/env python3
"""Regenerate docs/featured.md from the `featured` front matter flag of posts.

The site template (layouts/partials/home/featured-pages.html) reads the flags
directly; the Markdown file is only a human-readable reference of the current result.

Usage: sync_featured.py [project-root]
"""

import sys
from pathlib import Path

LANG_SUFFIXES = (".zh-cn", ".en")
TRUE_WEIGHT = 1e9


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def weight(value: str):
    value = value.strip().lower()
    if value in ("", "false", "no", "off", "0"):
        return None
    if value in ("true", "yes", "on"):
        return TRUE_WEIGHT
    try:
        return float(value)
    except ValueError:
        return None


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    posts = {}
    for path in sorted((root / "content" / "posts").glob("*.md")):
        stem = path.name[: -len(".md")]
        base = next((stem[: -len(s)] for s in LANG_SUFFIXES if stem.endswith(s)), stem)
        meta = front_matter(path)
        entry = posts.setdefault(base, {"weight": None, "flag": None, "date": "", "published": False})
        if meta.get("draft", "false").lower() != "true":
            entry["published"] = True
            entry["date"] = max(entry["date"], meta.get("date", ""))
        w = weight(meta.get("featured", ""))
        if w is not None and entry["weight"] is None:
            entry["weight"], entry["flag"] = w, meta["featured"]

    chosen = [(name, e) for name, e in posts.items() if e["weight"] is not None and e["published"]]
    chosen.sort(key=lambda item: item[1]["date"], reverse=True)
    chosen.sort(key=lambda item: item[1]["weight"])

    covers = root / "static" / "images" / "covers"
    lines = [
        "# 首页精选",
        "",
        "<!-- 自动生成，请勿手改：由 scripts/sync_featured.py 根据文章开头的 featured 标记生成，运行 ./scripts/check.sh 时自动更新。 -->",
        "",
        "首页实际以文章里的标记为准，本文件只供参考。",
        "",
        "- **设为精选**：在文章开头加一行 `featured: true`，中英文任一版本即可，按发布日期从新到旧排。",
        "  写数字如 `featured: 15` 则按数字从小到大排在所有 `true` 前面；用 10、20、30 留间隔，插入新文章时不用改其他文章。",
        "- **封面**：把图片命名为 `<文章文件名>.jpg`（或 `.png`、`.webp`）放进 `static/images/covers/`，没有则显示文字卡。",
        "",
    ]
    if chosen:
        lines += ["| 顺序 | 文章 | 标记 | 发布日期 | 封面 |", "|---|---|---|---|---|"]
        for index, (name, e) in enumerate(chosen, start=1):
            has_cover = any((covers / f"{name}.{ext}").is_file() for ext in ("jpg", "png", "webp"))
            cover = "有" if has_cover else "无，显示文字卡"
            lines.append(f"| {index} | `{name}` | `{e['flag']}` | {e['date']} | {cover} |")
    else:
        lines.append("当前没有精选文章，首页不显示精选区。")

    out = root / "docs" / "featured.md"
    content = "\n".join(lines) + "\n"
    if not out.exists() or out.read_text(encoding="utf-8") != content:
        out.write_text(content, encoding="utf-8")
        print(f"Updated {out.relative_to(root)}")


if __name__ == "__main__":
    main()
