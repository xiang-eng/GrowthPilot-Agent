'''1. 读取 product.csv
2. 读取 sales.csv
3. 读取 comments.csv
4. 合并商品数据和销售数据
5. 计算 GMV、CTR、CVR、退款率'''
import pandas as pd

from app.config import PRODUCT_PATH, SALES_PATH, COMMENTS_PATH


REQUIRED_COLUMNS = {
    "product.csv": ["product_id", "product_name", "category", "price"],
    "sales.csv": ["product_id", "views", "clicks", "orders", "refunds"],
    "comments.csv": ["product_id", "rating", "comment"],
}


def load_raw_data():
    """
    读取项目默认 CSV 数据。
    """
    products = pd.read_csv(PRODUCT_PATH)
    sales = pd.read_csv(SALES_PATH)
    comments = pd.read_csv(COMMENTS_PATH)

    return products, sales, comments


def validate_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    file_name: str,
) -> list[str]:
    """
    检查单个 DataFrame 是否包含必需字段。

    参数:
        df: 要检查的数据表
        required_columns: 必须包含的字段列表
        file_name: 当前检查的文件名

    返回:
        错误信息列表。如果没有错误，返回空列表。
    """
    errors = []

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"{file_name} 缺少字段：{', '.join(missing_columns)}"
        )

    return errors


def validate_uploaded_data(
    products: pd.DataFrame,
    sales: pd.DataFrame,
    comments: pd.DataFrame,
) -> list[str]:
    """
    校验上传的三张 CSV 数据字段是否完整。

    参数:
        products: 商品数据表
        sales: 销售数据表
        comments: 评论数据表

    返回:
        错误信息列表。如果没有错误，返回空列表。
    """
    errors = []

    errors.extend(
        validate_columns(
            df=products,
            required_columns=REQUIRED_COLUMNS["product.csv"],
            file_name="product.csv",
        )
    )

    errors.extend(
        validate_columns(
            df=sales,
            required_columns=REQUIRED_COLUMNS["sales.csv"],
            file_name="sales.csv",
        )
    )

    errors.extend(
        validate_columns(
            df=comments,
            required_columns=REQUIRED_COLUMNS["comments.csv"],
            file_name="comments.csv",
        )
    )

    return errors


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    根据商品数据和销售数据计算运营指标。
    """
    df = df.copy()

    df["gmv"] = df["price"] * df["orders"]
    df["ctr"] = df["clicks"] / df["views"]
    df["cvr"] = df["orders"] / df["clicks"]
    df["refund_rate"] = df["refunds"] / df["orders"]

    return df


def build_business_data(
    products: pd.DataFrame,
    sales: pd.DataFrame,
    comments: pd.DataFrame,
):
    """
    根据商品数据、销售数据、评论数据构建业务数据。

    参数:
        products: 商品数据表
        sales: 销售数据表
        comments: 用户评论数据表

    返回:
        products: 商品数据表
        sales: 销售数据表
        comments: 用户评论数据表
        df: 合并并计算运营指标后的业务数据表
    """
    df = pd.merge(products, sales, on="product_id")
    df = calculate_metrics(df)

    return products, sales, comments, df


def load_business_data():
    """
    读取项目默认数据，并生成带运营指标的业务数据。
    """
    products, sales, comments = load_raw_data()

    return build_business_data(
        products=products,
        sales=sales,
        comments=comments,
    )