# Eureka Evaluation

## 目标

评测 Eureka 是否真正解决网页阅读和调研痛点，而不是只生成流畅文本。

## 案例矩阵

| 案例 | 输入 | 期望行为 | 检查点 |
| --- | --- | --- | --- |
| 技术调研 | `examples/mcp_article.txt` | 判断为深度调研，生成 MCP vs API 报告 | Agent Trace、引用、证据卡 |
| AI 产品分析 | `examples/ai_product_article.txt` | 输出产品对比和适用场景 | 模板结构、来源列表 |
| 论文阅读 | `examples/paper_abstract.txt` | 输出论文阅读笔记 | 背景、方法、局限 |
| 网页总结 | 任意短网页 | 不搜索也能总结 | route 为 context_answer |
| 引用校验 | 有证据但正文无引用 | Citation Verifier 追加说明 | 引用校验区 |

## 人工评分表

| 维度 | 1 分 | 3 分 | 5 分 |
| --- | --- | --- | --- |
| 准确性 | 多处错误 | 基本正确 | 结论清晰且无明显错误 |
| 完整性 | 只回答局部 | 覆盖主要问题 | 覆盖背景、结论、限制和建议 |
| 引用质量 | 无来源 | 有来源但弱 | 来源明确、可追踪、有证据卡 |
| 可读性 | 结构混乱 | 基本可读 | Markdown 清晰、适合复用 |
| 实用性 | 难以使用 | 可辅助阅读 | 可直接作为调研笔记 |

## 当前自动化验证

运行：

```powershell
D:\conda_envs\eureka\python.exe -B -W ignore -m unittest discover -s backend\tests -v
```

自动测试覆盖 Agent 事件流、Provider 配置、导出、SQLite 存储、证据评分、引用校验和前端资产。
