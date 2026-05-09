# AGENTS.md

## Project Purpose

这是一个本地多 Agent 工作流平台，用于通过 Orchestrator 调度不同 Agent 和 Workflow 完成任务。

## Current Scope

当前项目先跑通第一个 workflow，但平台架构不能绑定某一个具体场景。

## Core Architecture

四层架构如下：

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

### Orchestrator

通用决策者，负责：
- 识别用户意图
- 选择 workflow
- 创建 workspace
- 调度 Agent
- 控制 human review gate
- 读取审核结果
- 决定继续、打回、暂停或完成

### Researcher

通用调研者，负责：
- 收集信息
- 整理资料
- 输出分析摘要
- 建立资料索引
- 标注不确定性和缺失信息

### Writer

通用写作者，负责：
- 根据 workflow 要求生成写作产物
- 根据用户确认内容继续写作
- 根据审核意见修改产物
- 保持已确认内容不被擅自改变

### Reviewer

通用审核者，负责：
- 根据 workflow 定义的标准审核产物
- 输出评分、问题、修改建议
- 为 Orchestrator 提供决策依据
- 不直接改写目标产物

## File Responsibilities

- profile.md：长期使用者背景文件。
- .agent/rules/：平台通用强规则。
- .agent/orchestrator/：通用决策者能力定义。
- .agent/agents/：通用 Agent 能力定义。
- .agent/workflows/：具体应用场景流程。
- workspaces/：任务产物目录。
