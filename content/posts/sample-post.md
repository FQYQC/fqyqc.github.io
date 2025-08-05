---
title: "Sample Post with Abstract"
date: 2025-01-15
draft: false
description: "A sample post demonstrating the abstract functionality"
abstract: "This is a sample post that demonstrates how abstracts work on the main page. You can include **bold text**, *italic text*, and even [internal links](/about/) or [external links](https://example.com). This provides a concise summary of what the post is about."
categories: ["sample", "demo"]
tags: ["abstract", "demo", "hugo"]
---

# Sample Post with Abstract

This is a sample post that demonstrates the new abstract functionality. The abstract field in the front matter will be displayed on the main page instead of the auto-generated summary.

## What is an Abstract?

An abstract is a brief summary of the content that appears on the main page. It gives readers a clear idea of what the post is about without having to read the entire content.

## Benefits of Using Abstracts

1. **Better User Experience**: Readers can quickly understand what each post is about
2. **Custom Control**: You can write exactly what you want to show, rather than relying on auto-generated summaries
3. **Consistent Length**: All abstracts can be the same length for a uniform appearance
4. **SEO Benefits**: Well-written abstracts can improve search engine optimization

## How to Add Abstracts

To add an abstract to your posts, simply include an `abstract` field in the front matter:

```yaml
---
title: "Your Post Title"
date: 2025-01-15
abstract: "Your custom abstract here..."
---
```

The abstract will be displayed on the main page, and if no abstract is provided, the system will fall back to the auto-generated summary or description. 