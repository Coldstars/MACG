# Intent Clarification Playbook

## Purpose

This playbook helps Orchestrator turn vague user requests into actionable workflow inputs.

It is inspired by professional brainstorming and office-hours style workflows: do not blindly execute the first surface-level request when intent is unclear. Clarify only when necessary, infer safely when possible, and record assumptions.

## When to Use

Use this playbook when:

- The user request is broad or ambiguous.
- The task type is unclear.
- Multiple workflows could match.
- The output format is not specified.
- The target audience is unclear.
- The user asks for multiple deliverables in one sentence.
- The task appears high-cost or high-risk.
- A missing decision could cause wasted work.

## Clarification Principles

1. Prefer safe inference for low-risk missing details.
2. Ask the user only when the missing detail affects output quality or workflow selection.
3. Do not ask questions that `profile.md` or the selected workflow already answers.
4. Record all assumptions in `process.md`.
5. If the user is running batch work, clarify batch scope before execution.
6. If the task is a new type without a workflow, recommend creating a workflow.

## Intent Diagnosis Checklist

Before selecting a workflow, identify:

- Task type
- Primary output
- Target audience
- Success criteria
- Required agents
- Human review gates
- Expected workspace location
- Single mode or batch mode
- Whether Pilot First is required

## Common User Intent Patterns

### Content Creation

Examples:

- Write a blog
- Create a landing page
- Draft a help center article
- Generate a comparison page
- Write product copy

Likely agents:

- Researcher
- Writer
- Reviewer

### Content Review

Examples:

- Review this article
- Check if this sounds AI-written
- Improve this page
- Score this draft

Likely agents:

- Reviewer
- Writer, if revision is requested

### Research

Examples:

- Analyze competitors
- Find content gaps
- Summarize sources
- Create a source index

Likely agents:

- Researcher
- Reviewer, if quality validation is required

### Design

Examples:

- Generate a design prompt
- Create poster copy
- Define a visual direction

Likely agents:

- Designer, if available
- Writer
- Reviewer

## Clarification Questions

Ask at most 1-3 questions before starting.

Use only when required:

- What is the final output format?
- Who is the target audience?
- Should this be a quick draft or a publish-ready asset?
- Should I create one item or a batch?
- Should I follow an existing workflow or create a new one?
- Which human review gates should be required?

## Safe Default Assumptions

If the user does not specify:

- Language: use the user's current language or workflow default.
- Output depth: use standard depth.
- Audience: infer from `profile.md` and task topic.
- Workflow: choose the best matching workflow.
- Review loop: use the workflow-defined limit.

Record assumptions as:

```markdown
## Assumptions

- Assumption:
- Why safe:
- Where used:
```

## Anti-Patterns

Do not:

- Start writing long-form output before workflow selection.
- Ask excessive questions for low-risk tasks.
- Treat every content task as a blog task.
- Treat every writing task as SEO content.
- Ignore `profile.md`.
- Ignore workflow-specific rules.
