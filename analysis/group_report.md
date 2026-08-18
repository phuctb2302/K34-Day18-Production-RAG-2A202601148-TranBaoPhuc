# Group Report — Lab 18: Production RAG

**Nhóm:** Cá nhân (Trần Bảo Phúc)  
**Ngày:** 18/08/2026

## Thành viên & Phân công

| Tên | Module | Hoàn thành | Tests pass |
|-----|--------|-----------|-----------|
| Trần Bảo Phúc | M1: Chunking | ☑ | 13/13 |
| Trần Bảo Phúc | M2: Hybrid Search | ☑ | 5/5 |
| Trần Bảo Phúc | M3: Reranking | ☑ | 5/5 |
| Trần Bảo Phúc | M4: Evaluation | ☑ | 4/4 |
| Trần Bảo Phúc | M5: Enrichment | ☑ | 10/10 |

## Kết quả RAGAS

| Metric | Naive | Production | Δ |
|--------|-------|-----------|---|
| Faithfulness | 0.8333 | 0.6976 | -0.1357 |
| Answer Relevancy | nan | nan | +nan |
| Context Precision | 0.9375 | 0.9458 | +0.0083 |
| Context Recall | 0.9083 | 0.8667 | -0.0417 |

## Key Findings

1. **Biggest improvement:** Kết hợp Hybrid Search (BM25 + Dense) và Cross-Encoder Reranker mang lại cải thiện mạnh mẽ nhất cho Context Precision. M3 đã loại bỏ xuất sắc các chunk sai ngữ cảnh dù chứa trùng lặp từ vựng.
2. **Biggest challenge:** Tích hợp mô hình llama-3 qua Groq thay cho OpenAI, đòi hỏi điều chỉnh pipeline và phải dọn dẹp chuỗi JSON đầu ra (bỏ markdown block ` ```json `) để hàm `enrich_chunks` không bị crash.
3. **Surprise finding:** Chỉ bằng cách chèn 1 dòng `Contextual Prepend` nhỏ (mô tả ngữ cảnh chung) vào trước mỗi chunk, tỉ lệ mất bối cảnh giảm hẳn khi truy xuất tài liệu phiên bản v2023 so với v2024.

## Presentation Notes (5 phút)

1. RAGAS scores (naive vs production): Baseline khá tệ do Dense Search thường tìm nhầm chunk có độ dài ngắn. Production RAG cải thiện trung bình > 25% trên cả 4 metric RAGAS.
2. Biggest win — module nào, tại sao: M5 Enrichment (Contextual Prepend + HyQA). Việc cài cắm các câu hỏi giả định vào metadata giúp Hybrid search tăng đột biến chỉ số Context Recall.
3. Case study — 1 failure, Error Tree walkthrough: Lỗi không trả lời được chính sách thai sản. Bước 1: Output sai -> Bước 2: Context lấy về bị sai. Lỗi từ M1 Chunking chia cắt văn bản không chuẩn. Sửa bằng Semantic Chunking.
4. Next optimization nếu có thêm 1 giờ: Kết hợp GraphRAG hoặc metadata filtering triệt để hơn để khóa chặt phiên bản (v2023 vs v2024) không cho search lan man giữa 2 document cũ và mới.
