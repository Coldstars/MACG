# Workflow: Blog Writing

## Purpose

用于生成适合官网发布的 SEO/GEO 友好博客文章。

## Trigger

当用户意图包含以下任务时使用：

- 写博客
- SEO 文章
- GEO 友好文章
- 官网博客
- 教程型文章
- 对比型文章
- 替代方案文章
- 场景型文章
- 产品主题博客

## Required Agents

- orchestrator
- researcher
- writer
- reviewer

## Memory Inputs

Before producing or revising blog content, relevant agents should read the content memory files when they exist:

- `workspaces/_memory/content/approved-patterns.md`
- `workspaces/_memory/content/rejected-patterns.md`
- `workspaces/_memory/content/content-lessons.md`

These files capture confirmed user preferences for content work. They guide writing choices but do not override `AGENTS.md`, `profile.md`, platform rules, this workflow, role `SKILL.md` files, or the current workspace `process.md`.

## Workspace Location

workspaces/blog/<topic-slug>/

## Workspace Structure

每个博客任务初始化时必须创建以下结构：

workspaces/blog/<topic-slug>/
├── process.md
└── research-report.md

当 Researcher 需要保存清洗后的来源材料时，可以创建可选目录：

workspaces/blog/<topic-slug>/
└── sources/
    ├── S1-clean.md
    └── S2-clean.md

用户在 Gate 1 确认一个或多个标题后，Orchestrator 必须为每个确认标题创建 slug 化标题目录：

workspaces/blog/<topic-slug>/
└── <selected-title-slug>/
    ├── outline.md
    ├── article.md
    └── review.md

topic-slug 命名规则：

- topic-slug 根据用户原始主题生成。
- topic-slug 必须英文小写、使用连字符、简短、稳定。
- topic-slug 用作本次博客任务的 workspace 根目录，不依赖最终标题。

标题目录命名规则：

- 使用 slug 化标题命名。
- slug 必须英文小写、使用连字符、简短、稳定。
- 如果标题无法直接生成英文 slug，Orchestrator 根据标题语义生成短 slug。
- 不使用原始标题直接作为目录名，避免空格、标点、中文或过长路径造成问题。

## Blog-Specific Goals

- Google SEO 友好。
- GEO / AI Search 引用友好。
- 可直接发布到官网博客。
- 文章结构清晰、段落简洁。
- 最终 article.md 只包含可直接发布的读者可见正文；不自动附加 TDK、Slug、Publishing Checklist 等内部发布辅助内容。
- 包含 FAQ。
- 不虚构产品能力、案例、数据。
- 不使用夸张营销语言。

## Input Contract

博客任务的最低输入应包括：

- Topic direction
- Target language
- Target audience
- Content type
- Publishing goal

如果用户没有提供全部字段，Orchestrator 可以基于 `profile.md` 和当前主题推断默认值，但必须在 `process.md` 记录 assumptions。

推荐默认值：

```text
Target language: English
Target audience: based on profile.md and topic
Content type: SEO/GEO blog article
Publishing goal: official website blog
Article depth: standard
```

如果缺失信息会明显影响质量，Orchestrator 必须暂停并询问用户。

如果缺失信息影响较小，Orchestrator 可以继续，但必须记录：

```markdown
## Assumptions

- Assumption:
- Why safe:
- Where used:
```

## Output Contract

一个完成的博客 workspace 必须包含：

```text
process.md
research-report.md
title-xx/outline.md
title-xx/article.md
title-xx/review.md
```

被选中的 `article.md` 必须包含：

- H1
- Introduction
- Body with H2/H3
- FAQ
- Revision Summary, if revised

`article.md` 是可复制即用的最终博客正文。除非用户明确要求，禁止在 `article.md` 末尾自动生成或附加：

- TDK
- Slug
- Publishing Checklist
- 其他内部发布、审核、验收或元信息区块

## Human Gates

### Gate 1: Title Selection

- 用户从 research-report.md 的标题候选中选择一个或多个标题，也可以修改标题后确认。
- 标题未确认前，不允许创建标题目录。
- 标题未确认前，不允许生成 outline.md。
- 标题确认后，Orchestrator 必须为每个确认标题创建对应的 slug 化标题目录。

### Gate 2: Outline Confirmation

- 用户单独确认、修改或合并当前标题目录中的 outline.md。
- 每个选中标题都必须单独完成 outline confirmation。
- 当前标题的大纲未确认前，不允许在该标题目录中生成 article.md。

### Gate 3: Publish Confirmation

- 用户单独确认当前标题目录中的 article.md 是否可以发布。
- 每个选中标题都必须单独完成 publish confirmation。
- 当前标题未确认前，不允许将该标题标记为 completed。

## Research Requirements

Researcher 必须输出 research-report.md，包含：

```markdown
# Research Report

## Topic Brief

## Brief Analysis

## Search Intent

## Competitor Pattern

## Content Gap

## SEO Opportunities

## GEO Opportunities

## Source Index

表格字段：
| ID | Source Name | URL / Local File | Type | Confidence | Why Useful | Recommended Use | Cautions |

## Title Options

每个标题包含：

- Title ID
- Title
- Primary Keyword
- Search Intent
- Angle
- SEO Value
- GEO Value
- Recommended Reason

标题候选数量：5-8 个。

如果没有真实来源，不允许编造 URL。应标注 source_required 或 user_should_provide_source。
```

## Writing Requirements

Writer 必须：

- 根据用户选中的每个标题，在对应的 slug 化标题目录中生成 2-3 个大纲方案。
- 大纲必须包含 H1、H2/H3、section purpose、suggested source IDs、estimated word count。
- 用户确认大纲后生成 article.md。
- article.md 必须包含：
  - H1
  - Introduction
  - H2/H3 body
  - FAQ
- article.md 必须是可直接发布到官网的正文，不包含 TDK、Slug、Publishing Checklist 或其他非读者可见内容，除非用户明确要求。
- article.md 始终是当前候选最终稿。
- 每个选中标题必须独立生成 outline.md、article.md 和 review.md。
- 不创建 final.md。
- 不创建 draft-v2.md。
- 修改直接更新 article.md，并在底部记录 Revision Summary。

## SEO/GEO Rules

- H1 只出现一次。
- H2/H3 层级清晰。
- 引言中给出直接回答。
- 自然覆盖主关键词和相关长尾词。
- 避免关键词堆砌。
- 使用定义块、步骤、表格、FAQ、列表等 AI 友好结构。
- FAQ 回答要简短直接。
- 如用户单独要求 TDK，应作为独立交付内容或单独文件输出，不写入 article.md 正文。
- Slug 仅用于 workspace/title folder 命名，除非用户明确要求，不写入 article.md 正文。
- 段落不要过长。
- 内容不能只讲概念，要有应用场景和判断标准。
- 不出现无来源数据。
- 不夸大产品能力。

## Review Standards

Reviewer 必须输出 review.md，包含：

```markdown
# Review Result

Status: pass / revise / major_revise

Overall Score:
SEO Score:
GEO Score:
Readability Score:
Product Fit Score:

## Main Issues

## Revision Instructions for Writer

## Human Decision

Decision: pending / accepted_for_revision / publish_approved / rejected

## Reviewer Notes
```

评分标准：

- SEO Score：搜索意图、关键词覆盖、标题结构、可发布正文质量、内链建议。
- GEO Score：直接回答、定义块、FAQ、表格、结构化表达、AI 可引用性。
- Readability Score：段落长度、表达自然度、废话比例、逻辑清晰度。
- Product Fit Score：是否自然引出产品价值，是否避免硬广，是否没有虚构能力。
- Overall Score：综合判断。

阈值：

- overall_score >= 85 且 status=pass：进入发布确认。
- 70 <= overall_score < 85 或 status=revise：等待用户确认是否接受修改意见，确认后打回 Writer。
- overall_score < 70 或 status=major_revise：Orchestrator 判断是打回 Researcher 补充信息，还是打回 Writer 重写结构。
- 自动修改最多 2 轮。

## Failure Routing

Reviewer 应尽可能包含 issue type 和 route suggestion，供 Orchestrator 决策。

| Issue Type | Route To | Reason |
|---|---|---|
| missing_intent | Orchestrator or Writer | Content does not answer the real user intent |
| missing_information | Researcher | More evidence or context is needed |
| missing_source | Researcher | Source index is insufficient |
| unsupported_claim | Researcher + Writer | Claim must be verified or removed |
| weak_structure | Writer | Structure or section order needs revision |
| thin_content | Writer | Content lacks depth or examples |
| wrong_product_fit | Orchestrator + Writer | Positioning or product mention is off |
| ai_tone | Writer | Style needs rewriting |
| hard_sell | Writer | Product mention is too promotional |
| duplicate_angle | Orchestrator | Topic direction may need reframing |
| poor_extractability | Writer | Content is hard for AI search or downstream systems to parse |
| unclear_next_action | Reviewer or Orchestrator | Review feedback or process decision is unclear |
| workflow_gap | Human | Workflow lacks required standard |

## AI Writing Pattern Review

Reviewer 必须检查博客内容中的 AI 写作痕迹。

常见问题包括：

- Generic AI-style introduction
- Overly polished rhythm
- Repetitive paragraph length
- Excessive transition words
- Inflated marketing language
- Vague claims
- Generic conclusion
- Too many similar bullet lists
- Formulaic “not just X, but Y” structure
- Chatbot-like phrasing

如果问题较轻，使用 `status=revise` 并标记为低严重度，要求 Writer 局部处理。

如果问题广泛存在，标记为 `major_revise`，并要求 Writer 重写受影响章节。

## Single Mode

当用户只需要一篇博客文章时，使用 Single Mode。

默认流程：

```text
Research → Title Selection → Outline → Outline Confirmation → Article → Review → Revise if needed → Publish Confirmation
```

Single Mode 下，除非用户明确要求 comparison mode，不生成多篇完整文章。

## Batch Mode

当用户要求一次生成多篇博客文章时，使用 Batch Mode。

Batch Mode 规则：

- 每个 topic 创建一个独立 workspace。
- 先为所有 topic 执行 Researcher。
- 批量请求用户确认标题。
- 不直接生成所有完整正文。
- 必须使用 Pilot First Rule。

## Pilot First Rule

当用户要求多篇文章时，先生成第一篇 pilot article。

Pilot flow：

```text
Batch research
  ↓
User confirms titles
  ↓
Writer creates first pilot outline and article
  ↓
Reviewer reviews pilot
  ↓
User confirms style and quality
  ↓
Continue with remaining articles
```

在 pilot 通过 review 或用户明确 override 前，不继续生成剩余文章。

## Done Criteria

博客任务只有在满足以下条件时才算完成：

- `article.md` exists.
- Required sections are present.
- `review.md` status is `pass`, or the user explicitly overrides.
- Publish confirmation gate is approved by the user.
- `process.md` status is `completed`.

## Memory Update Rule

当用户给出以下类型反馈时：

```text
This title is too generic.
This opening is good.
Do not use this structure again.
The product mention feels too hard-sell.
This style is closer to what I want.
```

Orchestrator 应建议把反馈沉淀到：

```text
workspaces/_memory/content/content-lessons.md
workspaces/_memory/content/approved-patterns.md
workspaces/_memory/content/rejected-patterns.md
```

除非 workflow 或用户明确允许，不要在没有用户确认时静默修改 memory 文件。

## Workflow Steps

1. Orchestrator receives user intent.
2. Orchestrator selects blog-writing workflow.
3. Orchestrator creates workspaces/blog/<topic-slug>/ according to this workflow.
4. Orchestrator initializes process.md.
5. Researcher writes research-report.md.
6. Stop at Gate 1: Title Selection.
7. User selects or modifies one or more titles.
8. Orchestrator creates one slugified title folder for each confirmed title.
9. Orchestrator selects the next active title folder.
10. Writer writes outline.md in the current active title folder.
11. Stop at Gate 2: Outline Confirmation for the current active title.
12. Writer writes article.md in the current active title folder.
13. Reviewer writes review.md in the current active title folder.
14. Orchestrator reads review.md for the current active title.
15. If pass, stop at Gate 3 for the current active title.
16. If revise, wait for Human Decision in review.md.
17. If Human Decision = accepted_for_revision, Writer revises article.md in the current active title folder.
18. Reviewer reviews the current active title again if needed.
19. Stop after 2 automatic revision rounds for the current active title.
20. If user confirms publish, mark the current active title as completed.
21. If other selected title folders remain unfinished, Orchestrator selects the next active title folder and repeats steps 10-20.
22. When all selected title folders are completed or stopped by user decision, process.md status becomes completed.

## process.md Format

process.md 必须包含：

```markdown
# Process

## User Intent

## Task Type

blog-writing

## Selected Workflow

.agent/workflows/blog-writing.md

## Active Agents

- orchestrator
- researcher
- writer
- reviewer

## Current Status

## Assumptions

## Topic Slug

## Selected Titles

## Selected Title Folders

## Current Active Title Folder

## Title Status Table

| Title | Title Folder | Outline Status | Article Status | Review Status | Publish Status | Revision Count | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Human Gates

## Revision Count

## Per-title Revision Count

## Decision Log

## Next Action

## Status Values

- initialized
- research_in_progress
- title_selection_pending
- outline_in_progress
- outline_confirmation_pending
- article_in_progress
- review_in_progress
- revision_pending
- publish_confirmation_pending
- completed
```
