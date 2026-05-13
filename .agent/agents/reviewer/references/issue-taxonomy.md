# Issue Taxonomy

## Purpose

This taxonomy gives Reviewer a shared language for classifying issues and helps Orchestrator route failures to the correct agent.

## Issue Format

Each issue should use this format:

```markdown
### Issue <number>: <short title>

- Issue Type:
- Severity: low / medium / high / blocking
- Location:
- Evidence:
- Why It Matters:
- Recommended Fix:
- Route To:
```

## Issue Types

### missing_intent

The artifact does not answer the real user intent.

Default route:

```text
Orchestrator or Writer
```

Use when:

- The content answers a different question.
- The output type does not match the task.
- The audience is misread.

---

### weak_structure

The structure does not fit the content type or workflow.

Default route:

```text
Writer
```

Use when:

- Section order is confusing.
- Required sections are missing.
- The structure is too generic.
- Headings repeat the same idea.

---

### thin_content

The content lacks depth, examples, details, or decision value.

Default route:

```text
Writer
```

Use when:

- Sections are too shallow.
- Claims are generic.
- No practical use cases appear.
- User would not learn enough.

---

### unsupported_claim

The artifact contains a claim without adequate support.

Default route:

```text
Researcher + Writer
```

Use when:

- Numbers are unsupported.
- Product capabilities are overstated.
- Competitor claims are treated as facts.
- Freshness is uncertain.

---

### missing_source

The artifact needs source support or source index is insufficient.

Default route:

```text
Researcher
```

Use when:

- Writer needs evidence.
- Source Index lacks usable references.
- Claims need verification.

---

### ai_tone

The content contains obvious AI writing patterns.

Default route:

```text
Writer
```

Use when:

- Generic transitions appear.
- Rhythm is too uniform.
- Opening feels templated.
- Phrases sound like chatbot output.

---

### hard_sell

The content is too promotional for the workflow.

Default route:

```text
Writer
```

Use when:

- Product mention feels forced.
- Claims are too broad.
- CTA appears too early.
- Education turns into sales copy.

---

### wrong_product_fit

Product positioning is inaccurate, irrelevant, or poorly timed.

Default route:

```text
Orchestrator + Writer
```

Use when:

- Product value is unrelated to user intent.
- Product mention conflicts with profile.md.
- The artifact implies unsupported capabilities.

---

### duplicate_angle

The content angle is too similar to existing or previous output.

Default route:

```text
Orchestrator
```

Use when:

- Another article uses the same structure.
- Title angle is too generic.
- The topic needs reframing.

---

### poor_extractability

The content is difficult for AI search or downstream systems to parse.

Default route:

```text
Writer
```

Use when:

- No direct answer
- No clear definitions
- Weak FAQ
- No structured comparison where useful
- Long dense paragraphs

---

### unclear_next_action

The review itself or artifact does not define what happens next.

Default route:

```text
Reviewer or Orchestrator
```

Use when:

- Feedback is vague.
- Human decision is missing.
- Route is unclear.

---

### workflow_gap

The selected workflow lacks a required rule, scoring standard, file structure, or gate.

Default route:

```text
Human
```

Use when:

- The workflow does not define review criteria.
- Output format is ambiguous.
- Agent cannot safely proceed.

## Severity Definitions

### low

Minor polish issue. Does not block progress.

### medium

Needs revision but not a full rewrite.

### high

Substantive issue that affects usefulness or quality.

### blocking

Cannot proceed without fixing or asking the user.

## Route Values

Use one of:

```text
Researcher
Writer
Reviewer
Orchestrator
Human
Researcher + Writer
Orchestrator + Writer
```
