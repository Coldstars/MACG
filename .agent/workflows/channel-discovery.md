# Workflow: Channel Discovery

## Purpose

`channel-discovery` 用于根据 `profile.md` 发现匹配产品、行业、目标用户和使用场景的推广/合作渠道，包括 YouTube 技术博主、Newsletter、技术博客、开发者社区、垂直生态创作者、SEO/开发者媒体和开源项目维护者等。

这个 workflow 的目标不是生成一堆过程文档，而是产出一个渠道运营可以直接打开查看的静态 HTML 看板，并同时保留 Agent 可读的结构化数据，用于后续合并、去重、复盘和二次分析。

## Trigger

当用户意图包含以下内容时，Orchestrator 应选择本 workflow：

- 找推广渠道
- 找付费推广渠道
- 找 YouTube 博主
- 找 Newsletter 赞助
- 找技术博客合作
- 找 AI Agent / LangChain / RAG 创作者
- 找 SEO / Python / Web scraping 渠道
- creator sponsorship
- newsletter sponsorship
- paid channel finder
- channel discovery agent
- 渠道发现 Agent

## Required Agents

- Orchestrator
- Channel Analyst

## Optional Agents

- Researcher
- Reviewer
- Writer

仅当需要补充关键词策略、渠道来源、市场/竞品渠道研究，或工具输出候选不足时启用 Researcher。
仅当准备真实 outreach、发现合规风险、候选质量异常，或用户明确要求最终审核时启用 Reviewer。
仅当需要生成合作邮件、私信模板、赞助介绍文案、落地页文案时启用 Writer。

## Workspace Location

```text
workspaces/channel-discovery/<campaign-slug>/
```

`<campaign-slug>` 必须简短、稳定、可读，例如：

```text
profile-channel-discovery
python-scraping-creators
seo-automation-newsletters
```

## Workspace Structure

本 workflow 是数据型 workflow。`data/runs/<run-id>.json` 是 `process.md` 的等价结构化运行记录，必须记录 input、provider status、候选数据、评分结果、summary 和下一步复核状态。

每次执行本 workflow，用户只看一个全局汇总文件：

```text
workspaces/channel-discovery/index.html
```

不要再为每个 campaign 生成单独 `index.html`。每次抓取只保存该次 campaign 的结构化数据，并把所有 campaign 的 master 数据合并、查重后刷新全局 `index.html`。

同时必须保留 Agent 可读数据层：

```text
workspaces/channel-discovery/
├── index.html
├── data/
│   ├── runs/
│   │   └── <run-id>.json
│   ├── master-candidates.json
│   ├── all-candidates.json
│   ├── review-queue.json
│   └── all-candidates.csv
└── <campaign-slug>/
    └── data/
        ├── runs/
        │   └── <run-id>.json
        ├── master-candidates.json
        ├── selected-50.json
        ├── review-queue.json
        └── selected-50.csv
```

### File Responsibilities

| File | Consumer | Responsibility |
| --- | --- | --- |
| `workspaces/channel-discovery/index.html` | 用户 / 渠道运营 | 唯一人类可读的全局渠道候选看板，必须使用中文 UI |
| `data/runs/<run-id>.json` | Agent / Codex | 单次抓取完整记录，包括 input、raw、normalized、scored、selected、summary |
| `data/master-candidates.json` | Agent / Codex | 跨 campaign、跨多次 run 合并后的长期渠道池 |
| `data/all-candidates.json` | HTML / Agent | 全局 HTML 展示使用的去重渠道合集 |
| `data/review-queue.json` | Agent / 用户 | 全局人工复核队列，包含 review status、review notes、缺失信息和复核重点 |
| `data/all-candidates.csv` | 用户 / 表格工具 | 全局渠道合集表格版本，方便导入 Excel、飞书、多维表格 |
| `<campaign-slug>/data/selected-50.json` | Agent / Codex | 单次 campaign 的 Top 50 候选，用于调试和复盘，不是用户主入口 |

默认不生成 `process.md`、`campaign-brief.md`、`seed-keywords.md`、`source-plan.md`、`shortlist.md`、`outreach-plan.md`、`review.md` 等大量 Markdown 产物。

如平台全局规则仍要求 `process.md`，Orchestrator 可把本 workflow 的 process 信息写入 `data/runs/<run-id>.json.summary`，或在全局规则中加入“数据型 workflow 可用 run JSON 替代 process.md”的例外。不要让用户日常查看过程 Markdown。

## Input Contract

执行本 workflow 前，至少需要确认以下输入：

```yaml
profile_path: profile.md
campaign_slug: profile-channel-discovery
product_name: 从 profile.md 或用户输入推导
target_channels:
  - youtube
  - newsletter
  - technical_blog
keywords:
  - 默认优先从 profile.md 的竞品/参考站生成竞品相关渠道查询
  - 然后补充行业关键词、产品线、目标用户和使用场景
language: English
max_raw_candidates: 500
selected_count: 50
recent_days: 120
providers:
  - auto
```

## Output Contract

每次执行 `channel-discovery` 必须生成：

```text
workspaces/channel-discovery/index.html
workspaces/channel-discovery/data/master-candidates.json
workspaces/channel-discovery/data/all-candidates.json
workspaces/channel-discovery/data/review-queue.json
workspaces/channel-discovery/data/all-candidates.csv
workspaces/channel-discovery/data/runs/<run-id>.json
workspaces/channel-discovery/<campaign-slug>/data/runs/<run-id>.json
workspaces/channel-discovery/<campaign-slug>/data/master-candidates.json
workspaces/channel-discovery/<campaign-slug>/data/selected-50.json
workspaces/channel-discovery/<campaign-slug>/data/review-queue.json
workspaces/channel-discovery/<campaign-slug>/data/selected-50.csv
```

### `index.html` 必须包含

- 页面标题：`<product_name> 渠道库`
- 中文 UI
- 最新 campaign / run 信息
- 更新时间
- 顶部统计卡片
- 本次搜索条件和 provider 状态
- Top 10 推荐渠道
- 多次抓取合并后的去重渠道表格
- 每个渠道的评分和分项分数
- 联系方式、联系页、赞助页、media kit 链接
- 推荐合作方式
- 缺失信息提示
- 搜索、筛选、排序、展开详情交互
- 评分规则说明
- 安全和数据边界提示

### `data/runs/<run-id>.json` 必须包含

```json
{
  "run_id": "2026-05-13-ai-agent-tutorial",
  "campaign": "profile-channel-discovery",
  "generated_at": "2026-05-13T18:30:00Z",
  "input": {
    "profile_context": {}
  },
  "raw_candidates": [],
  "normalized_candidates": [],
  "scored_candidates": [],
  "selected_50": [],
  "review_queue": [],
  "summary": {}
}
```

### `data/master-candidates.json` 必须包含

- 所有历史 run 合并后的候选渠道
- 去重后的唯一渠道记录
- `first_seen_run_id`
- `last_seen_run_id`
- `seen_count`
- `last_score`
- `best_score`
- `status`
- `notes`

### `data/all-candidates.json`

必须保存当前全局 HTML 展示使用的去重渠道合集。若 HTML 内嵌数据与 `all-candidates.json` 不一致，以 `all-candidates.json` 为准。

### `data/all-candidates.csv`

必须保存当前全局渠道合集的表格版本，用于人工导入 Excel、飞书、多维表格。

### `data/review-queue.json`

必须保存人工复核队列，默认 `review_status` 为 `new`，允许后续人工维护 `shortlisted`、`rejected`、`contacted`、`approved` 和 `review_notes`。

## Channel Types

支持以下渠道类型：

- YouTube creator
- Newsletter
- Technical blog
- Developer community
- AI tools directory
- SEO media
- Automation workflow creator
- GitHub project maintainer

## Candidate Fields

每个候选渠道至少包含：

```text
rank
channel_type
platform
name
url
canonical_url
domain
platform_id
topic
audience
subscribers_or_followers
avg_views
recent_activity
contact_email
contact_page
sponsor_page
media_kit_url
fit_score
priority
score_breakdown
score_reason
recommended_collaboration
estimated_priority
missing_fields
notes
source_keyword
source_run_id
source_provider
source_url
discovery_query
confidence
review_status
review_notes
first_seen_run_id
last_seen_run_id
seen_count
```

缺失字段必须显示 `Unknown`，不得编造。

## Scoring Standards

总分 100 分：

| Dimension | Max Score | Meaning |
| --- | ---: | --- |
| Audience Match Score | 30 | 受众是否匹配 profile.md 中的目标用户、行业关键词和使用场景 |
| Content Fit Score | 20 | 内容是否适合做教程、demo、工具集成、代码示例 |
| Activity Score | 15 | 最近是否持续更新，内容是否仍活跃 |
| Sponsorship Readiness Score | 10 | 是否有 sponsor、advertise、media kit、合作入口 |
| Contactability Score | 10 | 是否有邮箱、联系页、商务合作入口 |
| Authority / Reach Score | 10 | 粉丝数、浏览量、订阅数、影响力 |
| Long-term Search Value Score | 5 | 内容是否具有长期搜索流量价值 |

### Priority

```text
High:   fit_score >= 80
Medium: fit_score >= 60 and < 80
Low:    fit_score < 60
```

## Deduplication Rules

必须尽可能去重：

1. YouTube 使用 `channel_id` / `platform_id` 优先去重。
2. Newsletter / Blog 使用 `canonical_url` 或 `domain` 去重。
3. 如果没有 URL，使用 `normalized_name + platform` 去重。
4. `master-candidates.json` 中同一渠道多次出现时，更新：
   - `last_seen_run_id`
   - `seen_count`
   - `last_score`
   - `best_score`
5. 不要把同一频道、同一 newsletter、同一 domain 重复展示在全局渠道库中。

## HTML Report Requirements

`index.html` 必须是自包含静态页面：

- 内联 CSS
- 内联 JavaScript
- 不依赖外部 CDN
- 打开本地 HTML 即可查看
- 支持移动端
- 企业后台风格
- 浅灰背景
- 白色卡片
- 蓝色强调色
- 表格信息清晰
- 支持展开详情

表格交互必须包含：

- 关键词搜索
- 按 channel_type 筛选
- 按 priority 筛选
- 只看有联系方式的候选
- 只看有 sponsor page / media kit 的候选
- 按 fit_score 排序
- 点击行展开详情

## Recommended Collaboration Generation

`recommended_collaboration` 必须结合 `profile.md` 中的产品、目标用户和真实使用场景，不能泛泛写“推广产品”。

示例：

- 赞助 YouTube 教程：展示一个使用 `{product_name}` 的具体工作流
- Newsletter 赞助位：面向 profile 中的目标用户定位 `{product_name}`
- 技术文章：构建一个实用集成或工作流
- 工作流模板：自动化一个可复用使用场景
- 生态指南：解释 `{product_name}` 如何适配 profile 中定义的场景

## Human Gates

### Gate 1: Campaign Scope Confirmation

确认本次渠道发现范围：

- campaign slug
- channel types
- keywords
- language / region
- max raw candidates
- selected count
- 是否允许 YouTube Data API
- 是否允许公开网页抓取
- 是否使用 profile.md 自动生成关键词

### Gate 2: Candidate Review

生成全局 `index.html` 后，用户查看渠道合集，决定是否继续：

- 扩展关键词
- 加入新渠道类型
- 降低 / 提高阈值
- 进入 outreach 文案生成

### Gate 3: Outreach Confirmation

只有当用户明确要求生成合作邮件、私信或联系话术时，才启用 Writer。不得自动发送邮件。

## Safety and Compliance Rules

- 本 workflow 允许使用 workflow-scoped 外部工具：本地 Python 工具、公开搜索结果、公开网页抓取、可选 YouTube Data API、可选 SERP API endpoint。
- 只采集公开页面信息。
- 不绕过登录、验证码、付费墙或访问限制。
- 不抓取私人数据。
- 不做自动骚扰式群发。
- 不伪造邮箱、报价、播放量、订阅数。
- 不把猜测写成事实。
- 联系方式、赞助页、粉丝数、播放量、报价等缺失时必须显示 `Unknown`。
- 发现渠道时优先搜索已经覆盖、评测、教程、赞助或对比过 profile 中竞品/参考站的渠道。
- 必须尽量从公开页面、公开 contact/about/advertise/sponsor/media kit 页面、公开视频描述中提取邮箱。
- 如果抓不到邮箱，必须保留可人工继续联系或查找的公开联系方式入口，例如 contact/about 页面、赞助页、media kit、频道主页、GitHub profile、项目主页、作者网站或公开社交主页。
- 不得绕过登录或验证码去查看平台隐藏邮箱。
- API key 只能从 `.env` 或环境变量读取。
- 不允许把 API key 写入代码、日志、workspace 或 Git。
- 抓取必须使用合理请求频率。
- 所有候选渠道必须保留来源 keyword / source。

## Workflow Steps

1. Orchestrator 读取 registry，选择 `channel-discovery`。
2. Orchestrator 确认 campaign scope。
3. 如需要补充关键词策略、渠道来源或竞品渠道研究，Orchestrator 可启用 Researcher。
4. `tools/channel-finder` 执行候选发现、抓取、提取、评分、去重，保存 campaign 数据，并刷新全局 `workspaces/channel-discovery/index.html`。
5. Channel Analyst 检查全局 `data/all-candidates.json`、`data/review-queue.json` 和最新 `data/runs/<run-id>.json`。
6. 如准备真实 outreach、发现合规风险或候选质量异常，Orchestrator 可启用 Reviewer。
7. 用户打开 `workspaces/channel-discovery/index.html` 查看结果。

## Done Criteria

本 workflow 完成时必须满足：

- `workspaces/channel-discovery/index.html` 已生成且可本地打开。
- `data/runs/<run-id>.json` 已保存单次 run 数据。
- `data/master-candidates.json` 已更新。
- `data/all-candidates.json`、`data/review-queue.json` 和 `data/all-candidates.csv` 已生成。
- 全局 index 展示多次抓取后的去重渠道合集。
- 缺失信息显示 `Unknown`。
- 没有自动发送邮件。
- 没有绕过登录、验证码、付费墙或平台限制。
