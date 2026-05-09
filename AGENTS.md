# AGENTS.md

## Project Purpose

这是一个本地多 Agent 工作流平台，用于通过 Orchestrator 调度不同 Agent 和 Workflow 完成任务。

## Current Scope

当前项目先跑通第一个 workflow，但平台架构不能绑定某一个具体场景。

## Core Architecture

1. Orchestrator Layer
   - 负责理解用户意图、选择 workflow、调度 Agent、控制人工审核节点、维护 process 状态。

2. Agent Layer
   - Agent 是通用角色。
   - Agent 不绑定具体应用场景。
   - Agent 根据 selected workflow 执行对应任务。

3. Workflow Layer
   - Workflow 是具体应用场景文件。
   - Workflow 定义流程、文件结构、产物要求、人工审核点、评分规则、完成条件。

4. Workspace Layer
   - Workspace 保存每次任务的过程文件和最终产物。

## Universal Roles

平台包含 Orchestrator、Researcher、Writer、Reviewer 等通用角色。

具体角色边界以 .agent/rules/platform-rules.md 和对应 SKILL.md 为准。

## Read Order

AI 执行任何任务前，应按以下顺序读取信息：

1. AGENTS.md
2. profile.md
3. .agent/rules/platform-rules.md
4. .agent/workflows/registry.md
5. selected workflow file
6. 当前角色对应的 SKILL.md
7. 当前 workspace 的 process.md

## Role Read Map

- Orchestrator：.agent/orchestrator/SKILL.md、.agent/orchestrator/references/decision-principles.md
- Researcher：.agent/agents/researcher/SKILL.md
- Writer：.agent/agents/writer/SKILL.md
- Reviewer：.agent/agents/reviewer/SKILL.md

## Source Priority

- AGENTS.md 定义最高边界和读取入口。
- .agent/rules/ 定义平台强规则。
- selected workflow 定义具体流程、文件结构、评分标准、human gate 和完成条件。
- 当前角色对应的 SKILL.md 定义角色执行方式。
- workspace/process.md 记录当前任务状态和下一步动作。
- profile.md 只提供长期背景和偏好，不覆盖 selected workflow。

## File Responsibilities

- profile.md：长期使用者背景文件。
- .agent/rules/：平台通用强规则，当前核心文件是 platform-rules.md。
- .agent/orchestrator/：通用决策者能力定义。
- .agent/agents/：通用 Agent 能力定义。
- .agent/workflows/：具体应用场景流程。
- workspaces/：任务产物目录。
