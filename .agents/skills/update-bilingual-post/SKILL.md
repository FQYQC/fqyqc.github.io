---
name: update-bilingual-post
description: Review changes to an already published Chinese/English Hugo post pair, insert non-rendered suggestions without rewriting the Chinese source unless explicitly authorized, identify the last synchronized version, update only affected English passages after author confirmation, validate parity, and prepare an update commit. Use when the user says update, resync, recheck, retranslate changed parts, or fix the translation of an existing bilingual post. Do not use for a first English translation or initial release; use publish-bilingual-post instead.
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
4. Review only changed Chinese passages unless the user requests a broader review. Insert adjacent `AGENT-SUGGESTION` comments for Pangu spacing, capitalization, Chinese substitutions, grammar, structure, and ambiguities. Do not rewrite Chinese prose or front matter, including obvious errors, unless the user explicitly authorizes a defined edit scope. An update or translation request alone is not authorization.
5. Stop after adding suggestions and wait for the user to revise the Chinese source or explicitly authorize selected edits. Once the user confirms the source is final, update the corresponding English passages and ignore all `AGENT-SUGGESTION` comments.
6. Keep unaffected English blocks unchanged. Do not replace the entire translation merely because regenerating it is easier. Permit small adjacent English changes only when required for grammar, references, or narrative continuity.
7. Synchronize English front matter only where the confirmed source change requires it. Do not alter Chinese front matter without explicit authorization. Keep filename stem, date, draft state, language, categories, tags, description, and abstract valid before release.
8. Run:

   ```bash
   python3 scripts/check_post_pair.py content/posts/<stem>.zh-cn.md content/posts/<stem>.en.md --release
   ./scripts/check.sh
   ```

9. Inspect both the ordinary diff and a word-level diff. Fix validation errors and verify that unchanged English sections did not churn.
10. Report the baseline used, unresolved Chinese suggestions, a source-to-translation change map, files changed, validation results, and a proposed commit such as `[Ctt.][<series>] Update <post>.` or `[Ctt.][<series>] Fix <issue>.`

## Commit boundary

Prepare the commit but do not stage or commit by default. If the user explicitly asks to commit, stage only the target pair and explicitly related files, inspect the staged diff, and commit with the repository's established message style.
