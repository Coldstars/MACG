# Workspace Rules

## Purpose

这是平台级 workspace 和文件产物规则。

## Universal Workspace Rules

- 所有任务产物必须写入 workspaces/。
- 不同任务类型应使用不同子目录，例如 workspaces/<task-type>/。
- 每个任务 workspace 必须包含 process.md。
- 具体 workspace 文件结构由 selected workflow 定义。
- process.md 必须记录用户意图、任务类型、当前状态、active agents、human gates、revision count、decision log、next action。
- 不允许在 workspace-rules.md 中写死任何具体 workflow 的文件结构。
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
