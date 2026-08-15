Dưới đây là bản định dạng Markdown đã được gỡ bỏ toàn bộ các biểu tượng (icon):

---

# Chủ đề 7: Kiểm thử và kiểm chứng khi AI viết cả code lẫn test

**Câu hỏi trung tâm:**

> *Làm sao phá vỡ vòng lặp "AI hiểu sai yêu cầu → viết code sai → viết test chứng minh code sai là đúng"?*

### Bối cảnh cần khảo cứu

* **Hiện tượng "ảo tưởng kiểm thử":** Bộ test tuy đầy đủ (coverage cao) nhưng lại được xây dựng dựa trên cùng một giả định sai lệch ban đầu.
* **Vai trò của kiểm chứng độc lập:** Ứng dụng các phương pháp nâng cao như *Property-based testing* và *Mutation testing*.
* **Lớp chốt chặn của con người:** Tầm quan trọng của các tiêu chí nghiệm thu (acceptance criteria) do chính con người định nghĩa.

### Việc nhóm cần thực hiện

1. **Thử nghiệm với yêu cầu mơ hồ:** Chuẩn bị một yêu cầu cố tình thiếu rõ ràng, yêu cầu AI tự sinh cả code hiện thực (implementation) lẫn test case, sau đó quan sát xem AI có phát hiện/cảnh báo được sự mơ hồ đó không.
2. **Đo lường độ tin cậy của test:** Áp dụng *Mutation testing* hoặc *Property-based testing* lên chính bộ test do AI sinh ra để đo lường tỷ lệ phát hiện lỗi (fault-detection rate).
3. **Đề xuất quy trình mới:** Xây dựng mô hình phân tách trách nhiệm rõ ràng:
* *Ai viết đặc tả yêu cầu?*
* *Ai viết test?*
* *Ai viết code?*



### Sản phẩm đặc thù (Deliverables)

* **Báo cáo Mutation score:** Đánh giá độ hiệu quả của bộ test.
* **Phân tích các test "giả mạnh":** Chỉ ra các test case trông có vẻ chặt chẽ nhưng thực chất không bắt được lỗi cốt lõi.