import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


from app.agents.batch_agent import run_batch_growth_agent
from app.agents.compliance_agent import run_compliance_agent
from app.agents.content_agent import run_content_strategy_agent
from app.agents.insight_agent import run_user_insight_agent
from app.agents.sales_agent import run_sales_analysis_agent
from app.agents.supervisor_agent import run_supervisor_workflow
from app.data_service import (
    build_business_data,
    load_business_data,
    validate_uploaded_data,
)
from app.report_service import save_agent_trace, save_growth_report


PRODUCT_TEMPLATE_PATH = BASE_DIR / "examples" / "upload_samples" / "product.csv"
SALES_TEMPLATE_PATH = BASE_DIR / "examples" / "upload_samples" / "sales.csv"
COMMENTS_TEMPLATE_PATH = BASE_DIR / "examples" / "upload_samples" / "comments.csv"


def init_session_state() -> None:
    """
    初始化 Streamlit 页面状态。
    """
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = ""

    if "batch_growth_result" not in st.session_state:
        st.session_state.batch_growth_result = ""

    if "supervisor_result" not in st.session_state:
        st.session_state.supervisor_result = None

    if "report_markdown" not in st.session_state:
        st.session_state.report_markdown = ""

    if "report_path" not in st.session_state:
        st.session_state.report_path = ""

    if "trace_json" not in st.session_state:
        st.session_state.trace_json = ""

    if "trace_path" not in st.session_state:
        st.session_state.trace_path = ""


def render_template_download_buttons() -> None:
    """
    在侧边栏渲染 CSV 模板下载按钮。
    """
    with st.sidebar.expander("下载 CSV 模板", expanded=True):
        st.caption("可以先下载模板，按照字段格式填写自己的数据后再上传。")

        st.download_button(
            label="下载 product.csv 模板",
            data=PRODUCT_TEMPLATE_PATH.read_bytes(),
            file_name="product.csv",
            mime="text/csv",
            key="download_product_template",
        )

        st.download_button(
            label="下载 sales.csv 模板",
            data=SALES_TEMPLATE_PATH.read_bytes(),
            file_name="sales.csv",
            mime="text/csv",
            key="download_sales_template",
        )

        st.download_button(
            label="下载 comments.csv 模板",
            data=COMMENTS_TEMPLATE_PATH.read_bytes(),
            file_name="comments.csv",
            mime="text/csv",
            key="download_comments_template",
        )


def render_rag_context(rag_context: Dict[str, Any], key_prefix: str) -> None:
    """
    渲染单条 Trace 中的 RAG 检索信息。
    """
    if not rag_context:
        st.info("该步骤没有 RAG 检索信息。")
        return

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    metric_col1.metric(
        "used_chromadb",
        str(rag_context.get("used_chromadb", False)),
    )
    metric_col2.metric(
        "fallback_used",
        str(rag_context.get("fallback_used", False)),
    )
    metric_col3.metric(
        "top_k",
        str(rag_context.get("top_k", 0)),
    )
    metric_col4.metric(
        "chunk_count",
        str(rag_context.get("chunk_count", 0)),
    )

    embedding_col1, embedding_col2, embedding_col3, embedding_col4 = st.columns(4)

    embedding_col1.metric(
        "embedding_provider",
        str(rag_context.get("embedding_provider", "")),
    )
    embedding_col2.metric(
        "embedding_model",
        str(rag_context.get("embedding_model", "")),
    )
    embedding_col3.metric(
        "embedding_dimension",
        str(rag_context.get("embedding_dimension", 0)),
    )
    embedding_col4.metric(
        "fallback_provider",
        str(rag_context.get("fallback_provider", "")),
    )

    st.markdown(f"**Agent：** {rag_context.get('agent', '')}")

    sources = rag_context.get("sources", [])
    if sources:
        st.markdown("**命中的知识库来源：**")
        st.write(sources)
    else:
        st.markdown("**命中的知识库来源：** 无")

    query = rag_context.get("query", "")
    if query:
        st.markdown("**RAG Query：**")
        st.text_area(
            label="RAG Query",
            value=query,
            height=120,
            disabled=True,
            key=f"{key_prefix}_rag_query",
            label_visibility="collapsed",
        )

    retrieved_text_preview = rag_context.get("retrieved_text_preview", "")
    if retrieved_text_preview:
        st.markdown("**检索片段预览：**")
        st.text_area(
            label="检索片段预览",
            value=retrieved_text_preview,
            height=160,
            disabled=True,
            key=f"{key_prefix}_rag_preview",
            label_visibility="collapsed",
        )

    error = rag_context.get("error", "")
    if error:
        st.error(error)


def render_rag_trace_summary(traces: List[Dict[str, Any]]) -> None:
    """
    在 Trace 页面集中展示所有 RAG 检索信息。
    """
    rag_traces = [
        trace for trace in traces
        if trace.get("rag_context")
    ]

    st.markdown("### RAG 检索信息")

    if not rag_traces:
        st.info("暂无 RAG 检索信息。")
        return

    for index, trace in enumerate(rag_traces):
        rag_context = trace.get("rag_context", {})
        step = trace.get("step", "")

        with st.expander(f"{step}｜RAG 检索详情", expanded=False):
            render_rag_context(
                rag_context=rag_context,
                key_prefix=f"summary_{index}",
            )


def load_page_data():
    """
    根据用户上传情况读取页面数据。

    如果用户完整上传 product.csv、sales.csv、comments.csv，
    且字段校验通过，则使用上传数据。

    否则使用项目 data/ 目录下的默认数据。
    """
    st.sidebar.header("数据源配置")

    render_template_download_buttons()

    uploaded_product = st.sidebar.file_uploader(
        "上传 product.csv",
        type=["csv"],
        key="uploaded_product_csv",
    )

    uploaded_sales = st.sidebar.file_uploader(
        "上传 sales.csv",
        type=["csv"],
        key="uploaded_sales_csv",
    )

    uploaded_comments = st.sidebar.file_uploader(
        "上传 comments.csv",
        type=["csv"],
        key="uploaded_comments_csv",
    )

    uploaded_files = [uploaded_product, uploaded_sales, uploaded_comments]
    uploaded_count = sum(file is not None for file in uploaded_files)

    if uploaded_count == 0:
        st.sidebar.info("当前使用项目默认示例数据。")
        return load_business_data()

    if uploaded_count < 3:
        st.sidebar.warning("请同时上传 product.csv、sales.csv、comments.csv。当前仍使用默认示例数据。")
        return load_business_data()

    try:
        products = pd.read_csv(uploaded_product)
        sales = pd.read_csv(uploaded_sales)
        comments = pd.read_csv(uploaded_comments)

        validation_errors = validate_uploaded_data(
            products=products,
            sales=sales,
            comments=comments,
        )

        if validation_errors:
            st.sidebar.error("上传 CSV 字段校验失败，当前使用默认示例数据。")

            for error in validation_errors:
                st.sidebar.warning(error)

            return load_business_data()

        st.sidebar.success("上传 CSV 字段校验通过，已使用上传数据。")

        return build_business_data(
            products=products,
            sales=sales,
            comments=comments,
        )

    except Exception as error:
        st.sidebar.error("上传 CSV 读取失败，当前使用默认示例数据。")
        st.sidebar.exception(error)

        return load_business_data()


def main() -> None:
    """
    Streamlit 页面主入口。
    """
    st.set_page_config(
        page_title="GrowthPilot-Agent",
        page_icon="📊",
        layout="wide",
    )

    init_session_state()

    st.title("📊 GrowthPilot-Agent 内容电商多 Agent 商家增长助手")

    st.markdown(
        """
        当前系统已经包含：

        1. 销售数据分析 Agent  
        2. 用户评论洞察 Agent  
        3. 多商品批量增长分析 Agent  
        4. 内容策略 Agent  
        5. 合规审核 Agent  
        6. Supervisor Agent 多 Agent 工作流  
        7. Agent Trace 执行日志面板  
        8. Markdown 增长报告导出与下载  
        9. Agent Trace JSON 导出与下载  
        10. CSV 数据上传  
        11. 上传 CSV 字段校验  
        12. CSV 模板下载  
        13. 工作流 run_id 追踪  
        14. Supervisor 工作流进度展示  
        15. RAG query、sources、chunk_count 和检索片段预览展示  
        16. embedding_provider、embedding_model 和 embedding_dimension 展示  
        """
    )

    products, sales, comments, df = load_page_data()

    total_gmv = df["gmv"].sum()
    avg_ctr = df["ctr"].mean()
    avg_cvr = df["cvr"].mean()
    avg_refund = df["refund_rate"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("总 GMV", f"¥{total_gmv:.0f}")
    col2.metric("平均 CTR", f"{avg_ctr:.2%}")
    col3.metric("平均 CVR", f"{avg_cvr:.2%}")
    col4.metric("平均退款率", f"{avg_refund:.2%}")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["商品运营数据", "用户评论数据", "原始销售数据"])

    with tab1:
        st.subheader("商品运营数据明细")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("用户评论数据")
        st.dataframe(comments, use_container_width=True)

    with tab3:
        st.subheader("原始销售数据")
        st.dataframe(sales, use_container_width=True)

    st.divider()

    st.subheader("🤖 销售数据分析 Agent")

    if st.button("生成运营分析建议", key="sales_agent_button"):
        with st.spinner("销售数据分析 Agent 正在分析中..."):
            result = run_sales_analysis_agent(df)

        st.markdown(result)

    st.divider()

    st.subheader("🧠 用户评论洞察 Agent")

    if st.button("分析用户评论", key="insight_agent_button"):
        with st.spinner("用户评论洞察 Agent 正在分析中..."):
            result = run_user_insight_agent(comments)

        st.markdown(result)

    st.divider()

    st.subheader("📦 多商品批量增长分析 Agent")

    st.markdown(
        """
        这个 Agent 用于同时分析多个商品，输出商品优先级、增长机会、内容方向和运营动作。
        """
    )

    default_batch_products = df["product_name"].tolist()[:3]

    batch_selected_products = st.multiselect(
        "请选择要批量分析的商品",
        df["product_name"].tolist(),
        default=default_batch_products,
        key="batch_selected_products",
    )

    if st.button("生成多商品批量增长策略", key="batch_growth_agent_button"):
        if not batch_selected_products:
            st.warning("请至少选择一个商品。")
        else:
            with st.spinner("多商品批量增长分析 Agent 正在分析中..."):
                result = run_batch_growth_agent(
                    df=df,
                    comments=comments,
                    selected_products=batch_selected_products,
                )

            st.session_state.batch_growth_result = result

    if st.session_state.batch_growth_result:
        st.markdown("### 多商品批量增长策略")
        st.markdown(st.session_state.batch_growth_result)

    st.divider()

    st.subheader("✍️ 内容策略 Agent")

    selected_product = st.selectbox(
        "请选择要生成内容的商品",
        df["product_name"].tolist(),
        key="selected_product",
    )

    if st.button("生成小红书和抖音内容", key="content_agent_button"):
        with st.spinner("内容策略 Agent 正在生成中..."):
            result = run_content_strategy_agent(
                df=df,
                comments=comments,
                selected_product=selected_product,
            )

        st.session_state.generated_content = result

    if st.session_state.generated_content:
        st.markdown("### 已生成内容")
        st.markdown(st.session_state.generated_content)

    st.divider()

    st.subheader("🧭 Supervisor Agent：一键多 Agent 工作流")

    st.markdown(
        """
        Supervisor Agent 会自动串联以下流程：

        1. 销售数据分析  
        2. 用户评论洞察  
        3. 内容策略生成  
        4. 内容合规审核  

        注意：这个按钮会连续调用 4 次大模型接口，运行时间会比单个 Agent 更长。
        """
    )

    if st.button("一键运行完整增长工作流", key="supervisor_workflow_button"):
        progress_bar = st.progress(0)
        progress_text = st.empty()

        def update_progress(progress: int, message: str) -> None:
            progress_bar.progress(progress)
            progress_text.info(message)

        with st.spinner("Supervisor Agent 正在调度多个 Agent，请稍等..."):
            supervisor_result = run_supervisor_workflow(
                df=df,
                comments=comments,
                selected_product=selected_product,
                progress_callback=update_progress,
            )

        st.session_state.supervisor_result = supervisor_result
        st.session_state.generated_content = supervisor_result.get("content_strategy", "")

        st.session_state.report_markdown = ""
        st.session_state.report_path = ""
        st.session_state.trace_json = ""
        st.session_state.trace_path = ""

        progress_bar.progress(100)
        progress_text.success("Supervisor 多 Agent 工作流执行完成。")

    if st.session_state.supervisor_result:
        run_id = st.session_state.supervisor_result.get("run_id", "")

        st.success("Supervisor 多 Agent 工作流已完成")

        if run_id:
            st.info(f"当前工作流运行 ID：{run_id}")

        if st.button("生成并准备下载 Markdown 报告", key="prepare_report_button"):
            try:
                report_path = save_growth_report(
                    supervisor_result=st.session_state.supervisor_result,
                    selected_product=selected_product,
                )

                if not report_path.exists():
                    st.error("报告生成失败：没有找到 growth_report.md 文件。")
                else:
                    report_markdown = report_path.read_text(encoding="utf-8")

                    st.session_state.report_path = str(report_path)
                    st.session_state.report_markdown = report_markdown

                    st.success(f"报告已生成：{report_path}")

            except Exception as error:
                st.error("生成 Markdown 报告时发生错误。")
                st.exception(error)

        if st.session_state.report_markdown:
            st.download_button(
                label="下载 Markdown 增长报告",
                data=st.session_state.report_markdown.encode("utf-8"),
                file_name="growth_report.md",
                mime="text/markdown",
                key="download_growth_report_button",
            )

            st.caption(f"当前报告路径：{st.session_state.report_path}")

        if st.button("生成并准备下载 Agent Trace JSON", key="prepare_trace_json_button"):
            try:
                trace_path = save_agent_trace(
                    supervisor_result=st.session_state.supervisor_result,
                    selected_product=selected_product,
                )

                if not trace_path.exists():
                    st.error("Trace JSON 生成失败：没有找到 agent_trace.json 文件。")
                else:
                    trace_json = trace_path.read_text(encoding="utf-8")

                    st.session_state.trace_path = str(trace_path)
                    st.session_state.trace_json = trace_json

                    st.success(f"Trace JSON 已生成：{trace_path}")

            except Exception as error:
                st.error("生成 Agent Trace JSON 时发生错误。")
                st.exception(error)

        if st.session_state.trace_json:
            st.download_button(
                label="下载 Agent Trace JSON",
                data=st.session_state.trace_json.encode("utf-8"),
                file_name="agent_trace.json",
                mime="application/json",
                key="download_agent_trace_json_button",
            )

            st.caption(f"当前 Trace 路径：{st.session_state.trace_path}")

        traces = st.session_state.supervisor_result.get("traces", [])

        result_tabs = st.tabs(
            [
                "Trace 执行日志",
                "RAG 检索信息",
                "销售分析结果",
                "评论洞察结果",
                "内容策略结果",
                "合规审核结果",
            ]
        )

        with result_tabs[0]:
            st.subheader("Agent Trace 执行日志")

            if traces:
                trace_df = pd.DataFrame(traces)
                st.dataframe(trace_df, use_container_width=True)

                total_duration = trace_df["duration_seconds"].sum()
                success_count = (trace_df["status"] == "success").sum()
                failed_count = (trace_df["status"] == "failed").sum()

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                metric_col1.metric("总耗时", f"{total_duration:.2f} 秒")
                metric_col2.metric("成功步骤", f"{success_count}")
                metric_col3.metric("失败步骤", f"{failed_count}")

                st.markdown("### 分步骤日志")

                for index, trace in enumerate(traces):
                    with st.expander(
                        f"{trace['step']}｜{trace['status']}｜{trace['duration_seconds']} 秒"
                    ):
                        st.markdown(f"**运行 ID：** {trace.get('run_id', '')}")
                        st.markdown(f"**步骤说明：** {trace['description']}")
                        st.markdown(f"**输入摘要：** {trace.get('input_summary', '')}")
                        st.markdown(f"**执行状态：** {trace['status']}")
                        st.markdown(f"**耗时：** {trace['duration_seconds']} 秒")

                        if trace["output_preview"]:
                            st.markdown("**输出预览：**")
                            st.markdown(trace["output_preview"])

                        if trace.get("rag_context"):
                            st.markdown("**RAG 检索元信息：**")
                            render_rag_context(
                                rag_context=trace["rag_context"],
                                key_prefix=f"trace_{index}",
                            )

                        if trace["error"]:
                            st.error(trace["error"])
            else:
                st.info("暂无 Trace 日志。")

        with result_tabs[1]:
            render_rag_trace_summary(traces)

        with result_tabs[2]:
            st.markdown(st.session_state.supervisor_result["sales_analysis"])

        with result_tabs[3]:
            st.markdown(st.session_state.supervisor_result["user_insight"])

        with result_tabs[4]:
            st.markdown(st.session_state.supervisor_result["content_strategy"])

        with result_tabs[5]:
            st.markdown(st.session_state.supervisor_result["compliance_review"])

    st.divider()

    st.subheader("🛡️ 合规审核 Agent")

    st.markdown(
        """
        合规审核 Agent 会检查内容中是否存在：

        - 绝对化用语
        - 夸大宣传
        - 虚假承诺
        - 医疗功效暗示
        - 价格欺诈风险
        - 不适合发布的营销话术
        """
    )

    content_to_check = st.text_area(
        "需要审核的内容",
        value=st.session_state.generated_content,
        height=300,
        placeholder="可以粘贴小红书文案、抖音脚本，或者先让内容策略 Agent 生成内容。",
        key="content_to_check_text_area",
    )

    if st.button("审核内容合规风险", key="compliance_agent_button"):
        if not content_to_check.strip():
            st.warning("请先输入或生成一段需要审核的内容。")
        else:
            with st.spinner("合规审核 Agent 正在审核中..."):
                result = run_compliance_agent(content_to_check)

            st.markdown(result)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        st.error("页面运行时发生错误，请查看下面的详细报错。")
        st.exception(error)