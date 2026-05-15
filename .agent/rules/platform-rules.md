# Platform Rules

## Purpose

这是所有 Agent 和 Workflow 都必须遵守的平台级强规则。

## Global Rules

- Orchestrator 是唯一流程决策者。
- Agent 是通用角色，不绑定具体应用场景。
- Workflow 负责定义具体场景流程和约束。
- Agent 执行前必须读取当前 selected workflow。
- Agent 不能越权执行其他 Agent 的职责。
- Agent 必须通过 workspace 文件产物协作。
- 不允许跳过 selected workflow 中定义的步骤。
- 不允许跳过 human review gate。
- 不允许虚构事实、数据、来源、用户背景或产品能力。
- 默认不允许引入 API key、数据库、Web UI 或外部服务。
- 只有 selected workflow 明确声明允许外部工具时，才可以使用对应工具。
- API key 只能通过 .env 或环境变量读取，不得写入代码、日志、workspace 或 Git。
- 数据库默认不得使用；如 workflow 明确允许，仅可使用本地 SQLite 或 JSON/CSV 文件，除非用户另行批准。
- 抓取仅限公开可访问网页。
- 必须遵守 robots.txt、平台规则和合理请求频率。
- 不得绕过登录、验证码、付费墙或访问限制。
- 不得抓取私人数据。
- 不得自动群发联系信息。
- 所有外部工具使用必须在 workflow 输出数据中保留记录。
- 不允许把具体 workflow 的业务规则写进通用 Agent 文件。
- 每次关键动作必须更新 process.md。
- 所有输出必须可追踪、可审核、可复用。

## Role Boundaries

- Orchestrator 负责流程决策，不负责专业产物创作。
- Researcher 负责信息研究，不负责最终写作。
- Writer 负责写作产物，不负责最终审核。
- Reviewer 负责审核建议，不直接改写目标产物。
- Channel Analyst 负责渠道候选清洗、去重、评分解释和复核建议，不负责自动联系渠道。

## Human Review Rules

- 用户是最终甲方和最终决策者。
- Orchestrator 必须在 selected workflow 定义的 Human Gate 停止。
- Human Gate 的数量、位置和通过条件由当前 workflow 定义。
- 人工未确认前，不得进入下一阶段。
- 用户可以接受、拒绝、修改、合并、补充要求。
- 用户最新指令优先于之前的自动建议。
- 如果 workflow 定义了自动循环上限，达到上限后必须停止并交给用户判断。
- 不允许在该文件中写任何具体场景的审核点。

## Human Decision Types

通用人工决策可以包括：

- approve
- reject
- revise
- merge
- select
- add_requirements
- stop

具体决策含义由 selected workflow 定义。

## Workspace Rules

- 所有任务产物必须写入 workspaces/。
- 不同任务类型应使用不同子目录，例如 workspaces/<task-type>/。
- 默认每个任务 workspace 应包含 process.md。
- 如果 selected workflow 明确声明自身是数据型 workflow，并定义了等价的结构化运行记录文件，例如 data/runs/<run-id>.json，则可用该 run JSON 替代 process.md。
- 用户不需要日常查看过程文件；具体用户可见产物由 selected workflow 定义。
- 具体 workspace 文件结构由 selected workflow 定义。
- process.md 必须记录用户意图、任务类型、当前状态、active agents、human gates、revision count、decision log、next action。
- 不允许在 platform-rules.md 中写死任何具体 workflow 的文件结构。
- 产物文件命名必须简洁、稳定、可读。
- 版本管理优先交给 Git。
- 除非 workflow 或用户明确要求，不要生成大量重复版本文件。

## Process File Minimum Fields

process.md 至少应记录：

- User Intent
- Task Type
- Selected Workflow
- Active Agents
- Current Status
- Human Gates
- Revision Count
- Decision Log
- Next Action
