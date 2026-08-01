---
name: update-bilingual-post
description: Review changes to an already published Chinese/English Hugo post pair, identify the last synchronized version, revise only affected source passages and their translation, validate parity, and prepare an update commit. Use when the user says update, resync, recheck, retranslate changed parts, or fix the translation of an existing bilingual post. Do not use for a first English translation or initial release; use publish-bilingual-post instead.
---

# Update Bilingual Post

Synchronize an existing published translation without regenerating or churning unaffected prose.

## Required context

1. Read the repository `AGENTS.md` and check `git status --short`.
2. Read [references/incremental-sync.md](references/incremental-sync.md) completely.
3. Read the shared [editorial guide](../publish-bilingual-post/references/editorial-guide.md) completely before editing.
4. Resolve the pair as `content/posts/<stem>.zh-cn.md` and `content/posts/<stem>.en.md`. Treat Chinese as the source unless the user explicitly says otherwise.
5. If the target translation does not exist or either version has never been published, stop this workflow and use `$publish-bilingual-post`. Report the handoff reason, but leave release edits and the commit proposal to that skill.

## Workflow

1. Inspect both complete posts and the current working tree. Preserve unrelated dirty files.
2. Establish the last synchronized source state using the incremental guide. If the baseline is ambiguous and different choices would change the translation scope, ask the user before editing.
3. Build a change map grouped by heading: source additions, deletions, rewrites, moved blocks, metadata changes, links, and images.
4. Copyedit only changed source passages unless the user requests a broader review. Apply Pangu spacing, audit inconsistent capitalization of embedded English, and identify English expressions that would read better in Chinese according to the editorial guide. Then update the corresponding English passages. Permit small adjacent changes only when required for grammar, references, or narrative continuity.
5. Keep unaffected English blocks unchanged. Do not replace the entire translation merely because regenerating it is easier.
6. Synchronize front matter only where the source change requires it. Keep filename stem, date, draft state, language, categories, tags, description, and abstract valid.
7. Run:

   ```bash
   python3 scripts/check_post_pair.py content/posts/<stem>.zh-cn.md content/posts/<stem>.en.md --release
   ./scripts/check.sh
   ```

8. Inspect both the ordinary diff and a word-level diff. Fix validation errors and verify that unchanged English sections did not churn.
9. Report the baseline used, a source-to-translation change map, files changed, validation results, and a proposed commit such as `[Ctt.][<series>] Update <post>.` or `[Ctt.][<series>] Fix <issue>.`

## Commit boundary

Prepare the commit but do not stage or commit by default. If the user explicitly asks to commit, stage only the target pair and explicitly related files, inspect the staged diff, and commit with the repository's established message style.
