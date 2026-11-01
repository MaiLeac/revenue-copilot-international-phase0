# Vibe-Trading trên máy này

Nhấp đúp `01-Open-Vibe-Trading.cmd` để mở. Sau khi Windows khởi động lại, chạy file này; server có thể cần vài phút để kiểm tra dịch vụ. Giao diện: http://127.0.0.1:8899/.

- `02-Login-ChatGPT.cmd`: đăng nhập lại khi OAuth hết hiệu lực. Tự hoàn tất trong trình duyệt; không gửi mật khẩu hoặc callback vào chat.
- `03-Check-System.cmd`: kiểm tra phiên bản, dependencies, cấu hình, localhost và HALT.
- `04-Backtest-SOL.cmd`: chạy mẫu SOL cố định bằng engine tích hợp tới hôm qua, không tiêu hạn mức AI, không giao dịch thật. Chạy bốn bài: EMA và buy-and-hold, toàn kỳ và từ 2025. Muốn AI nghiên cứu chiến lược khác, nhập yêu cầu trong Web UI.
- `05-Stop-Server.cmd`: chỉ tắt PID server được xác minh thuộc Python venv hoặc tiến trình con trực tiếp của venv đó.

Giữ các file CMD, VibeTrading.ps1 và Run-SOL-Backtest.py cùng thư mục. Bản vận hành dự phòng ở `%LOCALAPPDATA%\MaiVibeTrading\launchers`. Mỗi launcher đều gọi `.venv\Scripts\python.exe -m cli`; mẫu SOL kiểm tra CLI rồi gọi trực tiếp engine bằng cùng Python. PATH ưu tiên venv cho các script con.

Đã xác minh Vibe-Trading 0.1.15, pip check, frontend hiển thị, OAuth và lời gọi model thực. Model hiện dùng `openai-codex/gpt-5.5`; `gpt-5.4` bị backend từ chối HTTP 400. Đã sao lưu .env trước thay đổi. OAuth lưu bởi Vibe-Trading, không sao chép thông tin đăng nhập Codex app.

Live HALT đang bật. Chưa cấu hình tài khoản giao dịch thật, chưa đặt lệnh, chưa cấp Withdraw. HALT là khóa phần mềm có thể bị người dùng gỡ, không phải sandbox bảo mật. Binance chỉ thử Spot Testnet và Exness chỉ MT5 demo/read-only khi có yêu cầu sau.

Kết quả AI phải được kiểm tra: lần chạy đầu đã tạo script nhưng báo cáo bị grounding gate từ chối. Không coi nhãn CLI SUCCESS là backtest đã được chứng nhận. Bản kiểm tra độc lập kèm dữ liệu và mã có tại thư mục SOL-Backtest bên cạnh.
