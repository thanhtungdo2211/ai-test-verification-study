# Đặc tả đồ án Chủ đề 7

## 1. Tên đề tài đề xuất

**Phá vỡ vòng lặp tự xác nhận khi AI sinh đồng thời mã nguồn và kiểm thử: thực nghiệm với property-based testing và mutation testing**

## 2. Mục tiêu

Đồ án phải chứng minh bằng thực nghiệm rằng một bộ test có thể:

- chạy xanh và có coverage cao;
- thậm chí có mutation score tương đối cao;
- nhưng vẫn xác nhận một hiện thực sai vì code và test cùng dựa trên một cách hiểu sai yêu cầu.

Sau đó, nhóm bổ sung một oracle độc lập do con người phê duyệt, acceptance tests và property-based tests để đo mức cải thiện khả năng phát hiện lỗi.

## 3. Câu hỏi nghiên cứu

1. Khi nhận yêu cầu cố tình mơ hồ, AI có nhận diện và hỏi lại các điểm mơ hồ hay tự đưa ra giả định?
2. Coverage và mutation score của test do cùng AI sinh có phản ánh đúng khả năng đáp ứng yêu cầu nghiệp vụ không?
3. Việc tách vai trò viết đặc tả, viết code và kiểm chứng độc lập cải thiện tỷ lệ phát hiện lỗi như thế nào?

## 4. Đối tượng thực nghiệm

Xây dựng một thư viện Python nhỏ tính phí chuyển tiền ví điện tử. Không làm web/API/database vì các thành phần đó gây nhiễu cho thí nghiệm kiểm thử.

Giao diện chung cho mọi lần chạy:

```python
def calculate_transfer_fee(amount_vnd: int, is_vip: bool = False) -> int:
    """Return the transfer fee in VND."""
```

### 4.1 Prompt mơ hồ được công khai cho AI

Giữ nguyên văn prompt sau cho mọi lần chạy:

> Create a Python function `calculate_transfer_fee(amount_vnd, is_vip=False)`. The transfer fee is 1% of the transferred amount, with a minimum of 5,000 VND and a maximum of 50,000 VND. VIP customers receive a 20% discount. Round the fee to the nearest 1,000 VND. Invalid amounts must be rejected. Provide the implementation and a complete pytest test suite.

Prompt này cố ý không nói rõ:

- áp dụng giảm giá trước hay sau giới hạn tối thiểu/tối đa;
- làm tròn theo `half-up`, `half-even` hay quy tắc khác;
- làm tròn ở bước nào;
- giá trị tại đúng biên có được tính hay không;
- kiểu dữ liệu nào hợp lệ và `bool` có được xem là `int` hay không;
- hành vi và loại exception cho dữ liệu không hợp lệ.

Không được sửa prompt giữa các lần chạy.

### 4.2 Oracle bí mật do con người chốt trước thí nghiệm

File oracle phải được viết, review và commit trước khi chạy AI. Không cung cấp file này cho AI sinh code/test ban đầu.

Quy tắc chuẩn để nghiệm thu:

1. `amount_vnd` phải là `int` nhưng không được là `bool`, và phải lớn hơn 0.
2. `is_vip` phải là `bool`.
3. Tính phí thô bằng `amount_vnd * 0.01` với số học chính xác, không dùng sai số `float` để quyết định biên.
4. Chặn phí thô trong đoạn đóng `[5_000, 50_000]`.
5. Nếu là VIP, nhân kết quả sau khi chặn biên với `0.8`.
6. Chỉ làm tròn một lần ở cuối, tới nghìn VND gần nhất, theo `ROUND_HALF_UP`.
7. Trả về `int`; input sai phải raise `TypeError` hoặc `ValueError` theo bảng acceptance test đã chốt.

Các ví dụ oracle tối thiểu:

| `amount_vnd` | VIP | Kết quả |
|---:|:---:|---:|
| 1 | Không | 5.000 |
| 1 | Có | 4.000 |
| 500.000 | Không | 5.000 |
| 500.000 | Có | 4.000 |
| 4.850.000 | Không | 49.000 |
| 4.850.000 | Có | 39.000 |
| 5.000.000 | Không | 50.000 |
| 5.000.000 | Có | 40.000 |
| 9.000.000 | Không | 50.000 |
| 9.000.000 | Có | 40.000 |

Input sai tối thiểu: `0`, `-1`, `1.5`, `"1000"`, `True`, `None`; đồng thời kiểm tra `is_vip=0`, `is_vip=1` và `is_vip=None`.

## 5. Thiết kế thực nghiệm

### 5.1 Số lần chạy

- Mức tối thiểu: 3 phiên AI độc lập.
- Mức khuyến nghị: 6 phiên, gồm 2 công cụ/mô hình × 3 lần chạy độc lập.
- Mỗi phiên dùng context sạch, cùng prompt, cùng giới hạn số lượt trao đổi và cùng phiên bản Python.
- Ghi lại công cụ, model/version hiển thị, ngày giờ, prompt, phản hồi thô, số lượt và mọi can thiệp của con người.

Nếu AI hỏi để làm rõ, ghi nhận là **phát hiện mơ hồ**. Sau đó trả lời thống nhất: “Proceed with reasonable assumptions and record every assumption in `ASSUMPTIONS.md`.” Nếu AI không hỏi, không được gợi ý thêm.

Không sửa logic hoặc expected value trong code/test do AI sinh. Chỉ được sửa lỗi đóng gói thuần túy để test có thể chạy; mọi sửa đổi phải lưu diff và báo cáo riêng.

### 5.2 Các pha

**Pha 0 — Freeze oracle**

- Con người viết `spec/acceptance-oracle.md` và acceptance table.
- Hai thành viên review, chốt bằng Git commit hash.
- Không cho AI implementer xem oracle.

**Pha 1 — AI sinh code và test trong cùng context**

- Chạy prompt mơ hồ.
- Lưu nguyên trạng implementation, tests, assumptions và transcript.
- Chạy test do AI sinh và đo line/branch coverage.

**Pha 2 — Kiểm chứng độc lập**

- Một người/phiên AI khác chỉ nhận oracle đã chốt và public interface.
- Viết example-based acceptance tests và property-based tests mà không xem test do AI implementer sinh.
- Chạy test độc lập lên từng implementation của Pha 1.

**Pha 3 — Mutation testing**

- Chạy mutation testing lần 1 chỉ với bộ test do AI sinh.
- Chạy mutation testing lần 2 với bộ test AI + bộ test kiểm chứng độc lập.
- Phân loại từng mutant còn sống theo quy tắc nghiệp vụ: validation, min/max, thứ tự discount, rounding, boundary, hoặc equivalent mutant.
- Không tự động coi mutant timeout/error là “killed”; báo cáo chúng thành cột riêng.

**Pha 4 — Phân tích và đề xuất quy trình**

- So sánh kết quả trước/sau kiểm chứng độc lập.
- Tìm các test “giả mạnh”.
- Đề xuất mô hình phân tách trách nhiệm và quality gate.

## 6. Property-based tests bắt buộc

Dùng Hypothesis để sinh dữ liệu. Bộ test độc lập phải kiểm tra ít nhất:

1. **Range:** phí thường thuộc `[5_000, 50_000]`; phí VIP thuộc `[4_000, 40_000]` với input hợp lệ.
2. **Monotonicity:** khi số tiền tăng, phí không được giảm trong cùng một nhóm khách hàng.
3. **VIP relation:** phí VIP không lớn hơn phí thường và tuân theo oracle sau bước clamp.
4. **Lower plateau:** mọi số tiền từ 1 đến 500.000 cho cùng mức phí tối thiểu tương ứng.
5. **Upper plateau:** mọi số tiền từ 5.000.000 trở lên cho cùng mức phí tối đa tương ứng.
6. **Boundary/rounding:** sinh dữ liệu quanh 500.000, 5.000.000 và các điểm `x.500` nghìn để phân biệt `half-up` với banker’s rounding.
7. **Type contract:** mọi kiểu ngoài contract đều bị từ chối, đặc biệt `True`/`False` vì `bool` là subclass của `int` trong Python.
8. **Reference oracle:** với miền input sinh ngẫu nhiên, kết quả phải bằng hàm oracle độc lập dùng `Decimal` và `ROUND_HALF_UP`.

Phải cấu hình seed hoặc lưu Hypothesis failure examples để có thể tái lập kết quả.

## 7. Công cụ và tiêu chuẩn kỹ thuật

- Python 3.12 (hoặc một phiên bản duy nhất được pin cho toàn bộ nhóm).
- Quản lý dự án bằng `pyproject.toml`; có thể dùng `uv`.
- `pytest` cho test runner.
- `pytest-cov` cho line và branch coverage.
- `hypothesis` cho property-based testing.
- `mutmut` cho mutation testing.
- `ruff` cho lint/format; `mypy` là tùy chọn.
- Pin toàn bộ dependency và lưu lockfile.
- CI phải chạy lint, toàn bộ pytest và coverage; mutation testing có thể chạy thành job riêng vì chậm.

Không đặt mục tiêu coverage như bằng chứng duy nhất. Coverage chỉ cho biết code đã được chạy, không chứng minh expected result đúng.

## 8. Chỉ số phải thu thập

### 8.1 Chỉ số theo từng AI run

- AI có hỏi làm rõ không (`yes/no`).
- Số điểm mơ hồ AI tự nhận diện.
- Số giả định AI ghi rõ.
- Số test AI sinh; tỷ lệ test pass.
- Line coverage và branch coverage.
- Số acceptance example bị sai.
- Số property bị vi phạm và counterexample nhỏ nhất.
- Mutant: `total`, `killed`, `survived`, `timeout`, `error`, `equivalent`.
- Mutation score trước và sau test độc lập.

### 8.2 Công thức

```text
raw mutation score = killed / total_generated × 100%

adjusted mutation score = killed /
  (killed + survived_non_equivalent) × 100%

acceptance score = passed_human_acceptance_tests /
  total_human_acceptance_tests × 100%

ambiguity detection rate = runs_asking_clarification /
  total_runs × 100%
```

Báo cáo cả raw và adjusted score; danh sách equivalent mutant phải được review thủ công và giải thích, không chỉ xóa khỏi mẫu số.

### 8.3 Định nghĩa test “giả mạnh”

Một test hoặc bộ test được xếp là “giả mạnh” khi có tín hiệu bề ngoài tốt (pass, coverage cao hoặc giết được nhiều mutant) nhưng vẫn chấp nhận ít nhất một hành vi trái oracle.

Phân tích theo bảng:

| Test ID | Vì sao có vẻ mạnh | Giả định sai/thiếu | Mutant liên quan | Counterexample | Test thay thế |
|---|---|---|---|---|---|

Các mẫu cần tìm: copy lại công thức từ implementation vào test, chỉ assert kiểu/range, chỉ happy path, bỏ biên, expected value sai theo cùng giả định, hoặc mock chính logic cần kiểm tra.

## 9. Cấu trúc repository

```text
.
├── README.md
├── pyproject.toml
├── uv.lock
├── spec/
│   ├── ambiguous-requirement.md
│   └── acceptance-oracle.md
├── candidates/
│   ├── run-01/
│   │   ├── src/transfer_fee/calculator.py
│   │   ├── tests_ai/
│   │   └── ASSUMPTIONS.md
│   └── run-02...run-06/
├── tests_independent/
│   ├── test_acceptance.py
│   └── test_properties.py
├── experiments/
│   ├── prompts/
│   ├── transcripts/
│   └── metadata.csv
├── results/
│   ├── measurements.csv
│   ├── mutation-ai-only/
│   ├── mutation-independent/
│   └── figures/
├── scripts/
│   ├── run_tests.py
│   ├── run_mutation.py
│   └── aggregate_results.py
├── report/
└── slides/
```

Các script phải cho phép tái tạo `measurements.csv`, bảng và biểu đồ từ artifact thô. Không chỉnh tay số trong report.

## 10. Quality gates

### Gate tái lập

- Một lệnh cài dependency từ lockfile.
- Một lệnh chạy toàn bộ test.
- Một lệnh tái tạo bảng/biểu đồ.
- README ghi OS, Python, dependency version và seed.

### Gate test

- Test độc lập không import helper nội bộ từ implementation.
- Test AI và test độc lập có marker/thư mục riêng để chạy tách biệt.
- Không đổi oracle sau khi xem output AI; nếu bắt buộc đổi, ghi commit và lý do như một threat to validity.

### Gate bằng chứng

- Mọi con số trong báo cáo liên kết được tới CSV/log/transcript/commit.
- Không tuyên bố mutant là equivalent nếu chưa có giải thích thủ công.
- Báo cáo cả kết quả bất lợi, lỗi setup và run không biên dịch.

## 11. Mô hình phân tách trách nhiệm đề xuất

| Vai trò | Được làm | Không được làm |
|---|---|---|
| Requirement owner (con người) | Chốt thuật ngữ, oracle, acceptance criteria | Viết expected value sau khi đã xem implementation |
| AI implementer | Sinh code và unit test nội bộ, ghi assumptions | Tự phê duyệt yêu cầu hoặc quality gate cuối |
| Independent verifier | Viết acceptance/property tests từ oracle | Dựa vào implementation để suy ra expected result |
| Mutation auditor | Chạy mutation, review survivor/equivalent, tổng hợp dữ liệu | Chỉ báo cáo một mutation score không có phân loại |
| Human reviewer | Phê duyệt ngoại lệ, thay đổi spec và nghiệm thu | Tin kết quả “all tests passed” mà không truy vết oracle |

Luồng khuyến nghị:

```text
Human-owned spec/oracle
        ↓
AI implementation + developer tests
        ↓
Independent acceptance/property tests
        ↓
Coverage + mutation analysis
        ↓
Human review of survivors and evidence
        ↓
Release decision
```

## 12. Cấu trúc báo cáo 12–18 trang, font 13

1. **Đặt vấn đề (1–1,5 trang):** testing illusion, rủi ro khi AI sinh code lẫn test, liên hệ thực tiễn đội phần mềm Việt Nam.
2. **Câu hỏi nghiên cứu (0,5 trang):** ba RQ ở trên và giả thuyết nếu có.
3. **Tổng quan tài liệu (2,5–3 trang):** tối thiểu 8 nguồn, trong đó ít nhất 3 nguồn học thuật hoặc khảo sát lớn; bao quát oracle problem, property-based testing, mutation testing, AI-generated tests và human-in-the-loop.
4. **Phương pháp (2–3 trang):** prompt, hidden oracle, biến độc lập/phụ thuộc, số run, môi trường, protocol, công thức và threat control.
5. **Kết quả và phân tích (3–4 trang):** bảng từng run, biểu đồ mutation score trước/sau, acceptance score, counterexamples, bảng test giả mạnh.
6. **Bàn luận và khuyến nghị (2–3 trang):** trả lời từng RQ, giải thích vì sao mutation testing một mình chưa đủ, mô hình phân tách trách nhiệm, áp dụng ở Việt Nam.
7. **Giới hạn nghiên cứu (0,5–1 trang):** bài toán nhỏ, số model/run ít, prompt/model thay đổi, equivalent mutants, độ chủ quan của oracle.
8. **Phân công công việc (0,5 trang):** bảng đóng góp từng thành viên.
9. **Tài liệu tham khảo và phụ lục:** transcript, prompt, AI disclosure, commit hash, dữ liệu thô, mutation logs và cách tái lập.

Các bảng/biểu đồ bắt buộc do nhóm tự tạo:

- bảng kết quả mọi run;
- biểu đồ mutation score AI-only so với independent tests;
- biểu đồ acceptance failures hoặc property violations theo run;
- bảng survivor theo nhóm lỗi nghiệp vụ;
- bảng phân tích test giả mạnh.

## 13. Slide thuyết trình tối đa 15 trang

1. Tiêu đề và thành viên.
2. Vấn đề và vòng lặp tự xác nhận.
3. Câu hỏi nghiên cứu.
4. Prompt mơ hồ.
5. Hidden oracle và các điểm mơ hồ.
6. Thiết kế thí nghiệm.
7. Toolchain và dữ liệu.
8. Kết quả AI phát hiện mơ hồ.
9. Coverage so với acceptance score.
10. Mutation score trước/sau.
11. Ví dụ test giả mạnh và counterexample.
12. Phân tích survivor.
13. Mô hình phân tách trách nhiệm.
14. Giới hạn và khuyến nghị.
15. Kết luận/Q&A.

## 14. Gói bàn giao

Theo đề cương môn học, hai sản phẩm nộp chính thức là:

1. Bài luận PDF 12–18 trang, font 13.
2. Slide PDF/PPTX tối đa 15 trang cho 15 phút trình bày và 5 phút hỏi đáp.

Đối với Chủ đề 7, repository mã nguồn không được gọi là “sản phẩm nộp thứ ba” trong quy định chung, nhưng thực tế là **bằng chứng thực nghiệm bắt buộc** để mutation score, test và số liệu có thể truy vết. Vì vậy nhóm nên nộp hoặc đính kèm link/ZIP repository gồm source code, tests, prompt/transcript, raw logs, CSV, script tái lập và dependency lockfile.

## 15. Definition of Done

Đồ án chỉ hoàn thành khi:

- oracle được commit trước các AI run;
- có ít nhất 3 run độc lập, khuyến nghị 6;
- lưu đầy đủ prompt, phản hồi và metadata;
- chạy được test AI-only và test độc lập tách biệt;
- có property-based tests và hai báo cáo mutation tương ứng;
- có raw/adjusted mutation score và review survivor/equivalent;
- có bằng chứng ít nhất một giả định sai hoặc báo cáo trung thực nếu không quan sát được;
- phân tích cụ thể test “giả mạnh”, không chỉ nêu lý thuyết;
- bảng/biểu đồ được sinh từ dữ liệu thô;
- bài luận đủ cấu trúc, ít nhất 8 nguồn với ít nhất 3 nguồn học thuật/khảo sát lớn;
- phụ lục công khai việc sử dụng AI và cho phép truy vết mọi số liệu;
- slide không quá 15 trang và trình bày được trong 15 phút.
