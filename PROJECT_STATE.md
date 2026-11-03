# 🧭 BẢN ĐỒ TRẠNG THÁI TOÀN DIỆN DỰ ÁN (MONEY HQ MASTER STATE)
> **Single Source of Truth (SSOT)** — Cập nhật lần cuối: **2026-11-03 16:12 (ICT)**  
> **Sổ tay lịch sử thử nghiệm toàn tập:** Xem chi tiết tại [`PROJECT_FLIGHT_RECORDER.md`](./PROJECT_FLIGHT_RECORDER.md)  
> **Quy tắc vàng:** Bất kỳ ai (Chủ dự án Mai, lập trình viên, hoặc các AI: ChatGPT, Claude, DeepSeek, Antigravity) khi bước vào repository này **chỉ cần đọc 2 file này** là nắm trọn vẹn 100% dự án: ĐÃ LÀM GÌ, ĐANG LÀM GÌ, SẼ LÀM GÌ, ĐANG MẮC CÁI GÌ và CẦN LÀM GÌ TIẾP THEO.

---

## 1. BẢNG ĐIỀU HÀNH THỜI GIAN THỰC (EXECUTIVE FLIGHT RECORDER)

* 💵 **Dòng tiền thực thu về túi (`L4 Realized Cash`):** `0 VND` 🔴 **(BÁO ĐỘNG ĐỎ VỀ DOANH THU)**
* 📈 **Tài khoản Bot Trading MT5:** `$100,000.00 USD` (Exness Demo `#46416***`, Server `Exness-MT5Trial17`)
* 🧪 **Chất lượng mã nguồn (Test Suite):** **125/125 PASSED (100% Pass, 0 Fail)**
* 🤖 **Các tiến trình tự động đang chạy ngầm trên máy:**
  1. `daemon.py`: Bot giao dịch tự động MT5 (EURUSD H4/H1) — *Đang quét phiên 07:00–16:00 UTC*.
  2. `telegram_listener.py`: Trợ lý điều hành Telegram 2 chiều — *Đang trực tuyến, nhận lệnh và trả lời ngay*.
  3. `daily_revenue_watchdog.py`: Giám sát doanh thu & điểm nghẽn — *Tự động gửi báo cáo sáng (08:30) & tối (20:30)*.

---

## 2. MA TRẬN TIẾN ĐỘ CÁC TRỤ CỘT DỰ ÁN (PORTFOLIO ROADMAP)

| Mã | Tên Trụ Cột | Trạng Thái | ĐÃ ĐẠT ĐƯỢC (Completed) | ĐANG MẮC CÁI GÌ (Blocker / Bottleneck) | CẦN CÁI GÌ TIẾP THEO (Next Action) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TRD-01** | **MT5 Algo Trading** *(Pilot EURUSD)* | 🟢 RUNNING (Demo) | • Kiến trúc 4 tầng chuẩn Quant.<br>• Bộ lọc Wilder ADX + Pinbar/Engulfing.<br>• Fail-closed Disk Persistence + Kill Switch.<br>• Pass 47/47 tests MT5. | • **Đang chạy DEMO ảo** nên dù có lãi cũng chưa phải tiền rút về tài khoản ngân hàng thật.<br>• Thị trường sideway thì bot giữ vị thế Flat (0 lệnh), không có tiền. | 1. Tiếp tục chạy forward-test demo 2 tuần.<br>2. Đạt chuẩn thống kê thì dùng bot đi **thi quỹ cấp vốn (Prop Firm FTMO/MFF)** lấy tài khoản $10,000 - $50,000 thật mà không cần bỏ vốn tự có. |
| **EXP-03** | **Dưỡng Nhan AI MVP** *(69k/lượt + Cẩm nang 299k)* | 🔴 **KHAI TỬ (KILLED / ARCHIVED)** | • Web trắc nghiệm 7 thể chất đông y.<br>• Cẩm nang có khóa bản quyền. | • **Vi phạm pháp lý y tế nghiêm trọng:** Thiếu giấy phép, thiếu Terms of Service, Privacy Policy, Medical Disclaimer.<br>• **Cổng thanh toán ảo:** Mã QR VietQR gắn tài khoản rác `MB-0000000000`.<br>• Sản phẩm chỉ là bài thuốc nhặt nhạnh, không có USP, bắt chủ dự án đi rải link dạo. | • Đã đóng băng và loại khỏi lộ trình kiếm tiền.<br>• Xem bài học thất bại chi tiết tại `PROJECT_FLIGHT_RECORDER.md`. |
| **EXP-02** | **SaaS B2B Clean CSV** *($9 USD / 199k)* | 🟢 LIVE ONLINE | • Tool dọn sạch dữ liệu TMĐT chạy 100% trên trình duyệt.<br>• Đã test 120 SKU Shopee/Shopify. | • Chưa có danh sách khách hàng doanh nghiệp / chủ shop để chào hàng (Outreach). | 1. Thu thập danh sách 20 chủ shop TMĐT.<br>2. Nhắn tin demo làm sạch file lỗi miễn phí để mời mua gói $9. |
| **KNOW-01** | **Kho Tri Thức Vĩ Mô** *(Đồng Chí Long & Vương Tố Linh)* | 🟢 COMPLETED V1 | • Cào sạch & làm sạch **1.857 bài viết chuyên sâu**.<br>• Đóng gói thành 3 file Markdown chuẩn trên Git. | • Mới là dữ liệu tài liệu thô trên GitHub, chưa thương mại hóa. | 1. Đóng gói thành bản tin phân tích vĩ mô (Newsletter) hoặc Ebook cẩm nang.<br>2. Dùng làm dữ liệu đầu vào cho các AI khác phản biện. |
| **SYS-01** | **Money HQ Control Plane & Telegram Bot** | 🟢 RUNNING | • Hệ thống Task Router phân loại tác vụ.<br>• Bot Telegram trả lời 2 chiều.<br>• Watchdog báo cáo doanh thu tự động. | • Trước đây chạy thủ công từng lần, nếu chủ nhân không hỏi là im re (đã khắc phục bằng Watchdog Daemon). | • Duy trì listener và watchdog chạy liên tục 24/7. |

---

## 3. PHÂN TÍCH GỐC RỄ: TẠI SAO HÔM NAY CHƯA RA TIỀN?

1. **Về Trading:** Bản chất tài khoản hiện tại là **Demo Sandbox**, mục đích là rèn luyện và chứng minh thuật toán, không phải tiền mặt khả dụng. Lệnh chỉ vào khi có xu hướng rõ ràng, ngày sideway không vào lệnh là **bảo vệ vốn**, không phải là lỗi.
2. **Về Sản phẩm Web (Dưỡng Nhan & Clean CSV):** Sản phẩm đã có sẵn trên mạng, thanh toán tự động đã có, nhưng **nút thắt cổ chai duy nhất là KHÂU PHÂN PHỐI (DISTRIBUTION)**. Một cửa hàng mở giữa sa mạc không có bảng chỉ đường thì dù hàng tốt đến mấy cũng không có khách.

---

## 4. MA TRẬN PHÂN CÔNG NHIỆM VỤ (WHO DOES WHAT)

### 👤 Phần việc của Con người (Chủ dự án - Mai):
* [ ] **Duyệt bài truyền thông:** Chọn 1 trong các kịch bản bài đăng Dưỡng Nhan do AI soạn sẵn để copy đăng lên trang cá nhân, Threads hoặc nhóm phụ nữ.
* [ ] **Quan sát phản hồi:** Xem có người dùng nào bấm vào làm bài test và thanh toán 69k không để phản hồi lại cho AI tối ưu giao diện.

### 🤖 Phần việc của Hệ thống AI (Antigravity & Background Daemons):
* [x] Đảm bảo bot MT5 chạy chuẩn kỷ luật, ghi log nến và quản trị rủi ro fail-closed.
* [x] Trực chiến Telegram 24/7: Nhận câu hỏi, báo cáo số dư, trạng thái lệnh bất kỳ lúc nào.
* [x] Tự động gửi **Daily Operations Brief** mỗi ngày vào 08:30 sáng và 20:30 tối lên Telegram, nêu rõ tiến độ, lý do chưa ra tiền và việc cần làm mà **chủ dự án không cần phải hỏi**.
* [ ] Soạn sẵn bộ kịch bản marketing kéo traffic thực chiến cho EXP-03 và EXP-02.
