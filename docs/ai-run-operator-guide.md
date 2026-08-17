# Hướng dẫn thành viên thực hiện AI run (`run-02`–`run-06`)

Tài liệu này dành cho thành viên đóng vai trò **AI Operator**. Mục tiêu là tạo
một candidate độc lập, lưu đủ bằng chứng và bàn giao để nhóm chạy baseline,
independent tests, coverage và mutation testing. Thành viên thực hiện run không
được sửa logic do AI sinh và không được xem hidden oracle hoặc test độc lập
trước khi phần sinh candidate hoàn tất.

## 1. Trước khi mở AI

Mỗi run phải dùng một cuộc trò chuyện mới, không dùng lại context của run khác.
Chọn đúng một ID chưa dùng: `run-02`, `run-03`, … `run-06`.

Ghi các thông tin sau trước khi gửi prompt:

- `run_id`: ví dụ `run-02`;
- công cụ AI và model/version đang hiển thị;
- thời điểm bắt đầu theo UTC, dạng ISO 8601, ví dụ `2026-08-16T08:00:00Z`;
- tên operator;
- xác nhận context sạch (`context_clean=yes`).

Không gửi cho AI repository, thư mục `candidates/`, hidden oracle,
`tests_independent/`, kết quả `run-01`, hoặc câu hỏi bổ sung. Chỉ gửi prompt
dưới đây, nguyên văn và không thêm lời mở đầu.

## 2. Prompt bắt buộc

```text
Create a Python function `calculate_transfer_fee(amount_vnd, is_vip=False)`. The transfer fee is 1% of the transferred amount, with a minimum of 5,000 VND and a maximum of 50,000 VND. VIP customers receive a 20% discount. Round the fee to the nearest 1,000 VND. Invalid amounts must be rejected. Provide the implementation and a complete pytest test suite.
```

Nếu AI **không** hỏi làm rõ, không gửi thêm tin nhắn nào.

Nếu AI hỏi làm rõ, chỉ gửi đúng câu sau:

```text
Proceed with reasonable assumptions and record every assumption in ASSUMPTIONS.md.
```

Không tự trả lời câu hỏi về kiểu dữ liệu, thứ tự discount/rounding, exception
hoặc các quy tắc khác. Ghi nhận `clarification_asked=yes` và
`followup_used=yes`; đếm số điểm mơ hồ mà AI đã hỏi vào
`ambiguities_detected`. Nếu AI không hỏi, ghi cả hai trường là `no` và không
bổ sung giả định cho AI.

## 3. Lưu raw transcript trước

Sau khi AI trả lời xong, lưu nguyên trạng toàn bộ cuộc trò chuyện (prompt,
câu hỏi làm rõ nếu có, follow-up và câu trả lời cuối) vào:

```text
experiments/transcripts/run-02.response.txt
```

Đổi `run-02` thành ID của run. Không chỉnh sửa, rút gọn, định dạng lại hoặc
xóa code fence trong file raw. Nếu công cụ có chức năng export transcript, ưu
tiên dùng file export đó rồi giữ bản raw này làm bằng chứng.

Tạo checksum và gửi checksum cùng bàn giao:

```bash
sha256sum experiments/transcripts/run-02.response.txt
```

## 4. Đóng gói candidate

Từ raw response, sắp xếp code vào đúng layout sau. Nội dung implementation và
AI tests phải được giữ nguyên như AI trả lời:

```text
candidates/run-02/
├── src/transfer_fee/calculator.py
├── src/transfer_fee/__init__.py
├── tests_ai/test_calculator.py
├── ASSUMPTIONS.md
└── README.md
```

Quy tắc:

1. Không sửa thuật toán, kiểu exception, expected value, tên test hoặc test
   case do AI sinh.
2. Nếu AI đã cung cấp `ASSUMPTIONS.md`, lưu nguyên trạng.
3. Nếu AI không cung cấp file assumptions, tạo một file ngắn ghi rõ rằng
   response không có `ASSUMPTIONS.md`; không tự biến cách hiểu của operator
   thành giả định của AI.
4. Nếu chỉ thiếu package initializer khiến import không chạy, có thể thêm
   packaging-only `__init__.py`. Không thêm business logic. Lưu diff vào
   `experiments/packaging-fixes/run-02-init.patch` và ghi lý do trong
   `experiments/packaging-fixes.csv`.
5. Nếu câu trả lời thiếu file, có nhiều implementation khác nhau, hoặc không
   thể đóng gói mà không sửa logic, giữ nguyên raw response, đánh dấu
   candidate là `non-executable` trong README và bàn giao; không tự chọn hoặc
   viết lại một phương án.

`README.md` của candidate phải ghi tối thiểu:

- run ID, tool, model hiển thị, operator, thời điểm bắt đầu/kết thúc UTC;
- đường dẫn transcript và raw-response checksum;
- `clarification_asked`, `ambiguities_detected`, `followup_used`;
- mọi packaging-only fix hoặc ghi rõ không có fix;
- số lần con người sửa nội dung (không tính việc sao chép file vào layout).

## 5. Metadata phải gửi kèm

Thêm **một dòng**, không sửa các dòng run trước, vào
`experiments/metadata.csv`:

```text
run-02,<tool>,<model_displayed>,<started_at_utc>,<ended_at_utc>,yes,<yes_or_no>,<integer_or_NA>,<yes_or_no>,<integer>,experiments/transcripts/run-02.response.txt,experiments/transcripts/run-02.response.txt,<operator>
```

Thay toàn bộ placeholder bằng dữ liệu thật. `human_edits` phải phản ánh can
thiệp thực tế; packaging-only fix vẫn phải mô tả riêng trong
`packaging-fixes.csv`. Không đoán model hoặc timestamp sau khi run đã kết thúc.

## 6. Cách bàn giao qua GitHub PR

Không dùng ảnh chụp làm artifact chính. Mỗi run cần một branch và một PR riêng;
PR phải chứa candidate, raw transcript, metadata và packaging patch nếu có.
Xem quy trình chi tiết, lệnh `gh`, issue body và PR template tại
[github-candidate-pr-workflow.md](github-candidate-pr-workflow.md).

Người đánh giá sẽ dùng đúng run ID để chạy các bước tiếp theo. Operator không
được chạy hoặc xem hidden acceptance oracle để chỉnh candidate trước khi bàn
giao.

## 7. Checklist trước khi gửi

- [ ] Đúng run ID và context sạch.
- [ ] Đã gửi đúng prompt, không thêm thông tin.
- [ ] Nếu AI hỏi, đã dùng đúng follow-up chuẩn duy nhất.
- [ ] Raw transcript đã lưu trước khi tách file.
- [ ] Candidate không bị sửa business logic hoặc expected value.
- [ ] Có `ASSUMPTIONS.md` hoặc ghi nhận rõ AI không cung cấp file.
- [ ] Có README, checksum và metadata đầy đủ.
- [ ] Packaging-only fix (nếu có) có patch và lý do riêng.
- [ ] Đã bàn giao toàn bộ thư mục/file, không chỉ kết quả tóm tắt.
