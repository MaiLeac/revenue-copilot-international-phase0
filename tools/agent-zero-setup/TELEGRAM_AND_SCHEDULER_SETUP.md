# Agent Zero và Telegram — trạng thái cấu hình

**Kiểm tra 05/11/2026, khoảng 08:55 ICT:** cổng Agent Zero `5080` không lắng nghe. Sự tồn tại của profile, skill hoặc file lịch **không chứng minh** Agent Zero đang chạy. Lượt scheduled trước đã báo sai rằng checkout xác nhận thanh toán tự động; xem [`operations/EXECUTION_HANDOFF.md`](../../operations/EXECUTION_HANDOFF.md). Không kích hoạt lại lịch tiêu token chỉ để tạo báo cáo.

**Kiểm tra lại 12:37 ICT:** container Agent Zero đang chạy trong WSL, dù cổng Windows không lắng nghe. Một lượt thử thủ công trên CatalogueQA đã chạy bằng task `Money HQ - Revenue Execution`: kết quả chỉ báo 5 test cũ qua, **không sửa file**, nên không đạt yêu cầu thực thi. Task đã được tắt lại; ba lịch trong runtime đều `disabled`. Chưa có worker AI tự làm hằng ngày. Gemini 3.5 Flash-Lite có free tier theo [bảng giá Google](https://ai.google.dev/gemini-api/docs/pricing?hl=en), nhưng trạng thái billing/quota thực tế cần kiểm tra trước khi bật lịch lặp lại.

## Nguồn cấu hình

- Repo được dự kiến gắn vào container tại `/a0/usr/projects/money-hq`; xác minh mount khi Docker chạy trước khi dùng.
- Prompt `money-coo` cục bộ đã được bổ sung hướng dẫn đọc [`AGENTS.md`](../../AGENTS.md) và [danh mục công cụ](../../assets/web_capability_library/CAPABILITY_ROUTING.md). Script đồng bộ: `sync_capability_profile.ps1`. Đây mới là thay đổi cấu hình trên đĩa, chưa xác minh lượt agent dùng đúng.
- [`tasks.json`](tasks.json) là **bản mẫu lịch cũ**, có tác vụ pytest/báo cáo; không dùng làm chỉ dẫn hiện hành. [`usr_config/scheduler/tasks.json`](usr_config/scheduler/tasks.json) hiện là danh sách rỗng trong repo. Trạng thái lịch thật trong runtime phải đọc trực tiếp trước khi tuyên bố hoạt động.
- Telegram chỉ là kênh nhận lệnh/thông báo. Tin nhắn của bot không chứng minh đã có khách, thanh toán, giao file hoặc doanh thu.

## Điều kiện cho một lượt agent hữu ích

1. Đọc README, PROJECT_STATE và sổ tiền; chọn một điểm nghẽn gần giao dịch thật.
2. Chỉ chạy việc được phép, có đầu ra, giới hạn thời gian/token; không chạy nhiều agent trùng việc.
3. Kiểm tra file hoặc hành vi đã thay đổi. Ghi kết quả thật và bước tiếp theo vào `operations/EXECUTION_HANDOFF.md`.
4. Nếu chỉ có report/test pass hoặc không thể làm, ghi `BLOCKED` cùng lý do; không báo hoàn thành.

Không đưa token, tài khoản hay thông tin thanh toán vào repo. Không chạy giao dịch thật, chi tiền, đăng bài hoặc liên hệ khách chỉ vì scheduler nhắc tới.
