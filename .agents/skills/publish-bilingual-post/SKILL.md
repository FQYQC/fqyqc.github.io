---
name: publish-bilingual-post
description: Polish a Chinese Hugo draft, produce its natural English translation, synchronize bilingual front matter and Markdown structure, validate the site, and prepare a release commit. Use for first publication of a post in this repository when the user says publish, release, finish and translate, create the English version, or prepare a bilingual post for commit. Do not use for incremental edits to an already published bilingual pair; use update-bilingual-post instead.
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
2. Copyedit the Chinese source. Apply safe improvements to spacing, punctuation, grammar, repetition, flow, and Markdown. Do not invent facts, experiences, dates, quotes, or opinions. Flag substantive ambiguities instead of silently resolving them.
3. Translate the reviewed source into idiomatic English. Preserve meaning and narrative voice rather than sentence order when natural English requires restructuring. Keep headings, paragraphs, lists, images, code, links, and shortcodes aligned.
4. Complete both front matters according to the editorial guide. Preserve an existing valid date; use the current local date only when the date is missing. Set `draft: false` only after both versions are complete.
5. Review the pair side by side. Confirm that no source paragraph was omitted, no unsupported detail was added, and all structural differences are intentional.
6. Run:

   ```bash
   python3 scripts/check_post_pair.py content/posts/<stem>.zh-cn.md content/posts/<stem>.en.md --release
   ./scripts/check.sh
   ```

7. Inspect `git diff` for only the target pair and explicitly related files such as `data/assets_mapping.json`. Fix failures before handoff.
8. Summarize meaningful editorial decisions, translation choices, files changed, and validation results. Propose a commit matching the repository style, normally `[Ctt.][<series>] Release <post>.`

## Commit boundary

Prepare the commit but do not stage or commit by default. If the user explicitly asks to commit, stage only the target pair and explicitly related files, recheck the staged diff, and then commit. Never include unrelated drafts or working-tree changes.
