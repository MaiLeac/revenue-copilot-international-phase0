# TikTok Knowledge Mining System — Architecture & Data Schema

## 1. Mục Tiêu Cốt Lõi
Tái dựng hoàn chỉnh **Hệ Thống Tư Duy (Thinking Framework)** của tác giả, thay vì tóm tắt video rời rạc:
* Những nguyên lý nền tảng được tác giả tin tưởng.
* Phương pháp phân tích, chọn cổ phiếu/tài sản và quản trị rủi ro.
* Những quan điểm nhất quán vs. quan điểm thay đổi theo chu kỳ thị trường.
* Phân loại phát biểu thành 4 nhóm để kiểm chứng độc lập.

---

## 2. Phân Loại 4 Tầng Tri Thức (Knowledge Taxonomy)

1. **Kiến thức nền (First-Principles Economics & Probability):**
   - Các nguyên lý toán học, tài chính, kinh tế học vi mô/vĩ mô đã được giới học thuật kiểm chứng độc lập (Expected Value, Law of Large Numbers, Market Regimes, Macro Liquidity).
2. **Phương pháp cá nhân (Proprietary Methodologies):**
   - Cách tác giả định giá doanh nghiệp, nhận diện chu kỳ, lọc cổ phiếu, căn điểm vào/ra, thiết lập tỷ lệ R:R và phân bổ tỷ trọng danh mục.
3. **Kinh nghiệm thực chiến (Battle Scars & Case Studies):**
   - Những bài học từ các thương vụ thực tế, các sai lầm đau đớn trong quá khứ, cách tác giả sống sót qua các cú sập thị trường (2008, 2020, 2022).
4. **Quan điểm chưa kiểm chứng (Unverified Opinions & Anecdotes):**
   - Những dự đoán tương lai, nhận định chủ quan, kinh nghiệm truyền miệng từ các "anh lớn" mà chưa có số liệu thống kê hoặc dữ liệu lịch sử đối chiếu.

---

## 3. Cấu Trúc Bản Ghi Tri Thức Video (Structured Knowledge Record)

Mỗi video được bóc tách thành một cấu trúc dữ liệu chuẩn:

```json
{
  "video_id": "7123456789012345678",
  "url": "https://www.tiktok.com/@creator/video/7123456789012345678",
  "posted_at": "2026-05-15T14:30:00Z",
  "title_or_caption": "Tại sao 90% trader phá sản vì không hiểu kỳ vọng toán học?",
  "duration_sec": 145,
  "topic": "Xác suất & Quản trị rủi ro",
  "core_claims": [
    {
      "claim": "Không cần đoán đúng mọi lần để có lợi nhuận bền vững.",
      "reasoning": "Lợi nhuận ròng là hàm số của xác suất thắng nhân với tỷ lệ lời/lỗ trung bình trừ đi chi phí giao dịch.",
      "conditions_of_applicability": "Chỉ đúng khi có lợi thế thống kê (Edge) và tuân thủ kỷ luật dừng lỗ tuyệt đối.",
      "concrete_example": "Ví dụ tung đồng xu có tỷ lệ 40% nhưng ăn 3 mất 1.",
      "timestamp_marker": "00:45 - 01:20",
      "statement_type": "Nguyên lý | Kinh nghiệm | Quan điểm | Dự đoán",
      "verifiability_tier": "Kiến thức nền | Phương pháp cá nhân | Kinh nghiệm thực chiến | Quan điểm chưa kiểm chứng"
    }
  ]
}
```

---

## 4. Ba Tài Sản Đầu Ra (Research Brain Outputs)

1. **Knowledge Base (`KNOWLEDGE_BASE.md`):** Toàn bộ cơ sở dữ liệu các luận điểm trích xuất từ tất cả video, đánh chỉ mục theo chủ đề và gắn link nguồn + timestamp.
2. **Thinking Framework (`THINKING_FRAMEWORK.md`):** Bản đồ tư duy tổng hợp thế giới quan đầu tư của tác giả: nguyên lý cốt lõi, ma trận ra quyết định, các mâu thuẫn/thay đổi quan điểm theo thời gian.
3. **Trading Research (`TESTABLE_HYPOTHESES.md`):** Danh sách các giả thuyết định lượng hoặc quy tắc quản trị rủi ro có thể chuyển hóa thành code để kiểm chứng trên tài khoản MT5 Demo.
