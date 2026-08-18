# Failure Analysis — Lab 18: Production RAG

**Nhóm:** Cá nhân  
**Thành viên:** Trần Bảo Phúc

---

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|--------|---------------|------------|---|
| Faithfulness | 0.8333 | 0.6976 | -0.1357 |
| Answer Relevancy | nan | nan | +nan |
| Context Precision | 0.9375 | 0.9458 | +0.0083 |
| Context Recall | 0.9083 | 0.8667 | -0.0417 |

## Bottom-5 Failures

### #1
- **Question:** Chính sách thai sản cho nam nhân viên là bao nhiêu ngày?
- **Expected:** Nam nhân viên được nghỉ 10 ngày làm việc.
- **Got:** Không tìm thấy thông tin.
- **Worst metric:** context_recall
- **Error Tree:** Output sai → Context đúng? (Không, thiếu context) → Query OK? (Có)
- **Root cause:** Chunking size (M1) bị cắt lỡ cỡ làm tách mất đoạn thai sản của nam nhân viên khỏi đoạn policy chính.
- **Suggested fix:** Cải thiện `SEMANTIC_THRESHOLD` trong chunk_semantic để gom cụm tốt hơn, hoặc tích hợp HyQA (M5) để sinh câu hỏi "Chính sách thai sản nam" lưu vào index.

### #2
- **Question:** Làm sao để đổi mật khẩu VPN?
- **Expected:** Gửi email tới IT helpdesk với tiêu đề "VPN Reset".
- **Got:** Mật khẩu thay đổi mỗi 90 ngày.
- **Worst metric:** answer_relevancy
- **Error Tree:** Output sai → Context đúng? (Có chứa kết quả) → Query OK? (Có)
- **Root cause:** Prompt cho LLM chưa chặt, dẫn tới LLM hiểu nhầm sang thời hạn mật khẩu thay vì quy trình reset.
- **Suggested fix:** Cải thiện prompt template ở `run_query`: yêu cầu "Chỉ trả lời hành động/quy trình được hỏi".

### #3
- **Question:** Công ty có phụ cấp ăn trưa không?
- **Expected:** Phụ cấp ăn trưa 50.000đ/ngày.
- **Got:** Phụ cấp ăn trưa 50k và phụ cấp đi lại 30k.
- **Worst metric:** faithfulness
- **Error Tree:** Output sai → Context đúng? (Đúng, chỉ nói ăn trưa) → Query OK? (Có)
- **Root cause:** LLM tự hallucinate thêm thông tin "phụ cấp đi lại" do bản năng tự hoàn thiện của model lớn.
- **Suggested fix:** Set parameter `temperature=0` khi gọi Groq API và thêm hướng dẫn nghiêm ngặt "KHÔNG thêm thông tin ngoài lề".

### #4
- **Question:** Vị trí Dev có mấy vòng phỏng vấn?
- **Expected:** Tùy cấp độ, thường 2-3 vòng.
- **Got:** 3 vòng phỏng vấn.
- **Worst metric:** context_precision
- **Error Tree:** Output sai → Context đúng? (Có quá nhiều nhiễu)
- **Root cause:** Hybrid Search trả về 20 chunks nhưng phần lớn là thông tin tuyển dụng phòng ban khác, gây nhiễu cho LLM.
- **Suggested fix:** Kích hoạt triệt để `CrossEncoderReranker` (M3) để đẩy các chunks không chính xác hẳn xuống dưới, lấy TOP_K=3.

### #5
- **Question:** Ngày thành lập công ty là khi nào?
- **Expected:** 01/01/2010.
- **Got:** Công ty VinUni thành lập năm 2010.
- **Worst metric:** answer_relevancy
- **Error Tree:** Output sai → Context đúng? (Đúng)
- **Root cause:** Câu trả lời của LLM dài dòng so với ground truth ngắn gọn.
- **Suggested fix:** Cập nhật prompt: "Trả lời cực kỳ ngắn gọn, trực diện, không dài dòng".

## Case Study (cho presentation)

**Question chọn phân tích:** Chính sách thai sản cho nam nhân viên là bao nhiêu ngày?

**Error Tree walkthrough:**
1. Output đúng? → Không, mô hình báo không tìm thấy.
2. Context đúng? → Sai, context thiếu đoạn có chứa "10 ngày".
3. Query rewrite OK? → Truy vấn trực tiếp đủ rõ.
4. Fix ở bước: **Retrieval (M1 & M2)**

**Nếu có thêm 1 giờ, sẽ optimize:**
- Viết regex đặc thù (Structure-aware chunking) để phát hiện và giữ nguyên các block List/Quy định, không cho phép cắt ngang một khoản luật.
- Kích hoạt kỹ thuật `contextual_prepend` (M5) cho toàn bộ tập dữ liệu.
