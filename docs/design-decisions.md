# Eureka Design Decisions

## 1. 为什么使用轻量 Multi-Agent

Eureka 没有引入 AutoGen、LangGraph 等重型框架，而是实现了内部 Orchestrator。

原因：

- 课程项目需要可读、可复现、易解释。
- 轻量 Agent 类更容易写测试。
- 用户能清楚看到每一步 Agent Trace。
- 降低安装复杂度，避免框架版本问题影响复现。

## 2. 为什么使用 NDJSON

报告生成需要流式输出，同时还要展示 Agent Trace。纯文本流无法表达事件类型，SSE 又需要额外前端处理。NDJSON 每行一个 JSON 对象，简单、稳定、易测试。

## 3. 为什么保留离线 Demo

真实模型 API Key 不适合提交到开源仓库，助教也不一定配置相同模型。离线 Demo 可以证明系统流程、前端展示和导出功能都可运行。

## 4. 为什么使用 SQLite

SQLite 不需要额外服务，适合本地课程项目。它能保存历史报告、Agent Trace 和证据来源，增强项目完整度。

## 5. 为什么增加证据评分和引用校验

大模型应用最常见问题是幻觉和无来源结论。Evidence Scorer 和 Citation Verifier 能把“答案生成”升级为“有证据链的调研”。
