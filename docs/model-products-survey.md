# 大模型产品调研

## 调研结论

Eureka 的设计参考了主流大模型产品的共同趋势：从单轮聊天走向带上下文、工具、来源和工作流的智能应用。

| 产品/厂商 | 代表能力 | 对 Eureka 的启发 |
| --- | --- | --- |
| OpenAI | ChatGPT、Responses API、工具调用、结构化输出 | 统一 OpenAI-compatible 消息格式，流式输出 |
| Google | Gemini、NotebookLM、长上下文、多模态 | 强调源材料阅读、引用和笔记生成 |
| DeepSeek | 推理模型、OpenAI-compatible API、reasoning_content | 兼容推理字段，避免写回 messages 导致 400 |
| Kimi | 长文本阅读、文档问答、Moonshot API | 面向长网页和长文档调研 |
| 智谱 GLM | GLM API、智能体应用模板 | 支持国产模型 Provider preset |
| Minimax | 多模态、语音、Agent 产品 | 保留未来扩展到多模态输入的架构空间 |
| Qwen | DashScope、通义千问、兼容模式 | 支持国内开发者常用模型 API |

## 为什么采用统一 Provider

课程要求可以调用 Qwen、Kimi、DeepSeek、智谱等 API。不同厂商细节不同，但大多数提供 OpenAI-compatible 接口。Eureka 使用 `providers.yaml` 保存非敏感配置，用 `.env` 保存 API Key。

优势：

- 代码不绑定单一模型。
- 助教可以用自己的 API Key 复现。
- 可以快速切换模型比较效果。
- 更符合真实工程中的模型网关设计。
