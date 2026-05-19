# Upload Samples

这个文件夹提供 GrowthPilot-Agent 的 CSV 上传测试样例。

你可以在 Streamlit 页面左侧上传以下 3 个文件：

1. product.csv
2. sales.csv
3. comments.csv

三个文件必须同时上传，否则系统会继续使用默认示例数据。

---

## 1. product.csv

商品数据文件，必须包含以下字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| product_name | 商品名称 |
| category | 商品类目 |
| price | 商品价格 |

---

## 2. sales.csv

销售数据文件，必须包含以下字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| views | 曝光量 |
| clicks | 点击量 |
| orders | 订单数 |
| refunds | 退款数 |

系统会基于这些字段自动计算：

- GMV
- CTR
- CVR
- refund_rate

---

## 3. comments.csv

用户评论数据文件，必须包含以下字段：

| 字段 | 含义 |
|---|---|
| product_id | 商品 ID |
| rating | 用户评分 |
| comment | 用户评论 |

---

## 4. 使用方式

启动项目：

```bash
python -m streamlit run frontend/streamlit_app.py