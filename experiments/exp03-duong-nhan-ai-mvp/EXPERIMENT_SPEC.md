# EXP-03 (`PROD-01`) — Dưỡng Nhan AI Companion & VietQR Funnel MVP

**Mô hình:** Sao chép cơ chế kinh doanh đã chứng minh dòng tiền của `biquyetduongnhan.vn` (`299.000₫` Impulse Buy + VietQR/SePay tự động + Affiliate KOC), đồng thời **giải quyết triệt để 3 lỗ hổng chí mạng của đối thủ** với chi phí vận hành **`0 VND`**.

---

## 1. Bảng Đối Chiếu: Đối Thủ (`biquyetduongnhan.vn`) vs. Bản Cải Tiến Của Ta (`EXP-03`)

| Hạng mục | Đối thủ (`biquyetduongnhan.vn`) | Bản cải tiến của Money HQ (`EXP-03 / PROD-01`) |
| :--- | :--- | :--- |
| **1. Phễu Lead Magnet (Trắc nghiệm 7 thể chất)** | Gửi khách sang link Claude Artifact rời rạc bên ngoài (`claude.ai/code/artifact/...`), dễ rớt khách giữa chừng. | **Tích hợp trực tiếp ngay trên trang (`index.html`):** Khách tick chọn triệu chứng trong 60 giây $\rightarrow$ Nhận chẩn đoán thể chất chủ đạo + thể chất kết hợp + **2 bài trà/chè mẫu miễn phí** ngay tại chỗ. |
| **2. Trải nghiệm tra cứu công thức** | Sách tĩnh 664 trang lật từng trang; khi bị mất ngủ, đau bụng kinh hay nổi mụn phải lướt tìm thủ công rất lâu. | **Trợ Lý Tra Cứu Triệu Chứng Tức Thì (`constitution_engine.py` + JS Search):** Gõ triệu chứng hoặc chọn thể chất $\rightarrow$ Lọc ngay công thức chuẩn định lượng + **Hộp cảnh báo kiêng kỵ an toàn (thai kỳ, dạ dày, huyết áp)** trong 3 giây (`0 VND` phí LLM). |
| **3. Quyền sở hữu & Trải nghiệm đọc/nghe** | Khóa cứng F12, cấm in, cấm tải PDF, khóa tài khoản nếu mở DevTools $\rightarrow$ gây ức chế cho người mua muốn in cho mẹ đọc hoặc xem offline. | **Đa định dạng thân thiện:** Vừa có Web App tra cứu nhanh, vừa cho tải **Sổ tay PDF chuẩn in ấn** + **Bản Audio Dưỡng Sinh** nghe khi đi bộ (tạo tự động bằng `edge-tts` miễn phí). |
| **4. Thanh toán & Affiliate KOC** | VietQR + SePay + cổng Affiliate. | **Tích hợp sẵn bộ tạo mã VietQR tự động kèm mã đơn & mã KOC (`?ref=KOC01`)** trong `constitution_engine.py` và modal thanh toán của `index.html`. |

---

## 2. Cấu Trúc Tài Sản Đã Xây Dựng Trong Repo

1. **Engine Chẩn Đoán & Tạo VietQR Tất Định (`0 VND` API Cost):**
   - [`assets/duong_nhan_engine/constitution_engine.py`](../../assets/duong_nhan_engine/constitution_engine.py): Chứa dữ liệu chuẩn hóa của **7 Thể Chất Đông Y** (*Huyết hư, Khí hư, Âm hư, Dương hư, Huyết ứ, Đàm thấp, Khí uất*), bộ công thức kèm cảnh báo kiêng kỵ (`contraindications`), hàm `diagnose_constitution()`, và hàm `build_vietqr_checkout_url()`.
2. **Web App Phễu Chuyển Đổi Trọn Gói (Zero-Cost Static Hosting Ready):**
   - [`experiments/exp03-duong-nhan-ai-mvp/index.html`](./index.html): Hoạt động độc lập 100% (có thể host miễn phí trên GitHub Pages / Cloudflare Pages với chi phí `0 VND`).
3. **Kiểm Thử Tự Động (`pytest`):**
   - [`tests/test_duong_nhan_engine.py`](../../tests/test_duong_nhan_engine.py)

---

## 3. Quy Tắc Thử Nghiệm Thị Trường & Điều Kiện Dừng (Zero-Waste Gate)

- **Chi phí tiền mặt:** `0 VND` (Host miễn phí trên GitHub Pages/Cloudflare Pages; dùng công cụ tạo video/audio có sẵn trong máy).
- **Cách kiểm chứng nhu cầu thật (`L2 -> L3/L4`) trước khi viết trọn bộ 187 bài:**
  - Dùng ngay trang [`index.html`](./index.html) (đã có sẵn bài test 7 thể chất + bộ công thức mẫu) kết hợp 3–5 video ngắn / bài đăng chia sẻ link làm bài test thể chất miễn phí.
  - **Điều kiện mở rộng:** Chỉ dành thời gian biên tập đầy đủ 187 bài PDF + Audio khi có **$\ge 30$ lượt hoàn thành bài test thể chất** và **$\ge 3$ khách bấm đặt mua / chuyển khoản `299.000₫`**. Nếu sau 10 bài đăng ngắn mà `0` người bấm nút đặt mua thì dừng ngay, không tốn tiền chạy quảng cáo.
