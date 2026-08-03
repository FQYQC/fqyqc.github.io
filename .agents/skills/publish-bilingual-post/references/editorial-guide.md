# Bilingual post editorial guide

## Chinese source editing

- Treat every `.zh-cn.md` file, including its front matter, as author-owned text. Never rewrite it unless the user explicitly authorizes direct edits. Requests to review, polish, publish, translate, update, or fix the bilingual pair do not grant that permission.
- By default, write only adjacent, non-rendered review comments in this form:

  ```html
  <!-- AGENT-SUGGESTION
  类型：结构｜措辞｜事实核对｜Pangu｜大小写｜中文化｜front matter
  理由：说明问题及其对含义、语气或阅读体验的影响。
  参考改写：提供可直接采用的版本；若只需核对事实，可省略。
  -->
  ```

- Place each comment immediately after the affected paragraph. Put insertion or structural proposals at the intended insertion point. For front matter, place the comment immediately after the closing delimiter. Never insert a comment inside YAML, code fences, shortcodes, or URLs.
- Do not alter original Chinese bytes for obvious typos, punctuation, Pangu spacing, capitalization, Markdown, or broken front matter. Put the correction in a suggestion comment instead.
- Preserve first-person voice, uncertainty, humor, chronology, and factual claims in every proposed rewrite. Distinguish copyedits from changes to tone, emphasis, order, interpretation, or argument.
- Suggest Pangu formatting as the default spacing standard: add a normal space between Chinese text and Latin words or Arabic numerals where appropriate; do not add spaces next to Chinese punctuation.
- Suggest Chinese punctuation in Chinese prose and retain the established spelling of proper nouns, routes, flight numbers, code identifiers, and product names.
- Audit embedded English case-insensitively across the title, summary, headings, and prose. Point out inconsistent forms such as `PyTorch` versus `Pytorch`, explain the preferred canonical form, and suggest normalization only when the intended term is unambiguous. Do not report ordinary sentence-initial capitalization as an inconsistency.
- Review every English expression embedded in Chinese prose for whether a clear Chinese equivalent would improve readability. Record suitable candidates as `original → suggested Chinese` with a short reason. Prefer Chinese for ordinary descriptive language; retain brand names, acronyms, code identifiers, established technical terms, and deliberate bilingual wording.
- Never translate `AGENT-SUGGESTION` comments. After the user confirms that suggestions are resolved, remove only these comments or retain them according to the user's direction; never change the surrounding prose while cleaning comments.

## English translation

- Add the established translation notice immediately after the English front matter: `> This page was translated from the [original Chinese version](/zh-cn/posts/<slug>) by <model>. Please refer to the original for definitive content.` Use the actual translation model and matching Chinese URL. Treat this English-only notice as an intentional structural difference.
- Write natural narrative English rather than a word-for-word rendering.
- Preserve every factual statement and meaningful qualifier. Do not add background information that is absent from the source.
- Keep proper nouns and common industry terms in their conventional form. Preserve useful bilingual terms when the author's style depends on them.
- Keep heading levels, paragraph boundaries, lists, block quotes, images, code blocks, and shortcodes aligned unless a documented editorial reason requires a difference.
- Translate image alt text and link labels, but keep image destinations stable. Adjust internal links to the matching language URL when necessary.

## Front matter

Require these fields in both files:

```yaml
title: "..."
date: YYYY-MM-DD
draft: false
language: zh-cn | en
description: "..."
abstract: "..."
categories: ["..."]
tags: ["..."]
```

- Use the same filename stem and date in both versions.
- Set `language` from the filename: `.zh-cn.md` uses `zh-cn`; `.en.md` uses `en`.
- Keep `description` and `abstract` identical within each language.
- Write a concise summary when they are empty; do not use placeholder values.
- Preserve a valid existing date unless the user requests a different release date. Use the current local date only when no date exists.
- Set both files to the same draft state and use `draft: false` for release.

## Established taxonomy

Prefer existing mappings when they fit:

| 中文 | English |
| --- | --- |
| 旅行 | Travel |
| 技术 | Tech |
| 运转 | Journeys |
| 飞机 | Flights |
| 公交 | Public Transport |
| 机器学习 | Machine Learning |
| 开发 | Code |
| 工具 | Tools |
| Mileage Run | Mileage Run |

For a new category or ambiguous tag, inspect existing posts first. Choose a stable translation and report it; ask the user only when the choice would materially change classification.

## Release review

- Report Pangu formatting changes, English capitalization inconsistencies, and optional English-to-Chinese substitutions separately from factual or structural edits.
- Confirm that the two posts render to the corresponding language URLs.
- Confirm heading-level, image, link, and code-block parity with `scripts/check_post_pair.py`.
- Confirm `./scripts/check.sh` succeeds and both local search indexes remain valid.
- Review the final diff for accidental global formatting, lost hard line breaks, changed asset paths, and unrelated files.
