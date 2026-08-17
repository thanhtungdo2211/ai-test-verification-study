# Experiment candidate run-03

## Mục tiêu

Thực hiện AI candidate run-03 theo prompt mơ hồ đã freeze và bàn giao bằng một
PR độc lập.

## Người thực hiện

- Operator: `<điền tên thành viên>`
- Tool/model: ghi đúng thông tin hiển thị trong metadata

## Quy tắc bắt buộc

- Dùng cuộc trò chuyện AI mới và context sạch.
- Không gửi repository, hidden oracle, `tests_independent/` hoặc kết quả run khác cho AI.
- Gửi đúng prompt trong `experiments/prompts/ambiguous-requirement.txt`.
- Chỉ dùng follow-up chuẩn nếu AI hỏi làm rõ.
- Lưu raw transcript trước khi tạo candidate files.
- Không sửa business logic, exception, rounding hoặc expected values.

## Definition of Done

- [ ] Có `candidates/run-03/` đầy đủ.
- [ ] Có `experiments/transcripts/run-03.response.txt` nguyên trạng.
- [ ] Có một dòng run-03 trong `experiments/metadata.csv`.
- [ ] Có packaging patch riêng nếu cần; không có patch logic.
- [ ] Có checksum raw transcript.
- [ ] Đã mở PR branch `candidate/run-03`.
- [ ] PR dùng body template và liên kết issue này.

## Không làm trong issue này

Không chạy independent evaluation để sửa candidate và không kết luận coverage,
acceptance hoặc mutation trước khi maintainer đánh giá sau merge.

