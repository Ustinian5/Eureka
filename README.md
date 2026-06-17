# Eureka: Multi-Agent Context-Aware Research Copilot

Eureka 是一个面向学生、研究者和开发者的多 Agent 网页调研助手。它可以读取当前网页正文，判断是否需要外部检索，拆解调研问题，搜索证据，生成带引用的 Markdown 报告，并保存为可导出的研究笔记。

项目提供 Chrome 插件和 Web Demo 两种展示方式，支持 Qwen、Kimi、DeepSeek、智谱 GLM、OpenAI 和任意 OpenAI-compatible API。

## 功能

- Chrome 插件读取当前标签页正文、标题和 URL。
- Chrome 插件采用 Manifest V3、`activeTab` 最小权限、动态脚本注入和独立设置页。
- 插件弹窗提供后端连接状态、Provider/模板切换、请求取消、Agent Trace、来源列表和 Markdown/PDF 导出入口。
- Web Demo 支持离线演示，不需要 API Key。
- Multi-Agent 工作流：Router、Context Analyst、Research Planner、Search Evidence、Report Writer、Critic。
- NDJSON 流式输出 Agent Trace 和最终报告。
- Provider preset 支持 Qwen、Kimi、DeepSeek、智谱 GLM、OpenAI 和 Custom。
- SQLite 保存历史报告、Agent Trace 和证据来源。
- 支持 Markdown/PDF 导出。
- Evidence Scorer 对来源进行类型识别、置信度评分和引文片段提取。
- Citation Verifier 检查最终报告是否包含来源引用。
- DeepSeek-R1 `reasoning_content` 兼容处理，避免 API 400。

## 目录结构

```text
backend/
  app/
    agents/         多 Agent 实现
    export/         Markdown 导出
    storage/        SQLite 历史记录
    tools/          网页抓取和引文提取工具
    config.py       环境变量配置
    intent.py       意图路由
    llm_client.py   OpenAI-compatible LLM 客户端
    main.py         FastAPI 入口
    models.py       共享数据结构
    search.py       DuckDuckGo 搜索工具
    workflow.py     总结/深度调研工作流
  tests/            核心单元测试
extension/
  manifest.json     Chrome MV3 清单
  content.js        网页正文提取
  options.html      插件设置页
  popup.html        插件面板
  popup.css         插件样式
  popup.js          流式请求和输出
web/
  index.html        Web 演示工作台
  app.js            NDJSON 事件流渲染
docs/
  report.md         课程报告
  report.pdf        提交 PDF
  screenshots/      Web Demo 截图和 GIF
examples/           固定评测样例
scripts/            启动、测试、文档构建脚本
```

## 启动后端

本项目使用 Conda 环境，推荐安装到 `D:\conda_envs\eureka`。当前 PowerShell 里 `conda` 不在 PATH，因此下面使用完整路径。

```powershell
$env:CONDA_OVERRIDE_CUDA='0'
& C:\Users\Lenovo\anaconda3\Scripts\conda.exe env create -p D:\conda_envs\eureka -f environment.yml --json
Copy-Item .env.example .env
```

编辑 `.env`：

```env
BASE_URL=https://api.openai.com/v1
API_KEY=你的 API Key
MODEL=gpt-4o-mini
DEEPSEEK_API_KEY=你的 DeepSeek Key
QWEN_API_KEY=你的 Qwen Key
KIMI_API_KEY=你的 Kimi Key
ZHIPU_API_KEY=你的智谱 Key
```

启动服务：

```powershell
D:\conda_envs\eureka\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Web Demo

打开：

```text
web/index.html
```

点击“运行离线演示”即可看到完整 Multi-Agent 流程，不需要 API Key。点击“调用真实模型”会使用所选 provider 调用后端 `/api/research`。

## 加载 Chrome 插件

1. 打开 `chrome://extensions/`。
2. 开启“开发者模式”。
3. 点击“加载已解压的扩展程序”。
4. 选择本项目的 `extension` 目录。
5. 打开任意网页，点击 Eureka 插件图标，输入问题或留空，点击“开始调研”。

插件设置页可配置后端地址、默认 Provider 和默认报告模板。默认后端地址为：

```text
http://127.0.0.1:8000
```

## Chrome 插件打包

项目已补齐 Chrome Web Store 上架前的基础材料：最小权限 Manifest、16/32/48/128 图标、隐私政策、商店文案草稿和打包脚本。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package_extension.ps1
```

产物：

```text
dist/eureka-extension.zip
```

## API

### `POST /api/research`

请求：

```json
{
  "context": "当前网页正文",
  "user_query": "结合文章内容，对比 MCP 和传统 API"
}
```

响应：`application/x-ndjson` 流式事件。

实际响应格式为 NDJSON：

```json
{"type":"trace","agent":"RouterAgent","content":"判断为 deep_research"}
{"type":"token","content":"# 调研报告"}
{"type":"done","report_id":1}
```

### `GET /api/providers`

返回可用模型供应商。

### `GET /api/reports`

返回历史报告。

### `GET /api/reports/{id}/markdown`

导出 Markdown 报告。

### `GET /api/reports/{id}/pdf`

导出 PDF 报告。

## 测试

当前测试不依赖 FastAPI/httpx 安装，覆盖核心纯 Python 逻辑：

```powershell
D:\conda_envs\eureka\python.exe -B -m unittest discover -s backend\tests -v
```

覆盖项：

- 意图路由 JSON 解析和安全降级。
- DeepSeek-R1 `reasoning_content` 流式解析。
- 标准 messages 清洗，防止把 `reasoning_content` 写回 API。
- 搜索结果归一化和去重。
- 深度调研工作流注入外部引用。
- Chrome Manifest V3 关键配置。
- Chrome Web Store readiness：最小权限、图标、选项页、CSP、隐私文档和打包脚本。
- Multi-Agent 事件流。
- Provider preset。
- SQLite 保存和 Markdown 导出。
- Web Demo 关键资产。
- 证据评分、引用校验、网页正文提取。
- PDF 导出 API。

## 一键脚本

```powershell
.\scripts\start_backend.ps1
.\scripts\run_tests.ps1
.\scripts\build_docs.ps1
```

## 演示资产

- Web Demo 截图：[docs/screenshots/web-demo.png](docs/screenshots/web-demo.png)
- Agent Trace 截图：[docs/screenshots/agent-trace.png](docs/screenshots/agent-trace.png)
- Demo GIF：[docs/screenshots/demo.gif](docs/screenshots/demo.gif)

## 课程提交材料

- 课程报告 Markdown：[docs/report.md](docs/report.md)
- 课程报告 PDF：[docs/report.pdf](docs/report.pdf)
- README PDF：[docs/README.pdf](docs/README.pdf)
- 架构说明：[docs/architecture.md](docs/architecture.md)
- 演示说明：[docs/demo.md](docs/demo.md)
- 模型产品调研：[docs/model-products-survey.md](docs/model-products-survey.md)
- 项目评测：[docs/evaluation.md](docs/evaluation.md)
- 设计决策：[docs/design-decisions.md](docs/design-decisions.md)
- Chrome 上架清单：[docs/chrome-store-readiness.md](docs/chrome-store-readiness.md)
- 隐私政策：[docs/privacy-policy.md](docs/privacy-policy.md)
- 商店文案草稿：[docs/store-listing.md](docs/store-listing.md)

## 开源协议

本项目使用 MIT License，见 [LICENSE](LICENSE)。
