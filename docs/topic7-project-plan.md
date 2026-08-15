# Kế hoạch thực hiện đồ án Chủ đề 7

Tài liệu này triển khai từ [đặc tả đồ án](topic7-project-spec.md). Kế hoạch mặc định cho nhóm 4 người trong 4 tuần. Nếu nhóm có 3 người, gộp vai trò **Experiment Engineer** và **Mutation/Data Engineer**, nhưng vẫn phải giữ độc lập giữa người/phiên sinh implementation với người/phiên viết acceptance oracle.

## 1. Kết quả cuối cùng

Nhóm phải bàn giao ba nhóm artifact:

1. **Bài luận:** PDF 12–18 trang, font 13, đúng 7 mục bắt buộc của đề cương và có phụ lục bằng chứng.
2. **Slide:** tối đa 15 trang, thuyết trình 15 phút và chuẩn bị 5 phút hỏi đáp.
3. **Repository bằng chứng:** mã nguồn của các AI run, test AI-only, test độc lập, transcript, metadata, coverage/mutation logs, CSV, biểu đồ và script tái lập.

Kết luận của đồ án phải được rút ra từ dữ liệu, không được viết trước rằng AI chắc chắn thất bại. Nếu không quan sát được “test giả mạnh”, nhóm báo cáo trung thực và phân tích vì sao thiết kế chưa tạo được hiện tượng đó.

## 2. Phân công vai trò

| Mã | Vai trò | Trách nhiệm chính | Hạn chế để tránh thiên lệch |
|---|---|---|---|
| M1 | Research Lead / Requirement Owner | Chốt RQ, oracle, tài liệu tham khảo, biên tập report | Không sửa oracle sau khi đã xem kết quả |
| M2 | Experiment Engineer / AI Operator | Scaffold project, chạy 6 phiên AI, lưu transcript, chạy baseline tests | Không được xem hidden oracle trước khi khóa toàn bộ AI run |
| M3 | Independent Verification Engineer | Review oracle, viết acceptance/property tests độc lập | Không xem implementation và tests AI trước khi khóa independent tests |
| M4 | Mutation & Data Engineer | Chạy coverage/mutation, review mutants, tạo CSV/biểu đồ | Không tự loại equivalent mutant mà không có reviewer |

Cross-review bắt buộc:

- M1 và M3 cùng ký duyệt oracle.
- M2 và M4 review script tái lập thí nghiệm.
- M1 review phân loại mutant của M4.
- Cả nhóm review report, nhưng chỉ một người làm final editor để giữ văn phong nhất quán.

## 3. Quy tắc bảo toàn thí nghiệm

Các quy tắc này áp dụng từ đầu đến cuối:

1. Freeze prompt mơ hồ và oracle trước AI run đầu tiên.
2. Phiên AI sinh code/test chỉ nhận đúng prompt mơ hồ, không được truy cập toàn repository.
3. Hidden oracle được giữ ở private branch/archive riêng cho tới khi hoàn tất toàn bộ AI run. Không đặt oracle trong working directory mà coding agent có quyền đọc.
4. Mỗi run dùng context sạch; không copy câu trả lời từ run trước.
5. Chỉ dùng câu follow-up chuẩn nếu AI hỏi làm rõ: `Proceed with reasonable assumptions and record every assumption in ASSUMPTIONS.md.`
6. Lưu raw response trước khi chuyển thành file.
7. Không sửa business logic hoặc expected value do AI sinh. Mọi packaging-only fix phải có patch riêng và lý do.
8. Independent verifier chỉ xem oracle và public function signature; không xem candidate code/test cho tới khi test độc lập đã được khóa.
9. Mọi số trong report phải truy ngược được về file CSV/log/transcript.
10. Ghi rõ mọi công cụ AI đã dùng, phần việc, model hiển thị và thời điểm sử dụng.

## 4. Mốc tổng thể

| Tuần | Mục tiêu | Exit gate |
|---|---|---|
| Tuần 1 | Khóa thiết kế nghiên cứu, oracle, môi trường và biểu mẫu dữ liệu | Có preregistration/oracle đã ký duyệt và dry-run thành công |
| Tuần 2 | Hoàn tất 6 AI run và baseline measurements | Mỗi run có code, tests, transcript, assumptions, pytest và coverage log |
| Tuần 3 | Hoàn tất independent tests và mutation testing | Có kết quả AI-only/full-suite và review survivor/equivalent |
| Tuần 4 | Phân tích, viết report, làm slide và rehearsal | Tái lập được kết quả, report/slide đúng giới hạn và traceable |

## 5. Kế hoạch chi tiết

### Tuần 1 — Thiết kế và chuẩn bị

#### Ngày 1: Kickoff và khóa phạm vi

Người phụ trách: M1; cả nhóm tham gia.

Việc cần làm:

- Đọc đề cương môn học và project spec.
- Chốt 3 câu hỏi nghiên cứu.
- Chọn cấu hình thí nghiệm khuyến nghị: 2 công cụ/mô hình × 3 run = 6 run.
- Chốt một phiên bản Python cho cả nhóm.
- Tạo task board với các cột `Backlog`, `In progress`, `Review`, `Done`.
- Tạo risk log và decision log.

Đầu ra:

- `docs/research-questions.md`
- `docs/decisions.md`
- `docs/risks.md`
- bảng phân công có tên thành viên thật.

Điều kiện hoàn thành: không còn thay đổi về bài toán, public interface, số run và cách follow-up AI.

#### Ngày 2: Viết và freeze oracle

Người phụ trách: M1 viết; M3 review.

Việc cần làm:

- Viết `spec/ambiguous-requirement.md` đúng nguyên văn prompt.
- Viết `spec/acceptance-oracle.md` gồm input contract, thứ tự tính, rounding, exception và acceptance table.
- Chốt expected exception cụ thể: đề xuất `TypeError` cho sai kiểu, `ValueError` cho số nguyên không dương.
- Viết trước danh sách điểm mơ hồ mà nhóm sẽ chấm AI có phát hiện hay không.
- Hash/commit tài liệu để chứng minh oracle có trước kết quả.
- Chuyển oracle sang vị trí M2 và coding AI không thể đọc.

Đầu ra:

- oracle version `v1.0` có chữ ký/review record;
- commit hash hoặc SHA-256;
- `experiments/ambiguity-rubric.csv`.

Điều kiện hoàn thành: M1 và M3 cùng xác nhận oracle đủ rõ để tính duy nhất một kết quả cho mọi input trong contract.

#### Ngày 3: Scaffold và data contract

Người phụ trách: M2; M4 review.

Việc cần làm:

- Tạo repository Python với `pyproject.toml`, lockfile và Python version pin.
- Cài `pytest`, `pytest-cov`, `hypothesis`, `mutmut`, `ruff`.
- Tạo đủ thư mục trong project spec.
- Thiết kế adapter/runner để cùng một independent test suite chạy trên từng candidate.
- Tạo script chạy baseline, coverage, independent tests và mutation.
- Tạo schemas cho metadata và measurements.

`metadata.csv` tối thiểu có các cột:

```text
run_id,tool,model_displayed,started_at,ended_at,context_clean,
clarification_asked,ambiguities_detected,followup_used,human_edits,
raw_response_path,transcript_path,operator
```

`measurements.csv` tối thiểu có các cột:

```text
run_id,ai_tests_collected,ai_tests_passed,line_coverage,branch_coverage,
acceptance_passed,acceptance_total,properties_failed,
mutants_total_ai,killed_ai,survived_ai,timeout_ai,error_ai,equivalent_ai,
mutants_total_full,killed_full,survived_full,timeout_full,error_full,equivalent_full,
raw_score_ai,adjusted_score_ai,raw_score_full,adjusted_score_full
```

Điều kiện hoàn thành: một dummy candidate có thể đi qua toàn bộ pipeline và sinh log/CSV; kết quả dummy không được đưa vào dataset chính.

#### Ngày 4–5: Literature review song song

Người phụ trách: M1 điều phối; mỗi thành viên tìm ít nhất 2 nguồn.

Nhóm nguồn cần có:

- oracle problem và test oracle;
- AI-generated unit tests hoặc self-confirming errors;
- property-based testing;
- mutation testing và equivalent mutant problem;
- human-in-the-loop hoặc separation of duties;
- bối cảnh sử dụng AI trong kỹ nghệ phần mềm.

Quy tắc nguồn:

- tối thiểu 8 nguồn cuối cùng;
- ít nhất 3 nguồn học thuật hoặc khảo sát quy mô lớn;
- ưu tiên paper gốc, tài liệu chính thức và DOI/URL truy cập được;
- không trích dẫn con số từ bản tóm tắt do AI tạo mà chưa mở nguồn gốc;
- lưu citation, claim được hỗ trợ, trang/section và người kiểm tra.

Đầu ra: `report/evidence-matrix.csv` và thư viện citation dùng chung.

### Tuần 2 — Chạy AI và đo baseline

#### Ngày 6: Pilot quy trình

Người phụ trách: M2; M4 quan sát.

- Pilot bằng một bài toán khác hoặc một prompt giả, không dùng prompt chính.
- Kiểm tra cách lưu timestamp, raw response, transcript, model metadata và packaging patch.
- Kiểm tra runner không vô tình đưa hidden oracle vào context.
- Sau pilot, khóa version của protocol; không tính pilot vào kết quả.

Exit gate: hai người có thể làm lại quy trình từ checklist mà không cần quyết định tùy hứng.

#### Ngày 7–8: Thực hiện 6 AI run

Người phụ trách: M2.

Cho từng `run-01` đến `run-06`:

1. Mở context sạch.
2. Ghi tool/model/time.
3. Gửi đúng prompt đã freeze.
4. Nếu AI hỏi, đánh dấu `clarification_asked=yes`, chấm ambiguity rubric, rồi gửi follow-up chuẩn.
5. Nếu AI không hỏi, không bổ sung thông tin.
6. Lưu raw transcript trước khi tạo file.
7. Lưu code, AI tests và `ASSUMPTIONS.md` nếu có.
8. Tạo checksum cho raw artifact.
9. Không chạy hidden acceptance tests ở giai đoạn này.

Exit gate: 6 thư mục candidate đầy đủ; số run thiếu/không build vẫn được giữ và báo cáo, không âm thầm chạy lại để thay thế.

#### Ngày 9: Packaging-only normalization

Người phụ trách: M2; M4 review.

- Chỉ sửa import path, package layout hoặc dependency declaration nếu cần để chạy.
- Mỗi sửa đổi lưu thành patch và mô tả trong `experiments/packaging-fixes.csv`.
- Không sửa thuật toán, exception, rounding hoặc expected value.
- Nếu candidate vẫn không chạy, ghi `non-executable`; không xóa run khỏi mẫu.

#### Ngày 10: Baseline pytest và coverage

Người phụ trách: M2 chạy; M4 xác nhận dữ liệu.

Với từng candidate:

- chạy AI-only tests;
- lưu stdout/stderr và exit code;
- đo line coverage và branch coverage;
- lưu số test collected/passed/failed;
- không diễn giải coverage là correctness.

Đầu ra:

- `results/baseline/run-XX/pytest.log`
- `results/baseline/run-XX/coverage.json`
- các cột baseline trong `measurements.csv`.

Gate tuần 2: chọn ngẫu nhiên một dòng CSV và truy ngược được tới transcript, code và raw log.

### Tuần 3 — Kiểm chứng độc lập và mutation testing

#### Ngày 11–12: Viết independent tests

Người phụ trách: M3; M1 review. M3 chưa xem candidate code/tests.

Việc cần làm:

- Viết acceptance tests từ table đã freeze.
- Viết reference oracle độc lập bằng `Decimal` và `ROUND_HALF_UP`.
- Viết 8 nhóm property tests theo spec: range, monotonicity, VIP relation, lower/upper plateau, boundary/rounding, type contract và reference equivalence.
- Cấu hình Hypothesis để counterexample có thể tái lập; lưu seed/failure example.
- Kiểm tra independent tests trên một implementation chuẩn viết từ oracle, không dùng candidate implementation.
- Review test để bảo đảm không import helper nội bộ của candidate.

Đầu ra:

- `tests_independent/test_acceptance.py`
- `tests_independent/test_properties.py`
- independent-test commit/hash trước khi mở candidate code.

Exit gate: reference implementation pass 100%; deliberate faulty fixtures cho sai discount order, banker’s rounding và bool validation đều bị test phát hiện.

#### Ngày 13: Chạy independent verification

Người phụ trách: M3 chạy; M4 thu thập.

- Mở khóa candidates sau khi independent tests đã freeze.
- Chạy cùng test suite lên mọi executable candidate.
- Lưu acceptance score, property failures và counterexample nhỏ nhất.
- Không sửa candidate sau khi thấy failure.
- Nếu adapter có lỗi, sửa adapter bằng patch riêng và chạy lại tất cả candidates để giữ công bằng.

#### Ngày 14–15: Mutation testing hai cấu hình

Người phụ trách: M4; M2 hỗ trợ tooling.

Cho từng executable candidate:

1. Chạy mutation với AI-only tests.
2. Xóa/tách mutation cache đúng cách.
3. Chạy mutation với AI + independent tests.
4. Lưu tool version, command/config, runtime và đầy đủ trạng thái mutant.
5. Không tính timeout/error là killed.
6. Tính raw score bằng script, không tính tay.

Nếu toàn bộ 6 run quá chậm:

- vẫn chạy coverage/acceptance cho cả 6;
- mutation đầy đủ trên ít nhất 3 run được chọn bằng quy tắc đã ghi trước, ví dụ run đầu của mỗi model và run có acceptance score trung vị;
- báo cáo rõ đây là giới hạn, không chọn run theo kết quả mutation thuận lợi.

#### Ngày 16: Review mutant và test “giả mạnh”

Người phụ trách: M4 phân loại; M1 review.

Với mỗi surviving mutant:

- xác định validation/min/max/discount order/rounding/boundary/other;
- xác định executable, unreachable hay equivalent;
- ghi lý do và reviewer;
- không loại khỏi adjusted score nếu chưa đạt đồng thuận.

Với test giả mạnh, hoàn thành bảng:

```text
test_id,run_id,apparent_strength,wrong_or_missing_assumption,
related_mutant,counterexample,replacement_test,evidence_path
```

Gate tuần 3:

- có kết quả AI-only và full-suite;
- raw/adjusted scores được script sinh;
- mọi equivalent mutant có justification;
- ít nhất một thành viên không trực tiếp chạy mutation kiểm tra lại 10% mẫu.

### Tuần 4 — Phân tích và bàn giao

#### Ngày 17: Tổng hợp và trực quan hóa

Người phụ trách: M4.

Sinh tự động ít nhất:

- bảng tổng hợp 6 run;
- biểu đồ AI-only mutation score so với full-suite score;
- biểu đồ coverage so với acceptance score;
- số property failures theo run;
- stacked chart survivor theo nhóm lỗi;
- bảng ambiguity detection và assumptions.

Sanity checks:

- score nằm trong `[0, 100]`;
- mẫu số không bằng 0 mà không được ghi chú;
- tổng mutant theo trạng thái khớp total;
- số liệu trên chart khớp CSV;
- missing run hiển thị là `NA`, không tự biến thành 0.

#### Ngày 18–19: Viết report

Owner theo phần:

| Phần | Owner | Reviewer |
|---|---|---|
| Đặt vấn đề, RQ, bối cảnh Việt Nam | M1 | M3 |
| Tổng quan tài liệu | M1 | Cả nhóm kiểm nguồn |
| Phương pháp và protocol | M2 | M3 |
| Independent testing | M3 | M2 |
| Mutation/results | M4 | M1 |
| Bàn luận, giới hạn, khuyến nghị | M1 | Cả nhóm |
| Phụ lục bằng chứng AI | M2 | M4 |

Cách trả lời RQ:

- RQ1 dùng clarification rate, ambiguity rubric và assumptions.
- RQ2 đối chiếu coverage/mutation score với acceptance/property failures; không suy quan hệ nhân quả từ 6 run.
- RQ3 dùng chênh lệch mutant killed và các failure chỉ independent suite phát hiện, rồi đề xuất workflow phân tách trách nhiệm.

Khi phân tích, phải nêu rõ: mutation testing đo khả năng test phân biệt các biến đổi quanh implementation hiện có; nó không tự tạo ra một business oracle đúng. Vì vậy mutation score cao không đủ chứng minh code đúng yêu cầu.

#### Ngày 20: Audit report

Cả nhóm thực hiện:

- kiểm đủ 12–18 trang, font 13;
- kiểm đủ 7 mục bắt buộc;
- kiểm tối thiểu 8 nguồn và ít nhất 3 nguồn học thuật/khảo sát lớn;
- mở từng link/DOI và đối chiếu claim;
- kiểm mọi số/bảng/biểu đồ có evidence path;
- kiểm phụ lục ghi công cụ AI, mục đích và phần nội dung liên quan;
- kiểm không lộ tên/model khác nhau giữa report và metadata;
- xuất PDF và kiểm font, bảng, caption, số trang.

#### Ngày 21: Slide và rehearsal

- Làm tối đa 15 slide theo project spec.
- Chỉ dùng 2–3 biểu đồ quan trọng nhất, font đủ lớn.
- Mỗi thành viên có phần nói rõ ràng.
- Rehearsal lần 1: ghi thời gian từng phần.
- Cắt nội dung nếu vượt 15 phút; không tăng tốc độ nói để bù.
- Rehearsal lần 2 trước người đóng vai giảng viên.

Câu hỏi phản biện phải chuẩn bị:

1. Vì sao oracle được xem là đúng và ai quyết định?
2. Vì sao chỉ dùng một bài toán nhỏ?
3. Mutation score cao có chứng minh correctness không?
4. Equivalent mutants được xác định thế nào?
5. AI run có thực sự độc lập không?
6. Vì sao 6 run đủ/chưa đủ để khái quát?
7. Kết quả áp dụng thế nào cho doanh nghiệp Việt Nam?
8. Nếu AI phát hiện hết ambiguity thì kết luận là gì?

#### Ngày 22: Release package

- Tag phiên bản cuối, ví dụ `submission-v1.0`.
- Từ môi trường sạch, cài bằng lockfile và chạy reproduction commands.
- Tạo ZIP repository nếu hệ thống nộp bài không nhận Git URL.
- Mở thử PDF/PPTX/ZIP sau khi copy sang máy khác.
- Nộp report, slide và repository/link trước deadline nội bộ ít nhất 24 giờ.

## 6. Task dependencies

```text
Freeze RQ + prompt
        ↓
Freeze hidden oracle ────────────────┐
        ↓                            │
Scaffold + dry-run                   │
        ↓                            │
Six AI code/test runs                │
        ↓                            │
Baseline pytest + coverage           │
                                     ↓
                         Independent tests frozen
                                     ↓
                  Run acceptance/property on candidates
                                     ↓
              Mutation: AI-only vs full independent suite
                                     ↓
                         Aggregate + review evidence
                                     ↓
                          Report + slides + release
```

Literature review có thể chạy song song từ Tuần 1 đến trước khi khóa report.

## 7. Quality gates và quyết định Go/No-Go

### Gate A — Trước AI runs

Go khi:

- prompt và oracle đều versioned;
- M2 không có quyền/context đọc oracle;
- protocol và schemas đã khóa;
- dummy pipeline chạy được.

No-Go nếu oracle còn mâu thuẫn hoặc runner vô tình cung cấp oracle cho AI.

### Gate B — Trước independent verification

Go khi raw transcript và candidate artifacts của mọi run đã khóa.

No-Go nếu nhóm đã sửa business logic AI output mà không giữ bản gốc.

### Gate C — Trước phân tích

Go khi independent tests có hash riêng, reference implementation pass và deliberate faults bị phát hiện.

No-Go nếu tests độc lập được viết sau khi đã đọc candidate expectations mà không ghi nhận nguy cơ thiên lệch.

### Gate D — Trước nộp

Go khi một thành viên có thể tái tạo bảng chính từ raw artifacts mà không chỉnh tay.

No-Go nếu report có con số không truy vết được hoặc trích dẫn chưa mở nguồn gốc.

## 8. Risk register

| Rủi ro | Xác suất/ảnh hưởng | Giảm thiểu |
|---|---|---|
| AI đọc được hidden oracle | Cao/Rất cao | Chạy AI trong context/chat sạch; giữ oracle ngoài workspace/branch được cung cấp |
| AI luôn hỏi đúng mọi ambiguity | Trung bình/Trung bình | Báo cáo đây là kết quả; vẫn phân tích assumptions sau follow-up, không sửa prompt để ép thất bại |
| Candidate không chạy | Trung bình/Trung bình | Giữ run trong dataset; chỉ packaging fix có log; phân tích executable subset riêng |
| Mutation quá chậm | Trung bình/Cao | Pilot runtime; giới hạn scope một module; dùng quy tắc chọn subset đã ghi trước |
| Nhiều equivalent mutants | Trung bình/Cao | Review thủ công hai người; báo cáo raw và adjusted score |
| Hypothesis flaky/khó tái lập | Thấp/Trung bình | Pin version, lưu seed/examples, kiểm chạy lặp lại |
| Model/version thay đổi | Cao/Trung bình | Lưu model hiển thị, thời gian, transcript; không tuyên bố vượt quá dataset |
| Coverage cao bị hiểu là đúng | Cao/Cao | Luôn đặt coverage cạnh acceptance score và counterexample |
| Chọn lọc kết quả đẹp | Trung bình/Cao | Giữ mọi run; preregister quy tắc loại/chọn subset |
| Report vượt 18 trang | Trung bình/Trung bình | Chuyển raw tables/logs sang phụ lục/repository; giữ phần chính trả lời RQ |
| Nguồn do AI bịa hoặc sai | Trung bình/Rất cao | Evidence matrix, mở DOI/URL, hai người kiểm claim quan trọng |

## 9. Definition of Done theo workstream

### Research

- 3 RQ được trả lời bằng dữ liệu.
- Có ít nhất 8 nguồn hợp lệ, 3 nguồn học thuật/khảo sát lớn.
- Threats to validity được viết rõ.

### Engineering

- Có ít nhất 3 run, mục tiêu 6.
- AI-only và independent tests chạy tách biệt.
- Pipeline tái lập từ lockfile.
- Raw artifacts không bị ghi đè.

### Testing

- Acceptance oracle được freeze trước AI runs.
- Có đủ 8 nhóm property.
- Deliberate faulty implementations bị independent suite phát hiện.
- Mutation chạy ở hai cấu hình và survivors được review.

### Evidence

- `metadata.csv` và `measurements.csv` đầy đủ.
- Biểu đồ được sinh bằng script.
- Mọi score có raw log và công thức.
- Test giả mạnh có counterexample cụ thể.

### Submission

- Report PDF 12–18 trang, font 13.
- Slide tối đa 15 trang và rehearsal không quá 15 phút.
- Phụ lục khai báo AI đầy đủ.
- Repository/ZIP mở và tái lập được.

## 10. Việc cần làm ngay trong buổi đầu tiên

1. Điền tên thật vào bảng vai trò M1–M4.
2. Chốt 2 công cụ/mô hình và 3 run cho mỗi công cụ.
3. Tạo repository Git dùng chung và task board.
4. M1 + M3 hoàn thiện oracle/exception table rồi freeze.
5. M2 + M4 scaffold Python project và chạy dummy pipeline.
6. Mỗi thành viên nhận 2 nhóm nguồn cho literature review.

Không chạy prompt chính trước khi hoàn tất Gate A.
