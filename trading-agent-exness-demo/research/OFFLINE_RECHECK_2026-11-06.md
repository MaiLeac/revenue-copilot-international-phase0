# MT5 demo: kiểm tra lại ngày 06/11/2026

## Kết quả đã chạy

Chạy `python tools/recheck_mt5_offline.py` trên sáu file nến H1/H4 trong `data/backtest_cache/`, không mở MT5 và không gửi lệnh. [Thống kê kèm SHA-256 từng nguồn](offline_recheck/stats.json) và [sổ 98 lệnh mô phỏng](offline_recheck/trades.csv) được giữ để đối soát. Tổng PnL của từng lệnh khớp báo cáo.

| Chỉ số | Kết quả mô phỏng |
|---|---:|
| 98 lệnh đóng | −4.299,30 USD |
| Lợi suất trên vốn giả định 100.000 USD | −4,30% |
| Profit factor | 0,75 |
| EURUSD / GBPUSD / XAUUSD | −898,15 / −3.357,72 / −43,42 USD |

Đây **không phải lỗ của tài khoản Exness demo** và không chứng minh lợi thế trong giao dịch thật. Nến cache có dấu vết hash nhưng chưa đối chiếu độc lập với sàn; spread, trượt giá và swap là giả định cố định. Không có lịch kinh tế lịch sử đã xác minh, nên phép chạy lại **không giả vờ lọc tin tức**. Dữ liệu khoảng 24/11/2025–04/11/2026; kết quả này là trong mẫu, chưa có phần ngoài mẫu dành riêng cho chiến lược sau khi sửa.

## Lỗi đã sửa và điều còn thiếu

- Tài liệu MT5 xác nhận `copy_rates_from_pos(..., 0, ...)` chứa nến hiện tại đang hình thành. Đường đọc nến cho chiến lược nay lấy từ vị trí 1.
- Backtester trước dùng OHLC của nến H1/H4 chưa đóng để tạo tín hiệu và khớp vào đầu chính cây nến đó. Nay tín hiệu chỉ thấy nến đã đóng và giá vào mô phỏng lấy từ open cây H1 kế tiếp. Kiểm thử thời gian kiểm chứng điều này.
- Bộ sinh báo cáo trước gán cứng chữ `PROFITABLE`, `POSITIVE EDGE`, `FTMO PASS`, `statistically significant` và tin tức tránh được dù số liệu âm hoặc không được đo. Đã thay bằng bảng số liệu và giới hạn phương pháp. Báo cáo cũ được giữ làm lịch sử, không dùng để quyết định.
- Bộ lọc tin của daemon trước có thể coi lịch rỗng hoặc quá cũ là an toàn. Nay chế độ demo chạy trực tiếp chặn lệnh khi không lấy được lịch tin còn mới; bản mô phỏng lịch sử khai báo rõ rằng không có dữ liệu tin đã xác minh.
- Daemon nay lưu lần đánh giá nến H1 đóng gần nhất, lý do `FLAT` hoặc chặn tin, và tổng số nến đã xét vào `run_state.json`. Đây là dấu vết chẩn đoán, không phải bằng chứng giao dịch có lãi.
- Tài khoản demo chưa có lệnh thực thi được ghi nhận; `RUNNING` trong file trạng thái không chứng minh daemon đang chạy. Kiểm tra 06/11 cho thấy heartbeat cũ hơn 17 giờ.

**Quyết định:** giữ demo; không dùng tiền thật hoặc trả phí thi quỹ. Việc tiếp theo là làm cho daemon chạy và ghi nhật ký tín hiệu, lý do từ chối, lệnh broker, PnL đóng thật trong demo; sau đó mới kiểm định ngoài mẫu và cải thiện chiến lược. Không nới điều kiện vào lệnh chỉ để có thêm lệnh.
