import argparse
import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


from app.config import BASE_DIR, COMMENTS_PATH, PRODUCT_PATH, SALES_PATH
from app.data_service import (
    build_business_data,
    load_business_data,
    validate_uploaded_data,
)
from app.prompt_loader import PROMPT_DIR, render_prompt


EVAL_CASES_PATH = BASE_DIR / "evals" / "eval_cases.json"


def load_eval_cases() -> Dict[str, Any]:
    """
    读取评测用例文件 eval_cases.json。
    """
    return json.loads(EVAL_CASES_PATH.read_text(encoding="utf-8"))


def print_eval_result(
    name: str,
    passed: Optional[bool],
    detail: str = "",
) -> None:
    """
    打印单条评测结果。

    passed:
        True 表示通过
        False 表示失败
        None 表示跳过
    """
    if passed is True:
        status = "PASS"
    elif passed is False:
        status = "FAIL"
    else:
        status = "SKIP"

    print(f"[{status}] {name}")

    if detail:
        print(f"       {detail}")


def check_columns(
    df: pd.DataFrame,
    required_columns: List[str],
) -> Tuple[bool, str]:
    """
    检查 DataFrame 是否包含指定列。
    """
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        return False, f"缺少列: {missing_columns}"

    return True, "列完整"


def is_llm_unavailable_error(error: Exception) -> bool:
    """
    判断异常是否属于大模型服务不可用。

    这类问题通常不是代码错误，而是：
    1. 账户欠费
    2. API Key 无权限
    3. 额度不足
    4. 服务暂时不可用
    """
    error_text = str(error)

    unavailable_keywords = [
        "Arrearage",
        "overdue-payment",
        "Access denied",
        "insufficient",
        "quota",
        "Quota",
        "balance",
        "billing",
        "payment",
        "欠费",
        "余额",
        "额度",
        "无权限",
    ]

    return any(keyword in error_text for keyword in unavailable_keywords)


def run_file_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    检查关键文件是否存在。
    """
    results: List[Optional[bool]] = []

    required_files = [
        PRODUCT_PATH,
        SALES_PATH,
        COMMENTS_PATH,
        BASE_DIR / ".env.example",
        BASE_DIR / "final_project_check.py",
        BASE_DIR / "app" / "agents" / "sales_agent.py",
        BASE_DIR / "app" / "agents" / "insight_agent.py",
        BASE_DIR / "app" / "agents" / "content_agent.py",
        BASE_DIR / "app" / "agents" / "compliance_agent.py",
        BASE_DIR / "app" / "agents" / "supervisor_agent.py",
        BASE_DIR / "app" / "agents" / "batch_agent.py",
        BASE_DIR / "app" / "config.py",
        BASE_DIR / "app" / "llm.py",
        BASE_DIR / "app" / "prompt_loader.py",
        BASE_DIR / "app" / "report_service.py",
    ]

    example_upload_files = eval_cases.get("example_upload_files", [])

    for relative_path in example_upload_files:
        required_files.append(BASE_DIR / relative_path)

    for file_path in required_files:
        passed = file_path.exists()
        print_eval_result(
            f"文件存在检查: {file_path.relative_to(BASE_DIR)}",
            passed,
        )
        results.append(passed)

    return results


def run_env_config_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    检查环境变量示例文件、配置模块和 LLM 调用函数是否完整。
    """
    results: List[Optional[bool]] = []

    env_example_path = BASE_DIR / ".env.example"
    required_env_keys = eval_cases.get("required_env_example_keys", [])
    required_config_attributes = eval_cases.get("required_config_attributes", [])
    required_llm_functions = eval_cases.get("required_llm_functions", [])

    env_file_exists = env_example_path.exists()

    print_eval_result(
        ".env.example 文件存在检查",
        env_file_exists,
        str(env_example_path),
    )
    results.append(env_file_exists)

    if env_file_exists:
        env_example_text = env_example_path.read_text(encoding="utf-8")

        for env_key in required_env_keys:
            has_key = env_key in env_example_text

            print_eval_result(
                f".env.example 环境变量检查: {env_key}",
                has_key,
                "变量存在" if has_key else "变量缺失",
            )
            results.append(has_key)

    try:
        config_module = importlib.import_module("app.config")
        config_imported = True
        config_detail = "app.config 导入成功"
    except Exception as error:
        config_module = None
        config_imported = False
        config_detail = str(error)

    print_eval_result(
        "config 模块导入检查",
        config_imported,
        config_detail,
    )
    results.append(config_imported)

    if config_imported:
        for attribute_name in required_config_attributes:
            has_attribute = hasattr(config_module, attribute_name)

            print_eval_result(
                f"config 配置项检查: {attribute_name}",
                has_attribute,
                "配置项存在" if has_attribute else "配置项缺失",
            )
            results.append(has_attribute)

    try:
        llm_module = importlib.import_module("app.llm")
        llm_imported = True
        llm_detail = "app.llm 导入成功"
    except Exception as error:
        llm_module = None
        llm_imported = False
        llm_detail = str(error)

    print_eval_result(
        "llm 模块导入检查",
        llm_imported,
        llm_detail,
    )
    results.append(llm_imported)

    if not llm_imported:
        return results

    for function_name in required_llm_functions:
        has_function = hasattr(llm_module, function_name)

        print_eval_result(
            f"llm 函数检查: {function_name}",
            has_function,
            "函数存在" if has_function else "函数缺失",
        )
        results.append(has_function)

    if hasattr(llm_module, "call_qwen"):
        try:
            signature = inspect.signature(llm_module.call_qwen)

            has_model_param = "model" in signature.parameters
            has_temperature_param = "temperature" in signature.parameters

            print_eval_result(
                "call_qwen model 参数检查",
                has_model_param,
                "支持 model 参数" if has_model_param else "缺少 model 参数",
            )
            results.append(has_model_param)

            print_eval_result(
                "call_qwen temperature 参数检查",
                has_temperature_param,
                (
                    "支持 temperature 参数"
                    if has_temperature_param
                    else "缺少 temperature 参数"
                ),
            )
            results.append(has_temperature_param)

        except Exception as error:
            print_eval_result(
                "call_qwen 参数签名检查",
                False,
                str(error),
            )
            results.append(False)

    return results


def run_data_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    评测默认数据读取和指标计算是否正常。
    """
    results: List[Optional[bool]] = []

    products, sales, comments, df = load_business_data()

    required_data_columns = eval_cases["required_data_columns"]

    product_passed, product_detail = check_columns(
        products,
        required_data_columns["product"],
    )
    print_eval_result("默认商品数据列检查", product_passed, product_detail)
    results.append(product_passed)

    sales_passed, sales_detail = check_columns(
        sales,
        required_data_columns["sales"],
    )
    print_eval_result("默认销售数据列检查", sales_passed, sales_detail)
    results.append(sales_passed)

    comments_passed, comments_detail = check_columns(
        comments,
        required_data_columns["comments"],
    )
    print_eval_result("默认评论数据列检查", comments_passed, comments_detail)
    results.append(comments_passed)

    metric_passed, metric_detail = check_columns(
        df,
        eval_cases["required_metric_columns"],
    )
    print_eval_result("默认运营指标列检查", metric_passed, metric_detail)
    results.append(metric_passed)

    row_count_passed = len(df) > 0
    print_eval_result(
        "默认业务数据非空检查",
        row_count_passed,
        f"当前业务数据行数: {len(df)}",
    )
    results.append(row_count_passed)

    return results


def run_example_upload_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    评测 examples/upload_samples 示例上传数据是否可用。
    """
    results: List[Optional[bool]] = []

    example_files = eval_cases.get("example_upload_files", [])

    product_path = BASE_DIR / "examples" / "upload_samples" / "product.csv"
    sales_path = BASE_DIR / "examples" / "upload_samples" / "sales.csv"
    comments_path = BASE_DIR / "examples" / "upload_samples" / "comments.csv"

    required_paths = [product_path, sales_path, comments_path]

    files_exist = all(path.exists() for path in required_paths)

    print_eval_result(
        "examples 上传示例文件整体存在检查",
        files_exist,
        f"配置文件数: {len(example_files)}",
    )
    results.append(files_exist)

    if not files_exist:
        return results

    try:
        products = pd.read_csv(product_path)
        sales = pd.read_csv(sales_path)
        comments = pd.read_csv(comments_path)

        validation_errors = validate_uploaded_data(
            products=products,
            sales=sales,
            comments=comments,
        )

        validation_passed = len(validation_errors) == 0
        validation_detail = (
            "字段完整"
            if validation_passed
            else "；".join(validation_errors)
        )

        print_eval_result(
            "examples 上传示例字段校验",
            validation_passed,
            validation_detail,
        )
        results.append(validation_passed)

        if not validation_passed:
            return results

        _, _, _, df = build_business_data(
            products=products,
            sales=sales,
            comments=comments,
        )

        metric_passed, metric_detail = check_columns(
            df,
            eval_cases["required_metric_columns"],
        )

        print_eval_result(
            "examples 上传示例运营指标生成检查",
            metric_passed,
            metric_detail,
        )
        results.append(metric_passed)

        row_count_passed = len(df) > 0
        print_eval_result(
            "examples 上传示例业务数据非空检查",
            row_count_passed,
            f"当前示例业务数据行数: {len(df)}",
        )
        results.append(row_count_passed)

    except Exception as error:
        print_eval_result(
            "examples 上传示例读取与构建检查",
            False,
            str(error),
        )
        results.append(False)

    return results


def run_prompt_template_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    检查 Prompt 模板文件和变量是否正常。
    """
    results: List[Optional[bool]] = []

    for template_case in eval_cases["prompt_templates"]:
        file_name = template_case["file_name"]
        required_placeholders = template_case["required_placeholders"]

        prompt_path = PROMPT_DIR / file_name

        file_exists = prompt_path.exists()
        print_eval_result(
            f"Prompt 文件存在检查: {file_name}",
            file_exists,
        )
        results.append(file_exists)

        if not file_exists:
            continue

        template_text = prompt_path.read_text(encoding="utf-8")

        for placeholder in required_placeholders:
            has_placeholder = placeholder in template_text
            print_eval_result(
                f"Prompt 变量检查: {file_name} 包含 {placeholder}",
                has_placeholder,
            )
            results.append(has_placeholder)

    return results


def run_prompt_render_evals() -> List[Optional[bool]]:
    """
    检查 Prompt 模板是否能正常渲染。
    """
    results: List[Optional[bool]] = []

    render_cases = [
        {
            "file_name": "sales_analysis_prompt.txt",
            "kwargs": {"data_text": "商品运营测试数据"},
        },
        {
            "file_name": "user_insight_prompt.txt",
            "kwargs": {"comments_text": "用户评论测试数据"},
        },
        {
            "file_name": "content_strategy_prompt.txt",
            "kwargs": {
                "product_text": "商品测试数据",
                "comment_text": "评论测试数据",
            },
        },
        {
            "file_name": "compliance_prompt.txt",
            "kwargs": {"content": "待审核测试内容"},
        },
        {
            "file_name": "batch_growth_prompt.txt",
            "kwargs": {
                "product_text": "多商品运营测试数据",
                "comments_text": "多商品评论测试数据",
            },
        },
    ]

    for case in render_cases:
        file_name = case["file_name"]
        kwargs = case["kwargs"]

        try:
            prompt = render_prompt(file_name, **kwargs)
            passed = all(str(value) in prompt for value in kwargs.values())
            detail = "渲染成功" if passed else "变量没有正确填入 Prompt"
        except Exception as error:
            passed = False
            detail = str(error)

        print_eval_result(
            f"Prompt 渲染检查: {file_name}",
            passed,
            detail,
        )
        results.append(passed)

    return results


def run_supervisor_static_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    检查 Supervisor Agent 的静态结构能力。

    这里不真实调用大模型，只检查：
    1. 模块能否导入
    2. 核心函数是否存在
    3. run_id 格式是否正确
    4. 是否支持 progress_callback
    5. notify_progress 是否能触发回调
    """
    results: List[Optional[bool]] = []

    required_functions = eval_cases.get("required_supervisor_functions", [])

    try:
        supervisor_agent = importlib.import_module("app.agents.supervisor_agent")
        module_imported = True
        module_detail = "app.agents.supervisor_agent 导入成功"
    except Exception as error:
        supervisor_agent = None
        module_imported = False
        module_detail = str(error)

    print_eval_result(
        "supervisor_agent 模块导入检查",
        module_imported,
        module_detail,
    )
    results.append(module_imported)

    if not module_imported:
        return results

    for function_name in required_functions:
        has_function = hasattr(supervisor_agent, function_name)
        detail = (
            "函数存在"
            if has_function
            else f"缺少函数: {function_name}"
        )

        print_eval_result(
            f"supervisor_agent 函数检查: {function_name}",
            has_function,
            detail,
        )
        results.append(has_function)

    if hasattr(supervisor_agent, "generate_run_id"):
        try:
            run_id = supervisor_agent.generate_run_id()
            run_id_passed = isinstance(run_id, str) and run_id.startswith("run_")
            run_id_detail = f"生成的 run_id: {run_id}"
        except Exception as error:
            run_id_passed = False
            run_id_detail = str(error)

        print_eval_result(
            "supervisor_agent run_id 格式检查",
            run_id_passed,
            run_id_detail,
        )
        results.append(run_id_passed)

    if hasattr(supervisor_agent, "run_supervisor_workflow"):
        try:
            signature = inspect.signature(supervisor_agent.run_supervisor_workflow)
            has_progress_callback = "progress_callback" in signature.parameters
            detail = (
                "包含 progress_callback 参数"
                if has_progress_callback
                else "缺少 progress_callback 参数"
            )
        except Exception as error:
            has_progress_callback = False
            detail = str(error)

        print_eval_result(
            "supervisor_agent progress_callback 参数检查",
            has_progress_callback,
            detail,
        )
        results.append(has_progress_callback)

    if hasattr(supervisor_agent, "notify_progress"):
        captured_progress = []

        def mock_progress_callback(progress: int, message: str) -> None:
            captured_progress.append(
                {
                    "progress": progress,
                    "message": message,
                }
            )

        try:
            supervisor_agent.notify_progress(
                mock_progress_callback,
                66,
                "测试进度回调",
            )

            callback_passed = (
                len(captured_progress) == 1
                and captured_progress[0]["progress"] == 66
                and captured_progress[0]["message"] == "测试进度回调"
            )

            callback_detail = f"捕获回调: {captured_progress}"

        except Exception as error:
            callback_passed = False
            callback_detail = str(error)

        print_eval_result(
            "supervisor_agent notify_progress 回调检查",
            callback_passed,
            callback_detail,
        )
        results.append(callback_passed)

    return results


def build_mock_supervisor_result() -> Dict[str, Any]:
    """
    构造一个模拟 Supervisor 工作流结果，用于测试 Trace JSON 导出。
    """
    run_id = "run_eval_test_123456"

    return {
        "run_id": run_id,
        "sales_analysis": "销售分析测试结果",
        "user_insight": "用户洞察测试结果",
        "content_strategy": "内容策略测试结果",
        "compliance_review": "合规审核测试结果",
        "traces": [
            {
                "run_id": run_id,
                "step": "测试 Agent",
                "description": "用于测试 Trace JSON 导出的模拟步骤",
                "input_summary": "输入摘要测试内容",
                "status": "success",
                "duration_seconds": 0.12,
                "output_preview": "输出预览测试内容",
                "error": "",
            }
        ],
    }


def run_report_service_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    检查报告导出和 Trace JSON 导出相关函数是否存在，
    并验证 Trace JSON 文件结构是否正确。
    """
    results: List[Optional[bool]] = []

    required_functions = eval_cases.get("required_report_service_functions", [])
    required_trace_json_keys = eval_cases.get("required_trace_json_keys", [])
    required_trace_item_keys = eval_cases.get("required_trace_item_keys", [])

    try:
        report_service = importlib.import_module("app.report_service")
        module_imported = True
        module_detail = "app.report_service 导入成功"
    except Exception as error:
        report_service = None
        module_imported = False
        module_detail = str(error)

    print_eval_result(
        "report_service 模块导入检查",
        module_imported,
        module_detail,
    )
    results.append(module_imported)

    if not module_imported:
        return results

    for function_name in required_functions:
        has_function = hasattr(report_service, function_name)
        detail = (
            "函数存在"
            if has_function
            else f"缺少函数: {function_name}"
        )

        print_eval_result(
            f"report_service 函数检查: {function_name}",
            has_function,
            detail,
        )
        results.append(has_function)

    if not hasattr(report_service, "save_agent_trace"):
        return results

    try:
        mock_supervisor_result = build_mock_supervisor_result()
        expected_run_id = mock_supervisor_result["run_id"]

        trace_path = report_service.save_agent_trace(
            supervisor_result=mock_supervisor_result,
            selected_product="测试商品",
        )

        trace_file_exists = trace_path.exists()

        print_eval_result(
            "Trace JSON 文件生成检查",
            trace_file_exists,
            str(trace_path),
        )
        results.append(trace_file_exists)

        if not trace_file_exists:
            return results

        trace_payload = json.loads(trace_path.read_text(encoding="utf-8"))

        missing_top_level_keys = [
            key for key in required_trace_json_keys
            if key not in trace_payload
        ]

        top_level_passed = len(missing_top_level_keys) == 0
        top_level_detail = (
            "顶层字段完整"
            if top_level_passed
            else f"缺少顶层字段: {missing_top_level_keys}"
        )

        print_eval_result(
            "Trace JSON 顶层字段检查",
            top_level_passed,
            top_level_detail,
        )
        results.append(top_level_passed)

        run_id_passed = trace_payload.get("run_id") == expected_run_id

        print_eval_result(
            "Trace JSON run_id 检查",
            run_id_passed,
            f"run_id: {trace_payload.get('run_id')}",
        )
        results.append(run_id_passed)

        selected_product_passed = trace_payload.get("selected_product") == "测试商品"

        print_eval_result(
            "Trace JSON selected_product 检查",
            selected_product_passed,
            f"selected_product: {trace_payload.get('selected_product')}",
        )
        results.append(selected_product_passed)

        traces = trace_payload.get("traces", [])
        traces_list_passed = isinstance(traces, list) and len(traces) > 0

        print_eval_result(
            "Trace JSON traces 列表检查",
            traces_list_passed,
            f"Trace 数量: {len(traces) if isinstance(traces, list) else 0}",
        )
        results.append(traces_list_passed)

        if not traces_list_passed:
            return results

        first_trace = traces[0]

        missing_trace_item_keys = [
            key for key in required_trace_item_keys
            if key not in first_trace
        ]

        trace_item_passed = len(missing_trace_item_keys) == 0
        trace_item_detail = (
            "单条 Trace 字段完整"
            if trace_item_passed
            else f"缺少 Trace 字段: {missing_trace_item_keys}"
        )

        print_eval_result(
            "Trace JSON 单条日志字段检查",
            trace_item_passed,
            trace_item_detail,
        )
        results.append(trace_item_passed)

        trace_item_run_id_passed = first_trace.get("run_id") == expected_run_id

        print_eval_result(
            "Trace JSON 单条日志 run_id 检查",
            trace_item_run_id_passed,
            f"run_id: {first_trace.get('run_id')}",
        )
        results.append(trace_item_run_id_passed)

    except Exception as error:
        print_eval_result(
            "Trace JSON 结构评测",
            False,
            str(error),
        )
        results.append(False)

    return results


def run_compliance_llm_evals(eval_cases: Dict[str, Any]) -> List[Optional[bool]]:
    """
    调用合规审核 Agent，检查是否能识别高风险表达。

    注意：
        这个函数会真实调用大模型，会消耗 DashScope 额度。
    """
    from app.agents.compliance_agent import run_compliance_agent

    results: List[Optional[bool]] = []

    for case in eval_cases["compliance_eval_cases"]:
        case_id = case["id"]
        content = case["input"]
        expected_keywords = case["expected_keywords"]
        min_match_count = case["min_match_count"]

        try:
            output = run_compliance_agent(content)
            matched_keywords = [
                keyword for keyword in expected_keywords
                if keyword in output
            ]

            passed = len(matched_keywords) >= min_match_count
            detail = (
                f"命中关键词: {matched_keywords}, "
                f"要求至少命中: {min_match_count}"
            )

        except Exception as error:
            if is_llm_unavailable_error(error):
                passed = None
                detail = (
                    "LLM 服务当前不可用，已跳过该用例。"
                    f"原因: {error}"
                )
            else:
                passed = False
                detail = str(error)

        print_eval_result(
            f"合规审核 LLM 评测: {case_id}",
            passed,
            detail,
        )
        results.append(passed)

    return results


def print_summary(results: List[Optional[bool]]) -> None:
    """
    打印评测汇总结果。
    """
    total = sum(result is not None for result in results)
    passed = sum(result is True for result in results)
    failed = sum(result is False for result in results)
    skipped = sum(result is None for result in results)

    print("\n==============================")
    print("评测汇总")
    print("==============================")
    print(f"总检查数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {failed}")
    print(f"跳过数: {skipped}")

    if failed == 0 and skipped == 0:
        print("结果: 全部通过")
    elif failed == 0 and skipped > 0:
        print("结果: 部分 LLM 用例因服务不可用被跳过，其余全部通过")
    else:
        print("结果: 存在失败项，请根据上面的 FAIL 信息修复")


def main() -> None:
    """
    评测入口函数。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-llm",
        action="store_true",
        help="是否运行需要调用大模型的评测",
    )

    args = parser.parse_args()

    eval_cases = load_eval_cases()

    results: List[Optional[bool]] = []

    print("\n==============================")
    print("1. 文件存在性评测")
    print("==============================")
    results.extend(run_file_evals(eval_cases))

    print("\n==============================")
    print("2. 环境变量与模型配置评测")
    print("==============================")
    results.extend(run_env_config_evals(eval_cases))

    print("\n==============================")
    print("3. 默认数据读取与指标评测")
    print("==============================")
    results.extend(run_data_evals(eval_cases))

    print("\n==============================")
    print("4. examples 上传示例数据评测")
    print("==============================")
    results.extend(run_example_upload_evals(eval_cases))

    print("\n==============================")
    print("5. Prompt 模板文件评测")
    print("==============================")
    results.extend(run_prompt_template_evals(eval_cases))

    print("\n==============================")
    print("6. Prompt 渲染评测")
    print("==============================")
    results.extend(run_prompt_render_evals())

    print("\n==============================")
    print("7. Supervisor 工作流静态能力评测")
    print("==============================")
    results.extend(run_supervisor_static_evals(eval_cases))

    print("\n==============================")
    print("8. 报告与 Trace 导出服务评测")
    print("==============================")
    results.extend(run_report_service_evals(eval_cases))

    if args.with_llm:
        print("\n==============================")
        print("9. 合规审核 LLM 评测")
        print("==============================")
        results.extend(run_compliance_llm_evals(eval_cases))
    else:
        print("\n==============================")
        print("9. 合规审核 LLM 评测")
        print("==============================")
        print("已跳过。需要运行时请使用：python evals/run_eval.py --with-llm")

    print_summary(results)


if __name__ == "__main__":
    main()