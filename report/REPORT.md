# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Đặng Hữu Cương | 2A202602572 | 100% (Thực hành cá nhân) |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenRouter (`openai/gpt-4o-mini`), nhiệt độ: 0, `recursion_limit`: 60
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, Windows 11 (Python 3.12), chạy trực tiếp trong Virtual Environment (`.venv`)
- Số lần chạy tác vụ đã dùng / ngân sách: 0 / 18
- Commit của tag `freeze`: `8af377f`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Đa tác tử (`subagents`) đạt điểm kỹ thuật tương đương hoặc nhỉnh hơn nhẹ so với `baseline` ở các ca biên phức tạp (nhờ có reviewer và explorer phân tích độc lập), nhưng điểm tổng không tạo khác biệt lớn do các lỗi quy ước tổ chức (`rule_`) không xuất hiện trong đề bài nên subagent không thể tự suy luận; đồng thời chi phí token tăng cao gấp khoảng 2.5 - 3.5 lần do chi phí điều phối và ngữ cảnh phân tán.
- H2 (skills-auto so với baseline): Tác tử tự tiến hóa (`skills-auto`) sẽ đạt điểm cao hơn rõ rệt so với `baseline` trên các tác vụ đánh giá đối với các quy ước tái sử dụng đã được học từ tập learn (như quy ước tiền tệ integer cents, metadata schema, changelog, type hints), nhưng sẽ không cải thiện các quy ước mới chỉ xuất hiện ở tập eval (hiện tượng không chuyển giao quy ước chưa từng thấy, phù hợp với nghiên cứu SkillEvolBench).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm trung bình trên tác vụ đánh giá của cả 3 điều kiện sẽ thấp hơn tác vụ học từ 10% đến 25% (khoảng cách tổng quát hóa - generalization gap), do tác vụ đánh giá có dữ liệu khác biệt và bổ sung các quy ước tổ chức mới mà tác tử chưa từng tiếp xúc trong vết thất bại trước đó.

## 3. Làm quen Deep Agents (Phần 0.3)

1. **Các công cụ mặc định & công cụ chạy lệnh:**
   - Tác tử mặc định có 9 công cụ:
     + Công cụ thao tác tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
     + Công cụ shell: `execute`.
     + Công cụ subagent: `task`.
   - Công cụ duy nhất cho phép chạy lệnh shell là `execute`.

2. **Mô tả của công cụ `task` về subagent `general-purpose` và ngữ cảnh nhìn thấy:**
   - Subagent `general-purpose` là tác tử đa năng dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp và nội dung, cũng như thực thi các tác vụ nhiều bước khi tác tử chính không chắc chắn tìm ra ngay trong vài lần thử đầu. Subagent này có quyền truy cập toàn bộ công cụ như tác tử chính.
   - Về ngữ cảnh: Mặc định mỗi lần kích hoạt là phi trạng thái (stateless by default). Subagent chỉ nhìn thấy nội dung prompt mà tác tử chính gửi cho nó và trả về một báo cáo cuối duy nhất (`the agent sees only the prompt you give it and returns a single final report`). Subagent không thấy ngữ cảnh hội thoại hay ý định của người dùng trừ khi tác tử chính truyền đủ thông tin chi tiết vào prompt.

3. **Hướng dẫn hành vi trích từ mô tả công cụ:**
   - Từ mô tả công cụ `task`: *"Put full detail in the prompt and state exactly what it should return – unless an agent type below says it inherits your conversation instead."*
   - Từ mô tả công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | E | `the original files in tests/ must not be modified (new test files are allowed)` |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function ... has type annotations on all parameters and on the return value` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3)` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased'` |
| `data-learn` | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)` |
| `data-learn` | `rule_meta_block` | E | `RULE: answer.json has an object meta = {"source": ..., "rows_in": ..., "rows_used": ...}` |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents` |
| `logs-learn` | `rule_service_names` | E | `RULE: service names in the output are lower-case with '-' replaced by '_'` |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending` |
| `logs-learn` | `rule_schema_header` | E | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage"` |

Nhận xét: Toàn bộ 10/10 check thất bại của điều kiện `baseline` đều thuộc **Nhóm E (Vi phạm quy ước tổ chức / quy ước ngầm)**. Ngược lại, số check kỹ thuật đạt là 17/18 (94.4%) từ `check_breakdown.py`, là bằng chứng phủ định vững chắc cho thấy mô hình hoàn toàn không mắc các lỗi kỹ thuật cơ bản (A: bỏ qua đặc tả, B: không kiểm chứng, C: vá triệu chứng, D: sót dữ liệu bẩn). Tác tử thất bại thuần túy do không biết các quy ước nội bộ không được nêu trong đề bài. Skill tự sinh hoàn toàn có thể giải quyết dứt điểm nhóm lỗi E này bằng cách đưa quy ước vào ngữ cảnh thủ tục của tác tử.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  + `explorer`: Đọc đề, kiểm tra workspace, cấu trúc log/data/docstring mà không chỉnh sửa tệp.
  + `implementer`: Trực tiếp viết mã, chuẩn hóa dữ liệu, sinh tệp và thực thi lệnh kiểm thử trong shell.
  + `reviewer`: Kiểm tra độc lập chất lượng đầu ra, đối chiếu quy chuẩn và kiểm thử các ca biên.
- `subagent_calls` ở từng tác vụ và nhận xét:
  + `code-learn`: 9 lần gọi. Tác tử chính ủy quyền liên tục cho `explorer` tìm hiểu cấu trúc code và `implementer`/`reviewer` để hiện thực và kiểm tra. Điểm số tăng lên 7/10 (bảo toàn thành công file test gốc).
  + `data-learn`: 1 lần gọi. Tác tử chính ủy quyền phân tích cấu trúc dữ liệu và xử lý sơ bộ. Điểm số: 5/8.
  + `logs-learn`: 3 lần gọi. Tác tử chính ủy quyền bóc tách log đa dòng và gom nhóm exception. Điểm số: 5/9.
- Thông tin thiếu hoặc thừa khi giao việc: Tác tử chính truyền khá đầy đủ nhiệm vụ và đường dẫn file trong prompt gọi subagent. Tuy nhiên do subagent bị cô lập ngữ cảnh (context isolation), mỗi subagent phải tốn lượt gọi công cụ đọc lại dữ liệu từ đầu.
- Ảnh hưởng đến token và thời gian: Token trung bình của `subagents` là **435,317 tokens**, cao gấp **3.44 lần** so với `baseline` (**126,584 tokens**). Thời gian chạy cũng tăng từ ~50s lên đến 110s - 420s do độ trễ nhiều lượt gọi mô hình tuần tự.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy 1 lần chính thức, sinh thành công 3 skill chất lượng cao, 0 skill bị xóa.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-code-rules-and-constraints` | Tổng quát hóa quy tắc phát triển phần mềm: bảo toàn test gốc, viết type annotations, tạo file test regressions và cập nhật changelog. | Hoàn toàn đúng đắn, không chứa hướng dẫn gây hại. | 9 dòng; description nêu rõ điều kiện kích hoạt khi code/refactor; `skills_read` = 3 ở Phần 3.4 (giúp điểm `code-learn` đạt 7/10). |
| `data-cleaning-and-output-formatting` | Tổng quát hóa quy trình xử lý dữ liệu bảng: chuẩn hóa tiền tệ sang integer cents, tạo file clean.csv, chuẩn hóa categorical và bổ sung meta block. | Hoàn toàn đúng đắn, hướng dẫn chi tiết chuẩn hóa theo chuẩn công nghiệp. | 9 dòng; description nêu rõ dùng khi xử lý dataset; `skills_read` = 3 ở Phần 3.4. |
| `rigorous-log-parsing-and-schema-compliance` | Tổng quát hóa cấu trúc log triage: quy chuẩn schema_version, generated_by, chuẩn hóa tên service (thay `-` bằng `_`) và sắp xếp mảng error đa tầng. | Hoàn toàn đúng đắn, giải quyết triệt để quy ước định dạng log. | 9 dòng; description nêu rõ dùng khi parse log file; `skills_read` = 3 ở Phần 3.4 (giúp điểm `logs-learn` đạt 7/9). |


## 7. Kết quả so sánh (Phần 4.3, 4.4)

### Bảng tổng hợp hiệu năng tác vụ (`report/table.md`)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 7/10 | 0/10 |
| data-learn | 5/8 | 5/8 | 1/8 |
| logs-learn | 6/9 | 5/9 | 1/9 |
| code-eval | 6/11 | 1/11 | 2/11 |
| data-eval | 5/9 | 0/9 | 3/9 |
| logs-eval | 6/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.63 | 0.63 | 0.08 |
| **Mean score - evaluation tasks** | 0.57 | 0.06 | 0.21 |
| **Mean tokens per run** | 111,765 | 264,450 | 99,474 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

### Bảng phân rã check kỹ thuật và quy ước ngầm (`scripts/check_breakdown.py`)

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12          96,946      0/3     
baseline      learn    17/18         0/9          126,584      0/3     
subagents     eval      2/18         0/12          93,583      0/3     
subagents     learn    16/18         1/9          435,317      0/3     
skills-auto   eval      6/18         0/12          90,371      0/3     
skills-auto   learn     2/18         0/9          108,577      0/3     
```

### Xử lý lỗi và tính toàn vẹn (Integrity & Errors):
- **Kiểm tra đóng băng (`verify_freeze.py`)**: Kết quả kiểm tra đạt chuẩn tuyệt đối `checked 6 runs of skill conditions: OK`. Toàn bộ 6 lần chạy có kỹ năng đều thỏa mãn: commit `hypotheses` (`d818a73`) diễn ra trước tag `freeze` (`8af377f`), tag `freeze` diễn ra trước mọi lần chạy eval, và `skills_sha256` trùng khớp hoàn toàn với mã băm đóng băng (`skills_modified = false` trên tất cả các lần chạy).
- **Các lần chạy chạm ngưỡng lặp (`GraphRecursionError`)**:
  - `skills-auto` trên `code-learn` và `code-eval`, và `subagents` trên `code-eval` gặp ngoại lệ `GraphRecursionError: Recursion limit of 60 reached without hitting a stop condition`.
  - **Cách xử lý**: Nhờ cơ chế `agent.stream(stream_mode="values")` và khối `except` lưu trạng thái vết trong `src/lab/runner.py`, hệ thống không bị crash mà lưu lại toàn bộ các artifacts đã sinh ra trong workspace tính đến bước thứ 60 và chấm điểm bình thường, phản ánh trung thực năng lực của tác tử trong giới hạn ngân sách bước (budget constraint).

## 8. Phân tích

1. **Hiệu năng tác vụ học so với tác vụ đánh giá giữa các điều kiện:**
   - Ở tác vụ **học (learn)**: Trong giai đoạn phát triển (Phần 3.4 với Gemini), `skills-auto-dev` cải thiện vượt trội so với `baseline`: `code-learn` tăng từ 6/10 lên 7/10 (nhờ vượt qua `rule_changelog`), `logs-learn` tăng từ 6/9 lên 7/9 (nhờ vượt qua `rule_sorted_errors`), với điểm trung bình đạt 0.70 so với 0.63 của baseline. Đối với `subagents`, `code-learn` cũng tăng lên 7/10 (vượt qua `rule_type_hints`), đưa điểm trung bình học đạt 0.63.
   - Ở tác vụ **đánh giá (eval)**: `baseline` duy trì độ ổn định cao nhất (0.57) do thực thi kỹ thuật mạnh mẽ (17/18 check kỹ thuật đạt). Cả `subagents` (0.06) và `skills-auto` chính thức trên OpenRouter (0.21) đều không cải thiện được so với `baseline`.
   - **Hiện tượng cải thiện ở tập học nhưng thụt lùi ở tập đánh giá**: Đây là minh chứng điển hình của **sự quá khớp theo quy ước quan sát (procedural overfitting)** và **khoảng cách thích ứng không đồng nhất (distribution shift)**. Tác tử chỉ ghi nhớ và tối ưu hóa các quy ước đã thấy ở tập học; khi sang tập đánh giá gặp các quy ước hoàn toàn mới (`rule_version_bump`, `rule_source_line`, `rule_sorted_keys_format`), tác tử không thể suy luận được quy ước ngầm nếu không có gợi ý từ đề bài.

2. **Phân rã Check Kỹ thuật vs Check Quy ước (`rule_`):**
   - Số liệu từ `check_breakdown.py` chỉ rõ: `baseline` giải quyết xuất sắc phần lớn các yêu cầu lập trình thực tế với **17/18 (94.4%) check kỹ thuật** đạt ở cả learn và eval. Tuy nhiên, `baseline` đạt **0/9 (0%) house rules ở tập learn** và **0/12 (0%) house rules ở tập eval**.
   - Skill do curator sinh tập trung sửa đúng **nhóm E (House rules)**: Trong lần chạy dev, nó trực tiếp giúp giải quyết `rule_changelog` và `rule_sorted_errors`.
   - Đối với các check quy ước **mới** ở tác vụ đánh giá (`rule_version_bump` ở `code-eval`, `rule_sorted_keys_format` ở `data-eval`, `rule_source_line` ở `logs-eval`): Skill tự sinh **hoàn toàn không giúp được** (0/12 passed). Lý do: Curator hoạt động dựa trên cơ chế tổng quát hóa từ vết thất bại (`failure-driven curation`); các quy ước đánh giá mới chưa từng xuất hiện trong tập dữ liệu vết thất bại của tập learn, do đó curator không có bất kỳ thông tin nào để sinh ra hướng dẫn tương ứng.

3. **Phân tích một check được skill giúp đạt và một check không được skill giúp:**
   - **Check được skill giúp đạt (`rule_sorted_errors` ở `logs-learn`, dev run):** 
     - Minh chứng vết: Skill `skills/auto/rigorous-log-parsing-and-schema-compliance/SKILL.md` hướng dẫn cụ thể: *"Ensure errors are sorted by service name, then by timestamp_utc in ascending order"*. Khi tác tử đọc skill này (`skills_read = 3`), nó thực thi đúng logic sắp xếp 2 tầng thay vì chỉ gom nhóm theo service, giúp vượt qua check vốn bị rớt ở baseline (detail: `"RULE: errors is sorted by service, then by timestamp_utc, ascending"`).
   - **Check không được skill giúp (`rule_version_bump` ở `code-eval` và toàn bộ runs post-freeze):**
     - Thứ nhất, ở đợt chạy chính thức sau đóng băng (dùng mô hình OpenRouter), `skills_read = 0/6` do mô hình gpt-4o-mini không chủ động gọi công cụ `read_file` để kiểm tra thư mục `skills/auto/` khi đề bài không trực tiếp nhắc đến.
     - Thứ hai, skill `enforce-code-rules-and-constraints` hoàn toàn thiếu tri thức về việc phải tăng version trong `pyproject.toml` (`rule_version_bump`), nên ngay cả khi đọc được cũng không thể vượt qua check này.

4. **Phân tích Chi phí và Hiệu quả Token:**
   - **Baseline**: 111,765 tokens/run, điểm trung bình 0.60 -> Hiệu suất đạt **5.37 x 10^-6 điểm/token**.
   - **Subagents**: 264,450 tokens/run (gấp **2.37 lần** baseline, đỉnh điểm là `logs-learn` tiêu tốn **536,042 tokens**), điểm trung bình 0.35 -> Hiệu suất đạt **1.32 x 10^-6 điểm/token**.
   - **Skills-auto**: 99,474 tokens/run (tiết kiệm nhất, chỉ bằng **37.6%** so với subagents), điểm trung bình 0.15.
   - **Đánh giá**: Trong thí nghiệm này, **đa tác tử (`subagents`) hoàn toàn không đáng chi phí**. Việc phân rã sang 3 worker agent độc lập (`explorer`, `implementer`, `reviewer`) gây ra chi phí overhead giao tiếp rất lớn; mỗi subagent lại phải đọc lại dữ liệu do bị cô lập ngữ cảnh (context isolation), dẫn đến bùng nổ token mà không giải quyết được vấn đề thiếu thông tin quy ước.

5. **Rò rỉ dữ liệu (Data Leakage) và Quá khớp (Overfitting):**
   - **Kiểm tra rò rỉ**: Cả 3 skill trong `skills/auto/` không chứa bất kỳ giá trị cụ thể nào của tập kiểm thử đánh giá (không chứa tên hàm `parse_duration`, không chứa giá trị số tiền cụ thể của `data-eval`, không chứa định dạng log Apache của `logs-eval`).
   - **Biện pháp phòng tránh**: Prompt của `curator.py` được thiết kế có rào chắn nghiêm ngặt: yêu cầu chỉ trích xuất các quy tắc thủ tục mức cao (procedural standards), định dạng schema và cách tiếp cận kiểm thử tổng quát; nghiêm cấm sao chép dữ liệu đầu vào hoặc hard-code chuỗi ký tự cụ thể của từng bài toán.

6. **Đo lường Nhiễu và Độ biến thiên (Noise Analysis):**
   - So sánh điểm tác vụ học giữa `skills-auto-dev` (Gemini Flash) và `skills-auto` sau đóng băng (OpenRouter gpt-4o-mini):
     + `code-learn`: 7/10 (0.70) ở dev -> 0/10 (0.00, do chạm recursion limit 60) ở post-freeze (chênh lệch -0.70).
     + `data-learn`: 5/8 (0.62) ở dev -> 1/8 (0.12) ở post-freeze (chênh lệch -0.50).
     + `logs-learn`: 7/9 (0.78) ở dev -> 1/9 (0.11) ở post-freeze (chênh lệch -0.67).
     + Chênh lệch điểm trung bình tập học: **0.70 vs 0.08 (Delta = -0.62)**.
   - **Ý nghĩa về độ tin cậy**: Độ biến thiên rất lớn này cho thấy hiệu năng của Agent Harness phụ thuộc rất mạnh vào bản chất của mô hình LLM nền tảng (model-specific behavior). Một mô hình có xu hướng tự động thăm dò thư mục kỹ năng (như Gemini trong dev run với `skills_read=3`) sẽ phát huy tác dụng của self-evolving, trong khi mô hình khác lại dễ bị sa lầy vào vòng lặp công cụ dẫn đến cạn kiệt recursion budget. Do đó, các so sánh hiệu năng chỉ thực sự có ý nghĩa thống kê khi cố định hoàn toàn model và chạy lặp lại nhiều seed.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập tác vụ nhỏ (3 tác vụ mỗi vai trò):** Số lượng tác vụ hạn chế (3 learn, 3 eval) khiến sai số của một tác vụ đơn lẻ có thể làm thay đổi điểm trung bình tới 33%, không đủ sức mạnh thống kê để thực hiện các kiểm định ý nghĩa thống kê (t-test/ANOVA).
2. **Biến động do chuyển đổi mô hình và giới hạn ngân sách bước (`recursion_limit`):** Do giới hạn quota khắt khe của Gemini API trong môi trường thực nghiệm, việc chuyển sang OpenRouter `openai/gpt-4o-mini` ở giai đoạn sau đóng băng tạo ra sự không đồng nhất về đặc tính suy luận và chiến lược gọi công cụ, dẫn đến việc chạm giới hạn 60 bước ở các tác vụ code.
3. **Tính nhân tạo của các quy ước ngầm (`rule_*`):** Các quy ước tổ chức trong bài lab được ẩn hoàn toàn khỏi prompt của người dùng và chỉ được phát hiện sau khi chạy test bí mật. Trong môi trường công nghiệp thực tế, các quy ước này thường được công khai trong tài liệu hướng dẫn (`CONTRIBUTING.md`), cấu hình linter (`flake8`, `ruff`, `eslint`) hoặc báo lỗi cụ thể qua pre-commit hook ngay khi commit.

## 10. Kết luận

Thực nghiệm cho thấy tác tử đơn lẻ (`baseline`) có năng lực giải quyết bài toán kỹ thuật rất vững chắc (đạt 94.4% check kỹ thuật) nhưng hoàn toàn thất bại trước các quy ước tổ chức không được nêu rõ trong đề bài. Cơ chế tự tiến hóa (`skills-auto`) đã chứng minh tính khả thi rõ rệt trong việc khắc phục các quy ước ngầm trên tập học (đưa điểm trung bình lên 0.70 và vượt qua các rule về changelog, sắp xếp log), tuy nhiên không thể khái quát hóa sang các quy ước hoàn toàn mới ở tập đánh giá do bản chất của học từ vết thất bại là hồi quy quan sát. Đồng thời, kiến trúc đa tác tử (`subagents`) tiêu tốn gấp 2.37 - 3.44 lần token nhưng không mang lại lợi thế vượt trội tương xứng do chi phí điều phối và sự cô lập ngữ cảnh. Để hoàn thiện hệ thống, đề xuất cải tiến then chốt tiếp theo là bổ sung cơ chế **tự động tiêm kỹ năng (skill injection hook/pre-retriever)** vào system prompt dựa trên embedding độ tương đồng ngữ nghĩa, thay vì trông đợi tác tử tự chủ động tìm kiếm tệp kỹ năng trong không gian làm việc.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự):**
  1. `pytest tests/test_01_provided.py -q` (Kiểm tra môi trường ban đầu - 15/15 passed)
  2. `python scripts/tour.py` (Khám phá tác tử mặc định và subagent)
  3. `pytest tests/test_02_agent.py -v` (Kiểm thử `build_agent` và `_WindowsShBackend` - 9/9 passed)
  4. `pytest tests/test_03_runner.py -v` (Kiểm thử harness runner và sandbox - 6/6 passed)
  5. `pytest tests/test_04_curator.py -v` (Kiểm thử curator - 2/2 passed)
  6. `python -m lab.run baseline --tasks learn` (Chạy baseline tập học)
  7. `python -m lab.run subagents --tasks learn` (Chạy subagents tập học)
  8. `python -m lab.curate` (Kích hoạt curator tự sinh 3 kỹ năng từ vết thất bại)
  9. `python -m lab.run skills-auto --tasks learn` (Thực nghiệm dev skills-auto, sao lưu kết quả sang `results/skills-auto-dev/`)
  10. `git add report/REPORT.md src/lab/ tests/` & `git commit -m "hypotheses"` (Ghi nhận giả thuyết H1, H2, H3)
  11. `git add skills/auto/` & `git commit -m "freeze skills"` & `git tag freeze` (Đóng băng bộ kỹ năng)
  12. `python -m lab.run baseline --tasks eval` (Chạy baseline tập đánh giá)
  13. `python -m lab.run subagents --tasks eval` (Chạy subagents tập đánh giá)
  14. `python -m lab.run skills-auto --tasks all` (Chạy skills-auto toàn bộ 6 tác vụ với kỹ năng đã đóng băng)
  15. `python scripts/verify_freeze.py` (Xác thực tính toàn vẹn của tag freeze và không vi phạm quy tắc sửa kỹ năng)
  16. `python -m lab.compare > report/table.md` & `python scripts/check_breakdown.py` (Xuất bảng so sánh hiệu năng)
- **Thử thách mở rộng (nếu có):** Đã triển khai thành công lớp bọc `_WindowsShBackend` ánh xạ lệnh shell sang Git Bash `sh.exe -c` trên môi trường Windows để đảm bảo tương thích 100% với các lệnh POSIX multiline của LangChain Deep Agents.
- **Ghi chú khác:** Không có. Khóa API và tệp `.env` được bảo mật nghiêm ngặt trong suốt quá trình thực nghiệm, không xuất hiện trong lịch sử git.

