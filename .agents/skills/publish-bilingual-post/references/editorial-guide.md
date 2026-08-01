# Bilingual post editorial guide

## Chinese source editing

- Preserve first-person voice, uncertainty, humor, chronology, and factual claims.
- Use Pangu formatting as the default spacing standard: add a normal space between Chinese text and Latin words or Arabic numerals where appropriate; do not add spaces next to Chinese punctuation.
- Use Chinese punctuation in Chinese prose and retain the established spelling of proper nouns, routes, flight numbers, code identifiers, and product names.
- Audit embedded English case-insensitively across the title, summary, headings, and prose. Point out inconsistent forms such as `PyTorch` versus `Pytorch`, explain the preferred canonical form, and normalize only when the intended term is unambiguous. Do not report ordinary sentence-initial capitalization as an inconsistency.
- Review every English expression embedded in Chinese prose for whether a clear Chinese equivalent would improve readability. Report suitable candidates as `original → suggested Chinese` with a short reason. Prefer Chinese for ordinary descriptive language; retain brand names, acronyms, code identifiers, established technical terms, and deliberate bilingual wording.
- Remove obvious repetition and repair grammar when intent is clear. Report edits that materially change tone, emphasis, order, or interpretation.
- Preserve Markdown semantics. Do not format prose inside code fences or alter URLs and asset keys.

## English translation

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
