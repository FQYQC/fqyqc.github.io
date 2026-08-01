# Incremental translation sync

## Select a baseline

Use the narrowest reliable comparison:

1. When the source has uncommitted changes, compare it with `HEAD`:

   ```bash
   git diff --word-diff=plain HEAD -- content/posts/<stem>.zh-cn.md
   ```

2. When the user provides a commit or range, use it exactly.
3. When the source change is already committed but the translation is stale, inspect the history of both files and select the most recent commit where they were intentionally synchronized:

   ```bash
   git log --oneline -- content/posts/<stem>.zh-cn.md content/posts/<stem>.en.md
   git show <candidate> -- content/posts/<stem>.zh-cn.md content/posts/<stem>.en.md
   ```

Do not assume that the latest commit touching either file is a synchronization point. If no reliable baseline exists, compare the complete pair and tell the user that the update requires a full reconciliation.

## Map changes

- Group changes under the nearest Markdown heading.
- Distinguish prose changes from moves, formatting-only changes, metadata, links, images, and code.
- Treat a moved unchanged block as a move, not new translation work.
- Re-read adjacent paragraphs for pronouns, tense, transitions, and references affected by the changed block.

## Update the translation

- Translate the changed meaning, not the textual diff in isolation.
- Preserve unchanged target paragraphs byte-for-byte where practical.
- Allow minimal adjacent edits for English grammar and continuity, and report them.
- Delete target content when its source content was deleted.
- Move the corresponding target block when the source block moved.
- Preserve image destinations, code, URLs, and factual details.
- Apply metadata changes symmetrically; never copy `language: zh-cn` into the `.en.md` file.

## Review the result

Run `git diff --word-diff=plain -- <source> <target>` and verify:

- Every changed source block has a corresponding translation decision.
- Unchanged target sections did not receive stylistic churn.
- Heading, image, link, and code-block structure still matches.
- The final commit can remain limited to the intended post pair and directly related assets.
