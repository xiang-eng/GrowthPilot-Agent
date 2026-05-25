\# GrowthPilot-Agent 项目总结



\## 1. 项目一句话介绍



GrowthPilot-Agent 是一个面向内容电商场景的多 Agent 商家增长助手。



项目基于 DashScope 通义千问、Streamlit 和 pandas 构建，围绕商品数据、销售数据和用户评论，自动完成经营分析、用户洞察、多商品增长策略、内容策略生成、合规审核、Agent Trace 记录、报告导出和 evals 自动化评测。



\---



\## 2. 项目定位



这个项目不是简单的 AI 文案生成器，而是一个具备工程化结构的 AI Agent 应用。



项目重点体现：



\- 多 Agent 协作

\- Supervisor 工作流调度

\- Prompt 模板解耦

\- Agent Trace 可观测性

\- run\_id 工作流追踪

\- CSV 数据上传和字段校验

\- Markdown 报告导出

\- Agent Trace JSON 导出

\- evals 自动化评测

\- final\_project\_check 最终交付检查

\- `.env` 环境变量配置化

\- `.gitignore` 安全上传控制



\---



\## 3. 业务背景



在内容电商场景中，商家和运营人员通常需要完成：



1\. 分析商品销售表现

2\. 判断商品 GMV、CTR、CVR、退款率是否异常

3\. 理解用户评论中的痛点和反馈

4\. 对多个商品进行优先级排序

5\. 生成小红书和抖音内容策略

6\. 审核营销内容是否存在合规风险

7\. 输出可复盘的运营报告

8\. 记录 Agent 执行链路，方便排查问题



传统方式依赖人工分析，效率较低。



GrowthPilot-Agent 将这些流程拆解为多个专业 Agent，并通过 Supervisor Agent 串联成完整工作流。



\---



\## 4. 技术架构



\### 4.1 整体架构



```text

CSV 数据

&#x20; ↓

pandas 数据处理

&#x20; ↓

业务指标计算

&#x20; ↓

多 Agent 分析

&#x20; ↓

Supervisor 工作流调度

&#x20; ↓

Agent Trace 记录

&#x20; ↓

Markdown 报告导出

&#x20; ↓

Trace JSON 导出

&#x20; ↓

evals 自动化评测

```



\---



\### 4.2 模块拆分



```text

GrowthPilot-Agent/

├── app/

│   ├── agents/              # 多 Agent 逻辑

│   ├── prompts/             # Prompt 模板

│   ├── config.py            # 环境变量配置

│   ├── llm.py               # 大模型调用封装

│   ├── data\_service.py      # 数据读取和指标计算

│   ├── prompt\_loader.py     # Prompt 加载和渲染

│   └── report\_service.py    # 报告和 Trace 导出

├── data/                    # 默认业务数据

├── examples/                # 上传示例数据

├── evals/                   # 自动化评测

├── frontend/                # Streamlit 页面

├── docs/                    # 项目文档和截图

├── final\_project\_check.py   # 最终交付检查脚本

└── README.md

```



\---



\## 5. Agent 设计



项目中包含 6 类 Agent。



| Agent | 作用 |

|---|---|

| Sales Analysis Agent | 分析 GMV、CTR、CVR、退款率等经营指标 |

| User Insight Agent | 从用户评论中提取痛点、正反馈、负反馈和内容机会 |

| Batch Growth Agent | 对多个商品进行优先级排序和增长策略生成 |

| Content Strategy Agent | 生成小红书内容、抖音脚本和发布建议 |

| Compliance Agent | 审核内容是否存在夸大宣传、绝对化表达等风险 |

| Supervisor Agent | 调度多个专业 Agent，形成完整增长工作流 |



\---



\## 6. Supervisor 工作流



Supervisor Agent 负责串联多个 Agent。



执行流程如下：



```text

生成 run\_id

&#x20; ↓

销售数据分析 Agent

&#x20; ↓

用户评论洞察 Agent

&#x20; ↓

内容策略 Agent

&#x20; ↓

合规审核 Agent

&#x20; ↓

生成 Trace 日志

&#x20; ↓

返回完整工作流结果

```



Supervisor 工作流具备两个重要能力：



1\. `run\_id`：每次运行生成唯一工作流编号。

2\. `progress\_callback`：支持前端展示当前执行进度。



\---



\## 7. Agent Trace 可观测性



项目会记录每个 Agent 的执行日志。



Trace 字段包括：



| 字段 | 说明 |

|---|---|

| run\_id | 当前工作流运行 ID |

| step | Agent 步骤名称 |

| description | 当前步骤说明 |

| input\_summary | 输入摘要 |

| status | 执行状态 |

| duration\_seconds | 执行耗时 |

| output\_preview | 输出预览 |

| error | 错误信息 |



这样可以看到：



\- 哪个 Agent 执行了

\- 是否成功

\- 执行用了多久

\- 输入是什么摘要

\- 输出预览是什么

\- 是否有错误



这让项目更接近真实 Agent 平台的可观测性设计。



\---



\## 8. 数据设计



项目使用三类 CSV 数据。



\### 8.1 商品数据



```text

data/product.csv

```



字段：



| 字段 | 含义 |

|---|---|

| product\_id | 商品 ID |

| product\_name | 商品名称 |

| category | 商品类目 |

| price | 商品价格 |



\---



\### 8.2 销售数据



```text

data/sales.csv

```



字段：



| 字段 | 含义 |

|---|---|

| product\_id | 商品 ID |

| views | 曝光量 |

| clicks | 点击量 |

| orders | 订单数 |

| refunds | 退款数 |



\---



\### 8.3 评论数据



```text

data/comments.csv

```



字段：



| 字段 | 含义 |

|---|---|

| product\_id | 商品 ID |

| rating | 用户评分 |

| comment | 用户评论 |



\---



\## 9. 运营指标



项目会自动计算以下指标：



| 指标 | 公式 | 含义 |

|---|---|---|

| GMV | price × orders | 成交金额 |

| CTR | clicks / views | 点击率 |

| CVR | orders / clicks | 转化率 |

| refund\_rate | refunds / orders | 退款率 |



这些指标会作为 Agent 分析和内容策略生成的基础。



\---



\## 10. Prompt 工程化



项目将 Prompt 从 Python 代码中拆出，统一放在：



```text

app/prompts/

```



好处是：



\- Prompt 和业务代码解耦

\- 方便单独修改 Prompt

\- 方便后续扩展多个 Prompt 版本

\- 便于 evals 检查 Prompt 变量是否完整



当前 Prompt 模板包括：



```text

sales\_analysis\_prompt.txt

user\_insight\_prompt.txt

content\_strategy\_prompt.txt

compliance\_prompt.txt

batch\_growth\_prompt.txt

```



\---



\## 11. 大模型配置工程化



项目通过 `.env` 管理大模型配置。



`.env.example` 示例：



```env

DASHSCOPE\_API\_KEY=your\_dashscope\_api\_key\_here

DASHSCOPE\_BASE\_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

QWEN\_MODEL=qwen-plus

QWEN\_TEMPERATURE=0.7

```



配置统一在：



```text

app/config.py

```



大模型调用统一封装在：



```text

app/llm.py

```



`call\_qwen()` 支持：



```python

call\_qwen(prompt)

```



也支持：



```python

call\_qwen(prompt, model="qwen-plus", temperature=0.2)

```



这样避免模型名称、temperature 和 API Key 写死在业务代码中。



\---



\## 12. Streamlit 页面功能



页面包含：



1\. 核心指标展示

2\. 商品运营数据表

3\. 用户评论数据表

4\. 原始销售数据表

5\. CSV 模板下载

6\. CSV 数据上传

7\. 上传字段校验

8\. 销售数据分析 Agent

9\. 用户评论洞察 Agent

10\. 多商品批量增长分析 Agent

11\. 内容策略 Agent

12\. Supervisor 多 Agent 工作流

13\. Supervisor 工作流进度条

14\. 当前 run\_id 展示

15\. Agent Trace 执行日志

16\. Agent Trace JSON 下载

17\. Markdown 报告下载

18\. 合规审核 Agent



\---



\## 13. 报告导出



项目支持导出 Markdown 增长报告。



默认路径：



```text

outputs/growth\_report.md

```



报告内容包括：



\- 报告生成时间

\- run\_id

\- 分析商品

\- Agent Trace 执行日志

\- 销售分析结果

\- 用户评论洞察结果

\- 内容策略结果

\- 合规审核结果



\---



\## 14. Trace JSON 导出



项目支持导出结构化 Trace JSON。



默认路径：



```text

outputs/agent\_trace.json

```



Trace JSON 包含：



\- generated\_at

\- run\_id

\- selected\_product

\- workflow

\- traces



适合后续用于：



\- 调试

\- 复盘

\- 平台化接入

\- 历史任务查询

\- Agent 运行监控



\---



\## 15. evals 自动化评测



项目构建了 evals 自动化评测脚本。



运行静态评测：



```bash

python evals/run\_eval.py

```



运行带 LLM 评测：



```bash

python evals/run\_eval.py --with-llm

```



当前结果：



```text

静态 evals：80 / 80 通过

带 LLM evals：83 / 83 通过

```



evals 覆盖：



\- 文件存在性

\- 环境变量配置

\- 数据字段完整性

\- 运营指标生成

\- examples 上传示例

\- Prompt 文件存在性

\- Prompt 变量检查

\- Prompt 渲染

\- Supervisor 静态能力

\- progress\_callback

\- report\_service 函数

\- Trace JSON 结构

\- LLM 合规审核能力



\---



\## 16. final\_project\_check 最终交付检查



项目新增：



```text

final\_project\_check.py

```



运行：



```bash

python final\_project\_check.py

```



或：



```bash

python final\_project\_check.py --with-llm

```



当前结果：



```text

不带 LLM：4 / 4 通过

带 LLM：5 / 5 通过

结果：项目当前处于可交付状态

```



该脚本适合在以下场景使用：



\- GitHub 提交前

\- 面试演示前

\- 修改代码后

\- 项目最终交付前



\---



\## 17. .gitignore 安全控制



项目通过 `.gitignore` 避免上传敏感文件和运行产物。



已忽略：



```text

.env

.env.\*

outputs/

\_\_pycache\_\_/

\*.pyc

.streamlit/secrets.toml

requirements\_freeze.txt

```



保留：



```text

.env.example

```



原因：



\- `.env` 包含真实 API Key，不能上传

\- `.env.example` 是示例配置，可以上传

\- `outputs/` 是运行时生成内容，不需要上传

\- 缓存和临时文件不应进入 Git 仓库



\---



\## 18. 当前项目完成度



当前项目完成度较高，已经具备简历项目条件。



已完成：



\- 多 Agent 架构

\- Supervisor 工作流

\- Agent Trace

\- run\_id

\- 进度条

\- CSV 上传

\- 模板下载

\- 字段校验

\- Markdown 报告

\- Trace JSON

\- evals 自动化评测

\- LLM 合规审核评测

\- 最终交付检查

\- GitHub 提交

\- README 完整说明



当前适合作为：



```text

AI Agent 工程项目

```



也可以在简历中定位为：



```text

内容电商多 Agent 商家增长助手

```



\---



\## 19. 简历项目描述



GrowthPilot-Agent 是一个面向内容电商场景的多 Agent 商家增长助手。项目基于 DashScope 通义千问、Streamlit 和 pandas 构建，设计 Sales Analysis Agent、User Insight Agent、Batch Growth Agent、Content Strategy Agent、Compliance Agent 和 Supervisor Agent，实现从商品经营分析、用户评论洞察、多商品增长策略、内容策略生成到合规审核的完整业务闭环。



项目对 Agent 调用链路进行了工程化拆分，将数据处理、大模型调用、Prompt 模板、Agent 逻辑、环境变量配置、报告导出和 evals 评测模块解耦为独立模块；支持 Streamlit 侧边栏上传商品、销售和评论 CSV 数据，提供 CSV 模板下载，并对上传文件进行字段完整性校验，保证用户输入数据可用。



系统实现 Agent Trace 可观测性面板，为每次 Supervisor 工作流生成唯一 run\_id，记录每个 Agent 的执行状态、耗时、输入摘要、输出预览和错误信息；通过 progress\_callback 支持 Supervisor 工作流进度展示；支持将 Supervisor 工作流结果导出并下载为 Markdown 增长报告，同时支持将 Agent Trace 导出为 JSON 文件，便于任务复盘、调试和后续平台化接入。



项目构建 evals 自动化评测脚本，覆盖文件完整性、环境变量配置、默认数据字段、examples 上传示例数据、运营指标生成、Prompt 模板变量检查、Prompt 渲染、Supervisor 静态能力、report\_service 导出函数检查、Agent Trace JSON 结构校验和合规审核能力；当前本地静态评测 80/80 通过，带 LLM 评测 83/83 通过，最终交付检查 5/5 通过。



\---



\## 20. 面试讲解重点



面试时可以重点讲：



1\. 为什么做多 Agent，而不是单个 Prompt

2\. Supervisor Agent 如何调度多个 Agent

3\. Batch Growth Agent 如何做多商品分析

4\. Agent Trace 为什么重要

5\. run\_id 如何追踪每次工作流

6\. progress\_callback 如何驱动前端进度条

7\. Prompt 为什么要拆成模板文件

8\. 为什么要做 Trace JSON 导出

9\. evals 为什么要检查 Prompt、数据和 Trace

10\. LLM 服务不可用时为什么要 SKIP 而不是 FAIL

11\. final\_project\_check.py 解决了什么问题

12\. `.gitignore` 如何避免密钥误传

13\. 项目如何从 demo 变成工程化应用



\---



\## 21. 后续可升级方向



后续可以继续升级：



\### 21.1 项目截图



在 README 中补充：



```text

首页截图

Supervisor 工作流截图

Agent Trace 截图

evals 结果截图

```



\---



\### 21.2 RAG 知识库



接入 ChromaDB，构建：



```text

小红书内容风格知识库

抖音脚本风格知识库

平台合规规则知识库

营销禁用词知识库

```



\---



\### 21.3 LangGraph 工作流



将当前自定义 Supervisor 工作流升级为 LangGraph 状态图。



\---



\### 21.4 Docker 部署



补充：



```text

Dockerfile

docker-compose.yml

```



提升部署能力。



\---



\### 21.5 报告格式扩展



支持：



```text

PDF 报告

Word 报告

带图表报告

多商品批量报告

```

