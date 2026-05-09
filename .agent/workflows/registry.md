# Workflow Registry

## Purpose

这是 Orchestrator 选择 workflow 的入口文件。

## Registered Workflows

| Workflow | Path | Status | Required Agents | Trigger Intent |
| --- | --- | --- | --- | --- |
| blog-writing | .agent/workflows/blog-writing.md | active | orchestrator, researcher, writer, reviewer | 写博客、SEO 文章、GEO 友好文章、官网博客、教程型文章、对比型文章、替代方案文章、场景型文章、产品主题博客 |

## Selection Rules

- Orchestrator 必须先读取本文件，再选择 workflow。
- 如果用户意图明确匹配已注册 workflow，优先选择该 workflow。
- 如果用户意图没有匹配项，Orchestrator 必须询问用户或建议创建新 workflow。
