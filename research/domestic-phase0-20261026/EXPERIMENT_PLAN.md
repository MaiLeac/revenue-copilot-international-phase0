# Đề xuất experiment một trang — CHƯA ĐƯỢC DUYỆT

**Giả thuyết:** trong10 người mua phù hợp được tiếp cận hợp lệ, ≥1 người trả500.000 VND cho lô QA catalogue nhỏ. Đây là giả thuyết, không phải dự báo tỷ lệ10%.

**Khách và offer:** shop/agency Việt có file catalogue và nhu cầu sửa trong14 ngày. Một file ≤200 dòng variant/10 cột/1 schema; file sạch, issue log, mapping và đối chiếu dòng; một lượt sửa,48h từ khi đủ brief. Giá500.000; dự kiến250.000 đặt trước và250.000 sau nghiệm thu. Không đảm bảo import, doanh số hay dữ liệu nguồn đúng. Giá dựa scope; tham chiếu E01–E07 trong EVIDENCE_LOG.csv, không lấy ngân sách quốc tế làm giá Việt đã xác nhận.

**Điều kiện trước bán:** Gate0 explicit; kiểm tra thủ công công cụ sẵn có; bài QA giả lập≤1h; operator tự xác nhận đường nhận tiền/phí và đăng ký-thuế-hóa đơn phù hợp, không chia sẻ credentials. Chưa giải quyết thì không nhận cọc. Không prototype/portfolio được tạo trước Gate0.

**Kênh:** tìm thủ công6 bài buyer yêu cầu catalogue +4 agency công khai mời ứng tuyển; phải đủ điều kiện và rules cho phép. Tối đa4h tìm,10 phản hồi cá nhân hóa; chỉ DM khi mời/đồng ý. Không biến bài forum cũ E03/E04 thành lead nóng. Không paid ads, scraping, mua lead, chuyển khách marketplace ra ngoài. Không có đủ10 thì ghi thiếu, không lấp bằng tin nhắn ngẫu nhiên.

**Giao thủ công sau duyệt:** (1) chốt mẫu đã loại thông tin cá nhân, quy tắc và phạm vi; (2) giữ nguyên file nguồn, bản làm việc riêng, mã dòng/SKU dạng text; (3) kiểm trống/trùng/kiểu và variant; (4) sửa theo quy tắc khách duyệt, flag phần không rõ; (5) rà100% SKU/giá/dòng sửa, đối chiếu tổng dòng và20 dòng do khách chọn; (6) bàn giao file + log, khách tự test/import; một lượt sửa. Không ghi đè production, tự xóa record hay đoán thuộc tính. Kiểm phát hiện công thức nguy hiểm trong CSV trước mở; không chạy macro/file thực thi của khách.

**Nguồn lực L0:** 2h setup +8h acquisition/brief +6h giao/QA/admin=16h; tối đa20h toàn thử trước review. Tiền dự kiến0–25.000/pilot, đề nghị hạn mức50.000 và vẫn xin duyệt từng khoản; không API/thuê bao. Trần tuyệt đối500.000; phần chưa phân bổ không được tự tiêu. Sau công50k/h, trường hợp16h thu đủ500k và chi25k → -325k, không gọi là profit.

**Thời hạn:** D0 là ngày được duyệt; D1–3 kiểm điều kiện + mẫu; D4–10 tìm/trao đổi; D10 đánh giá kênh; D14 phải có cọc hoặc commercial next step cụ thể; D21 mục tiêu giao và thu đủ; D30 kết thúc. Nếu D0=26/10/2026 thì D30=25/11/2026; duyệt muộn phải chốt lại deadline, không âm thầm kéo dài mục tiêu.

**Đo:** số lead đủ điều kiện, quyền liên hệ, phản hồi, cuộc trao đổi, brief đủ dữ liệu, quote, L3, tiền thực nhận/hoàn, doanh thu thực hiện, phí, giờ, lỗi, rework. Không lưu payment instruments. Operator tự xác nhận giao dịch đáng tin cậy tại ngân hàng; báo cáo phân biệt tự xác nhận với độc lập kiểm chứng. Ảnh chuyển khoản/pending/escrow không coi là cash available.

**Pass:** ≥3 trao đổi đủ điều kiện; ≥1 pilot thu đủ500k trướcD30; giao≤6h; không lỗi critical SKU/giá hoặc mất dòng chưa ghi log, mẫu20 dòng đúng100% quy tắc; khách nghiệm thu; chi≤50k. Cash milestone phụ: cọc250k thực vào trướcD14 nhưng chưa là thành công hoàn chỉnh. Một khách không chứng minh repeatability hoặc profit.

**Stop/pivot:** chưa xác minh pháp lý/rail → dừng thương mại; sau10 tiếp cận hoặc10h mà <3 trao đổi → review kênh; D14 không cọc → dừng offer hiện tại, không tăng chi; scope>6h/nhạy cảm/quyền production → từ chối hoặc báo lại sau duyệt; đạt20h/chi vượt50k → xin quyết định mới; hếtD30 không tiền → thất bại mục tiêu. Không tự chạy backup.

**Sau thử:** chỉ đề nghị lặp nếu khách hài lòng và lần tiếp theo có thể ≤9,5h tổng; cần khách thứ hai thu tiền và contribution sau công dương mới xét lặp lại. Chỉ tự động hóa bước đã lặp ổn định ở hai delivery; khách tái mua hoặc batch tiếp theo có trả tiền mới là bằng chứng asset/workflow, không phải lời khen. Không mở pha sau trong phiên này.
