# GrowthPilot-Agent 项目总结

## 1. 项目一句话介绍

GrowthPilot-Agent 是一个面向内容电商场景的轻量 RAG 增强多 Agent 商家增长助手。

项目基于 DashScope 通义千问、Streamlit 和 pandas 构建，围绕商品数据、销售数据和用户评论，自动完成经营分析、用户洞察、多商品增长策略、内容策略生成、合规审核、Agent Trace 记录、报告导出和 evals 自动化评测。

项目进一步引入轻量 RAG 风格知识库，将内容平台规则、内容风格指南和合规风险词沉淀为 Markdown 知识库，并通过 `knowledge_service.py` 注入到 Content Strategy Agent 和 Compliance Agent 的 Prompt 中，提高生成内容的业务一致性和合规可控性。

---

## 2. 项目定位

这个项目不是简单的 AI 文案生成器，而是一个具备工程化结构的 AI Agent 应用。

项目重点体现：

- 多 Agent 协作
- Supervisor 工作流调度
- Prompt 模板解耦
- 轻量 RAG 风格知识库增强
- Agent Trace 可观测性
- run_id 工作流追踪
- CSV 数据上传和字段校验
- Markdown 报告导出
- Agent Trace JSON 导出
- evals 自动化评测
- final_project_check 最终交付检查
- `.env` 环境变量配置化
- `.gitignore` 安全上传控制

当前项目可以定位为：

```text
轻量 RAG 增强的内容电商多 Agent 商家增长助手
```

---

## 3. 业务背景

在内容电商场景中，商家和运营人员通常需要完成：

1. 分析商品销售表现
2. 判断商品 GMV、CTR、CVR、退款率是否异常
3. 理解用户评论中的痛点和反馈
4. 对多个商品进行优先级排序
5. 生成小红书和抖音内容策略
6. 审核营销内容是否存在合规风险
7. 输出可复盘的运营报告
8. 记录 Agent 执行链路，方便排查问题
9. 参考平台规则和内容风格，降低生成内容失控风险

传统方式依赖人工分析，效率较低。

GrowthPilot-Agent 将这些流程拆解为多个专业 Agent，并通过 Supervisor Agent 串联成完整工作流。

---

## 4. 技术架构

### 4.1 整体架构

```text
CSV 数据
  ↓
pandas 数据处理
  ↓
业务指标计算
  ↓
轻量知识库读取
  ↓
多 Agent 分析
  ↓
Supervisor 工作流调度
  ↓
Agent Trace 记录
  ↓
Markdown 报告导出
  ↓
Trace JSON 导出
  ↓
evals 自动化评测
```

---

### 4.2 模块拆分

```text
GrowthPilot-Agent/
├── app/
│   ├── agents/              # 多 Agent 逻辑
│   ├── prompts/             # Prompt 模板
│   ├── config.py            # 环境变量配置
│   ├── llm.py               # 大模型调用封装
│   ├── data_service.py      # 数据读取和指标计算
│   ├── prompt_loader.py     # Prompt 加载和渲染
│   ├── knowledge_service.py # 轻量知识库读取服务
│   └── report_service.py    # 报告和 Trace 导出
├── knowledge_base/          # 轻量 RAG 知识库
├── data/                    # 默认业务数据
├── examples/                # 上传示例数据
├── evals/                   # 自动化评测
├── frontend/                # Streamlit 页面
├── docs/                    # 项目文档和截图
├── final_project_check.py   # 最终交付检查脚本
└── README.md
```

---

## 5. Agent 设计

项目中包含 6 类 Agent。

| Agent | 作用 |
|---|---|
| Sales Analysis Agent | 分析 GMV、CTR、CVR、退款率等经营指标 |
| User Insight Agent | 从用户评论中提取痛点、正反馈、负反馈和内容机会 |
| Batch Growth Agent | 对多个商品进行优先级排序和增长策略生成 |
| Content Strategy Agent | 结合商品数据、评论数据和内容风格知识库，生成小红书 / 抖音内容策略 |
| Compliance Agent | 结合待审核内容和合规知识库，识别夸大宣传、绝对化表达和医疗化风险 |
| Supervisor Agent | 调度多个专业 Agent，形成完整增长工作流 |

---

## 6. Supervisor 工作流

Supervisor Agent 负责串联多个 Agent。

执行流程如下：

```text
生成 run_id
  ↓
销售数据分析 Agent
  ↓
用户评论洞察 Agent
  ↓
内容策略 Agent
  ↓
合规审核 Agent
  ↓
生成 Trace 日志
  ↓
返回完整工作流结果
```

Supervisor 工作流具备两个重要能力：

1. `run_id`：每次运行生成唯一工作流编号。
2. `progress_callback`：支持前端展示当前执行进度。

---

## 7. 轻量 RAG 知识库设计

### 7.1 知识库目录

项目新增：

```text
knowledge_base/
├── platform_rules.md
├── content_style_guide.md
└── compliance_terms.md
```

三个文件分别负责：

| 文件 | 作用 |
|---|---|
| platform_rules.md | 内容电商平台运营规则，包括真实性、功效宣传、绝对化用语、价格促销和用户评价引用规则 |
| content_style_guide.md | 小红书 / 抖音内容风格指南，包括标题风格、正文结构、口播脚本结构和表达建议 |
| compliance_terms.md | 合规风险词知识库，包括绝对化风险词、功效承诺词、医疗化风险词和虚假稀缺词 |

---

### 7.2 knowledge_service.py

项目新增：

```text
app/knowledge_service.py
```

该模块负责读取和组合知识库内容。

核心函数包括：

```text
load_platform_rules()
load_content_style_guide()
load_compliance_terms()
load_content_strategy_knowledge()
load_compliance_knowledge()
load_all_knowledge()
```

其中：

```text
load_content_strategy_knowledge()
```

会读取：

```text
platform_rules.md
content_style_guide.md
```

用于增强 Content Strategy Agent。

```text
load_compliance_knowledge()
```

会读取：

```text
platform_rules.md
compliance_terms.md
```

用于增强 Compliance Agent。

---

### 7.3 Content Strategy Agent 如何接入知识库

Content Strategy Agent 原始输入是：

```text
商品运营数据
用户评论数据
```

现在增强为：

```text
商品运营数据
用户评论数据
内容平台规则
小红书 / 抖音内容风格指南
```

增强后的 Prompt 构成：

```text
原始内容策略 Prompt
+
内容平台规则和内容风格知识
```

这样生成的小红书标题、正文和抖音脚本会更符合平台内容风格，也更能避免明显违规表达。

---

### 7.4 Compliance Agent 如何接入知识库

Compliance Agent 原始输入是：

```text
待审核营销内容
```

现在增强为：

```text
待审核营销内容
平台规则
合规风险词
风险等级判断标准
```

增强后的 Prompt 构成：

```text
原始合规审核 Prompt
+
平台规则和合规风险词知识库
```

这样合规审核可以更稳定地识别：

- 绝对化表达
- 功效承诺
- 医疗化表达
- 虚假稀缺
- 用户评价夸大
- 价格促销误导

---

### 7.5 为什么叫轻量 RAG

严格来说，这一版不是完整向量数据库 RAG。

完整 RAG 通常包括：

```text
文档切分
Embedding
向量数据库
相似度检索
Top-K 召回
上下文注入
```

当前实现是：

```text
Markdown 知识库
读取文本
按 Agent 用途组合知识
注入 Prompt
```

所以更准确的说法是：

```text
轻量 RAG 风格知识库增强
```

该设计优点是：

- 实现简单
- 风险低
- 容易评测
- 容易维护
- 后续可以自然升级到 ChromaDB 向量检索

---

## 8. Agent Trace 可观测性

项目会记录每个 Agent 的执行日志。

Trace 字段包括：

| 字段 | 说明 |
|---|---|
| run_id | 当前工作流运行 ID |
| step | Agent 步骤名称 |
| description | 当前步骤说明 |
| input_summary | 输入摘要 |
| status | 执行状态 |
| duration_seconds | 执行耗时 |
| output_preview | 输出预览 |
| error | 错误信息 |

这样可以看到：

- 哪个 Agent 执行了
- 是否成功
- 执行用了多久
- 输入是什么摘要
- 输出预览是什么
- 是否有错误

这让项目更接近真实 Agent 平台的可观测性设计。

---

## 9. 数据设计

项目使用三类 CSV 数据。

### 9.1 商品数据

```text
data/product.csv
```

字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| product_name | 商品名称 |
| category | 商品类目 |
| price | 商品价格 |

---

### 9.2 销售数据

```text
data/sales.csv
```

字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| views | 曝光量 |
| clicks | 点击量 |
| orders | 订单数 |
| refunds | 退款数 |

---

### 9.3 评论数据

```text
data/comments.csv
```

字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| rating | 用户评分 |
| comment | 用户评论 |

---

## 10. 运营指标

项目会自动计算以下指标：

| 指标 | 公式 | 含义 |
|---|---|---|
| GMV | price × orders | 成交金额 |
| CTR | clicks / views | 点击率 |
| CVR | orders / clicks | 转化率 |
| refund_rate | refunds / orders | 退款率 |

这些指标会作为 Agent 分析和内容策略生成的基础。

---

## 11. Prompt 工程化

项目将 Prompt 从 Python 代码中拆出，统一放在：

```text
app/prompts/
```

好处是：

- Prompt 和业务代码解耦
- 方便单独修改 Prompt
- 方便后续扩展多个 Prompt 版本
- 便于 evals 检查 Prompt 变量是否完整

当前 Prompt 模板包括：

```text
sales_analysis_prompt.txt
user_insight_prompt.txt
content_strategy_prompt.txt
compliance_prompt.txt
batch_growth_prompt.txt
```

---

## 12. 大模型配置工程化

项目通过 `.env` 管理大模型配置。

`.env.example` 示例：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
QWEN_TEMPERATURE=0.7
```

配置统一在：

```text
app/config.py
```

大模型调用统一封装在：

```text
app/llm.py
```

`call_qwen()` 支持：

```python
call_qwen(prompt)
```

也支持：

```python
call_qwen(prompt, model="qwen-plus", temperature=0.2)
```

这样避免模型名称、temperature 和 API Key 写死在业务代码中。

---

## 13. Streamlit 页面功能

页面包含：

1. 核心指标展示
2. 商品运营数据表
3. 用户评论数据表
4. 原始销售数据表
5. CSV 模板下载
6. CSV 数据上传
7. 上传字段校验
8. 销售数据分析 Agent
9. 用户评论洞察 Agent
10. 多商品批量增长分析 Agent
11. 内容策略 Agent
12. Supervisor 多 Agent 工作流
13. Supervisor 工作流进度条
14. 当前 run_id 展示
15. Agent Trace 执行日志
16. Agent Trace JSON 下载
17. Markdown 报告下载
18. 合规审核 Agent

---

## 14. 报告导出

项目支持导出 Markdown 增长报告。

默认路径：

```text
outputs/growth_report.md
```

报告内容包括：

- 报告生成时间
- run_id
- 分析商品
- Agent Trace 执行日志
- 销售分析结果
- 用户评论洞察结果
- 内容策略结果
- 合规审核结果

---

## 15. Trace JSON 导出

项目支持导出结构化 Trace JSON。

默认路径：

```text
outputs/agent_trace.json
```

Trace JSON 包含：

- generated_at
- run_id
- selected_product
- workflow
- traces

适合后续用于：

- 调试
- 复盘
- 平台化接入
- 历史任务查询
- Agent 运行监控

---

## 16. evals 自动化评测

项目构建了 evals 自动化评测脚本。

运行静态评测：

```bash
python evals/run_eval.py
```

运行带 LLM 评测：

```bash
python evals/run_eval.py --with-llm
```

当前静态评测结果：

```text
静态 evals：96 / 96 通过
```

evals 覆盖：

- 文件存在性
- 环境变量配置
- 轻量知识库文件检查
- knowledge_service 模块导入
- knowledge_service 核心函数检查
- 内容策略知识库读取
- 合规知识库读取
- 数据字段完整性
- 运营指标生成
- examples 上传示例
- Prompt 文件存在性
- Prompt 变量检查
- Prompt 渲染
- Supervisor 静态能力
- progress_callback
- report_service 函数
- Trace JSON 结构
- LLM 合规审核能力

轻量知识库相关 evals 包括：

```text
知识库文件存在检查
knowledge_service 模块导入检查
knowledge_service 函数检查
内容策略知识库读取检查
合规知识库读取检查
```

---

## 17. final_project_check 最终交付检查

项目新增：

```text
final_project_check.py
```

运行：

```bash
python final_project_check.py
```

或：

```bash
python final_project_check.py --with-llm
```

该脚本适合在以下场景使用：

- GitHub 提交前
- 面试演示前
- 修改代码后
- 项目最终交付前

---

## 18. .gitignore 安全控制

项目通过 `.gitignore` 避免上传敏感文件和运行产物。

已忽略：

```text
.env
.env.*
outputs/
__pycache__/
*.pyc
.streamlit/secrets.toml
requirements_freeze.txt
```

保留：

```text
.env.example
```

原因：

- `.env` 包含真实 API Key，不能上传
- `.env.example` 是示例配置，可以上传
- `outputs/` 是运行时生成内容，不需要上传
- 缓存和临时文件不应进入 Git 仓库

---

## 19. 当前项目完成度

当前项目完成度较高，已经具备简历项目条件。

已完成：

- 多 Agent 架构
- Supervisor 工作流
- 轻量 RAG 知识库增强
- Agent Trace
- run_id
- 进度条
- CSV 上传
- 模板下载
- 字段校验
- Markdown 报告
- Trace JSON
- evals 自动化评测
- LLM 合规审核评测
- 最终交付检查
- GitHub 提交
- README 完整说明

当前适合作为：

```text
AI Agent 工程项目
```

也可以在简历中定位为：

```text
轻量 RAG 增强的内容电商多 Agent 商家增长助手
```

---

## 20. 简历项目描述

GrowthPilot-Agent 是一个面向内容电商场景的轻量 RAG 增强多 Agent 商家增长助手。项目基于 DashScope 通义千问、Streamlit 和 pandas 构建，设计 Sales Analysis Agent、User Insight Agent、Batch Growth Agent、Content Strategy Agent、Compliance Agent 和 Supervisor Agent，实现从商品经营分析、用户评论洞察、多商品增长策略、内容策略生成到合规审核的完整业务闭环。

项目对 Agent 调用链路进行了工程化拆分，将数据处理、大模型调用、Prompt 模板、Agent 逻辑、轻量知识库、环境变量配置、报告导出和 evals 评测模块解耦为独立模块；支持 Streamlit 侧边栏上传商品、销售和评论 CSV 数据，提供 CSV 模板下载，并对上传文件进行字段完整性校验，保证用户输入数据可用。

系统引入轻量 RAG 风格知识库，将内容平台规则、内容风格指南和合规风险词沉淀为 Markdown 文档，并通过 `knowledge_service.py` 分别注入 Content Strategy Agent 和 Compliance Agent 的 Prompt 中，提高内容生成的业务一致性和合规可控性。

系统实现 Agent Trace 可观测性面板，为每次 Supervisor 工作流生成唯一 run_id，记录每个 Agent 的执行状态、耗时、输入摘要、输出预览和错误信息；通过 progress_callback 支持 Supervisor 工作流进度展示；支持将 Supervisor 工作流结果导出并下载为 Markdown 增长报告，同时支持将 Agent Trace 导出为 JSON 文件，便于任务复盘、调试和后续平台化接入。

项目构建 evals 自动化评测脚本，覆盖文件完整性、环境变量配置、轻量知识库文件、knowledge_service 核心函数、默认数据字段、examples 上传示例数据、运营指标生成、Prompt 模板变量检查、Prompt 渲染、Supervisor 静态能力、report_service 导出函数检查、Agent Trace JSON 结构校验和合规审核能力；当前本地静态评测 96/96 通过。

---

## 21. 面试讲解重点

面试时可以重点讲：

1. 为什么做多 Agent，而不是单个 Prompt
2. Supervisor Agent 如何调度多个 Agent
3. Batch Growth Agent 如何做多商品分析
4. 为什么要引入轻量 RAG 知识库
5. knowledge_base 里放了哪些知识
6. knowledge_service.py 如何读取和组合知识
7. Content Agent 如何接入内容风格知识库
8. Compliance Agent 如何接入合规风险词知识库
9. 为什么当前叫轻量 RAG，而不是 ChromaDB RAG
10. Agent Trace 为什么重要
11. run_id 如何追踪每次工作流
12. progress_callback 如何驱动前端进度条
13. Prompt 为什么要拆成模板文件
14. 为什么要做 Trace JSON 导出
15. evals 为什么要检查 Prompt、数据、Trace 和知识库
16. LLM 服务不可用时为什么要 SKIP 而不是 FAIL
17. final_project_check.py 解决了什么问题
18. `.gitignore` 如何避免密钥误传
19. 项目如何从 demo 变成工程化应用

---

## 22. 后续可升级方向

后续可以继续升级：

### 22.1 ChromaDB 向量检索 RAG

将当前轻量知识库升级为真正的向量检索 RAG：

```text
文档切分
Embedding
ChromaDB 存储
相似度检索
Top-K 召回
上下文注入
```

---

### 22.2 LangGraph 工作流

将当前自定义 Supervisor 工作流升级为 LangGraph 状态图。

---

### 22.3 Docker 部署

补充：

```text
Dockerfile
docker-compose.yml
```

提升部署能力。

---

### 22.4 报告格式扩展

支持：

```text
PDF 报告
Word 报告
带图表报告
多商品批量报告
```