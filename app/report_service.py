import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.config import BASE_DIR


OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_PATH = OUTPUT_DIR / "growth_report.md"
TRACE_PATH = OUTPUT_DIR / "agent_trace.json"


def build_trace_section(traces: List[Dict[str, Any]]) -> str:
    """
    构建 Agent Trace 执行日志部分。

    参数:
        traces: Supervisor Agent 返回的执行日志列表

    返回:
        Markdown 格式的 Trace 文本
    """
    if not traces:
        return "暂无 Trace 执行日志。\n"

    lines = []

    for index, trace in enumerate(traces, start=1):
        lines.append(f"### {index}. {trace.get('step', '未知步骤')}")
        lines.append("")
        lines.append(f"- 运行 ID：{trace.get('run_id', '')}")
        lines.append(f"- 步骤说明：{trace.get('description', '')}")
        lines.append(f"- 输入摘要：{trace.get('input_summary', '')}")
        lines.append(f"- 执行状态：{trace.get('status', '')}")
        lines.append(f"- 执行耗时：{trace.get('duration_seconds', 0)} 秒")

        output_preview = trace.get("output_preview", "")
        error = trace.get("error", "")

        if output_preview:
            lines.append("")
            lines.append("输出预览：")
            lines.append("")
            lines.append(output_preview)

        if error:
            lines.append("")
            lines.append("错误信息：")
            lines.append("")
            lines.append(error)

        lines.append("")

    return "\n".join(lines)


def build_growth_report(
    supervisor_result: Dict[str, Any],
    selected_product: str,
) -> str:
    """
    根据 Supervisor 多 Agent 工作流结果构建 Markdown 报告。

    参数:
        supervisor_result: Supervisor Agent 返回的完整结果
        selected_product: 用户选择的商品名称

    返回:
        Markdown 报告内容
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    run_id = supervisor_result.get("run_id", "")
    sales_analysis = supervisor_result.get("sales_analysis", "")
    user_insight = supervisor_result.get("user_insight", "")
    content_strategy = supervisor_result.get("content_strategy", "")
    compliance_review = supervisor_result.get("compliance_review", "")
    traces = supervisor_result.get("traces", [])

    trace_section = build_trace_section(traces)

    report = f"""# GrowthPilot-Agent 内容电商多 Agent 增长报告

## 一、报告信息

- 生成时间：{now}
- 运行 ID：{run_id}
- 分析商品：{selected_product}
- 报告来源：Supervisor 多 Agent 工作流

---

## 二、Agent Trace 执行日志

{trace_section}

---

## 三、销售数据分析结果

{sales_analysis}

---

## 四、用户评论洞察结果

{user_insight}

---

## 五、内容策略生成结果

{content_strategy}

---

## 六、合规审核结果

{compliance_review}

---

## 七、报告说明

本报告由 GrowthPilot-Agent 自动生成。

系统通过 Supervisor Agent 调度多个专业 Agent，完成从经营数据分析、用户洞察、内容生成到合规审核的完整流程。
"""

    return report


def save_growth_report(
    supervisor_result: Dict[str, Any],
    selected_product: str,
) -> Path:
    """
    保存 Supervisor 多 Agent 工作流报告到 outputs/growth_report.md。

    参数:
        supervisor_result: Supervisor Agent 返回的完整结果
        selected_product: 用户选择的商品名称

    返回:
        保存后的报告路径
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_content = build_growth_report(
        supervisor_result=supervisor_result,
        selected_product=selected_product,
    )

    REPORT_PATH.write_text(report_content, encoding="utf-8")

    return REPORT_PATH


def save_agent_trace(
    supervisor_result: Dict[str, Any],
    selected_product: str,
) -> Path:
    """
    保存 Supervisor 多 Agent 工作流 Trace 到 outputs/agent_trace.json。

    参数:
        supervisor_result: Supervisor Agent 返回的完整结果
        selected_product: 用户选择的商品名称

    返回:
        保存后的 Trace JSON 文件路径
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    trace_payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": supervisor_result.get("run_id", ""),
        "selected_product": selected_product,
        "workflow": "Supervisor Agent Workflow",
        "traces": supervisor_result.get("traces", []),
    }

    TRACE_PATH.write_text(
        json.dumps(trace_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return TRACE_PATH