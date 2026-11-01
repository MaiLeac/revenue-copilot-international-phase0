# Kiểm tra độc lập SOL spot

Đây là bản mã do Vibe-Trading tạo, được rà soát và chạy lại bằng Python của virtual environment. Không phải báo cáo được grounding gate của Vibe-Trading chứng nhận. Dữ liệu và kết quả có trong `data/raw` và `artifacts/sol_backtest_summary.json`.

Nguồn: OKX public history-candles, SOL-USDT, nến 1Dutc đã đóng. Kỳ đo 2021-01-01 đến hết 2026-09-27; 2.096 ngày. Phí 0,1% và slippage 0,05% mỗi chiều, áp dụng nhân vào giá/giá trị giao dịch. Không vay, không funding. Tín hiệu close hôm trước khớp open hôm sau. Vốn đầu kỳ = 1; có tính ngày đầu. Sharpe dùng lợi nhuận ngày, sqrt(365), lãi phi rủi ro = 0.

| Kỳ / chiến lược | Tổng lợi nhuận | CAGR | Max drawdown | Sharpe | Số lần mua/bán |
|---|---:|---:|---:|---:|---:|
| Toàn kỳ: buy-and-hold | 7.954,61% | 114,74% | -96,27% | 1,243 | 1 |
| Toàn kỳ: EMA50/200 | 996,09% | 51,73% | -67,12% | 0,929 | 9 |
| Từ 2025: buy-and-hold | -35,76% | -22,46% | -76,25% | 0,059 | 1 |
| Từ 2025: EMA50/200 | -38,65% | -24,49% | -64,68% | -0,254 | 5 |

Số lần mua/bán là số lần đổi vị thế, chưa cộng lần bán giả định cuối kỳ. EMA toàn kỳ có 4 vòng mua-bán đóng và 1 vị thế mở; kỳ 2025 có 2 vòng đóng và 1 vị thế mở. Equity mỗi ngày đã trừ chi phí bán giả định nếu còn giữ tài sản; không trừ dồn phí bán qua các ngày.

Giới hạn: OKX chỉ trả lịch sử từ 2020-10-01, có 92 nến trước đầu 2021, chưa đủ EMA200. Mã giữ tiền mặt cho tới khi đủ 200 nến, khởi tạo EMA bằng SMA; do đó bỏ lỡ một phần sóng tăng đầu 2021. OOS là một kỳ lịch sử tách theo ngày với tham số cố định và vốn đặt lại 1, không phải thử nghiệm tiền thật hoặc kiểm định được đăng ký trước. Không tối ưu tham số. Giá khớp lý tưởng, không mô phỏng sổ lệnh, độ trễ, giới hạn lô, thuế hoặc rủi ro lưu ký. Chưa đối chiếu từng nến với sàn thứ hai.

Đã sửa so với mã ban đầu: chọn nến UTC đã đóng, tính từ vốn đầu kỳ, tính đủ thời lượng đến close ngày cuối, tính phí và slippage riêng. Kết quả tốt toàn kỳ không chứng minh kiếm tiền tương lai; kỳ từ 2025 của cả hai chiến lược đều âm.
