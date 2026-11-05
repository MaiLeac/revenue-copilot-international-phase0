# AI routing — chọn công cụ theo điểm nghẽn

Đọc [README](../README.md), [trạng thái](../PROJECT_STATE.md) và [AGENTS.md](../AGENTS.md) trước. Agent, model, bot và repo là tài nguyên dùng **theo tác vụ**, không phải bộ phận cần chạy hết giờ để chứng minh hoạt động.

| Việc | Cách dùng phù hợp | Bằng chứng hoàn thành |
|---|---|---|
| Tính sổ, kiểm tra file, QA lặp lại | Script cục bộ trước; AI chỉ phân tích điều script chưa quyết định | Đầu ra script, số liệu nguồn, lỗi được sửa |
| Web, sản phẩm số, video | Tra `python tools/capability_lookup.py "tác vụ"`; dùng component/repo khi tiết kiệm công sức thật | Trang/file thật, kiểm tra desktop/mobile và luồng người mua |
| Tìm nghẽn tạo tiền | Một agent kiểm tra dữ liệu gốc của cơ chế đã chọn, chẩn đoán nguyên nhân và sửa | Thay đổi có kiểm chứng; nếu bị chặn, nêu phương án, chi phí và quyết định cần Mai đưa ra |
| Agent Zero | Chỉ chạy nhiệm vụ đã có đầu ra, giới hạn thời gian và token; kiểm tra kết quả trước khi báo | Log lượt chạy **và** file/hành vi thay đổi thật |
| Telegram/watchdog | Thông báo thay đổi quan trọng hoặc hành động cần thiết | Thông báo đúng sự thật; không tính là doanh thu |
| MT5 | Nghiên cứu/demo riêng | Bằng chứng demo, không gộp L4 hay kích hoạt tài khoản thật |

Không lặp một task trên nhiều mô hình khi chưa có lý do. Không giả định subscription có API miễn phí, repo được đánh dấu sao đã cài, hoặc cổng local đang chạy. Kiểm tra trạng thái ở thời điểm dùng; lần quan sát 05/11/2026 khoảng 08:55 ICT thấy cổng Agent Zero `5080` không lắng nghe.

Nếu công việc chưa tăng xác suất nhận tiền thực, giảm chi phí/rủi ro hoặc sửa được nguyên nhân thất bại, xác định lại tác dụng của nó trước khi dùng token. Không bỏ một hướng chỉ vì lần thử đầu thất bại. Giữ một người/agent chịu trách nhiệm đầu ra, không tạo chuỗi handoff chỉ để có nhiều agent.
