# Reflection: Lab 18 - Production RAG

**Họ và tên:** Trần Bảo Phúc

## 1. Mapping Concept sang Code thực tế

- **M1 (Chunking):** 
  - *Hàm áp dụng:* `chunk_semantic`, `chunk_hierarchical`, `chunk_structure_aware`.
  - *Bài học:* Không phải lúc nào chunk nhỏ cũng tốt. `chunk_hierarchical` với Parent-Child strategy mang lại sự kết hợp tốt nhất (Retrieve child nhỏ để có độ chính xác cao, đưa parent lớn vào LLM để giữ trọn ngữ cảnh bao quát).
- **M2 (Hybrid Search):**
  - *Hàm áp dụng:* `HybridSearch.search()`, `reciprocal_rank_fusion()`.
  - *Bài học:* Tiếng Việt cần phải token hóa cẩn thận (`underthesea`) và đổi `_` thành space thì thuật toán BM25 mới hoạt động tốt, không bị miss keyword.
- **M3 (Reranking):**
  - *Hàm áp dụng:* `CrossEncoderReranker.rerank()`.
  - *Bài học:* Reranker như `BAAI/bge-reranker-v2-m3` siêu chính xác nhưng tính toán rất tốn kém thời gian. Việc lấy TOP_K=20 của Hybrid trước rồi mới Rerank lấy TOP_K=3 là thiết kế cực kỳ hợp lý để cân bằng giữa Performance và Latency.
- **M4 (Evaluation):**
  - *Hàm áp dụng:* `evaluate_ragas()`, `failure_analysis()`.
  - *Bài học:* Phương pháp RAGAS và sử dụng Diagnostic Tree làm kim chỉ nam rất giá trị. Nhờ biết rõ Context Recall thấp hay Answer Relevancy thấp, ta có thể nhanh chóng sửa đúng lỗi ở M1 (Chunking) hay M5 (Prompting) thay vì sửa mò.
- **M5 (Enrichment):**
  - *Hàm áp dụng:* `enrich_chunks()` (với chế độ _enrich_single_call).
  - *Bài học:* Chạy LLM (Groq API) để sinh Metadata, HyQA và Contextual Prepend trong 1 API call JSON là kỹ thuật optimization cost tuyệt vời và đáng giá nhất khi đưa lên Production. 

## 2. Bug lớn nhất đã gặp và Cách debug

**Vấn đề:** 
Lỗi parse JSON khi tích hợp mô hình LLM thông qua Groq (ví dụ `llama-3.3-70b-versatile`) ở phần M5 Enrichment. LLM đôi khi chèn markdown format `` ```json ... ``` `` bọc ngoài string, làm cho hàm `json.loads` bị crash toàn bộ pipeline.

**Cách khắc phục:**
Viết code tiền xử lý (pre-processing) để tự động check và loại bỏ chuỗi ` ```json ` ở đầu và ` ``` ` ở cuối nếu có. Đồng thời chỉnh lại logic merge metadata `{**auto_meta, **chunk.get("metadata", {})}` để metadata mới từ LLM không vô tình đè mất key `"source"` gốc.

## 3. Action Plan áp dụng vào project sắp tới

1. **Triển khai ngay Hybrid Search + RRF:** Khả năng mix giữa keyword-exact match (BM25) và semantic match (Dense) là "no-brainer" cho hầu hết các search system doanh nghiệp nội bộ hiện nay.
2. **Contextual Prepend M5:** Tôi sẽ đưa kĩ thuật này vào luồng nhập liệu chuẩn. Rất dễ làm nhưng giảm thiểu hẳn bệnh "mất bối cảnh đoạn văn".
3. **Data-Driven Tuning bằng RAGAS:** Dừng việc tuning prompt dựa trên cảm tính. Sẽ dựng tự động kịch bản eval RAGAS để đo đạc chỉ số trước, ra quyết định sau.
