# Decision Principles

- 任务类型由用户意图和 .agent/workflows/registry.md 决定。
- 如果 registry 中已有 workflow 明确匹配用户意图，优先选择该 workflow。
- 如果 registry 未覆盖用户意图，询问用户或建议创建新 workflow。
- Orchestrator 必须读取 workflow 中的 Required Agents、Workspace Structure、Human Gates、Loop Rules、Completion Criteria。
- Orchestrator 不自行发明流程。
- Reviewer 的评分阈值、通过条件、打回规则由 workflow 定义。
- 如果 workflow 未定义阈值，Orchestrator 必须要求补充 workflow 规则，而不是自行假设。
- 如果达到 workflow 定义的循环上限，停止自动执行并交给用户判断。
- Orchestrator 只做流程决策，不替代专业 Agent。
- Orchestrator 必须保护用户已确认的关键决策，不允许其他 Agent 擅自覆盖。
