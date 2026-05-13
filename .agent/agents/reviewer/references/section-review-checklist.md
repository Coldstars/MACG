# Section Review Checklist

## Purpose

This checklist helps Reviewer evaluate long-form artifacts section by section.

It is especially useful for articles, landing pages, reports, help docs, and tutorials.

## Review Each Section For

### 1. Section Purpose

Ask:

- What job is this section supposed to do?
- Does it move the artifact forward?
- Is it necessary?
- Is it in the right place?

Issue types:

- weak_structure
- thin_content
- duplicate_angle

### 2. Clarity

Ask:

- Is the main point clear?
- Does the section use precise terms?
- Are sentences easy to follow?
- Is there unnecessary abstraction?

Issue types:

- thin_content
- ai_tone
- unclear_next_action

### 3. Flow

Ask:

- Does this section connect naturally to the previous one?
- Does it prepare the next section?
- Does it repeat information?
- Does it jump too quickly?

Issue types:

- weak_structure
- duplicate_angle

### 4. Evidence

Ask:

- Are claims supported?
- Are examples specific?
- Is a source needed?
- Is uncertainty acknowledged?

Issue types:

- unsupported_claim
- missing_source

### 5. Specificity

Ask:

- Could this section appear in any generic article?
- Does it use concrete scenarios?
- Does it include actionable detail?
- Does it avoid empty claims?

Issue types:

- thin_content
- ai_tone

### 6. Style

Ask:

- Does it sound natural?
- Does it match profile.md and workflow tone?
- Is it too polished or mechanical?
- Is it too promotional?

Issue types:

- ai_tone
- hard_sell
- wrong_product_fit

### 7. Workflow Fit

Ask:

- Does this section satisfy workflow requirements?
- Does it preserve confirmed user decisions?
- Does it violate any constraints?

Issue types:

- workflow_gap
- missing_intent

## Section Review Output Format

Use this format when section-level feedback is needed:

```markdown
## Section Review

### Section: <heading>

- Purpose Fit:
- Clarity:
- Flow:
- Evidence:
- Style:
- Issues:
- Recommended Fix:
- Route To:
```

## Good Reviewer Behavior

- Quote or identify the problematic text when possible.
- Explain why it matters.
- Give a fix the Writer can execute.
- Avoid vague comments.
- Do not rewrite the entire section unless the workflow asks for rewrite suggestions.
