# GrowthPilot-Agent 项目总结

## 1. 项目一句话介绍

GrowthPilot-Agent 是一个面向内容电商场景的 ChromaDB RAG 增强多 Agent 商家增长助手。

项目基于 DashScope 通义千问、Streamlit、pandas 和 ChromaDB 构建，围绕商品数据、销售数据和用户评论，自动完成经营分析、用户洞察、多商品增长策略、内容策略生成、合规审核、RAG 检索增强、Agent Trace 记录、Markdown 报告导出、Trace JSON 导出和 evals 自动化评测。

本项目不是普通的 AI 文案生成器，而是一个包含多 Agent 编排、ChromaDB 向量检索 RAG、RAG Trace 可观测性、前端 RAG 检索信息展示、报告 RAG 信息汇总和自动化评测的大模型应用工程项目。

---

## 2. 项目定位

当前项目可以定位为：

```text
ChromaDB RAG 增强的内容电商多 Agent 商家增长助手
```

项目重点体现：

- 多 Agent 协作
- Supervisor 工作流调度
- Prompt 模板管理
- ChromaDB 向量检索 RAG
- RAG query 构造
- RAG 检索结果注入 Prompt
- RAG Trace 可观测性
- 前端 RAG 检索信息展示
- Markdown 报告 RAG 信息汇总
- Agent Trace JSON 导出
- run_id 工作流追踪
- CSV 数据上传和字段校验
- evals 自动化评测
- final_project_check 最终交付检查
- `.env` 环境变量配置
- `.gitignore` 安全上传控制

---

## 3. 业务背景

在内容电商场景中，商家和运营人员通常需要完成：

1. 分析商品销售表现
2. 判断商品 GMV、CTR、CVR、退款率是否异常
3. 理解用户评论中的真实痛点和反馈
4. 对多个商品进行优先级排序
5. 生成适合小红书和抖音的内容策略
6. 审核营销内容是否存在合规风险
7. 输出可复盘的运营报告
8. 记录 Agent 执行链路，方便调试和复盘
9. 参考平台规则和内容风格，降低生成内容失控风险
10. 查看 RAG 检索到底命中了哪些知识库内容

传统方式依赖人工分析，效率低、复盘难、合规风险高。

GrowthPilot-Agent 将这些流程拆解为多个专业 Agent，并通过 Supervisor Agent 串联成完整工作流。

---

## 4. 技术架构

### 4.1 整体架构

```text
CSV 数据
    ↓
pandas 数据处理
    ↓
运营指标计算
    ↓
knowledge_base Markdown 知识库
    ↓
rag_service.py 构建 ChromaDB 向量索引
    ↓
retrieve_knowledge_with_details() 检索相关知识片段
    ↓
Content Agent / Compliance Agent 注入 RAG 上下文
    ↓
Supervisor Agent 调度多 Agent 工作流
    ↓
Agent Trace 记录
    ↓
前端展示 RAG 检索信息
    ↓
Markdown 报告写入 RAG 检索汇总
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
│   ├── knowledge_service.py # 轻量知识库读取服务
│   ├── rag_service.py       # ChromaDB RAG 检索服务
│   ├── prompt_loader.py     # Prompt 加载和渲染
│   └── report_service.py    # Markdown 报告和 Trace JSON 导出
├── knowledge_base/          # RAG 知识库
├── data/                    # 默认业务数据
├── examples/                # 上传示例数据
├── evals/                   # 自动化评测
├── frontend/                # Streamlit 页面
├── docs/                    # 项目文档和截图
├── outputs/                 # 运行时输出，已被忽略
├── vector_db/               # ChromaDB 本地向量库，已被忽略
├── final_project_check.py   # 最终交付检查脚本
└── README.md
```

---

## 5. Agent 设计

| Agent | 作用 |
|---|---|
| Sales Analysis Agent | 分析 GMV、CTR、CVR、退款率等经营指标 |
| User Insight Agent | 从用户评论中提取痛点、正反馈、负反馈和内容机会 |
| Batch Growth Agent | 对多个商品进行优先级排序、分层策略和批量增长动作推荐 |
| Content Strategy Agent | 结合商品数据、评论数据和 RAG 检索结果，生成小红书内容、抖音脚本和发布建议 |
| Compliance Agent | 结合待审核内容和 RAG 检索结果，识别绝对化表达、功效承诺、医疗化表达和夸大宣传风险 |
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

## 7. ChromaDB RAG 设计

### 7.1 知识库目录

项目知识库位于：

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

### 7.2 rag_service.py

项目新增：

```text
app/rag_service.py
```

该模块负责 ChromaDB RAG 检索链路。

核心函数包括：

```text
read_markdown_file()
load_knowledge_documents()
split_text_into_chunks()
build_hash_embedding()
get_chroma_client()
reset_knowledge_collection()
get_knowledge_collection()
build_knowledge_chunks()
index_knowledge_base()
ensure_knowledge_index()
retrieve_knowledge()
retrieve_knowledge_with_details()
```

---

### 7.3 RAG 检索流程

```text
knowledge_base Markdown 文档
    ↓
读取文档
    ↓
split_text_into_chunks() 切分 chunk
    ↓
build_hash_embedding() 生成本地哈希 embedding
    ↓
写入 ChromaDB PersistentClient
    ↓
根据 query 检索 Top-K 相关 chunk
    ↓
返回 retrieved_text 和检索元信息
    ↓
注入 Content Agent / Compliance Agent Prompt
```

当前 embedding 使用本地哈希 embedding。

优点：

- 不需要额外 API Key
- 不依赖外网下载模型
- 本地运行稳定
- 方便 evals 自动化评测
- 可以完整展示 ChromaDB RAG 工程链路

不足：

- 语义理解能力不如真实 embedding 模型
- 检索质量有限
- 后续可替换为 DashScope Embedding、OpenAI Embedding 或 sentence-transformers

---

## 8. RAG 可观测性设计

项目不仅做了 RAG 检索，还记录了 RAG 检索过程。

`retrieve_knowledge_with_details()` 返回：

```text
retrieved_text
query
top_k
sources
chunk_count
used_chromadb
```

Supervisor Trace 中额外记录：

```text
rag_context
```

`rag_context` 包含：

```text
enabled
agent
query
top_k
sources
chunk_count
used_chromadb
fallback_used
retrieved_text_preview
error
```

这使得每次 Agent 运行后都能看到：

- 当前 RAG query 是什么
- 检索了几个 chunk
- 命中了哪些知识库文件
- 是否使用了 ChromaDB
- 是否触发 fallback
- 检索片段预览是什么

---

## 9. 前端 RAG 检索信息展示

Streamlit 页面已经新增 RAG 检索信息展示。

在 Supervisor 工作流运行完成后，页面会出现：

```text
RAG 检索信息
```

该页面集中展示：

```text
used_chromadb
fallback_used
top_k
chunk_count
sources
RAG Query
检索片段预览
```

同时在 Trace 执行日志中，内容策略 Agent 和合规审核 Agent 的展开项里也会显示对应的 RAG 检索元信息。

这使面试演示时可以直接展示：

```text
这个 Agent 不是凭空生成，而是先检索了知识库，并且能看到命中了哪些知识。
```

---

## 10. Markdown 报告 RAG 汇总

项目在 `app/report_service.py` 中增强了 Markdown 报告导出能力。

报告新增：

```text
RAG 检索信息汇总
```

报告中会记录：

```text
Agent
used_chromadb
fallback_used
top_k
chunk_count
sources
RAG Query
检索片段预览
```

这样下载后的 `growth_report.md` 不仅能看到最终分析结果，还能看到本次工作流中的 RAG 检索过程。

---

## 11. knowledge_service.py 兜底能力

项目保留：

```text
app/knowledge_service.py
```

该模块负责直接读取和组合 Markdown 知识库内容。

核心函数包括：

```text
load_platform_rules()
load_content_style_guide()
load_compliance_terms()
load_content_strategy_knowledge()
load_compliance_knowledge()
load_all_knowledge()
```

作用：

1. 为非向量检索场景提供直接知识库读取能力。
2. 作为 ChromaDB RAG 检索失败时的 fallback。
3. 保证 Content Agent 和 Compliance Agent 在 ChromaDB 异常时仍然能运行。

---

## 12. Content Strategy Agent 如何接入 RAG

Content Strategy Agent 原始输入：

```text
商品运营数据
用户评论数据
```

现在增强为：

```text
商品运营数据
用户评论数据
ChromaDB 检索到的内容平台规则
ChromaDB 检索到的小红书 / 抖音内容风格知识
RAG 检索元信息
```

增强后的 Prompt 组成：

```text
原始内容策略 Prompt
+
RAG 检索到的内容平台规则和内容风格知识
+
RAG 检索元信息
```

这样生成的小红书标题、正文和抖音脚本会更符合平台内容风格，也更能规避明显违规表达。

---

## 13. Compliance Agent 如何接入 RAG

Compliance Agent 原始输入：

```text
待审核营销内容
```

现在增强为：

```text
待审核营销内容
ChromaDB 检索到的平台规则
ChromaDB 检索到的合规风险词
RAG 检索元信息
```

增强后的 Prompt 组成：

```text
原始合规审核 Prompt
+
RAG 检索到的平台规则和合规风险知识
+
RAG 检索元信息
```

合规审核可以更稳定地识别：

- 绝对化表达
- 功效承诺
- 医疗化表达
- 虚假稀缺
- 用户评价夸大
- 价格促销误导

---

## 14. Agent Trace 可观测性

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
| rag_context | RAG 检索上下文，只有相关 Agent 才有 |

这样可以看到：

- 哪个 Agent 执行了
- 是否成功
- 执行用了多久
- 输入摘要是什么
- 输出预览是什么
- 是否有错误
- RAG 检索命中了什么知识

这让项目更接近真实 Agent 平台的可观测性设计。

---

## 15. 数据设计

项目使用三类 CSV 数据。

### 15.1 商品数据

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

### 15.2 销售数据

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

### 15.3 评论数据

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

## 16. 运营指标

项目自动计算：

| 指标 | 公式 | 含义 |
|---|---|---|
| GMV | price × orders | 成交金额 |
| CTR | clicks / views | 点击率 |
| CVR | orders / clicks | 转化率 |
| refund_rate | refunds / orders | 退款率 |

这些指标会作为 Agent 分析和内容策略生成的基础。

---

## 17. Prompt 工程化

项目将 Prompt 从 Python 代码中拆出，统一放在：

```text
app/prompts/
```

当前 Prompt 模板包括：

```text
sales_analysis_prompt.txt
user_insight_prompt.txt
content_strategy_prompt.txt
compliance_prompt.txt
batch_growth_prompt.txt
```

优点：

- Prompt 和业务代码解耦
- 方便单独修改 Prompt
- 方便后续扩展多个 Prompt 版本
- 便于 evals 检查 Prompt 变量是否完整

---

## 18. 大模型配置工程化

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

## 19. Streamlit 页面功能

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
16. RAG 检索信息展示
17. Markdown 报告下载
18. Agent Trace JSON 下载
19. 合规审核 Agent

---

## 20. 报告导出

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
- RAG 检索信息汇总
- 销售分析结果
- 用户评论洞察结果
- 内容策略结果
- 合规审核结果

---

## 21. Trace JSON 导出

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

其中每条 trace 可以包含：

```text
rag_context
```

适合后续用于：

- 调试
- 复盘
- 平台化接入
- 历史任务查询
- Agent 运行监控

---

## 22. evals 自动化评测

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
总检查数: 117
通过数: 117
失败数: 0
跳过数: 0
结果: 全部通过
```

evals 覆盖：

- 文件存在性
- 环境变量配置
- 知识库文件检查
- knowledge_service 模块导入
- knowledge_service 核心函数检查
- rag_service 模块导入
- rag_service 核心函数检查
- ChromaDB 索引构建
- RAG 检索结果
- 默认数据字段完整性
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

---

## 23. final_project_check 最终交付检查

项目提供：

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

适合在以下场景使用：

- GitHub 提交前
- 面试演示前
- 修改代码后
- 项目最终交付前

---

## 24. .gitignore 安全控制

项目通过 `.gitignore` 避免上传敏感文件和运行产物。

已忽略：

```text
.env
.env.*
outputs/
vector_db/
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
- `vector_db/` 是 ChromaDB 本地向量库，可以运行时重新生成
- 缓存和临时文件不应进入 Git 仓库

---

## 25. 当前项目完成度

当前项目完成度较高，已经具备简历项目条件。

已完成：

- 多 Agent 架构
- Supervisor 工作流
- ChromaDB RAG 检索
- 本地哈希 embedding
- RAG 检索元信息返回
- RAG Trace 可观测性
- 前端 RAG 检索信息展示
- Markdown 报告 RAG 检索信息汇总
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

当前适合定位为：

```text
AI Agent 工程项目
```

也可以在简历中定位为：

```text
ChromaDB RAG 增强的内容电商多 Agent 商家增长助手
```

---

## 26. 简历项目描述

GrowthPilot-Agent 是一个面向内容电商场景的 ChromaDB RAG 增强多 Agent 商家增长助手。项目基于 DashScope 通义千问、Streamlit、pandas 和 ChromaDB 构建，设计 Sales Analysis Agent、User Insight Agent、Batch Growth Agent、Content Strategy Agent、Compliance Agent 和 Supervisor Agent，实现从商品经营分析、用户评论洞察、多商品增长策略、RAG 知识检索、内容策略生成到合规审核的完整业务闭环。

项目将内容平台规则、内容风格指南和合规风险词沉淀为 Markdown 知识库，通过 `rag_service.py` 完成文档读取、chunk 切分、本地哈希 embedding、ChromaDB 持久化存储和 Top-K 检索，并将检索结果注入 Content Strategy Agent 和 Compliance Agent 的 Prompt 中，提高内容生成的业务一致性和合规可控性。

系统实现 RAG Trace 可观测性，为每次 Supervisor 工作流生成唯一 run_id，记录每个 Agent 的执行状态、耗时、输入摘要、输出预览和错误信息，并额外记录 RAG query、命中 sources、chunk_count、used_chromadb、fallback_used 和检索片段预览；同时支持在前端页面展示 RAG 检索信息，并将 RAG 检索信息写入 Markdown 增长报告和 Trace JSON 文件。

项目构建 evals 自动化评测脚本，覆盖文件完整性、环境变量配置、知识库文件、knowledge_service 核心函数、rag_service 核心函数、ChromaDB 索引构建、RAG 检索结果、默认数据字段、examples 上传示例数据、运营指标生成、Prompt 模板变量检查、Prompt 渲染、Supervisor 静态能力、report_service 导出函数检查、Agent Trace JSON 结构校验和合规审核能力；当前本地静态评测 117/117 通过。

---

## 27. 面试讲解重点

面试时可以重点讲：

1. 为什么做多 Agent，而不是单个 Prompt
2. Supervisor Agent 如何调度多个 Agent
3. Batch Growth Agent 如何做多商品分析
4. 为什么要引入 RAG 知识库
5. knowledge_base 里放了哪些知识
6. rag_service.py 如何读取文档、切分 chunk、生成 embedding、写入 ChromaDB
7. 当前为什么使用本地哈希 embedding
8. 如何升级为 DashScope Embedding 或 sentence-transformers
9. Content Agent 如何构造 RAG query
10. Compliance Agent 如何构造 RAG query
11. RAG query、sources、chunk_count 如何写入 Trace
12. 前端如何展示 RAG 检索信息
13. Markdown 报告为什么要写入 RAG 检索信息
14. Agent Trace 为什么重要
15. run_id 如何追踪每次工作流
16. progress_callback 如何驱动前端进度条
17. Prompt 为什么要拆成模板文件
18. 为什么要做 Trace JSON 导出
19. evals 为什么要检查 Prompt、数据、Trace 和 RAG
20. LLM 服务不可用时为什么要 SKIP 而不是 FAIL
21. final_project_check.py 解决了什么问题
22. `.gitignore` 如何避免密钥误传
23. 项目如何从 demo 变成工程化应用

---

## 28. 后续可升级方向

### 28.1 真实 Embedding 模型

将当前本地哈希 embedding 升级为真实 embedding：

```text
DashScope Embedding
OpenAI Embedding
sentence-transformers
```

目标：

- 提升语义检索质量
- 提高 Top-K 命中准确率
- 更接近真实生产 RAG 系统

---

### 28.2 RAG 检索增强

可以继续增加：

- 按知识库来源过滤
- 动态 top_k
- 相似度阈值过滤
- 检索结果去重
- reranker
- 前端展示完整命中 chunk

---

### 28.3 LangGraph 工作流

将当前自定义 Supervisor 工作流升级为 LangGraph 状态图。

可以支持：

- 条件分支
- 失败重试
- 人工确认节点
- 根据合规风险动态决定是否进入改写流程

---

### 28.4 Docker 部署

补充：

```text
Dockerfile
docker-compose.yml
```

提升部署能力。

---

### 28.5 GitHub Actions

补充 CI：

```text
push / pull_request 时自动运行 evals
```

提升工程化完整度。

---

### 28.6 报告格式扩展

支持：

```text
PDF 报告
Word 报告
带图表报告
多商品批量报告
```