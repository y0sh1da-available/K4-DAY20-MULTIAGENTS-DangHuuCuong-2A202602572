"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use this agent to inspect the workspace, read instructions, README files, "
                "docstrings, raw data formats, or log files. Delegate when you need to "
                "understand the codebase structure or diagnose errors without modifying any files."
            ),
            "system_prompt": (
                "You are an exploratory research subagent. Your role is to inspect the workspace, "
                "read relevant files, trace code logic, and accurately report findings to the coordinator. "
                "Do not modify, write, or delete any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use this agent to carry out code modifications, data cleaning transformations, "
                "file generation, and execute verification commands or tests in the workspace."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your role is to modify code, clean data, "
                "and generate requested files strictly following all requirements. "
                "Always run verification scripts or tests in the shell to ensure your changes work."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use this agent to perform independent quality checks, review generated outputs "
                "against task requirements, verify edge cases, and ensure no rules or constraints were violated."
            ),
            "system_prompt": (
                "You are a quality assurance and verification subagent. Your role is to independently "
                "inspect modified files, verify schema and formatting conventions, and test edge cases. "
                "Report any discrepancies or confirm full compliance with the specification."
            ),
        },
    ]

