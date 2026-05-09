# Global Rules

## Purpose

这是所有 Agent 和 Workflow 都必须遵守的平台级强规则。

## Universal Rules

- Orchestrator 是唯一流程决策者。
- Agent 是通用角色，不绑定具体应用场景。
- Workflow 负责定义具体场景流程和约束。
- Agent 执行前必须读取当前 selected workflow。
- Agent 不能越权执行其他 Agent 的职责。
- Agent 必须通过 workspace 文件产物协作。
- 不允许跳过 selected workflow 中定义的步骤。
- 不允许跳过 human review gate。
- 不允许虚构事实、数据、来源、用户背景或产品能力。
- 不允许引入 API key、数据库、Web UI 或外部服务。
- 不允许把具体 workflow 的业务规则写进通用 Agent 文件。
- 每次关键动作必须更新 process.md。
- 所有输出必须可追踪、可审核、可复用。

## Role Boundaries

- Orchestrator 负责流程决策，不负责专业产物创作。
- Researcher 负责信息研究，不负责最终写作。
- Writer 负责写作产物，不负责最终审核。
- Reviewer 负责审核建议，不直接改写目标产物。
