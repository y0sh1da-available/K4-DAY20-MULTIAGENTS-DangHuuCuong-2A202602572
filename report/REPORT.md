# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Đặng Hữu Cương | 2A202602572 | 100% (Thực hành cá nhân) |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: Google GenAI (`google_genai:gemini-3.5-flash-lite`), nhiệt độ: 0, `recursion_limit`: 60
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, Windows 11 (Python 3.12), chạy trực tiếp trong Virtual Environment (`.venv`)
- Số lần chạy tác vụ đã dùng / ngân sách: 0 / 18
- Commit của tag `freeze`: Chưa gắn tag (sẽ thực hiện ở Phần 4)

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

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
