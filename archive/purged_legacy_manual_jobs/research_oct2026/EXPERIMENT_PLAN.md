# Đề xuất 14 ngày — chưa thực hiện
D0 là ngày Gate0 được duyệt; deadline tiền thực thu D30. Nếu D0=26/10/2026 thì reviewD7=02/11, D14=09/11 vàD30=25/11/2026.

## Giả thuyết và thiết kế
Path A: kỹ năng QA/quy trình và tiếng Việt đủ để nhận một hợp đồng qua tối đa3 ứng tuyển miễn phí đã kiểm tra, với payout có thể về trướcD30. Ưu tiên Lionbridge; RWS/Welo là hai lựa chọn phụ trong cùng chiến lược, phải kiểm tra điều khoản làm chéo. Không cam kết tuyển hay volume.
Backup B: một merchant/agency quốc tế trả100 USD cho catalogue QA <=200 dòng; đề xuất50% cọc, phần còn lại nghiệm thu. Chi tiết scope và kinh tế ở OPPORTUNITY_RESEARCH.md. Cọc là tiền nhận trước, không tự coi toàn bộ là doanh thu đã hoàn thành hoặc lợi nhuận.

|Mốc|Việc đề xuất sau phê duyệt|Giới hạn / bằng chứng|
|--|--|--|
|D1–2|Người dùng tự xác nhận rail, eligibility, viết/đọc brief; draft CV trung thực và1 sample synthetic nhỏ nếu được duyệt|3h; không dùng data thật, không tạo app|
|D3–4|Kiểm tra lại3 tin; người dùng duyệt hồ sơ rồi ứng tuyển qua đúng kênh, hỏi pay unit/start/payout/timezone khi có chỗ phù hợp|3h tổng; không phí, không nộp giấy tờ qua chat|
|D5–7|Chỉ làm assessment hợp lệ, tự làm; ghi thời gian, lời mời và điều khoản|Tối đa2h mỗi test,6h toàn bộ; không test tạo sản phẩm dùng được đáng kể miễn phí|
|D7 review|Nếu không có next step cụ thể hoặc payout vượtD30, ngừng tăng giờ A; xin kích hoạtB nếu chưa được duyệt trong Gate0|“Đã gửi hồ sơ” không là thành công; waiting0h|
|D8–10, nhánh B|Tìm <=10 request/buyer phù hợp mới ở kênh cho phép; xin duyệt nội dung nếu approval chưa bao phủ; phản hồi cá nhân hóa|Không giả định10buyer sẵn có; không DM hàng loạt; tối đa5h giai đoạn này|
|D11–14|A: nhận task chỉ khi điều khoản chấp nhận được; hoặc B: chốt schema/giá/rail/tiêu chí, yêu cầu cọc hợp lệ rồi giao thủ công|Tổng acquisition+test+chuẩn bị unpaid trước hợp đồng cả2nhánh <=12h; vượt phải review, không âm thầm cộng|
|D14 review|Cần hợp đồng/task có điều khoản nhận tiền trướcD30 hoặc B có cọc thực nhận; L3 đơn thuần chưa đạt mục tiêu tiền|Nếu không có: dừng tiếp cận mới, báo thiếu bằng chứng, không mua leads/tools|
|D30|Đối chiếu tiền thực thu, khoản chờ, phí, hoàn tiền và tổng giờ|Không có tiền về: mục tiêu thất bại, kể cả dashboard hiển thị earnings|

Các phân bổ ngày là lựa chọn, không cộng mặc định: nếu A dùng hết12h unpaid thì dừng xin điều chỉnh trước khi B thêm giờ. Khối lượng delivery20h là kịch bản kinh tế, không quota bắt buộc. Sửa/learning4h A vẫn phải được ghi, không coi paid.

## Giao hàng thủ công B
Nhận file tối thiểu đã loại PII qua kênh được khách chấp thuận; giữ bản gốc. Chốt schema và danh sách trường được sửa; kiểm tra row counts/SKU/duplicate/missing/format. Không suy dữ liệu thiếu. Giao corrected copy + unresolved issues + changelog; client duyệt trước import. Một vòng sửa trong scope; phát sinh đổi scope phải báo giá lại, không nhận tự động.

## Thành công và dừng
- Kết quả giữa kỳ: có đề nghị trả tiền và deadline rõ (L3); kết quả chính: tiền thực vào tài khoản, dùng được/rút được, trướcD30 (L4).
- Ghi số hồ sơ hợp lệ, phản hồi, test hours, task offered/accepted/rejected, invoice date, due date, tiền gross/fees/net, refund và giờ thực tế. Người dùng tự xác nhận bằng số liệu đã che thông tin nhạy cảm; không đưa credentials vào log.
- Cash mới trước doanh thu dự kiến0đ; chỉ cho phép phí nhận/rút đã chấp thuận, mọi phí/FX cộng <=500.000đ. Không API/hosting/subscription.
- Dừng nếu trả phí ứng tuyển, mua training, deposit, yêu cầu giả danh/VPN/copy bài thi, lộ PII, quyền ghi âm không chấp nhận, hoặc công sau phí dự kiến<50.000đ/h sau giai đoạn học có giới hạn.
- Nếu chỉ8h paid ở5 USD nhưng28h công tổng thì sau công âm: không tiếp tục vì advertised hourly đẹp.
- Lặp lại khi có tiền thật + contribution sau công dương + lỗi/rework chấp nhận được. Chỉ tự động hóa sau ít nhất2 batch có tiền với cùng loại lỗi/quy tắc, được khách cho phép. Dừng/pivot khi không có task, không chốt sau10 tiếp cận hợp lệ, hoặc2 batch liên tiếp âm sau công.

Không có bước nào trong kế hoạch này đã được thực hiện. Gate0 cần phê duyệt phạm vi A và quyền kích hoạt B riêng.

