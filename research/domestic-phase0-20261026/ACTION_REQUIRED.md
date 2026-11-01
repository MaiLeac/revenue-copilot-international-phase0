# Quyền cần duyệt — Gate0 chưa thông qua

Không hành động dưới đây đã được thực hiện. YELLOW do yêu cầu Revenue Copilot v2.1 của người dùng, không phải yêu cầu phát sinh từ skill. Im lặng không có giá trị phê duyệt. Chọn approve/defer/reject từng nhóm; phê duyệt hướng kinh doanh không mặc định cho phép mọi chi phí hay truy cập.

| ID | Mục đích và hành động cụ thể đề nghị | Chi tăng thêm | Rủi ro | Cách rẻ hơn | Lợi ích kỳ vọng | Quyền cần |
|---|---|---:|---|---|---|---|
| A1 | Sau Gate0 làm một mẫu QA dữ liệu giả≤1h và brief chuẩn; kiểm công cụ có sẵn, không cài | 0 | Làm quá scope, nhầm mẫu thành case thật | Không mẫu, chỉ mô tả nhưng khó tạo tin cậy | Kiểm năng lực trước bán | Phê duyệt experiment và giới hạn20h |
| A2 | Operator tự xác minh ngân hàng nhận tiền dịch vụ, biểu phí; xác định nghĩa vụ đăng ký/thuế/chứng từ qua nguồn chính thức, tư vấn nếu cần | 0 khi tự kiểm; tư vấn có phí chưa được duyệt | Phân loại pháp lý sai, phí hoặc chậm thanh toán | Giữ nghiên cứu, chưa nhận đơn | Loại điểm nghẽn trước nhận tiền | Không cung cấp agent mật khẩu/tài khoản/chứng từ; khoản phí cụ thể xin riêng |
| A3 | Tìm thủ công và trả lời tối đa10 yêu cầu tuyển/cần hỗ trợ phù hợp; DM chỉ khi mời; tối đa một mẫu giới thiệu tại nơi cho phép nếu duyệt riêng nội dung | 0 | Vi phạm group rules, làm phiền, mất uy tín | Ba cuộc trao đổi opt-in thuần nghiên cứu sau duyệt | Kiểm demand địa phương và giá | Duyệt kênh, nội dung và danh sách đủ điều kiện trước gửi; chưa có10 tên |
| A4 | Quote pilot500k, tối đa200 dòng/10 cột,48h,1 lượt sửa; đề nghị cọc250k, phần còn lại sau nghiệm thu | 0 dự kiến; phí thực tế chưa biết | Tranh chấp scope, nghĩa vụ hoàn cọc/hóa đơn | Chỉ phỏng vấn, chưa cam kết | L3 rồi cash collected | Operator duyệt brief/điều kiện hoàn, tự xử lý thanh toán; không agent financial action |
| A5 | Nhận file catalogue được phép và đã bỏ thông tin cá nhân; lưu cục bộ, xử lý, bàn giao đúng người nhận | Dự phòng25k/đơn | Dữ liệu bí mật/IP, nhầm file, macro độc hại | Dữ liệu giả/khách chia sẻ mẫu không nhạy cảm | Kiểm delivery thật | Duyệt dữ liệu, người nhận, nơi lưu, thời hạn giữ; không upload AI |
| A6 | Nếu có chi phí thật: trình tên hàng/dịch vụ, nhà cung cấp, số tiền, thuế, lý do và phương án0đ trước chi | Đề nghị tổng≤50k, cap tuyệt đối500k | Chi lẻ tích lũy, subscription | Không mua, dừng | Chỉ tháo nút thắt có bằng chứng | Không blanket spending approval; chưa có khoản mua cụ thể |
| A7 | Chỉ nếu chọn thị trường quốc tế sau review: xác minh eligibility và phí, tạo tài khoản hoặc mua Connects | Chưa ước lượng đầy đủ; KHÔNG trong pilot mặc định | KYC, payout, phí đấu thầu, ToS | Khách nội địa opt-in | Mở kênh khác nếu chứng minh hợp lý | Phê duyệt riêng; không thực hiện |
| A8 | Bất kỳ API, cài tool, publish, upload data hoặc sửa production sau này | Chưa xác định | Quyền truy cập, dữ liệu, phí định kỳ | Manual/offline file-only | Chưa chứng minh cần thiết | Không đề nghị duyệt lúc này; phải có action cụ thể mới |

Đề nghị Gate0: chọn A làm primary; B dự phòng nhưng chưa chạy; ngân sách dự kiến0 trước khách, reserve≤50k sau duyệt từng khoản; trần500k giữ nguyên. Nếu chỉ muốn thêm nghiên cứu, chọn tối đa3 cuộc trao đổi opt-in và chưa chào bán. Bước đầu sau duyệt là chuẩn bị mẫu/brief và danh sách cho duyệt, không tự gửi ngay.

Không yêu cầu hay lưu API keys, số tài khoản, thẻ, mật khẩu, token, giấy tờ hoặc payment screenshots. Người dùng thực hiện xác minh/payment trong môi trường của mình, chỉ báo kết quả và khoản phí cần tính.
