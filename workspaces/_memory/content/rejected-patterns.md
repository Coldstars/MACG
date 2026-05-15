# Rejected Patterns

## Purpose

This file stores writing patterns, structures, tones, and expressions the user disliked.

Use this file to avoid repeating known problems.

## Pattern Format

```markdown
## Rejected Pattern: <short title>

- Date:
- Source Task:
- Applies To:
- User Feedback:
- What To Avoid:
- Better Alternative:
```

## Rejected Patterns

## Rejected Pattern: Internal publishing metadata in final article

- Date: 2026-05-14
- Source Task: `workspaces/blog/live-search-results-ai-agent/how-to-give-an-ai-agent-access-to-live-search-results/article.md`
- Applies To: Blog writing outputs, especially final `article.md` files meant to be copied directly into the official website CMS.
- User Feedback: The final blog result should be copy-ready and should not include non-body content that the user has to manually delete.
- What To Avoid: Do not append `TDK`, `Slug`, `Publishing Checklist`, internal review notes, acceptance checklists, or other publishing metadata to the end of final article body files.
- Better Alternative: Keep `article.md` as reader-visible blog content only. If publishing metadata is explicitly requested, provide it separately outside the article body or in a separate file.
