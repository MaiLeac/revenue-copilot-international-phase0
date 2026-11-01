# Single Strategy Specification: H4/H1 Trend-Following Pullback Engine
**Document Version:** 2.0 (Institutional Focus Pilot)  
**Target Instrument:** `EURUSD` (Primary Pilot — Most liquid, lowest spread, zero slippage footprint)  
**Execution Environment:** Exness MT5 Demo (`#464160066`, Server: `Exness-MT5Trial17`)  
**Design Philosophy:** "Cá nhỏ bơi theo dấu chân Cá Voi" — Giảm tần số giao dịch, loại bỏ cuộc đua tốc độ, ưu tiên bảo toàn vốn, biến khả năng đứng ngoài thành lợi thế cấu trúc.

---

## 1. Triết Lý & Vị Thế Cạnh Tranh Của "Cá Nhỏ"

### 1.1. Từ Bỏ Cuộc Chơi Của Quỹ Lớn
* **Không Scalping / HFT:** Không cạnh tranh tốc độ mili-giây, không ăn chênh lệch giá vài giây trên khung M1/M5.
* **Không News Sniping:** Không đặt cược giật giá 2 đầu vào đúng giây công bố tin tức đỏ.
* **Không Indicator Bloat:** Loại bỏ hoàn toàn hệ thống 27 chỉ báo phức tạp. Một chỉ báo chỉ được tồn tại nếu có giả thuyết kinh tế/toán học rõ ràng.

### 1.2. Khai Thác 3 Lợi Thế Cấu Trúc Độc Quyền
1. **Thanh khoản tức thời (Liquidity Agility):** Vào/thoát toàn bộ vị thế chỉ trong 0.1 giây mà không làm trượt giá thị trường.
2. **Quyền đứng ngoài (No Mandate Pressure):** Không chịu áp lực giải ngân hàng ngày hay báo cáo tháng; chỉ giao dịch khi xác suất nghiêng hẳn về phía mình.
3. **Bơi theo dòng tiền lớn:** Để các quỹ lớn tranh chấp và thiết lập xu hướng trên H4/D1, ta chỉ đóng vai trò "bắn tỉa du kích" tại các nhịp hồi có giá trị.

---

## 2. Kiến Trúc Chiến Thuật 4 Tầng (The 4-Tier Engine)

```
[TẦNG 1: MARKET REGIME (H4)] ──► Trend Rõ Ràng?
            │
            ├── KHÔNG (Chop / Sideway / Nhiễu) ──► ĐỨNG NGOÀI (Cash is King)
            └── CÓ (Uptrend hoặc Downtrend)
                     │
                     ▼
[TẦNG 2: SETUP SELECTION (H1)] ──► Nhịp Hồi Về Value Zone + Nến Xác Nhận Tiếp Diễn?
            │
            ├── KHÔNG ──► ĐỨNG NGOÀI (Không đuổi giá)
            └── CÓ
                     │
                     ▼
[TẦNG 3: RISK & SIZING GATE] ──► Rủi ro <= 0.25%? SL theo cấu trúc? Spread hợp lệ?
            │
            ├── VI PHẠM ──► HỦY LỆNH (Không nâng rủi ro để cố vào lệnh)
            └── ĐẠT CHUẨN
                     │
                     ▼
[TẦNG 4: TRADE MANAGEMENT] ──► Giữ theo luận điểm, Breakeven tại 1R, Cắt khi vô hiệu
```

---

### Tầng 1: Nhận Diện Trạng Thái Thị Trường (H4 Market Regime)

* **Khung thời gian:** `H4` (4 Giờ).
* **Mục đích:** Xác định xem thị trường có đang trong xu hướng mạnh hay đang đi ngang/nhiễu.
* **Quy tắc định lượng:**
  * **Uptrend (Xu hướng Tăng):**
    1. Cấu trúc đỉnh/đáy: Tạo Higher High (HH) và Higher Low (HL) rõ ràng trên H4.
    2. Đường trung bình động: $\text{EMA}(50) > \text{EMA}(200)$, giá nằm trên cả 2 đường EMA.
    3. Độ mạnh xu hướng: $\text{ADX}(14) \ge 20$ và $\text{DI}^+ > \text{DI}^-$.
  * **Downtrend (Xu hướng Giảm):**
    1. Cấu trúc đỉnh/đáy: Tạo Lower High (LH) và Lower Low (LL) rõ ràng trên H4.
    2. Đường trung bình động: $\text{EMA}(50) < \text{EMA}(200)$, giá nằm dưới cả 2 đường EMA.
    3. Độ mạnh xu hướng: $\text{ADX}(14) \ge 20$ và $\text{DI}^- > \text{DI}^+$.
  * **Regime Nhiễu / Đi Ngang (Sideway / Chop):**
    * Khi $\text{ADX}(14) < 20$ HOẶC $\text{EMA}(50)$ cắt xoắn liên tục qua $\text{EMA}(200)$ trong vòng 20 nến gần nhất.
    * **HÀNH ĐỘNG BẮT BUỘC: ĐỨNG NGOÀI 100%. Không tìm kiếm bất kỳ tín hiệu nào.**

---

### Tầng 2: Chọn Lọc Tín Hiệu (H1 Setup Selection)

* **Khung thời gian:** `H1` (1 Giờ).
* **Mục đích:** Tìm điểm vào lệnh có biên an toàn cao khi giá hồi về vùng giá trị (Value Zone), tuyệt đối không mua đuổi tại đỉnh hay bán đuổi tại đáy.
* **Quy tắc vào lệnh Mua (BUY Setup):**
  1. H4 Regime xác nhận **Uptrend**.
  2. Giá H1 hồi về **Vùng Giá Trị (Value Zone)**:
     - Nằm giữa $\text{EMA}(21)$ và $\text{EMA}(50)$ trên H1, HOẶC chạm vùng hỗ trợ đỉnh cũ đã phá vỡ (Resistance turned Support).
  3. **Tín hiệu kích hoạt (Trigger Bar):**
     - Xuất hiện nến từ chối giảm (Bullish Rejection Pinbar có bóng nến dưới dài tối thiểu $60\%$ thân nến) HOẶC nến nhấn chìm tăng (Bullish Engulfing).
     - Giá đóng cửa của nến Trigger phải nằm trên $\text{EMA}(21)$ H1.
* **Quy tắc vào lệnh Bán (SELL Setup):**
  1. H4 Regime xác nhận **Downtrend**.
  2. Giá H1 hồi lên **Vùng Giá Trị (Value Zone)**:
     - Nằm giữa $\text{EMA}(21)$ và $\text{EMA}(50)$ trên H1, HOẶC chạm vùng kháng cự đáy cũ đã phá vỡ (Support turned Resistance).
  3. **Tín hiệu kích hoạt (Trigger Bar):**
     - Xuất hiện nến từ chối tăng (Bearish Rejection Pinbar có bóng nến trên dài tối thiểu $60\%$ thân nến) HOẶC nến nhấn chìm giảm (Bearish Engulfing).
     - Giá đóng cửa của nến Trigger phải nằm dưới $\text{EMA}(21)$ H1.

---

### Tầng 3: Quản Lý Vốn & Kiểm Soát Rủi Ro (Risk & Sizing Gate)

* **Mức rủi ro tối đa mỗi lệnh:** Cố định **$0.25\%$** vốn chủ sở hữu (`Equity`).
* **Tổng rủi ro danh mục mở:** Tối đa **$0.50\%$** (tối đa 1–2 vị thế cùng lúc).
* **Xác định điểm Cắt Lỗ (Stop-Loss - SL) theo cấu trúc:**
  - Lệnh BUY: Đặt SL dưới đáy nến Trigger hoặc dưới đáy sóng hồi H1 gần nhất $- 1.0 \times \text{ATR}(14, \text{H1})$.
  - Lệnh SELL: Đặt SL trên đỉnh nến Trigger hoặc trên đỉnh sóng hồi H1 gần nhất $+ 1.0 \times \text{ATR}(14, \text{H1})$.
* **Tính toán Lot Size chuẩn xác:**
  $$\text{Cash Risk} = \text{Equity} \times 0.0025$$
  $$\text{Stop Distance} = |\text{Entry Price} - \text{Stop Loss}|$$
  $$\text{Cash Risk Per Lot} = \frac{\text{Stop Distance}}{\text{Trade Tick Size}} \times \text{Trade Tick Value}$$
  $$\text{Lots} = \text{Quantize}\left(\frac{\text{Cash Risk}}{\text{Cash Risk Per Lot}}, \text{Volume Step}\right)$$
* **Luật Bảo Vệ Tuyệt Đối:**
  * Nếu $\text{Lots} < \text{Volume Min}$ (0.01) mà mức rủi ro thực tế vượt quá $0.25\%$ vốn $\rightarrow$ **BỎ LỆNH**. Tuyệt đối không được gượng ép làm tròn lên để vào lệnh.
  * Kiểm tra chênh lệch giá (`Spread`): Nếu $\text{Spread} > 1.5 \times \text{Spread Trung Bình}$ (vượt quá 25 points đối với EURUSD) $\rightarrow$ **BỎ LỆNH**.

---

### Tầng 4: Quản Lý Lệnh & Thoát Vị Thế (Trade Management)

* **Tỷ lệ Lợi Nhuận / Rủi Ro (Target R:R):**
  - Mục tiêu tối thiểu: **$R:R = 1:2.0$** (kỳ vọng lợi nhuận dương $EV$).
  - Take Profit (TP) đặt tại vùng cấu trúc cản đối diện (Recent H4 Swing High/Low) hoặc bằng $\text{Entry} + 2.0 \times |\text{Entry} - \text{SL}|$.
* **Quy tắc Dời Chặn Lỗ (Breakeven & Trailing):**
  - Khi giá di chuyển có lãi đạt **$+1.0 R$**: Dời SL về điểm hòa vốn (`Entry Price + Commission/Spread Buffer`). Bảo toàn $100\%$ rủi ro còn lại của lệnh.
  - Khi giá hình thành các đỉnh/đáy mới trên H1 theo xu hướng: Dời SL theo sau các đáy sóng hồi (HL) mới hình thành.
* **Quy tắc Thoát Lệnh Chủ Động (Thesis Invalidation Exit):**
  - Nếu xuất hiện nến H4 đóng cửa hoàn toàn phá vỡ $\text{EMA}(50)$ H4 theo chiều ngược lại $\rightarrow$ Luận điểm xu hướng đã bị bẻ gãy. Đóng lệnh thị trường ngay lập tức, không đợi giá chạm SL ban đầu.
* **Cấm Tuyệt Đối:**
  - Không bao giờ nới rộng SL khi giá tiến sát SL.
  - Không nhồi thêm vị thế bình quân giá giảm (Martingale / Averaging Down).

---

## 3. Điều Kiện Đứng Ngoài Thị Trường (Stand-Down Rules)

Hệ thống xem việc **"Không vào lệnh"** là một vị thế phòng thủ chủ động:

1. **Khung Giờ Giao Dịch (Session Filter):**
   - Chỉ quét và kích hoạt vào lệnh từ **07:00 UTC đến 16:00 UTC** (giai đoạn trùng lặp sôi động nhất của Phiên London và Phiên New York).
   - Đứng ngoài hoàn toàn trong Phiên Á (thanh khoản mỏng, dễ bị quét râu giả tạo) và phiên giao dịch chuyển giao ngày (Rollover 21:00 - 23:00 UTC).
2. **Bộ Lọc Lịch Kinh Tế Đỏ (High-Impact News Freeze):**
   - Đứng ngoài trước 30 phút và sau 30 phút của các tin tức đặc biệt: Non-Farm Payrolls (NFP), CPI Mỹ, Họp lãi suất FOMC / FED, ECB Rate Decision.
3. **Bộ Ngắt Mạch Tự Động (Risk Kill-Switch Tripping):**
   - Sụt giảm vốn trong ngày (`Daily Loss`) chạm ngưỡng **$1.0\%$** $\rightarrow$ Dừng mở lệnh mới trong 24 giờ.
   - Sụt giảm từ đỉnh (`Peak Drawdown`) chạm ngưỡng **$3.0\%$** $\rightarrow$ Dừng toàn bộ hệ thống, khóa giao dịch và yêu cầu người vận hành rà soát nguyên nhân.

---

## 4. Tiêu Chí Loại Bỏ Chiến Lược (Strategy Decommissioning Criteria)

Một chiến lược sẽ bị **LẬP TỨC KHAI TỬ HOẶC VIẾT LẠI TỪ ĐẦU** nếu vi phạm bất kỳ tiêu chí nào sau đây trong quá trình thử nghiệm:

| Tiêu Chí Đánh Giá | Ngưỡng Cho Phép | Hành Động Khi Vi Phạm |
| :--- | :--- | :--- |
| **Kỳ Vọng Toán Học (EV Out-of-Sample)** | $EV > 0$ sau khi trừ đủ Spread, Commission và Slippage | Loại bỏ ngay lập tức nếu $EV \le 0$ trên tập dữ liệu ngoài mẫu. |
| **Số Lượng Giao Dịch Thử Nghiệm** | Tối thiểu $\ge 50$ giao dịch trong Backtest nghiêm ngặt | Không phê duyệt bất kỳ báo cáo nào có dưới 50 lệnh (tránh bẫy ăn may ngẫu nhiên). |
| **Chuỗi Thua Liên Tiếp Tối Đa** | $\le 7$ lệnh liên tiếp | Nếu chạm 8 lệnh thua liên tiếp $\rightarrow$ Dừng hệ thống để rà soát Market Regime. |
| **Mức Sụt Giảm Tài Khoản (Max DD)** | $\le 5.0\%$ vốn | Khóa bot, hủy chiến lược. |
| **Độ Khớp Giữa Backtest và Forward Test** | Sai lệch Winrate hoặc Slippage $\le 20\%$ | Nếu Demo Forward Test thua lỗ trong khi Backtest lãi $\rightarrow$ Bị Overfitting / rò rỉ dữ liệu, hủy bỏ kết quả. |

---

## 5. Kế Hoạch Triển Khai Thực Tế

1. **Bước 1 (Đã hoàn tất):** Nền móng thực thi an toàn, quản trị vốn `RiskManager`, chống trùng nến, ghi file nguyên tử và xác thực Demo MT5.
2. **Bước 2 (Hiện tại):** Đóng băng việc mở rộng đa mã. Khóa tập trung vào duy nhất cặp `EURUSD` theo bản đặc tả `H4/H1 Trend-Following Pullback Engine`.
3. **Bước 3:** Lập trình module tính toán Market Regime H4 và Trigger H1 trong [`app/strategies/trend_pullback.py`](../app/strategies/trend_pullback.py).
4. **Bước 4:** Thực hiện kiểm thử quá khứ (Backtest) nghiêm ngặt trên ít nhất 1 năm nến MT5 thật, chia tách 70% In-Sample và 30% Out-of-Sample có tính trượt giá.
5. **Bước 5:** Trình nộp diffs và kết quả backtest sang **Gemini Independent Reviewer** để nhận phản biện độc lập trước khi mở cho daemon chạy Demo dài hạn.
