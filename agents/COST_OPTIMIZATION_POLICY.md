# Chi phí và năng suất thực

**Mục tiêu:** tiền ròng đã nhận và khả năng lặp lại trên mỗi giờ của Mai, mỗi đồng chi thêm, mỗi token và mỗi đơn vị rủi ro. Tối ưu không có nghĩa bật tất cả dịch vụ liên tục.

## Quy tắc hiện tại

- `finance/COST_LEDGER.csv` chỉ có tiêu đề. Đây là **0 chi phí được ghi**, không chứng minh mọi dịch vụ hoặc subscription đều miễn phí.
- Dashboard hiện đặt **0 VND chi tiêu tăng thêm được phép trong phép tính**. Mốc 500.000 VND ở kế hoạch cũ là giới hạn tối đa lịch sử, **không phải quyền tự chi**. Mỗi khoản tiền/API mới cần chủ dự án duyệt đúng hành động, số tiền và tính lặp lại.
- Với từng nguồn thu nhỏ, tính `tiền thực nhận - phí nền tảng/thanh toán - chi phí giao - chi phí AI tăng thêm`. Chỉ nhân rộng khi số này dương và biết số giờ Mai bỏ ra. Khi chưa có tiền thực nhận, dùng AI sẵn có không phát sinh thêm phí; doanh thu dự kiến không phải ngân sách API. Ghi cả phần subscription đã cam kết khi đánh giá lợi nhuận đầy đủ, nhưng tách khỏi chi phí tăng thêm của quyết định mới.
- Trước khi dùng một repo, model hay dịch vụ: kiểm tra đã cài chưa, quyền dùng, chi phí tăng thêm, giới hạn quota và đầu ra cần có. Star, README và nhãn “free” không chứng minh chi phí bằng 0 trong môi trường này.
- Dùng script cho tính toán chắc chắn; dùng AI cho phán đoán, viết và sửa khi có việc cụ thể. Không gọi nhiều model để xác nhận điều đã có thể kiểm tra trực tiếp.
- Khi tác vụ nền chưa giúp tạo tiền hoặc sửa nghẽn, trước hết tìm nguyên nhân: sai đầu vào, sai mục tiêu, lỗi thực thi hay thiếu kênh sử dụng. Sửa và kiểm tra lại nếu chi phí hợp lý; chỉ tắt phần tiêu hao vô ích sau khi đã ghi chẩn đoán và phương án thay thế.
- Ghi giờ của chủ dự án; nếu chưa ghi đủ, không gọi đóng góp sau lao động là lợi nhuận.

## Trước mỗi thử nghiệm

Ghi: cơ chế tạo tiền, điểm nghẽn, thay đổi dự kiến, cách kiểm chứng, giờ dự kiến, chi phí tiền mặt tối đa, giới hạn rủi ro và tiêu chí chẩn đoán lại. Sau đó ghi số thật phù hợp cơ chế: phản hồi/đơn nếu bán hàng; lợi thế sau phí, drawdown và kiểm định ngoài mẫu nếu là trading demo; L4, phí và giờ cho mọi hướng. Không dựng bảng “tiết kiệm hàng triệu đồng/tháng” khi chưa có đối chứng.
