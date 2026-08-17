# Evaluation runbook: từ candidate đến mutation score

Dùng runbook này sau khi `run-01`, `run-02`, … đã được merge vào `master` hoặc
đã có trong cùng một clean checkout. Người chạy đánh giá không sửa candidate,
AI tests, oracle hoặc raw logs. Mỗi `run-XX` phải dùng đúng cùng ID trong
`candidates/`, `results/`, `experiments/metadata.csv` và report.

## 0. Kiểm tra trước khi chạy

```bash
git switch master
git pull --ff-only origin master
uv sync --locked
```

Nếu `uv` không thể tải dependency trong môi trường hiện tại, dùng virtualenv
đã cài sẵn thay cho `uv run`:

```bash
./.venv/bin/python --version
```

Kiểm tra oracle/reference trước khi mở candidate:

```bash
uv run python scripts/check_independent.py
```

Kết quả phải cho biết reference implementation pass và ba deliberate faulty
fixtures đều bị phát hiện. Nếu gate này fail, dừng đánh giá và báo người phụ
trách oracle.

## 1. Điều kiện dữ liệu

Trước khi aggregate, thêm một dòng metadata thật cho từng candidate vào
`experiments/metadata.csv`. Không điền tool/model/timestamp/operator bằng cách
đoán. Ví dụ cấu trúc dòng:

```text
run-02,<tool>,<model>,<started_utc>,<ended_utc>,yes,no,0,no,<human_edits>,experiments/transcripts/run-02.response.txt,experiments/transcripts/run-02.response.txt,<operator>
```

Nếu transcript hoặc run không đầy đủ, ghi rõ trạng thái trong candidate
README/decision log; không biến missing evidence thành số 0. Kiểm tra:

```bash
uv run topic7 validate-data
```

## 2. Baseline AI-only

Chạy từng run một lần. Ví dụ với `run-01` và `run-02`:

```bash
uv run python scripts/run_tests.py --candidate run-01 --suite ai-only
uv run python scripts/run_tests.py --candidate run-02 --suite ai-only
```

Output tương ứng:

```text
results/baseline/run-01/
results/baseline/run-02/
```

Mỗi thư mục có `pytest.log`, `junit.xml`, `coverage.json` và `manifest.json`.
Đọc manifest để lấy số test pass/fail, line coverage và branch coverage.

Nếu lệnh trả lỗi, vẫn giữ evidence đã tạo. Không xóa để chạy lại vào cùng thư
mục. Ghi nguyên nhân và, nếu cần một lần chạy lại sau khi sửa packaging/tooling,
dùng thư mục attempt riêng theo decision log.

## 3. Baseline full suite

`full` chạy cả AI-generated tests và `tests_independent`:

```bash
uv run python scripts/run_tests.py --candidate run-01 --suite full
uv run python scripts/run_tests.py --candidate run-02 --suite full
```

Output nằm ở:

```text
results/baseline/run-01/full/
results/baseline/run-02/full/
```

Đây là bước cho biết independent acceptance/property tests có tìm ra hành vi
khác oracle hay không. Candidate có thể pass AI-only nhưng fail full; không sửa
candidate sau khi thấy failure.

## 4. Mutation testing với AI-only tests

Chỉ chạy mutation khi baseline AI-only của candidate đã kết thúc thành công:

```bash
uv run python scripts/run_mutation.py --candidate run-01 --suite ai-only
uv run python scripts/run_mutation.py --candidate run-02 --suite ai-only
```

Output:

```text
results/mutation-ai-only/run-01/
results/mutation-ai-only/run-02/
```

Các file chính:

- `manifest.json`: tổng số mutant và các trạng thái;
- `mutmut-cicd-stats.json`: raw counters từ mutmut;
- `results.txt`: trạng thái từng mutant;
- `baseline.log`, `mutation.log`: log tái lập.

Raw AI-only mutation score được tính tự động:

```text
raw_score_ai = killed_ai / mutants_total_ai × 100
```

Ví dụ `run-01`: `35 / 51 × 100 = 68.63%`.

`survived`, `timeout` và `error` không được tính là killed.

## 5. Mutation testing với full suite

Sau khi full baseline đã pass, chạy:

```bash
uv run python scripts/run_mutation.py --candidate run-01 --suite full
uv run python scripts/run_mutation.py --candidate run-02 --suite full
```

Wrapper lưu kết quả full suite tại:

```text
results/mutation-independent/run-01/
results/mutation-independent/run-02/
```

Tên thư mục là `mutation-independent` vì suite full có thêm independent
tests. Nếu full baseline fail, mutation full sẽ không chạy; manifest phải được
giữ lại và các cột `*_full` sẽ để trống.

## 6. Sinh bảng và biểu đồ

Sau khi tất cả raw baseline/mutation evidence của các run hiện có đã xong:

```bash
uv run python scripts/aggregate_results.py --force
```

Lệnh này đọc metadata và raw manifests, rồi sinh:

```text
results/measurements.csv
results/figures/mutation-scores.svg
results/figures/coverage-acceptance.svg
results/figures/property-failures.svg
results/figures/mutation-survivors.svg
results/figures/acceptance-score.svg
```

Không sửa tay các file generated. Kiểm tra lại:

```bash
uv run topic7 validate-data
```

## 7. Review survivor/equivalent mutant

`raw_score_*` có thể báo ngay sau mutation run. `adjusted_score_*` chỉ được
chấp nhận sau khi một người review survivor và người thứ hai kiểm tra lại.
Với từng survivor, ghi loại lỗi (validation, min/max, discount order, rounding,
boundary, other), counterexample nếu có và lý do equivalent/unreachable nếu
được phân loại như vậy. Không xóa mutant khỏi raw `results.txt` và không sửa
manifest raw.

Nếu chưa có review equivalent được lưu theo format nhóm thống nhất, để
`equivalent_*` và `adjusted_score_*` trống; không tự đặt chúng bằng `0`.

## 8. Kiểm tra cuối và báo cáo

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run topic7 validate-data
```

Khi viết báo cáo, lấy số từ `results/measurements.csv` nhưng dẫn ngược được từ
mỗi dòng tới manifest/log/transcript. Với mỗi run tối thiểu báo cáo:

- AI tests collected/passed;
- line/branch coverage;
- acceptance và property failures;
- `raw_score_ai` và `raw_score_full` nếu có;
- killed/survived/timeout/error;
- adjusted score chỉ khi equivalent review đã được phê duyệt.

