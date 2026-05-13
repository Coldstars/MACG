# Source Extraction Rules

## Purpose

This file defines how Researcher should treat web pages, competitor pages, articles, and reference material when a workflow requires source-based work.

The goal is to avoid passing noisy web pages to Writer or Reviewer.

## Core Principle

Sources should be turned into clean, reusable research material whenever possible.

```text
URL → Extract main content → Remove noise → Save local source note → Add to Source Index
```

## What to Extract

When a workflow requires source extraction, extract:

- Page title
- URL
- Author or organization, if available
- Publication date, if available
- Main headings
- Main body content
- Tables, if important
- Key claims
- Product claims
- FAQ content
- CTA or conversion sections, if relevant
- Any data or statistics, with caution

## What to Remove

Remove:

- Navigation
- Sidebar links
- Newsletter popups
- Cookie notices
- Ads
- Footer links
- Related article widgets
- Comment sections, unless workflow needs them
- Social sharing UI
- Repeated boilerplate

## Local Source File Convention

If the workflow supports local source files, use:

```text
workspaces/<task-type>/<slug>/sources/
├── S1-clean.md
├── S2-clean.md
└── S3-clean.md
```

Each source file should include:

```markdown
# Source: <Title>

URL:
Source Type:
Extracted Date:
Confidence:

## Why This Source Matters

## Main Content

## Key Claims

## Useful Sections for Downstream Agents

## Cautions
```

## Source Confidence

Use:

- High: official docs, product docs, first-party page, clearly dated source
- Medium: reputable industry article, competitor page, well-known blog
- Low: vague page, undated content, unclear source, low-quality aggregator

## Source Index Requirements

When adding a source to Source Index, use this standard schema:

```markdown
| ID | Source Name | URL / Local File | Type | Confidence | Why Useful | Recommended Use | Cautions |
|---|---|---|---|---|---|---|---|
```

Workflow files may add workflow-specific instructions, but should not remove `Confidence` or `Cautions` when source quality matters.

## Do Not

- Do not invent URL content.
- Do not quote from a source you did not read.
- Do not include a source only because it looks authoritative.
- Do not pass raw noisy HTML to Writer.
- Do not summarize competitor claims as if they are facts.
- Do not ignore source dates when freshness matters.
