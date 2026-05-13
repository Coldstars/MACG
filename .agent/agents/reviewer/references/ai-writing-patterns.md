# AI Writing Patterns

## Purpose

This file helps Reviewer detect common AI-generated writing patterns and provide actionable feedback.

It is generic and can be used by any workflow that requires natural, human-like writing.

## Review Modes

### Detect Only

Use when Reviewer should identify AI writing patterns without rewriting.

Output:

- Issue type
- Location
- Quoted text or description
- Why it feels AI-written
- Recommended fix direction

### Rewrite Suggestion

Use when the workflow allows rewrite suggestions.

Output:

- Original issue
- Suggested rewrite direction
- Notes for Writer

Reviewer should not directly overwrite the target artifact unless the workflow explicitly allows it.

## Common AI Writing Patterns

### 1. Generic Grand Opening

Examples:

```text
In today's fast-paced digital world...
In the ever-evolving landscape...
As businesses increasingly rely on...
```

Why it matters:

- Sounds generic
- Delays the real answer
- Could fit any topic

Fix:

- Start with the concrete user problem or direct answer.

---

### 2. Inflated Marketing Language

Examples:

```text
powerful solution
seamless experience
robust platform
unlock the power
game-changing
revolutionary
```

Why it matters:

- Feels promotional
- Often hides lack of specificity

Fix:

- Replace with concrete capability and use case.

---

### 3. Mechanical Transitions

Examples:

```text
Furthermore
Moreover
Additionally
In conclusion
It is important to note
```

Why it matters:

- Creates obvious AI rhythm
- Makes prose feel templated

Fix:

- Use natural transitions or remove them.

---

### 4. Formulaic Contrast

Examples:

```text
It is not just X, but Y.
Not only does it..., but it also...
```

Why it matters:

- Overused in AI writing
- Often adds drama without value

Fix:

- State the actual distinction directly.

---

### 5. Vague Attribution

Examples:

```text
Experts say...
Many businesses believe...
Studies show...
```

Why it matters:

- Unsupported claim
- Weakens trust

Fix:

- Provide a source or remove the claim.

---

### 6. Uniform Paragraph Rhythm

Signs:

- Every paragraph has similar length.
- Every section ends with a summary sentence.
- Every bullet list has the same structure.

Fix:

- Vary paragraph length.
- Cut unnecessary wrap-up sentences.
- Use examples where needed.

---

### 7. Generic Conclusion

Examples:

```text
By understanding X, businesses can unlock new opportunities...
Ultimately, X is essential for success...
```

Fix:

- End with a practical decision point, next step, or concise summary.

---

### 8. Empty Definitions

Signs:

- Defines a familiar concept without adding context.
- Starts every article with “X is...”
- Does not connect definition to user need.

Fix:

- Use definition only when it helps the reader decide or act.

---

### 9. Excessive List Formatting

Signs:

- Too many bullet lists
- Every idea becomes a list
- No narrative flow

Fix:

- Use bullets for scannability, but paragraphs for reasoning.

---

### 10. Over-Explaining Obvious Points

Signs:

- Explains common concepts at length
- Adds filler before useful information
- Avoids concrete examples

Fix:

- Cut the obvious explanation.
- Add a real scenario or decision criterion.

## Severity Guidance

### minor

One or two local issues. Use `revise` with low severity.

### moderate

Multiple sections sound generic. Use `revise`.

### severe

The entire artifact feels AI-generated. Use `major_revise`.

## Output Format

```markdown
### AI Writing Pattern Issue

- Pattern:
- Severity:
- Location:
- Example:
- Why It Matters:
- Recommended Fix:
- Route To: Writer
```

## Reviewer Anti-Patterns

Do not:

- Say “sounds AI” without identifying why.
- Rewrite everything when a local edit is enough.
- Remove useful structure just to make text casual.
- Make technical content vague in the name of sounding human.
