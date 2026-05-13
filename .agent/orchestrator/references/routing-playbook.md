# Routing Playbook

## Purpose

This playbook helps Orchestrator decide what to do after a review, failure, or user intervention.

It prevents the common mistake of sending every failed artifact back to Writer.

## Core Routing Principle

Route the problem to the agent that can actually fix the root cause.

```text
Bad facts → Researcher
Bad structure → Writer
Bad quality standard → Workflow / Human
Bad direction → Orchestrator / Human
Bad style → Writer
Bad evidence → Researcher + Writer
```

## Route Types

### route_to_researcher

Use when the problem is caused by missing or weak information.

Examples:

- Missing source
- Unsupported claim
- Outdated information
- Weak competitor understanding
- Missing user/audience insight
- Search intent not understood
- Source index not usable

Expected action:

```text
Researcher updates research material, source index, or missing context.
Writer should not rewrite until research is improved.
```

### route_to_writer

Use when the research is sufficient but the artifact is poorly written or structured.

Examples:

- Weak outline
- Thin section
- Poor flow
- Bad introduction
- AI tone
- Hard-sell language
- Missing section required by workflow
- Poor section hierarchy

Expected action:

```text
Writer revises the target artifact using review instructions.
```

### route_to_reviewer

Use when review quality is incomplete or unclear.

Examples:

- Reviewer gives vague feedback
- No issue types
- No severity
- No route recommendation
- No actionable instruction
- Missing workflow-defined scoring

Expected action:

```text
Reviewer re-runs review using the workflow review standard.
```

### route_to_orchestrator

Use when the root problem is planning or direction.

Examples:

- Wrong workflow selected
- Wrong audience inferred
- Wrong output type
- Topic too broad
- Conflicting human instructions
- Product positioning unclear
- Batch task needs pilot mode

Expected action:

```text
Orchestrator repairs the task brief, updates process.md, or asks the user.
```

### ask_human

Use when the system cannot safely decide.

Examples:

- User preference conflict
- Workflow missing a required standard
- Product capability uncertainty
- Need to choose between multiple viable directions
- Revision loop limit reached

Expected action:

```text
Stop and ask user for decision.
```

## Routing Decision Table

| Issue Type | Default Route | Notes |
|---|---|---|
| missing_information | Researcher | Add missing research |
| missing_source | Researcher | Improve source index |
| unsupported_claim | Researcher + Writer | Verify or remove claim |
| missing_intent | Orchestrator or Writer | Reframe task brief or revise artifact focus |
| weak_structure | Writer | Improve outline/structure |
| thin_content | Writer | Add depth/examples |
| ai_tone | Writer | Rewrite affected sections |
| hard_sell | Writer | Reduce product push |
| wrong_product_fit | Orchestrator + Writer | Reposition product mention |
| duplicate_angle | Orchestrator | Reframe content angle |
| poor_extractability | Writer | Improve direct answers, structure, FAQ, and parseability |
| unclear_next_action | Reviewer or Orchestrator | Clarify review feedback or process decision |
| workflow_gap | Human | Workflow must be updated |
| revision_limit_reached | Human | User decides next step |

## Cost Control Rules

- Do not generate multiple full artifacts unless the workflow allows it.
- For batch tasks, run a pilot first.
- Stop after the workflow-defined revision limit.
- If two revision loops fail for the same reason, do not repeat the same route.
- If a failure repeats, escalate to Orchestrator or Human.

## process.md Logging

Every routing decision should be recorded:

```markdown
## Decision Log

- Date:
- Issue:
- Route:
- Reason:
- Next Action:
```

## Anti-Patterns

Do not:

- Route every failure to Writer.
- Ignore Reviewer route suggestions.
- Keep looping when the workflow limit is reached.
- Ask Researcher to fix writing style.
- Ask Writer to invent missing facts.
- Ask Reviewer to rewrite the artifact directly.
