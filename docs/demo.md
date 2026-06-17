# Eureka Demo Guide

## 演示目标

证明 Eureka 能真实解决网页阅读和课程调研中的问题：用户不用离开当前页面，就能得到带引用的结构化调研报告。

## 离线演示

1. 启动后端：

```powershell
D:\conda_envs\eureka\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

2. 打开 `web/index.html`。
3. 点击“运行离线演示”。
4. 观察页面中间的 `Agent Trace`。
5. 观察右侧最终报告。
6. 查看证据来源卡片。
7. 点击导出 Markdown 或 PDF。

离线演示不需要 API Key，适合课堂展示和助教复现。

## 真实模型演示

1. 复制 `.env.example` 为 `.env`。
2. 填写对应模型 API Key。
3. 在 Web Demo 或 Chrome 插件中选择 provider。
4. 点击“调用真实模型”或“开始调研”。

## 推荐演示问题

- 对比 MCP 和传统 API 的区别，并说明适合哪些场景。
- 把当前网页整理成课程学习笔记。
- 结合外部资料，分析某个 AI 产品的优势和不足。

## 截图和 GIF

- `docs/screenshots/web-demo.png`
- `docs/screenshots/agent-trace.png`
- `docs/screenshots/demo.gif`
