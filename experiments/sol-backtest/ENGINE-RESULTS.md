# Engine Vibe-Trading: đã chạy thành công

Ngày kiểm tra: 2026-09-28. Bốn lần gọi backtest tool trả `status=ok`, `exit_code=0`; có config, mã tín hiệu, metrics.csv, equity.csv, trades.csv và run card trong `engine-runs`.

| Kỳ / chiến lược | Tổng lợi nhuận | Annual return của engine | Max drawdown | Sharpe | Trade count của engine |
|---|---:|---:|---:|---:|---:|
| 2021–2026: buy-and-hold | 7.257,89% | 111,46% | -96,29% | 1,211 | 1 |
| 2021–2026: EMA50/200 | 1.264,36% | 57,66% | -67,82% | 0,978 | 5 |
| Từ 2025: buy-and-hold | -36,74% | -23,17% | -77,06% | -0,071 | 1 |
| Từ 2025: EMA50/200 | -35,83% | -22,54% | -63,60% | -0,431 | 3 |

Nguồn: loader OKX công khai, SOL-USDT, interval 1D mặc định của repo, kết thúc 2026-09-27. Bắt đầu tải từ 2020-06-15 nhưng lịch sử OKX thực tế ngắn hơn; evaluation_start_date lần lượt 2021-01-01 và 2025-01-01. Vốn 10.000, taker/maker 0,001, slippage 0,0005, leverage=1, funding_rate=0, hold giữa các lần đổi tín hiệu. Không tối ưu tham số.

Đây là kiểm tra engine của repo. Repo route crypto qua CryptoEngine vốn được viết cho perpetual; leverage=1 và funding=0 làm mẫu gần với spot, không biến nó thành mô phỏng sàn spot hoàn chỉnh. Không dùng kết quả này như chứng nhận lợi nhuận hay chứng nhận grounding gate của cuộc chat AI.

Không trộn với bảng README.md: bản kiểm tra độc lập dùng nến 1Dutc, EMA khởi tạo SMA, tính equity sau chi phí bán giả định mỗi ngày. Engine dùng nến 1D của OKX, ewm(adjust=False), quy ước khớp/đóng cuối kỳ và đếm giao dịch riêng. Vì vậy hai bảng không đồng nhất. Cả hai đều cho thấy kỳ tách từ 2025 bị lỗ; đây là một kỳ lịch sử giữ cố định tham số, chưa phải kiểm định forward thực sự.

Hai lần thử AI trước: lần đầu tạo script nhưng grounding gate từ chối báo cáo; lần hai đọc code kéo dài nên đã dừng. Cài đặt, OAuth và engine hoạt động; khả năng AI tự hoàn tất mọi yêu cầu vẫn chưa đáng tin cậy. Launcher mẫu SOL chạy trực tiếp engine và không gọi model.
