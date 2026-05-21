# GrowthPilot-Agent

GrowthPilot-Agent 是一个面向内容电商场景的多 Agent 商家增长助手。

项目模拟小红书 / 抖音 / 内容电商平台中的商家运营流程，基于商品数据、销售数据和用户评论，自动完成经营分析、用户洞察、内容策略生成、合规审核和增长报告导出。

本项目不是普通的“AI 文案生成器”，而是一个包含多 Agent 工作流、Prompt 模板管理、Agent Trace 可观测性、CSV 上传、上传字段校验、Markdown 报告导出与下载、evals 自动化评测的 Agent 应用工程项目。

---

## 1. 项目背景

在内容电商场景中，商家和运营人员通常需要完成以下工作：

1. 分析商品销售表现
2. 理解用户评论和真实痛点
3. 生成适合小红书、抖音等平台的内容策略
4. 检查内容是否存在夸大宣传、绝对化用语或违规风险
5. 输出可复盘的运营报告

传统方式依赖人工分析，效率较低。GrowthPilot-Agent 通过多 Agent 协作，将这些流程自动化，形成从数据分析到内容生成再到合规审核的完整闭环。

---

## 2. 核心功能

当前项目已经实现：

- 商品、销售、评论数据读取
- GMV、CTR、CVR、退款率等运营指标计算
- Streamlit 页面侧边栏 CSV 上传
- 上传 CSV 字段校验
- examples 上传示例数据
- 销售数据分析 Agent
- 用户评论洞察 Agent
- 内容策略 Agent
- 合规审核 Agent
- Supervisor 多 Agent 工作流
- Agent Trace 执行日志面板
- Prompt 模板文件管理
- Markdown 增长报告导出与下载
- evals 自动化评测模块

---

## 3. 项目亮点

### 3.1 多 Agent 协作

项目将复杂运营任务拆成多个专业 Agent：

| Agent | 作用 |
|---|---|
| Sales Analysis Agent | 分析 GMV、CTR、CVR、退款率等经营指标 |
| User Insight Agent | 从用户评论中提取痛点、正反馈、负反馈和内容机会 |
| Content Strategy Agent | 生成小红书标题、正文、抖音脚本和发布建议 |
| Compliance Agent | 审核内容中的合规风险 |
| Supervisor Agent | 串联多个专业 Agent，形成完整工作流 |

---

### 3.2 Supervisor 多 Agent 工作流

Supervisor Agent 会自动调度以下流程：

```text
销售数据分析
    ↓
用户评论洞察
    ↓
内容策略生成
    ↓
内容合规审核
    ↓
生成完整增长报告
```

这使项目从“多个独立按钮”升级为“多 Agent 工作流系统”。

---

### 3.3 Agent Trace 可观测性

Supervisor 工作流会记录每个 Agent 的执行日志，包括：

- Agent 名称
- 执行说明
- 执行状态
- 执行耗时
- 输出预览
- 错误信息

这有助于定位问题，也更接近真实 Agent 平台中的可观测性能力。

---

### 3.4 Prompt 模板管理

项目将 Prompt 从 Python 代码中拆出，统一放在：

```text
app/prompts/
```

这样可以做到：

- Prompt 和业务代码解耦
- 方便单独调试 Prompt
- 方便后续版本迭代
- 更符合工程化开发习惯

---

### 3.5 CSV 上传与字段校验

项目支持在 Streamlit 页面侧边栏上传：

```text
product.csv
sales.csv
comments.csv
```

上传后系统会自动检查字段是否完整。

如果字段缺失，例如 `product.csv` 缺少 `product_name`，页面会提示：

```text
product.csv 缺少字段：product_name
```

如果上传不完整或字段校验失败，系统会自动回退到默认示例数据，避免页面崩溃。

---

### 3.6 evals 自动化评测

项目提供 `evals` 模块，可以自动检查：

- 默认数据文件是否存在
- 默认数据列是否完整
- 默认运营指标是否生成
- examples 上传示例文件是否存在
- examples 上传示例字段是否完整
- examples 上传示例是否能正常生成运营指标
- Prompt 模板文件是否存在
- Prompt 模板变量是否正确
- Prompt 是否能正常渲染
- 合规审核 Agent 是否能识别高风险内容

当前评测结果：

```text
本地静态评测：34 / 34 通过
带 LLM 评测：37 / 37 通过
```

---

## 4. 技术栈

| 模块 | 技术 |
|---|---|
| 编程语言 | Python |
| 前端页面 | Streamlit |
| 数据处理 | pandas |
| 大模型调用 | DashScope 通义千问，OpenAI SDK 兼容模式 |
| Agent 编排 | 自定义多 Agent 工作流 |
| Prompt 管理 | txt 模板文件 |
| 评测模块 | Python 脚本 + JSON 测试用例 |
| 报告导出 | Markdown |
| 环境管理 | conda |

---

## 5. 项目结构

```text
GrowthPilot-Agent/
├── app/
│   ├── agents/
│   │   ├── compliance_agent.py
│   │   ├── content_agent.py
│   │   ├── insight_agent.py
│   │   ├── sales_agent.py
│   │   └── supervisor_agent.py
│   ├── prompts/
│   │   ├── compliance_prompt.txt
│   │   ├── content_strategy_prompt.txt
│   │   ├── sales_analysis_prompt.txt
│   │   └── user_insight_prompt.txt
│   ├── __init__.py
│   ├── config.py
│   ├── data_service.py
│   ├── llm.py
│   ├── prompt_loader.py
│   └── report_service.py
├── data/
│   ├── product.csv
│   ├── sales.csv
│   └── comments.csv
├── evals/
│   ├── eval_cases.json
│   └── run_eval.py
├── examples/
│   └── upload_samples/
│       ├── product.csv
│       ├── sales.csv
│       ├── comments.csv
│       └── README.md
├── frontend/
│   └── streamlit_app.py
├── outputs/
│   └── growth_report.md
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 6. 数据说明

项目使用三类数据。

### 6.1 商品数据

文件位置：

```text
data/product.csv
```

包含字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| product_name | 商品名称 |
| category | 商品类目 |
| price | 商品价格 |

---

### 6.2 销售数据

文件位置：

```text
data/sales.csv
```

包含字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| views | 曝光量 |
| clicks | 点击量 |
| orders | 订单数 |
| refunds | 退款数 |

---

### 6.3 用户评论数据

文件位置：

```text
data/comments.csv
```

包含字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| rating | 用户评分 |
| comment | 用户评论 |

---

## 7. 核心指标

项目会自动计算以下运营指标：

| 指标 | 公式 | 含义 |
|---|---|---|
| GMV | price × orders | 成交金额 |
| CTR | clicks / views | 点击率 |
| CVR | orders / clicks | 转化率 |
| refund_rate | refunds / orders | 退款率 |

---

## 8. 环境准备

### 8.1 创建 conda 环境

```bash
conda create -n agenttt python=3.10 -y
conda activate agenttt
```

---

### 8.2 安装依赖

```bash
pip install -r requirements.txt
```

当前推荐依赖版本：

```txt
streamlit==1.49.1
pandas==2.3.3
python-dotenv==1.2.2
openai==2.36.0
```

说明：本项目使用 `streamlit==1.49.1`，用于避免部分新版本 Streamlit 服务端兼容性问题。

---

### 8.3 配置 DashScope API Key

在项目根目录创建 `.env` 文件：

```env
DASHSCOPE_API_KEY=你的DashScope_API_Key
```

注意：

`.env` 文件不要上传到 GitHub。

---

## 9. 启动项目

在项目根目录执行：

```bash
python -m streamlit run frontend/streamlit_app.py
```

启动后浏览器会打开：

```text
http://localhost:8501
```

---

## 10. 页面功能说明

页面主要包括以下模块：

1. 核心经营指标展示
2. 商品运营数据表
3. 用户评论数据表
4. 原始销售数据表
5. CSV 数据上传
6. 上传 CSV 字段校验
7. 销售数据分析 Agent
8. 用户评论洞察 Agent
9. 内容策略 Agent
10. Supervisor 多 Agent 工作流
11. Agent Trace 执行日志
12. 合规审核 Agent
13. Markdown 增长报告导出与下载

---

## 11. CSV 上传示例数据

项目支持在 Streamlit 页面侧边栏上传自定义 CSV 数据。

为了方便测试，项目提供了一套标准上传样例：

```text
examples/upload_samples/product.csv
examples/upload_samples/sales.csv
examples/upload_samples/comments.csv
```

使用方式：

1. 启动项目：

```bash
python -m streamlit run frontend/streamlit_app.py
```

2. 打开页面左侧侧边栏。

3. 依次上传以下 3 个文件：

```text
examples/upload_samples/product.csv
examples/upload_samples/sales.csv
examples/upload_samples/comments.csv
```

4. 如果上传成功，页面会提示：

```text
上传 CSV 字段校验通过，已使用上传数据。
```

上传后，系统会基于上传数据重新计算：

- GMV
- CTR
- CVR
- refund_rate

之后所有 Agent 都会基于上传数据运行，包括：

- 销售数据分析 Agent
- 用户评论洞察 Agent
- 内容策略 Agent
- Supervisor 多 Agent 工作流
- 合规审核 Agent

如果只上传了部分文件，系统会提示需要同时上传 3 个 CSV，并自动回退到默认示例数据。

---

## 12. Supervisor 工作流使用方式

在页面中：

1. 选择一个商品
2. 点击“一键运行完整增长工作流”
3. 等待 Supervisor 调度多个 Agent
4. 查看以下结果：
   - Trace 执行日志
   - 销售分析结果
   - 评论洞察结果
   - 内容策略结果
   - 合规审核结果
5. 点击“生成并准备下载 Markdown 报告”
6. 点击“下载 Markdown 增长报告”
7. 在本地或 `outputs/growth_report.md` 查看报告

---

## 13. 评测方式

项目提供 evals 自动化评测模块，用于检查项目关键链路是否正常。

---

### 13.1 本地静态评测

运行：

```bash
python evals/run_eval.py
```

该命令会检查：

- 默认数据文件是否存在
- 默认数据列是否完整
- 默认运营指标是否生成
- examples 上传示例文件是否存在
- examples 上传示例字段是否完整
- examples 上传示例是否能正常生成运营指标
- Prompt 模板文件是否存在
- Prompt 模板变量是否正确
- Prompt 是否能正常渲染

当前评测结果：

```text
总检查数: 34
通过数: 34
失败数: 0
结果: 全部通过
```

---

### 13.2 带 LLM 的合规审核评测

运行：

```bash
python evals/run_eval.py --with-llm
```

该命令会真实调用 DashScope 通义千问模型，检查合规审核 Agent 是否能识别高风险营销内容。

当前评测结果：

```text
总检查数: 37
通过数: 37
失败数: 0
结果: 全部通过
```

注意：带 LLM 的评测会消耗 DashScope API 调用额度。

---

## 14. 报告导出与下载

Supervisor 工作流完成后，可以生成 Markdown 增长报告。

报告默认保存到：

```text
outputs/growth_report.md
```

同时页面会提供下载按钮，可以直接下载：

```text
growth_report.md
```

报告包含：

- 报告信息
- Agent Trace 执行日志
- 销售数据分析结果
- 用户评论洞察结果
- 内容策略生成结果
- 合规审核结果
- 报告说明

---

## 15. 项目运行效果

系统可以根据商品数据、销售数据和评论数据，自动输出：

- 哪些商品表现较好
- 哪些商品表现较差
- 哪些指标异常
- 用户关心的问题
- 正面反馈和负面反馈
- 小红书爆款标题
- 小红书正文
- 抖音短视频脚本
- 内容发布建议
- 合规风险等级
- 合规改写版本
- Markdown 增长报告
- Agent Trace 执行日志

---

## 16. 简历项目描述

可以在简历中这样描述：

GrowthPilot-Agent 是一个面向内容电商场景的多 Agent 商家增长助手。项目基于 DashScope 通义千问和 Streamlit 构建，设计 Sales Analysis Agent、User Insight Agent、Content Strategy Agent、Compliance Agent 和 Supervisor Agent，实现从商品经营分析、用户评论洞察、内容策略生成到合规审核的完整业务闭环。

项目对 Agent 调用链路进行了工程化拆分，将数据处理、大模型调用、Prompt 模板、Agent 逻辑、报告导出和 evals 评测模块解耦；支持 Streamlit 侧边栏上传商品、销售和评论 CSV 数据，并对上传文件进行字段完整性校验，保证用户输入数据可用。

系统实现 Agent Trace 可观测性面板，记录每个 Agent 的执行状态、耗时、输出预览和错误信息；支持将 Supervisor 工作流结果导出并下载为 Markdown 增长报告。项目构建 evals 自动化评测脚本，覆盖文件完整性、默认数据字段、examples 上传示例数据、运营指标生成、Prompt 模板变量检查、Prompt 渲染和合规审核能力，当前本地静态评测 34/34 通过，带 LLM 的合规审核评测 37/37 通过。

---

## 17. 简历 bullet 版本

如果写进简历，可以压缩成：

- 基于 DashScope 通义千问和 Streamlit 构建内容电商多 Agent 商家增长助手，设计 Sales Analysis、User Insight、Content Strategy、Compliance 4 个专业 Agent，并通过 Supervisor Agent 串联销售分析、用户洞察、内容生成和合规审核流程。
- 对项目进行模块化工程拆分，将数据处理、大模型调用、Prompt 模板、Agent 逻辑、报告导出和 evals 评测解耦为独立模块，提升代码可维护性和扩展性。
- 实现 Agent Trace 可观测性面板，记录每个 Agent 的执行状态、耗时、输出预览和错误信息，并支持将 Supervisor 工作流结果导出并下载为 Markdown 增长报告。
- 支持用户上传商品、销售和评论 CSV 数据，并进行字段完整性校验；构建 evals 自动化评测脚本，覆盖文件完整性、默认数据、examples 上传示例数据、运营指标生成、Prompt 渲染和合规审核能力，当前静态评测 34/34 通过，带 LLM 评测 37/37 通过。

---

## 18. 面试讲解重点

面试时可以重点讲：

1. 为什么要做多 Agent，而不是单个 Prompt
2. Supervisor Agent 如何调度多个专业 Agent
3. 如何用 Trace 记录每个 Agent 的执行过程
4. 如何用 Prompt 模板管理提升可维护性
5. 如何用 evals 检查项目稳定性
6. 如何通过合规审核 Agent 降低内容生成风险
7. 如何通过 Markdown 报告形成业务交付物
8. 如何通过 CSV 上传和字段校验增强产品可用性

---

## 19. 后续规划

后续可以继续扩展：

### 19.1 RAG 知识库增强

- 接入 ChromaDB，构建内容电商知识库
- 加入小红书 / 抖音平台内容风格知识
- 加入平台合规规则、营销禁用词和优秀内容案例
- 让内容策略 Agent 和合规审核 Agent 可以基于知识库检索结果生成更可靠的建议

### 19.2 多商品批量分析

- 支持选择多个商品进行批量分析
- 支持为不同商品批量生成小红书笔记和抖音脚本
- 支持生成多商品对比分析报告
- 支持识别高潜商品、低转化商品和高退款风险商品

### 19.3 工作流编排升级

- 引入 LangGraph 实现显式多 Agent 工作流编排
- 将 Supervisor Agent 从顺序调用升级为可配置状态图
- 支持失败重试、条件分支和人工确认节点
- 支持根据商品风险等级动态决定是否触发合规审核 Agent

### 19.4 工具层与 MCP 风格扩展

- 抽象统一 Tool 调用层
- 支持接入搜索、知识库、文件解析、报告生成等工具
- 参考 MCP 思路，将 Agent 能力和外部工具解耦
- 为后续接入更多数据源和业务系统做准备

### 19.5 更细粒度 Agent Trace

- 记录每个 Agent 的输入 Prompt
- 记录每个 Agent 的完整输出
- 记录 token 用量和接口耗时
- 支持 Trace 日志导出为 JSON
- 支持按任务 ID 查询历史运行记录

### 19.6 evals 评测增强

- 增加内容结构完整度评测
- 增加合规风险关键词覆盖率评测
- 增加生成内容与商品卖点相关性评测
- 增加用户评论引用覆盖率评测
- 增加 Supervisor 工作流输出完整性评测

### 19.7 报告格式扩展

- 支持 PDF 格式报告导出
- 支持 Word 格式报告导出
- 支持带图表的经营分析报告
- 支持多商品批量报告导出

### 19.8 部署与产品化

- 支持 Streamlit Cloud 或 Docker 部署
- 增加用户上传数据的异常提示和模板下载
- 增加页面样式优化和交互体验优化
- 增加任务运行进度条和历史任务记录

---

## 20. 注意事项

- `.env` 文件不要上传到 GitHub
- DashScope API Key 不要写进代码
- `outputs/` 中的报告是运行时生成结果，可以按需保留
- LLM 评测会消耗 API 调用额度
- 上传 CSV 时需要同时上传 product.csv、sales.csv、comments.csv 三个文件
- 上传 CSV 必须包含项目要求的字段，否则系统会回退到默认数据