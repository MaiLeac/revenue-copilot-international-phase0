# Điểm cần chú ý — 05/11/2026

**Đích:** một khoản tiền thật được nhận và ghi bằng chứng, tiến tới mục tiêu 15 tỷ VND của Mai. Hai sổ `finance/CASH_LEDGER.csv` và `finance/COST_LEDGER.csv` hiện chỉ có tiêu đề. Không suy ra traffic hoặc doanh thu ngoài sổ.

| Ưu tiên | Điểm nghẽn | Việc AI có thể làm ngay | Điều kiện kết thúc |
|---|---|---|---|
| 1 | Sách Bản Thảo chưa hoàn tất; web chỉ có minh họa | Giữ catalog trung thực, kiểm tra luồng đọc thử, chuẩn bị cách đưa file thật vào khi tác giả giao | Sản phẩm/file/quyền sử dụng được xác nhận |
| 2 | Checkout và giao file chưa được kiểm thử | Chuẩn bị quy trình đơn → xác nhận chuyển khoản thủ công → giao file riêng tư; không nhận tiền khi chưa sẵn sàng | Một dry run không thu tiền đi hết luồng, thông tin giá và liên hệ chính xác |
| 3 | Nhu cầu mua và traffic chưa đo | Khi có sản phẩm giao được, thử một kênh phân phối được phép, ghi nguồn và phản hồi | Có quan sát người thật hoặc kết luận thử nghiệm thất bại có dữ liệu |

Danh sách trên là các nghẽn của đường sách số, không loại trừ đường tạo tiền khác. MT5 cần một vòng riêng để chẩn đoán lỗi chạy và kiểm định lợi thế sau phí trong demo. Little Loop, Agent Zero, Telegram và repo khác dùng khi giúp thực thi, đo hoặc sửa một nghẽn cụ thể. Không báo `healthy` hoặc `100% ready` chỉ vì script qua test hay cổng local từng mở.

**Trạng thái máy tại 08:55 ICT:** các cổng `5080`, `8000`, `8888`, `3210`, `8899` không lắng nghe. Kiểm tra lại trước khi dùng; dòng này không phải theo dõi thời gian thực. Xem [`PROJECT_STATE.md`](../PROJECT_STATE.md).
