---
name: publish-bilingual-post
description: Review a Chinese Hugo draft by inserting non-rendered editorial suggestions without rewriting the Chinese source unless explicitly authorized, then produce a natural English translation from the author-confirmed source, synchronize bilingual front matter and Markdown structure, validate the site, and prepare a release commit. Use for first publication of a post in this repository when the user says publish, release, finish and translate, create the English version, or prepare a bilingual post for commit. Do not use for incremental edits to an already published bilingual pair; use update-bilingual-post instead.
---

# Publish Bilingual Post

Turn one Chinese draft into a reviewed, publish-ready Chinese/English pair while preserving the author's facts, voice, media, and repository state.

## Required context

1. Read the repository `AGENTS.md` and check `git status --short`.
2. Read [references/editorial-guide.md](references/editorial-guide.md) completely before editing.
3. Resolve the target pair as `content/posts/<stem>.zh-cn.md` and `content/posts/<stem>.en.md`. Treat Chinese as the source unless the user explicitly says otherwise.
4. If both files are already published and the request concerns later edits, stop this workflow and use `$update-bilingual-post`.

## Workflow

1. Inspect the complete source post, its front matter, referenced images, links, and any existing target file. Preserve unrelated dirty files.
2. Review the Chinese source without rewriting it. Insert adjacent `AGENT-SUGGESTION` comments for Pangu spacing, punctuation, grammar, repetition, structure, capitalization, Chinese substitutions, factual ambiguities, and proposed front matter. A request to publish, polish, translate, or update is not permission to alter Chinese prose. Do not change even obvious errors unless the user explicitly authorizes direct edits.
3. Stop after adding suggestions and let the user revise the Chinese source. Continue only after the user confirms that the source is final, explicitly accepts or rejects the suggestions, or explicitly authorizes the Agent to apply a defined set of edits. Treat authorization as scoped to that request, not as a permanent exception.
4. Translate only the author-confirmed Chinese source into idiomatic English. Never translate `AGENT-SUGGESTION` comments. Preserve meaning and narrative voice rather than sentence order when natural English requires restructuring. Keep headings, paragraphs, lists, images, code, links, and shortcodes aligned.
5. Complete the English front matter according to the editorial guide. Do not modify Chinese front matter without explicit authorization; add a suggestion after its closing delimiter instead. Preserve an existing valid date and use the current local date only when the date is missing. Require both versions to be complete and `draft: false` before release.
6. Review the pair side by side. Confirm that no source paragraph was omitted, no unsupported detail was added, and all structural differences are intentional.
7. Run:

   ```bash
   python3 scripts/check_post_pair.py content/posts/<stem>.zh-cn.md content/posts/<stem>.en.md --release
   ./scripts/check.sh
   ```

8. Inspect `git diff` for only the target pair and explicitly related files such as `data/assets_mapping.json` and `data/assets_optimized.json`. Fix failures before handoff. If the post adds mapped images, run `python3 scripts/optimize_images.py build` and tell the user to upload the new files in `optimized-images/` and send back their URLs, then run `python3 scripts/optimize_images.py link <file>`; until then the images fall back to the full-size originals.
9. Summarize unresolved Chinese suggestions, author-approved editorial decisions, translation choices, files changed, and validation results. Propose a commit matching the repository style, normally `[Ctt.][<series>] Release <post>.`

## Commit boundary

Prepare the commit but do not stage or commit by default. If the user explicitly asks to commit, stage only the target pair and explicitly related files, recheck the staged diff, and then commit. Never include unrelated drafts or working-tree changes.
