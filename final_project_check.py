#一条命令检查项目是否处于可交付状态
import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


BASE_DIR = Path(__file__).resolve().parent


REQUIRED_FILES = [
    ".env.example",
    "README.md",
    "requirements.txt",
    "app/config.py",
    "app/llm.py",
    "app/data_service.py",
    "app/prompt_loader.py",
    "app/report_service.py",
    "app/agents/sales_agent.py",
    "app/agents/insight_agent.py",
    "app/agents/content_agent.py",
    "app/agents/compliance_agent.py",
    "app/agents/supervisor_agent.py",
    "app/agents/batch_agent.py",
    "app/prompts/sales_analysis_prompt.txt",
    "app/prompts/user_insight_prompt.txt",
    "app/prompts/content_strategy_prompt.txt",
    "app/prompts/compliance_prompt.txt",
    "app/prompts/batch_growth_prompt.txt",
    "data/product.csv",
    "data/sales.csv",
    "data/comments.csv",
    "examples/upload_samples/product.csv",
    "examples/upload_samples/sales.csv",
    "examples/upload_samples/comments.csv",
    "evals/eval_cases.json",
    "evals/run_eval.py",
    "frontend/streamlit_app.py",
]


PYTHON_FILES_TO_COMPILE = [
    "app/config.py",
    "app/llm.py",
    "app/data_service.py",
    "app/prompt_loader.py",
    "app/report_service.py",
    "app/agents/sales_agent.py",
    "app/agents/insight_agent.py",
    "app/agents/content_agent.py",
    "app/agents/compliance_agent.py",
    "app/agents/supervisor_agent.py",
    "app/agents/batch_agent.py",
    "evals/run_eval.py",
    "frontend/streamlit_app.py",
]


def print_section(title: str) -> None:
    """
    打印分区标题。
    """
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_check_result(
    name: str,
    passed: bool,
    detail: str = "",
) -> None:
    """
    打印单项检查结果。
    """
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")

    if detail:
        print(f"       {detail}")


def check_required_files() -> bool:
    """
    检查项目交付所需关键文件是否存在。

    返回:
        全部存在返回 True，否则返回 False。
    """
    print_section("1. 关键文件存在性检查")

    all_passed = True

    for relative_path in REQUIRED_FILES:
        file_path = BASE_DIR / relative_path
        exists = file_path.exists()

        print_check_result(
            f"文件存在检查: {relative_path}",
            exists,
        )

        if not exists:
            all_passed = False

    return all_passed


def check_env_file() -> bool:
    """
    检查 .env 文件是否存在。

    注意:
        .env 不应该上传 GitHub，但本地运行 LLM 需要它。
    """
    print_section("2. 环境变量文件检查")

    env_example_path = BASE_DIR / ".env.example"
    env_path = BASE_DIR / ".env"

    env_example_exists = env_example_path.exists()
    env_exists = env_path.exists()

    print_check_result(
        ".env.example 文件检查",
        env_example_exists,
        str(env_example_path),
    )

    print_check_result(
        ".env 文件检查",
        env_exists,
        (
            "本地存在 .env，可以运行 LLM 功能"
            if env_exists
            else "本地未发现 .env。静态评测可运行，但 LLM 调用需要先创建 .env"
        ),
    )

    return env_example_exists


def run_command(command: List[str]) -> Tuple[bool, str]:
    """
    执行命令并返回是否成功和输出内容。

    参数:
        command: 命令列表

    返回:
        passed: 命令返回码是否为 0
        output: 标准输出和错误输出合并文本
    """
    completed_process = subprocess.run(
        command,
        cwd=BASE_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = completed_process.stdout
    passed = completed_process.returncode == 0

    return passed, output


def run_python_compile_checks() -> bool:
    """
    对核心 Python 文件执行语法检查。

    返回:
        全部通过返回 True，否则返回 False。
    """
    print_section("3. Python 语法检查")

    all_passed = True

    for relative_path in PYTHON_FILES_TO_COMPILE:
        file_path = BASE_DIR / relative_path

        if not file_path.exists():
            print_check_result(
                f"语法检查跳过: {relative_path}",
                False,
                "文件不存在",
            )
            all_passed = False
            continue

        passed, output = run_command(
            [
                sys.executable,
                "-m",
                "py_compile",
                relative_path,
            ]
        )

        print_check_result(
            f"语法检查: {relative_path}",
            passed,
            output.strip(),
        )

        if not passed:
            all_passed = False

    return all_passed


def run_static_evals() -> bool:
    """
    运行静态 evals 自动化评测。

    返回:
        评测命令是否成功。
    """
    print_section("4. 静态 evals 自动化评测")

    passed, output = run_command(
        [
            sys.executable,
            "evals/run_eval.py",
        ]
    )

    print(output)

    print_check_result(
        "静态 evals 命令检查",
        passed,
        "python evals/run_eval.py",
    )

    return passed


def run_llm_evals() -> bool:
    """
    运行带 LLM 的 evals 自动化评测。

    返回:
        评测命令是否成功。
    """
    print_section("5. 带 LLM 的 evals 自动化评测")

    passed, output = run_command(
        [
            sys.executable,
            "evals/run_eval.py",
            "--with-llm",
        ]
    )

    print(output)

    print_check_result(
        "带 LLM evals 命令检查",
        passed,
        "python evals/run_eval.py --with-llm",
    )

    return passed


def print_final_summary(results: List[Tuple[str, bool]]) -> None:
    """
    打印最终检查汇总。
    """
    print_section("最终交付检查汇总")

    total = len(results)
    passed_count = sum(passed for _, passed in results)
    failed_count = total - passed_count

    for name, passed in results:
        print_check_result(name, passed)

    print("\n汇总：")
    print(f"总检查项: {total}")
    print(f"通过项: {passed_count}")
    print(f"失败项: {failed_count}")

    if failed_count == 0:
        print("\n结果: 项目当前处于可交付状态")
    else:
        print("\n结果: 项目仍存在问题，请先修复 FAIL 项")


def main() -> None:
    """
    项目最终交付检查入口。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-llm",
        action="store_true",
        help="是否运行需要真实调用大模型的 evals",
    )

    args = parser.parse_args()

    results: List[Tuple[str, bool]] = []

    required_files_passed = check_required_files()
    results.append(("关键文件存在性检查", required_files_passed))

    env_check_passed = check_env_file()
    results.append(("环境变量文件检查", env_check_passed))

    compile_passed = run_python_compile_checks()
    results.append(("Python 语法检查", compile_passed))

    static_evals_passed = run_static_evals()
    results.append(("静态 evals 自动化评测", static_evals_passed))

    if args.with_llm:
        llm_evals_passed = run_llm_evals()
        results.append(("带 LLM 的 evals 自动化评测", llm_evals_passed))
    else:
        print_section("5. 带 LLM 的 evals 自动化评测")
        print("已跳过。需要运行时请使用：python final_project_check.py --with-llm")

    print_final_summary(results)


if __name__ == "__main__":
    main()