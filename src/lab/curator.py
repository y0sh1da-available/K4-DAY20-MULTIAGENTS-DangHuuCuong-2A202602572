"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    if out_dir is None:
        target_dir = ROOT / "skills" / "auto"
    else:
        target_dir = Path(out_dir)

    results_path = Path(results_dir) / source_condition
    if not results_path.exists():
        print(f"Warning: results path '{results_path}' does not exist.")
        return []

    runs = []
    for run_file in sorted(results_path.glob("*/run.json")):
        try:
            data = json.loads(run_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        if data.get("role") != "learn":
            continue

        trace_file = run_file.parent / "trace.md"
        trace_tail = ""
        if trace_file.exists():
            trace_tail = trace_file.read_text(encoding="utf-8")[-6000:]

        failed_checks = []
        for c in data.get("checks", []):
            if not c.get("passed", False):
                failed_checks.append({
                    "name": c.get("name", ""),
                    "detail": c.get("detail", ""),
                })

        if failed_checks:
            runs.append({
                "task": data.get("task", run_file.parent.name),
                "failed_checks": failed_checks,
                "trace": trace_tail,
            })

    if not runs:
        print("Warning: Không có check thất bại ở tác vụ học.")
        return []

    # Format failures for prompt
    blocks = []
    for r in runs:
        checks_text = "\n".join(f"  - Check failed: {c['name']} | Feedback: {c['detail']}" for c in r["failed_checks"])
        blocks.append(
            f"### Task: {r['task']}\n"
            f"Failed checks:\n{checks_text}\n"
            f"Trace excerpt:\n{r['trace']}\n"
        )
    runs_formatted = "\n".join(blocks)

    prompt = (
        f"You are writing reusable SKILL manuals for an engineering coding and data agent.\n"
        f"Below are failed checks (check names and evaluation feedback) and traces from learning runs.\n"
        f"Identify common procedural mistakes and write at most {max_skills} concise skills to prevent them on new tasks.\n\n"
        f"Rules:\n"
        f"- Skills must be general: do not mention specific task IDs, file names specific to one task, or specific solutions/numbers.\n"
        f"- Each skill must have YAML frontmatter with `name` (lowercase alphanumeric and hyphens) and `description` (one sentence: WHEN to use it).\n"
        f"- Body instructions must be at most 40 lines (an imperative checklist works best).\n"
        f"- Output format strictly as:\n"
        f"=== SKILL: <name> ===\n"
        f"---\n"
        f"name: <name>\n"
        f"description: <when to use>\n"
        f"---\n"
        f"<body checklist>\n"
        f"=== END ===\n\n"
        f"{runs_formatted}"
    )

    llm = model or make_model()
    response = llm.invoke(prompt)
    reply_content = response.content if hasattr(response, "content") else str(response)

    written = []
    for name, skill_text in parse_skill_blocks(reply_content):
        if len(written) >= max_skills:
            break
        issues = validate_skill(skill_text, expected_name=name)
        if issues:
            continue
        skill_dir = target_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(skill_text + "\n", encoding="utf-8")
        written.append(skill_path)

    return written



if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
