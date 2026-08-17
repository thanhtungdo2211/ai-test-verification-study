# Khung viết bài luận Topic 7

Đây là khung viết theo đặc tả và kế hoạch của repository. Không điền số liệu
đoán. Mọi số trong bản cuối phải lấy từ `results/measurements.csv` và truy
ngược được tới manifest/log/transcript tương ứng.

## Thông điệp trung tâm

Bài không cần chứng minh trước rằng AI thất bại. Câu hỏi là liệu test sinh cùng
context với implementation có thể nhất quán nội bộ nhưng vẫn bỏ sót yêu cầu
độc lập hay không. Kết luận phải giới hạn trong các run, model và prompt đã
quan sát.

Không viết: “AI luôn tạo code sai.”

Nên viết: “Trong các run quan sát được, chúng tôi so sánh sự nhất quán của
AI-generated tests với một acceptance oracle độc lập và báo cáo counterexample,
mutation score cùng các giới hạn của thiết kế.”

## 1. Đặt vấn đề — khoảng 1–1,5 trang

Trình bày theo thứ tự:

1. AI coding assistant có thể sinh implementation và test trong cùng một
   context.
2. Nếu implementation hiểu sai yêu cầu mơ hồ, test sinh cùng context có thể
   kiểm tra lại chính cách hiểu sai đó.
3. Coverage hoặc “all tests passed” vì vậy chưa phải bằng chứng correctness.
4. Bài toán transfer fee là một case study nhỏ để tách requirement owner,
   AI operator, independent verifier và mutation reviewer.

Đoạn cuối phần này nêu khoảng trống và đóng góp:

- prompt mơ hồ được freeze;
- oracle và independent tests do người sở hữu yêu cầu kiểm soát;
- so sánh AI-only với full suite;
- lưu raw evidence để tái lập.

## 2. Câu hỏi nghiên cứu — khoảng 0,5 trang

Giữ nguyên ba RQ đã freeze trong `docs/research-questions.md`:

- **RQ1:** AI có hỏi làm rõ hoặc ghi nhận ambiguity/assumptions không?
- **RQ2:** coverage và mutation score của test cùng context có phản ánh kết quả
  trên acceptance oracle độc lập không?
- **RQ3:** tách independent testing và mutation review có tăng fault detection
  so với AI-only không?

Không đổi wording RQ sau khi xem kết quả. Có thể nêu expectation như câu hỏi,
không biến thành kết luận định trước.

## 3. Tổng quan tài liệu — khoảng 2,5–3 trang

Tối thiểu 8 nguồn, trong đó ít nhất 3 nguồn học thuật hoặc khảo sát lớn. Chia
thành các nhóm:

1. Test oracle problem và specification ambiguity.
2. AI-generated code/tests và self-confirming hoặc correlated errors.
3. Property-based testing và acceptance testing.
4. Mutation testing, mutation score và equivalent mutants.
5. Human-in-the-loop, separation of duties và review trong kỹ nghệ phần mềm.

Mỗi claim quan trọng phải có dòng trong `report/evidence-matrix.csv` gồm citation,
claim, page/section, URL/DOI và người verify. Không dùng citation do AI tự
nhớ nếu chưa mở nguồn gốc.

## 4. Phương pháp — khoảng 2–3 trang

### 4.1 Đối tượng và prompt

Đưa prompt mơ hồ nguyên văn hoặc dẫn tới
`experiments/prompts/ambiguous-requirement.txt`. Mô tả các điểm chưa quy định
duy nhất: kiểu amount, thứ tự min/max-discount-rounding, rounding tie rule và
exception contract.

### 4.2 Oracle và phân tách trách nhiệm

Mô tả oracle v1.0 được freeze trước AI run; AI không được xem oracle hoặc
`tests_independent/`. Nêu vai trò M1–M4 và review chéo. Đây là biện pháp kiểm
soát bias, không chỉ là phân công hành chính.

### 4.3 Thiết kế run

Thiết kế khuyến nghị: 2 tool/model × 3 context sạch = 6 run (`run-01` đến
`run-06`). Đặc tả cho phép tối thiểu 3 run nhưng sáu run là mục tiêu đã
preregister. Một run không đủ để khái quát hành vi của AI.

Mỗi run ghi tool, model hiển thị, UTC timestamps, operator, clarification,
ambiguities, follow-up, raw transcript, assumptions và mọi packaging-only fix.

### 4.4 Pipeline đo lường

Mỗi candidate được chạy theo thứ tự:

1. AI-only pytest và line/branch coverage.
2. Full suite gồm AI tests và independent acceptance/property tests.
3. Mutation với AI-only tests.
4. Mutation với full suite nếu full baseline pass.
5. Review survivors/equivalent và aggregate raw artifacts.

### 4.5 Công thức

```text
raw mutation score = killed / total_generated × 100%
adjusted mutation score = killed /
  (killed + survived_non_equivalent) × 100%
acceptance score = acceptance_passed / acceptance_total × 100%
```

Timeout/error không phải killed. Adjusted score để trống cho tới khi
equivalent mutant được review và có justification của reviewer thứ hai.

### 4.6 Threats to validity

Nêu trước các giới hạn: bài toán nhỏ, số model/run ít, prompt/model drift,
oracle do người thiết kế, equivalent mutant chủ quan, candidate không
executable và việc mutation score chỉ đo test adequacy quanh implementation.

## 5. Kết quả và phân tích — khoảng 3–4 trang

Không viết phần này trước khi aggregate. Dùng một bảng cho mọi run với các cột:

```text
run_id, tool, model_displayed, clarification_asked,
ai_tests_passed, line_coverage, branch_coverage,
acceptance_passed, acceptance_total, properties_failed,
killed_ai, survived_ai, raw_score_ai,
killed_full, survived_full, raw_score_full
```

### 5.1 RQ1 — ambiguity và assumptions

Tạo bảng per-run từ `metadata.csv` và `ASSUMPTIONS.md`. Báo cáo số run hỏi
clarification, số ambiguity được nhận diện và follow-up. Nếu AI không hỏi,
ghi nhận đúng là “không hỏi trong run này”, không biến thành “AI không thể hỏi”.

### 5.2 RQ2 — coverage so với oracle

Đặt coverage cạnh acceptance/property failures. Câu mẫu:

> Trong `run-01`, AI-only tests pass 41/41 và coverage cao, nhưng independent
> suite vẫn phát hiện candidate chấp nhận `1.5` và `1.0` dù contract độc lập yêu
> cầu TypeError. Đây là counterexample cho việc dùng coverage/all-pass như
> proxy của correctness; kết quả này chỉ đại diện cho run-01.

Sau khi có thêm run, thay câu “run-01” bằng bảng tổng hợp và báo cả các run
không tái hiện hiện tượng.

### 5.3 RQ3 — AI-only so với full suite

So sánh killed/survived/timeout/error của hai cấu hình. Không chỉ so sánh một
phần trăm. Báo rõ full mutation bị bỏ trống nếu full baseline fail.

### 5.4 Test “giả mạnh”

Dùng bảng:

```text
test_id,run_id,apparent_strength,wrong_or_missing_assumption,
related_mutant,counterexample,replacement_test,evidence_path
```

Ví dụ run-01: test AI cho float xác nhận một lựa chọn kiểu dữ liệu mà
independent contract không chấp nhận; đây là sự khác nhau về assumption, không
được mô tả quá mức thành “bug chắc chắn” nếu prompt ban đầu mơ hồ.

## 6. Bàn luận và khuyến nghị — khoảng 2–3 trang

Trả lời từng RQ theo cấu trúc “kết quả → giải thích → giới hạn”:

- **RQ1:** clarification/assumption rate quan sát được là bao nhiêu; có run
  nào không hỏi không?
- **RQ2:** coverage/mutation có đồng biến với acceptance không; counterexample
  nào cho thấy chúng không đủ?
- **RQ3:** independent suite giết thêm mutant hoặc phát hiện failure nào; full
  suite có bị giới hạn bởi candidate baseline fail không?

Khuyến nghị workflow:

1. Human-owned prompt/oracle.
2. AI implementation/test trong context sạch.
3. Independent acceptance/property tests.
4. Coverage và mutation như tín hiệu test adequacy.
5. Human review survivor/equivalent trước release.

Nhấn mạnh mutation score cao không chứng minh business correctness; mutation
testing chỉ kiểm tra khả năng test phân biệt các biến đổi của implementation.

## 7. Giới hạn nghiên cứu — khoảng 0,5–1 trang

Bắt buộc ghi:

- một bài toán transfer fee nhỏ;
- số run/model hữu hạn, không suy causal/general AI claims;
- transcript hoặc metadata thiếu nếu có (run-01 hiện là response-only);
- full mutation không có ở candidate fail baseline;
- chủ quan khi phân loại equivalent mutant;
- thay đổi phiên bản tool/model và khả năng tái lập.

Nếu cuối cùng chỉ có một run, phải viết đây là exploratory case study, không
được trình bày như kết luận của thiết kế sáu run. Definition of Done yêu cầu
ít nhất 3 run, khuyến nghị 6.

## 8. Phân công công việc — khoảng 0,5 trang

Điền tên thật vào `docs/roles.md` và mô tả đóng góp:

- M1: RQ, oracle, literature, final editing.
- M2: clean AI runs, transcript, candidate packaging.
- M3: independent acceptance/property tests.
- M4: mutation, data aggregation, survivor review.

Ghi ai review phần nào; không chỉ liệt kê tên.

## 9. Tài liệu tham khảo và phụ lục

Phụ lục nên có:

- prompt đóng băng và follow-up chuẩn;
- oracle/review record;
- metadata và bảng measurements;
- transcript/candidate tree/checksum;
- raw pytest/coverage/mutation logs;
- commands tái lập;
- AI-use disclosure;
- commit/tag của release.

## Checklist trước khi xuất PDF

- [ ] 12–18 trang, font 13.
- [ ] Đủ các phần bắt buộc và mục giới hạn.
- [ ] Có tối thiểu 8 nguồn, trong đó 3 nguồn học thuật/khảo sát lớn.
- [ ] Mọi số liệu khớp `results/measurements.csv`.
- [ ] Mọi số liệu có raw evidence path.
- [ ] Có bảng mọi run, acceptance/property, mutation và survivor.
- [ ] Có raw và adjusted score; adjusted chỉ khi equivalent đã review.
- [ ] Không dùng một run để khẳng định hành vi chung của AI.
- [ ] PDF, slide và repository tái lập được từ clean checkout.

