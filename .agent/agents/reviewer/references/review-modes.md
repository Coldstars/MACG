# Review Modes

## Purpose

Reviewer should select a review mode based on the selected workflow and artifact type.

Do not apply the same review style to every artifact.

## Review Modes

| Mode | Best For |
|---|---|
| Gate Review | Pass/fail decision at a workflow checkpoint |
| Section Review | Detailed feedback by section |
| Spec Alignment Review | Check artifact against workflow and confirmed decisions |
| Style Review | Tone, clarity, AI writing pattern, brand voice |
| Evidence Review | Claims, sources, and unsupported statements |
| Conversion Review | Landing pages, product pages, CTAs |
| Final Publish Review | Final readiness before user approval |

## 1. Gate Review

Use when Orchestrator needs a decision.

Must output:

- Status
- Scores, if workflow defines them
- Blocking issues
- Route recommendation
- Human decision needed, if any

## 2. Section Review

Use when reviewing long-form artifacts.

For each important section, check:

- Purpose
- Clarity
- Flow
- Evidence
- Specificity
- Style
- Fit with previous and next section

## 3. Spec Alignment Review

Use when the workflow has a confirmed outline, brief, or requirements.

Check:

- Does the artifact follow selected workflow?
- Does it preserve confirmed human decisions?
- Does it satisfy required sections?
- Does it violate constraints?
- Does it include unapproved changes?

## 4. Style Review

Use when content feels generic, awkward, or AI-written.

Check:

- AI writing patterns
- Overly uniform rhythm
- Inflated language
- Generic transitions
- Weak hook
- Generic ending
- Brand voice fit

## 5. Evidence Review

Use when claims matter.

Check:

- Unsupported claims
- Missing sources
- Outdated or uncertain facts
- Competitor claims presented as facts
- Overpromising

## 6. Conversion Review

Use for landing pages, topic pages, and product-led copy.

Check:

- Value proposition
- Pain-point clarity
- CTA logic
- Product fit
- Trust signals
- Section flow

## 7. Final Publish Review

Use at final gate.

Check:

- Required sections exist
- Known issues resolved
- No new unsupported claims
- No workflow violations
- No obvious AI writing patterns
- User confirmation required

## Review Output Principle

Reviewer should produce feedback that a downstream agent can execute without guessing.
