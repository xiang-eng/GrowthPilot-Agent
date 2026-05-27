# GrowthPilot-Agent

GrowthPilot-Agent 是一个面向内容电商场景的 ChromaDB RAG 增强多 Agent 商家增长助手。

项目基于 DashScope 通义千问、Streamlit、pandas 和 ChromaDB 构建，模拟内容电商商家在小红书、抖音等平台中的运营分析流程。系统可以根据商品数据、销售数据和用户评论，自动完成销售分析、用户洞察、多商品增长策略、内容策略生成、合规审核、RAG 检索增强、Agent Trace 记录、Markdown 报告导出和 Trace JSON 导出。

本项目重点不是单纯调用大模型生成文案，而是实现了一个具备多 Agent 编排、ChromaDB 向量检索 RAG、RAG Trace 可观测性、前端 RAG 检索信息展示、报告 RAG 信息汇总和 evals 自动化评测的大模型应用工程项目。

---

## 1. 核心能力

当前项目已经实现：

- 商品、销售、评论 CSV 数据读取
- GMV、CTR、CVR、退款率等运营指标计算
- Streamlit 前端页面
- CSV 模板下载
- CSV 数据上传
- 上传字段校验
- Sales Analysis Agent 销售分析
- User Insight Agent 用户评论洞察
- Batch Growth Agent 多商品批量增长分析
- Content Strategy Agent 内容策略生成
- Compliance Agent 合规审核
- Supervisor Agent 多 Agent 工作流编排
- Supervisor 工作流进度条
- run_id 工作流追踪
- Agent Trace 执行日志
- Agent Trace JSON 导出
- Markdown 增长报告导出
- knowledge_base Markdown 知识库
- knowledge_service 轻量知识库读取服务
- rag_service ChromaDB RAG 检索服务
- 本地哈希 embedding
- ChromaDB PersistentClient 本地向量库
- retrieve_knowledge(query, top_k)
- retrieve_knowledge_with_details(query, top_k)
- Content Agent 接入 RAG 检索结果
- Compliance Agent 接入 RAG 检索结果
- Supervisor Trace 记录 rag_context
- 前端页面展示 RAG query、sources、chunk_count、used_chromadb、fallback_used 和检索片段预览
- Markdown 报告写入 RAG 检索信息汇总
- evals 自动化评测
- final_project_check.py 最终交付检查
- `.gitignore` 安全上传控制

---

## 2. 技术栈

| 模块 | 技术 |
|---|---|
| 编程语言 | Python |
| 前端页面 | Streamlit |
| 数据处理 | pandas |
| 大模型调用 | DashScope 通义千问，OpenAI SDK 兼容模式 |
| 多 Agent 编排 | 自定义 Supervisor 工作流 |
| Prompt 管理 | txt 模板文件 |
| 知识库 | Markdown |
| 向量数据库 | ChromaDB |
| Embedding | 本地哈希 embedding |
| RAG 服务 | app/rag_service.py |
| Trace 导出 | JSON |
| 报告导出 | Markdown |
| 自动化评测 | evals/run_eval.py |
| 环境变量管理 | python-dotenv |
| 安全上传控制 | .gitignore |

---

## 3. 多 Agent 设计

| Agent | 作用 |
|---|---|
| Sales Analysis Agent | 分析商品 GMV、CTR、CVR、退款率等经营指标 |
| User Insight Agent | 从用户评论中提取用户痛点、正反馈、负反馈和内容机会 |
| Batch Growth Agent | 对多个商品进行优先级排序、分层运营和增长动作建议 |
| Content Strategy Agent | 结合商品数据、评论数据和 RAG 检索结果，生成小红书内容、抖音脚本和发布建议 |
| Compliance Agent | 结合待审核内容和 RAG 检索结果，识别绝对化表达、功效承诺、医疗化表达和夸大宣传风险 |
| Supervisor Agent | 串联多个专业 Agent，形成完整增长工作流 |

Supervisor 工作流：

```text
销售数据分析
    ↓
用户评论洞察
    ↓
内容策略生成
    ↓
内容合规审核
    ↓
生成 Agent Trace
    ↓
导出 Markdown 报告和 Trace JSON
```

---

## 4. ChromaDB RAG 设计

知识库目录：

```text
knowledge_base/
├── platform_rules.md
├── content_style_guide.md
└── compliance_terms.md
```

知识库文件说明：

| 文件 | 作用 |
|---|---|
| platform_rules.md | 内容电商平台规则，包括真实性、功效宣传、绝对化用语、促销表达和用户评价引用规则 |
| content_style_guide.md | 小红书 / 抖音内容风格指南，包括标题结构、正文结构、脚本结构和推荐表达方式 |
| compliance_terms.md | 合规风险词知识库，包括绝对化风险词、功效承诺词、医疗化风险词、虚假稀缺词和用户评价夸大风险 |

RAG 服务文件：

```text
app/rag_service.py
```

核心函数：

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

RAG 流程：

```text
knowledge_base Markdown 文档
    ↓
读取文档
    ↓
切分 chunk
    ↓
本地哈希 embedding
    ↓
写入 ChromaDB
    ↓
根据 query 检索 Top-K 知识片段
    ↓
注入 Content Agent / Compliance Agent Prompt
    ↓
写入 Supervisor Trace
    ↓
展示到前端页面
    ↓
写入 Markdown 报告
```

---

## 5. RAG 可观测性

项目不仅实现了 RAG 检索，还记录并展示了 RAG 检索过程。

每次 Content Agent 和 Compliance Agent 运行时，系统会记录：

```text
query
top_k
sources
chunk_count
used_chromadb
fallback_used
retrieved_text_preview
error
```

这些信息会出现在三个地方：

1. Supervisor Trace 的 `rag_context`
2. Streamlit 页面中的「RAG 检索信息」标签页
3. Markdown 增长报告中的「RAG 检索信息汇总」

这使项目具备更强的可解释性和可调试性。

---

## 6. 前端页面功能

Streamlit 页面支持：

1. 核心经营指标展示
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
14. 当前工作流 run_id 展示
15. Agent Trace 执行日志
16. RAG 检索信息展示
17. Markdown 增长报告导出
18. Agent Trace JSON 导出
19. 合规审核 Agent

RAG 前端展示内容包括：

```text
used_chromadb
fallback_used
top_k
chunk_count
sources
RAG Query
检索片段预览
```

---

## 7. Markdown 报告导出

Supervisor 工作流完成后，可以生成 Markdown 增长报告。

报告默认保存到：

```text
outputs/growth_report.md
```

报告包含：

- 报告信息
- 运行 ID
- 分析商品
- Agent Trace 执行日志
- RAG 检索信息汇总
- 销售数据分析结果
- 用户评论洞察结果
- 内容策略生成结果
- 合规审核结果
- 报告说明

其中 RAG 检索信息汇总会展示：

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

---

## 8. Agent Trace JSON 导出

Trace JSON 默认保存到：

```text
outputs/agent_trace.json
```

Trace JSON 包含：

- generated_at
- run_id
- selected_product
- workflow
- traces

每条 trace 包含：

```text
run_id
step
description
input_summary
status
duration_seconds
output_preview
error
rag_context
```

其中 `rag_context` 用于记录 RAG 检索过程。

---

## 9. 项目结构

```text
GrowthPilot-Agent/
├── app/
│   ├── agents/
│   │   ├── batch_agent.py
│   │   ├── compliance_agent.py
│   │   ├── content_agent.py
│   │   ├── insight_agent.py
│   │   ├── sales_agent.py
│   │   └── supervisor_agent.py
│   ├── prompts/
│   │   ├── batch_growth_prompt.txt
│   │   ├── compliance_prompt.txt
│   │   ├── content_strategy_prompt.txt
│   │   ├── sales_analysis_prompt.txt
│   │   └── user_insight_prompt.txt
│   ├── __init__.py
│   ├── config.py
│   ├── data_service.py
│   ├── knowledge_service.py
│   ├── llm.py
│   ├── prompt_loader.py
│   ├── rag_service.py
│   └── report_service.py
├── knowledge_base/
│   ├── platform_rules.md
│   ├── content_style_guide.md
│   └── compliance_terms.md
├── data/
│   ├── product.csv
│   ├── sales.csv
│   └── comments.csv
├── docs/
│   ├── PROJECT_SUMMARY.md
│   └── images/
├── evals/
│   ├── eval_cases.json
│   └── run_eval.py
├── examples/
│   └── upload_samples/
│       ├── product.csv
│       ├── sales.csv
│       └── comments.csv
├── frontend/
│   └── streamlit_app.py
├── outputs/
│   ├── growth_report.md
│   └── agent_trace.json
├── vector_db/
├── .env.example
├── .gitignore
├── final_project_check.py
├── README.md
└── requirements.txt
```

说明：

```text
outputs/ 是运行时生成目录，已被 .gitignore 忽略。
vector_db/ 是 ChromaDB 本地向量库目录，已被 .gitignore 忽略。
.env 不应上传 GitHub。
.env.example 可以上传 GitHub。
```

---

## 10. 环境准备

创建 conda 环境：

```bash
conda create -n agenttt python=3.10 -y
conda activate agenttt
```

安装依赖：

```bash
pip install -r requirements.txt
```

当前依赖：

```txt
streamlit==1.49.1
pandas==2.3.3
python-dotenv==1.2.2
openai==2.36.0
chromadb
```

复制环境变量文件：

```bash
copy .env.example .env
```

macOS / Linux：

```bash
cp .env.example .env
```

`.env` 示例：

```env
DASHSCOPE_API_KEY=你的DashScope_API_Key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
QWEN_TEMPERATURE=0.7
```

---

## 11. 启动项目

```bash
python -m streamlit run frontend/streamlit_app.py
```

如果 8501 端口被占用：

```bash
python -m streamlit run frontend/streamlit_app.py --server.port 8502
```

打开浏览器后，访问：

```text
http://localhost:8501
```

---

## 12. 构建 ChromaDB 向量库

手动构建向量库：

```bash
python app/rag_service.py
```

运行后会生成：

```text
vector_db/
```

该目录已被 `.gitignore` 忽略，不需要上传 GitHub。

测试 RAG 检索：

```bash
python -c "from app.rag_service import retrieve_knowledge_with_details; result = retrieve_knowledge_with_details('小红书内容生成需要注意哪些合规风险？', top_k=3); print(len(result['retrieved_text'])); print(result['sources']); print(result['chunk_count']); print(result['used_chromadb'])"
```

---

## 13. 使用方式

启动项目后：

1. 选择商品
2. 点击「一键运行完整增长工作流」
3. 等待 Supervisor 调度多个 Agent
4. 查看销售分析结果
5. 查看用户评论洞察结果
6. 查看内容策略结果
7. 查看合规审核结果
8. 打开「Trace 执行日志」
9. 打开「RAG 检索信息」
10. 查看 RAG Query、sources、chunk_count 和检索片段预览
11. 点击生成 Markdown 报告
12. 下载 Markdown 增长报告
13. 点击生成 Agent Trace JSON
14. 下载 Agent Trace JSON

---

## 14. evals 自动化评测

运行静态评测：

```bash
python evals/run_eval.py
```

当前静态评测结果：

```text
总检查数: 117
通过数: 117
失败数: 0
跳过数: 0
结果: 全部通过
```

评测覆盖：

- 关键文件存在性
- 环境变量示例文件
- config 配置项
- llm 调用函数
- 默认数据字段
- 运营指标计算
- examples 上传示例数据
- Prompt 模板文件
- Prompt 变量
- Prompt 渲染
- knowledge_service 函数
- rag_service 函数
- ChromaDB 索引构建
- RAG 检索结果
- Supervisor 静态能力
- run_id 格式
- progress_callback
- report_service 函数
- Trace JSON 结构
- rag_context 相关函数

带 LLM 的评测：

```bash
python evals/run_eval.py --with-llm
```

注意：带 LLM 的评测会真实调用 DashScope，会消耗 API 额度。

---

## 15. 最终交付检查

运行：

```bash
python final_project_check.py
```

带 LLM：

```bash
python final_project_check.py --with-llm
```

该脚本用于项目提交前、面试演示前或重要修改后的最终检查。

---

## 16. .gitignore 安全控制

项目忽略以下运行时和敏感文件：

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

检查忽略规则：

```bash
git check-ignore -v .env
git check-ignore -v outputs/agent_trace.json
git check-ignore -v vector_db/
git check-ignore -v __pycache__/test.pyc
git check-ignore -v .env.example
```

其中 `.env.example` 没有输出，说明它不会被忽略，可以安全上传。

---

## 17. 项目运行效果

系统可以自动输出：

- 商品经营表现分析
- GMV、CTR、CVR、退款率异常判断
- 用户评论洞察
- 用户痛点总结
- 多商品优先级排序
- 多商品增长策略
- 小红书标题和正文
- 抖音短视频脚本
- 内容发布建议
- 合规风险等级
- 合规风险说明
- 合规改写建议
- RAG Query
- RAG 命中 sources
- RAG chunk_count
- RAG 检索片段预览
- Agent Trace 执行日志
- Markdown 增长报告
- Agent Trace JSON

---

## 18. 简历项目描述

GrowthPilot-Agent 是一个面向内容电商场景的 ChromaDB RAG 增强多 Agent 商家增长助手。项目基于 DashScope 通义千问、Streamlit、pandas 和 ChromaDB 构建，设计 Sales Analysis Agent、User Insight Agent、Batch Growth Agent、Content Strategy Agent、Compliance Agent 和 Supervisor Agent，实现从商品经营分析、用户评论洞察、多商品增长策略、RAG 知识检索、内容策略生成到合规审核的完整业务闭环。

项目将内容平台规则、内容风格指南和合规风险词沉淀为 Markdown 知识库，通过 `rag_service.py` 完成文档读取、chunk 切分、本地哈希 embedding、ChromaDB 持久化存储和 Top-K 检索，并将检索结果注入 Content Strategy Agent 和 Compliance Agent 的 Prompt 中，提高内容生成的业务一致性和合规可控性。

系统实现 RAG Trace 可观测性，为每次 Supervisor 工作流生成唯一 run_id，记录每个 Agent 的执行状态、耗时、输入摘要、输出预览和错误信息，并额外记录 RAG query、命中 sources、chunk_count、used_chromadb、fallback_used 和检索片段预览；同时支持在前端页面展示 RAG 检索信息，并将 RAG 检索信息写入 Markdown 增长报告和 Trace JSON 文件。

项目构建 evals 自动化评测脚本，覆盖文件完整性、环境变量配置、知识库文件、knowledge_service 核心函数、rag_service 核心函数、ChromaDB 索引构建、RAG 检索结果、默认数据字段、examples 上传示例数据、运营指标生成、Prompt 模板变量检查、Prompt 渲染、Supervisor 静态能力、report_service 导出函数检查、Agent Trace JSON 结构校验和合规审核能力；当前本地静态评测 117/117 通过。

---

## 19. 简历 bullet 版本

- 基于 DashScope 通义千问、Streamlit、pandas 和 ChromaDB 构建内容电商多 Agent 商家增长助手，设计 Sales Analysis、User Insight、Batch Growth、Content Strategy、Compliance 等 Agent，并通过 Supervisor Agent 串联销售分析、用户洞察、内容生成和合规审核流程。
- 基于 ChromaDB 构建 RAG 检索模块，将平台规则、内容风格指南和合规风险词沉淀为 Markdown 文档，通过 `rag_service.py` 完成文档读取、chunk 切分、本地哈希 embedding、ChromaDB 持久化存储和 Top-K 检索。
- 实现 `retrieve_knowledge_with_details()`，在返回检索文本的同时返回 query、top_k、sources、chunk_count、used_chromadb、fallback_used 等元信息，用于 RAG 可观测性。
- 将 RAG 检索结果分别注入 Content Strategy Agent 和 Compliance Agent 的 Prompt 中，提高内容生成的业务一致性和合规可控性。
- 实现 Agent Trace 可观测性，为每次 Supervisor 工作流生成唯一 run_id，记录每个 Agent 的输入摘要、执行状态、耗时、输出预览和错误信息，并额外记录 RAG 检索上下文。
- 在 Streamlit 前端新增 RAG 检索信息展示，支持查看每个 RAG Agent 的 query、命中 sources、chunk_count、used_chromadb、fallback_used 和检索片段预览。
- 在 Markdown 增长报告中新增 RAG 检索信息汇总，并支持 Agent Trace JSON 导出，便于任务复盘和调试。
- 构建 evals 自动化评测体系，覆盖文件完整性、配置项、Prompt 渲染、RAG 检索、Supervisor 静态能力、Trace JSON 结构等检查，当前静态评测 117/117 通过。
- 完善 `.gitignore` 安全上传规则，忽略 `.env`、outputs、vector_db、Python 缓存、Streamlit secrets 和临时文件，避免密钥、运行产物和本地向量库被误传到 GitHub。

---

## 20. 面试讲解重点

面试时可以重点讲：

1. 为什么使用多 Agent，而不是单个 Prompt
2. Supervisor Agent 如何串联多个专业 Agent
3. Batch Growth Agent 如何支持多商品批量运营决策
4. 为什么引入 RAG 知识库
5. knowledge_base 中沉淀了哪些知识
6. rag_service.py 如何读取文档、切分 chunk、生成 embedding、写入 ChromaDB
7. 为什么当前使用本地哈希 embedding
8. 本地哈希 embedding 和真实语义 embedding 的区别
9. 如何升级为 DashScope Embedding 或 sentence-transformers
10. Content Agent 如何构造 RAG query
11. Compliance Agent 如何构造 RAG query
12. 如何记录 RAG query、sources、chunk_count 和 fallback 状态
13. 为什么 RAG 可观测性对调试很重要
14. 前端如何展示 RAG 检索信息
15. Markdown 报告为什么要写入 RAG 检索信息
16. Trace JSON 如何用于后续平台化接入
17. 为什么要记录 run_id
18. 为什么要做 evals 自动化评测
19. 为什么 LLM 服务不可用时标记 SKIP 而不是 FAIL
20. 为什么 vector_db 不上传 GitHub

---

## 21. 后续规划

### 21.1 真实 Embedding 模型

- 接入 DashScope Embedding
- 接入 OpenAI Embedding
- 接入 sentence-transformers
- 替换当前本地哈希 embedding
- 提升语义检索质量

### 21.2 RAG 检索增强

- 支持按知识库来源过滤
- 支持动态 top_k
- 支持相似度阈值过滤
- 支持检索结果去重
- 支持 reranker
- 支持在前端展示完整命中 chunk

### 21.3 工作流编排升级

- 接入 LangGraph
- 支持条件分支
- 支持失败重试
- 支持人工确认节点
- 支持根据合规风险动态决定是否进入改写流程

### 21.4 工程化增强

- 增加 Dockerfile
- 增加 GitHub Actions
- 自动运行 evals
- 支持部署到 Streamlit Cloud
- 支持历史任务记录

### 21.5 评测增强

- 增加 RAG 命中率评测
- 增加 RAG 来源正确性评测
- 增加内容结构完整度评测
- 增加合规风险覆盖率评测
- 增加生成内容与商品卖点相关性评测