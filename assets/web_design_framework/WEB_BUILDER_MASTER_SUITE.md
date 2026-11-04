# WINK WEB BUILDER MASTER SUITE & DESIGN REPOSITORY ENGINE
> **Mục đích:** Bộ tài liệu chuẩn hóa toàn bộ công nghệ, quy tắc UI/UX, thư viện mã nguồn và kho repo GitHub được tuyển chọn để AI và nhà phát triển sử dụng ngay khi xây dựng sản phẩm web chuyển đổi cao.

---

## 1. Danh Mục Các Repo GitHub Cốt Lõi (Đã Kiểm Định & Tích Hợp)

| Tên Repo | Tác Giả / Nguồn | Điểm Mạnh & Mục Đích Sử Dụng |
|---|---|---|
| **[huashu-design](https://github.com/alchaincyf/huashu-design)** | `alchaincyf` | Huashu Design 3.0: 84 phong cách thẩm mỹ, hệ thống khám sức khỏe thiết kế (design checkup), sinh giao diện HTML-native không bị AI Slop. |
| **[ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** | `nextlevelbuilder` | Design intelligence cho UI/UX đa nền tảng: quy tắc lưới (grid), hệ số tỉ lệ vàng, phối màu cảm xúc (color psychology). |
| **[hallmark](https://github.com/Nutlope/hallmark)** | `Nutlope` | Bộ quy tắc cấm kỵ (Anti-AI-slop): Cấm nền đen xì vô hồn, cấm font chia glyph diacritics, cấm card thụ động không hành động, kiểm soát độ tương phản WCAG AAA. |
| **[auto-animate](https://github.com/formkit/auto-animate)** | `formkit` | Thư viện chuyển động 0-config, tự động làm mượt mà giỏ hàng (Cart Drawer), danh sách sản phẩm, modal popup mà không cần cấu hình phức tạp. |
| **[video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)** | `Vincentwei1021` | Remotion video generator: 124 shot recipes, render video quảng cáo chuyển đổi cao tự động bằng code. |
| **[Agent-Reach](https://github.com/Panniantong/Agent-Reach)** | `Panniantong` | Công cụ cào và nghiên cứu nội dung đa nền tảng (TikTok, XiaoHongShu, Reddit, X) miễn phí API. |
| **[HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter)** | `eternity4719` | Kho tri thức sức khỏe, phòng bệnh, trường thọ dựa trên nghiên cứu khoa học và Đông Y chuẩn mực. |

---

## 2. Thư Viện Cảm Hứng & Trực Quan Hóa (Design Reference Vault)

1. **[MotionSites AI (motionsites.ai)](https://motionsites.ai/):**
   - Phong cách: **Botanical Symbiosis (Cộng Sinh Thảo Mộc)**.
   - Thẩm mỹ: Sang trọng, hoa lá tươi sáng, cánh hoa bay lượn (floating petals), kết hợp giữa giải phẫu cơ thể học và thảo dược tự nhiên.
2. **[GetLayers AI (getlayers.ai)](https://www.getlayers.ai/):**
   - Phong cách: Obsidian & Emerald tương phản cao, thẻ kính mờ (glassmorphism), typography sắc sảo.
3. **[Pageflows (pageflows.com)](https://pageflows.com/):**
   - Kho mẫu luồng thanh toán (Checkout flow), giỏ hàng trượt (Cart drawer), bộ lọc sản phẩm từ các thương hiệu e-commerce hàng đầu thế giới (Aesop, Apple, Shopify, Glossier).
4. **[Lucian Labs (lucianlabs.com)](https://lucianlabs.com/):**
   - Phong cách tương tác vi mô (micro-interactions) giữa người và AI.

---

## 3. Quy Chuẩn Thiết Kế Cho Web Sức Khỏe & Dưỡng Sinh (Luminous Botanical Luxury)

### A. Bảng Màu Sáng Sủa & Hữu Cơ (Không Đen Xì)
- **Background chính:** `#fcfbf8` (Pearl Alabaster / Trắng ngọc trai ấm) kết hợp dải gradient mềm `#f4f8f5` (Morning Mist).
- **Surface Cards:** `rgba(255, 255, 255, 0.88)` kèm viền mềm `rgba(16, 185, 129, 0.16)` và bóng đổ sâu `0 20px 40px -15px rgba(16, 185, 129, 0.08)`.
- **Text Headings:** `#04261a` (Forest Obsidian - Đen ngọc sâu thẳm, cực kỳ sắc nét và tương phản 16:1).
- **Text Body:** `#2d4a3e` (Deep Sage - Dịu mắt, thanh lịch).
- **Accent Emerald & Mint:** `#059669` và `#10b981` (Thảo mộc xanh tươi, sinh lực).
- **Accent Rose & Amber:** `#f43f5e`, `#fb7185` (Cánh hoa mẫu đơn, hoa đào) và `#d97706` (Hoàng kỳ, mật ong).

### B. Quy Tắc Typography Tiếng Việt (Chống Lỗi Vỡ Chữ Glyph Splitting)
- **TUYỆT ĐỐI KHÔNG DÙNG:** `Cinzel`, `Cinzel Decorative`, `Trajan` cho tiếng Việt vì không có glyph dấu tiếng Việt (`ấ`, `ề`, `ự`, `ọ`), gây lỗi chữ "THẤ U", "TạNG".
- **FONTS CHUẨN:**
  - Tiêu đề sang trọng: `'Playfair Display', 'Cormorant Garamond', serif` (nạp kèm `&subset=vietnamese`).
  - Nội dung thanh thoát: `'Plus Jakarta Sans', -apple-system, sans-serif`.
  - Số liệu & Mã đơn: `'JetBrains Mono', monospace`.

---

## 4. Kiến Trúc E-Commerce Chuyển Đổi Cao (Checkout & Payment Matrix)

```
[Khách Làm Trắc Nghiệm 3D / Đọc Thử]
                 │
                 ▼
[Phát Hiện Thể Trạng: Khí Hư / Dương Hư / Đàm Thấp...]
                 │
                 ▼
[Gợi Ý Gói Combo Cá Nhân Hóa (Bán Trà Tặng Sách)]
                 │
                 ▼
[Thêm Vào Giỏ Hàng Trượt (Cart Drawer)]
                 │
                 ▼
[Trang Checkout 1 Bước Tích Hợp Đa Cổng Thanh Toán]
  ├── 1. Quét VietQR Napas 24/7 (Techcombank 1022 7786 86 - LE THI THANH MAI)
  │      └── Tự render mã QR với đúng số tiền và cú pháp đơn hàng + Nút mở app ngân hàng
  ├── 2. Thẻ Quốc Tế (Visa / Mastercard) qua Payoneer / Stripe
  └── 3. Ví Điện Tử MoMo / Cà Thẻ
```

---

## 5. Hướng Dẫn Vượt Duyệt Payoneer Cho Chủ Sở Hữu
Khi Payoneer yêu cầu URL doanh nghiệp trực tuyến (`myaccount.payoneer.com/ma/getpaid/paymentlink/url`):
1. Nhập URL chính của hệ sinh thái: `https://winkhere.com/` (Đã chạy thực tế trên Vercel).
2. Hoặc nhập trang landing page dưỡng sinh sau khi đẩy lên hosting.
3. Khi khách quốc tế thanh toán qua Visa trên Payoneer, phí xử lý giao dịch là **3.00%**. Thanh toán nội địa qua VietQR Techcombank là **0.00% (Miễn phí)**.
