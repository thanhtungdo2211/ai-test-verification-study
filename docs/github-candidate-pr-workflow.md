# Quy trình GitHub Issue/PR cho candidate AI

Dùng quy trình này để nhận `run-02` và `run-03` từ các thành viên. Mỗi run có
một issue và một PR riêng; không gửi ảnh chụp hoặc chỉ gửi file
`calculator.py`. PR là nơi lưu bằng chứng, review và truy vết thay đổi.

## Mô hình làm việc

| Người | Việc cần làm |
|---|---|
| Maintainer | Tạo issue, cấp `run_id`, review PR và sau đó chạy đánh giá |
| AI Operator | Chạy prompt trong context sạch, lưu transcript, đóng gói candidate và mở PR |
| Reviewer | Kiểm tra protocol/evidence; không sửa logic AI trong PR |

Chỉ mở PR khi đã có artifact thật. Không mở PR rỗng hoặc tạo code mẫu để giữ
chỗ. Mỗi PR chỉ chứa một run:

```text
PR candidate/run-02  -> candidates/run-02 + transcript + metadata
PR candidate/run-03  -> candidates/run-03 + transcript + metadata
```

## A. Maintainer tạo issue

Sau khi `gh auth status` báo tài khoản hợp lệ, chạy từ repository root:

```bash
gh issue create \
  --title "Experiment candidate run-02" \
  --body-file docs/github-issues/run-02.md

gh issue create \
  --title "Experiment candidate run-03" \
  --body-file docs/github-issues/run-03.md
```

Ghi lại số issue được GitHub trả về. Số đó sẽ được đặt vào PR body ở dạng
`Closes #<issue-number>`.

## B. Thành viên tạo candidate và branch

Thành viên phải dùng clone sạch, cập nhật `master`, rồi tạo branch riêng:

```bash
git switch master
git pull --ff-only origin master
git switch -c candidate/run-02
```

Đổi `run-02` thành ID được cấp. Không dùng lại branch của run khác và không
đưa repository/oracle/tests độc lập vào cuộc trò chuyện AI.

Thực hiện đúng các bước trong
[ai-run-operator-guide.md](ai-run-operator-guide.md): context mới, prompt
đóng băng, follow-up chuẩn nếu AI hỏi, lưu raw transcript trước khi tách file,
và không sửa business logic hoặc expected value.

## C. Kiểm tra trước khi commit

Candidate phải có layout:

```text
candidates/run-02/
├── src/transfer_fee/calculator.py
├── src/transfer_fee/__init__.py
├── tests_ai/test_calculator.py
├── ASSUMPTIONS.md
└── README.md
```

Ngoài ra, branch phải chứa:

```text
experiments/transcripts/run-02.response.txt
experiments/metadata.csv       # thêm đúng một dòng run-02
experiments/packaging-fixes.csv # chỉ khi có packaging fix
experiments/packaging-fixes/run-02-*.patch # nếu có
```

Chạy các kiểm tra không làm thay đổi artifact:

```bash
git diff --check
sha256sum experiments/transcripts/run-02.response.txt
git status --short
```

Không chạy independent oracle để chỉnh candidate. Nếu candidate không thể chạy
mà không sửa logic, ghi `candidate_status: non-executable` trong README và vẫn
bàn giao nguyên bằng chứng.

## D. Commit, push và mở PR

Thay `run-02` bằng run ID thật. Chỉ stage file thuộc run đó; không stage các
thay đổi của run khác:

```bash
git add candidates/run-02 \
  experiments/transcripts/run-02.response.txt \
  experiments/metadata.csv

# Chỉ thêm hai đường dẫn sau nếu branch thực sự có packaging fix.
git add experiments/packaging-fixes.csv \
  experiments/packaging-fixes/run-02-*.patch

git commit -m "experiment: add candidate run-02"
git push --set-upstream origin candidate/run-02
```

Mở PR bằng `gh`:

```bash
gh pr create \
  --base master \
  --head candidate/run-02 \
  --title "Experiment candidate run-02" \
  --body-file docs/github-pr-body-template.md
```

Trước khi gửi, thay các placeholder trong body template bằng run ID, issue
number, checksum, operator, model và trạng thái thực tế. Nếu body template
không nằm trong branch, copy nội dung của nó vào tùy chọn `--body` hoặc mở PR
trên GitHub và dán nội dung tương tự.

## E. Nội dung bắt buộc của PR

PR phải có:

- `Closes #<issue-number>`;
- run ID và operator;
- tool/model hiển thị, thời gian UTC;
- trạng thái clarification/follow-up và số ambiguity;
- đường dẫn raw transcript và SHA-256;
- xác nhận prompt được gửi nguyên văn trong context sạch;
- xác nhận implementation/test không bị sửa;
- mô tả packaging-only fix, hoặc `none`;
- `executable` hoặc `non-executable`;
- danh sách file chính trong PR.

Không ghi kết quả coverage, acceptance hoặc mutation vào PR nếu chưa được
maintainer chạy từ artifact đã merge. PR này là bước **thu thập candidate**,
không phải kết quả đánh giá.

## F. Review và merge

Maintainer kiểm tra theo thứ tự:

1. PR chỉ chứa đúng một `run_id` và không sửa oracle/independent tests.
2. Raw transcript có trước candidate files và không bị chỉnh sửa.
3. Metadata đầy đủ, timestamp là UTC, checksum khớp.
4. Mọi packaging-only fix có patch và lý do; không có sửa thuật toán.
5. README/ASSUMPTIONS phản ánh đúng response của AI.

Sau khi review đạt, maintainer merge PR. Chỉ sau đó mới chạy baseline,
independent suite, coverage, mutation và aggregate results trên branch chính.

## G. Nếu `gh` báo lỗi đăng nhập

Không dùng token của người khác. Maintainer hoặc operator tự xác thực trên máy
của mình:

```bash
gh auth status
gh auth login -h github.com
```

Sau đó kiểm tra lại quyền tạo issue/branch/PR. Nếu chưa có quyền repository,
hỏi maintainer cấp quyền trước khi thực hiện run; không gửi artifact qua ảnh
chụp thay thế cho PR.

