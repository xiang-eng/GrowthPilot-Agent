import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

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


def print_eval_result(name: str, passed: bool, detail: str = "") -> None:
    """
    打印单条评测结果。
    """
    status = "PASS" if passed else "FAIL"
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


def run_file_evals(eval_cases: Dict[str, Any]) -> List[bool]:
    """
    检查关键文件是否存在。
    """
    results = []

    required_files = [
        PRODUCT_PATH,
        SALES_PATH,
        COMMENTS_PATH,
        BASE_DIR / "app" / "agents" / "sales_agent.py",
        BASE_DIR / "app" / "agents" / "insight_agent.py",
        BASE_DIR / "app" / "agents" / "content_agent.py",
        BASE_DIR / "app" / "agents" / "compliance_agent.py",
        BASE_DIR / "app" / "agents" / "supervisor_agent.py",
        BASE_DIR / "app" / "agents" / "batch_agent.py",
        BASE_DIR / "app" / "prompt_loader.py",
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


def run_data_evals(eval_cases: Dict[str, Any]) -> List[bool]:
    """
    评测默认数据读取和指标计算是否正常。
    """
    results = []

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


def run_example_upload_evals(eval_cases: Dict[str, Any]) -> List[bool]:
    """
    评测 examples/upload_samples 示例上传数据是否可用。
    """
    results = []

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


def run_prompt_template_evals(eval_cases: Dict[str, Any]) -> List[bool]:
    """
    检查 Prompt 模板文件和变量是否正常。
    """
    results = []

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


def run_prompt_render_evals() -> List[bool]:
    """
    检查 Prompt 模板是否能正常渲染。
    """
    results = []

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


def run_compliance_llm_evals(eval_cases: Dict[str, Any]) -> List[bool]:
    """
    调用合规审核 Agent，检查是否能识别高风险表达。

    注意：
        这个函数会真实调用大模型，会消耗 DashScope 额度。
    """
    from app.agents.compliance_agent import run_compliance_agent

    results = []

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
            passed = False
            detail = str(error)

        print_eval_result(
            f"合规审核 LLM 评测: {case_id}",
            passed,
            detail,
        )
        results.append(passed)

    return results


def print_summary(results: List[bool]) -> None:
    """
    打印评测汇总结果。
    """
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print("\n==============================")
    print("评测汇总")
    print("==============================")
    print(f"总检查数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {failed}")

    if failed == 0:
        print("结果: 全部通过")
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

    results = []

    print("\n==============================")
    print("1. 文件存在性评测")
    print("==============================")
    results.extend(run_file_evals(eval_cases))

    print("\n==============================")
    print("2. 默认数据读取与指标评测")
    print("==============================")
    results.extend(run_data_evals(eval_cases))

    print("\n==============================")
    print("3. examples 上传示例数据评测")
    print("==============================")
    results.extend(run_example_upload_evals(eval_cases))

    print("\n==============================")
    print("4. Prompt 模板文件评测")
    print("==============================")
    results.extend(run_prompt_template_evals(eval_cases))

    print("\n==============================")
    print("5. Prompt 渲染评测")
    print("==============================")
    results.extend(run_prompt_render_evals())

    if args.with_llm:
        print("\n==============================")
        print("6. 合规审核 LLM 评测")
        print("==============================")
        results.extend(run_compliance_llm_evals(eval_cases))
    else:
        print("\n==============================")
        print("6. 合规审核 LLM 评测")
        print("==============================")
        print("已跳过。需要运行时请使用：python evals/run_eval.py --with-llm")

    print_summary(results)


if __name__ == "__main__":
    main()