# Human Review Rules

## Purpose

这是平台级 human in the loop 规则。

## Universal Human Review Principles

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
