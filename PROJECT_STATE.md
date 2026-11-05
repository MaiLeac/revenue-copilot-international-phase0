# Money HQ — trạng thái có bằng chứng

**Kiểm tra cục bộ:** 05/11/2026, khoảng 08:55 ICT. Đây là ảnh chụp tại thời điểm kiểm tra, không phải giám sát thời gian thực. Trạng thái dịch vụ phải được kiểm tra lại trước khi hành động. Xem [README](README.md) để biết thứ tự ưu tiên.

## Doanh thu và chi phí

- [`finance/CASH_LEDGER.csv`](finance/CASH_LEDGER.csv) và [`finance/COST_LEDGER.csv`](finance/COST_LEDGER.csv) chỉ có tiêu đề. **Chưa ghi nhận khoản L4 hay chi phí tăng thêm trong hai sổ.** Chưa đối soát trực tiếp ngân hàng hay các nguồn thu ngoài sổ.
- Giờ của chủ dự án chưa được ghi đầy đủ; không được kết luận là `0 giờ` hay tính lợi nhuận sau công lao động.
- Không có bằng chứng về lượt xem, khách có ý định mua, đơn thật hoặc tỷ lệ chuyển đổi. Ghi `chưa biết`, không tự gán `0 traffic`.
- Mục tiêu 15 tỷ VND là định hướng của Mai; chưa định nghĩa đây là tổng tiền thu, lợi nhuận tích lũy hay tài sản ròng. Không báo phần trăm hoàn thành mốc đó khi chưa chốt thước đo.

## Tài sản và điểm nghẽn

| Tài sản | Điều đã kiểm tra | Điểm nghẽn gần tiền | Không được suy ra |
|---|---|---|---|
| Bản Thảo / EXP-03 | Có web và [danh mục](experiments/exp03-duong-nhan-ai-mvp/products.json) với sách ở trạng thái `draft`; [checkout](experiments/exp03-duong-nhan-ai-mvp/checkout.html) ghi rõ chưa mở | Sách do chủ dự án viết chưa hoàn tất; chưa có file giao, giá và đường đặt mua đã thử | Đã mở bán, có trà/quà, VietQR tự xác nhận, có doanh thu |
| CatalogueQA / EXP-02 | Có nguyên mẫu web và bộ dữ liệu 120 dòng tổng hợp | Chưa có bằng chứng người mua và khác biệt trả phí | Mẫu tổng hợp là khách thật hoặc giá niêm yết là doanh thu |
| Wink Living | Có mã/đường dẫn dự án trong hồ sơ | Chưa đối chiếu khách, giao dịch và quyền thu tiền | Link tồn tại nghĩa là có thu nhập |
| Loser Kingdom | Có tài sản ứng dụng; cổng `8888` không lắng nghe lúc kiểm tra | Chưa có sản phẩm trả tiền và dữ liệu khách | Ứng dụng local là sản phẩm thương mại đang hoạt động |
| Little Loop Factory | Có tài sản sản xuất video; cổng `3210` không lắng nghe lúc kiểm tra | Chỉ hữu ích khi có sản phẩm/offer và kênh phân phối được thử | Render video là có traffic hoặc bán hàng |
| MT5 / Vibe-Trading | `run_state.json` ghi tài khoản **demo**, không có lệnh gần đây; heartbeat cuối 08:02 ICT. Cổng `8899` không lắng nghe lúc kiểm tra | Chưa có bằng chứng lợi thế sau phí và độ ổn định ngoài mẫu; cần chẩn đoán và sửa trong demo | Nhãn `RUNNING`, backtest hoặc hai tuần demo chứng minh có lãi hay đủ thi quỹ |
| Agent Zero / Telegram | 08:55: cổng Windows `5080` không lắng nghe. 12:37: container WSL chạy, ba lịch runtime đều `disabled`; lượt thử CatalogueQA chỉ chạy 5 test cũ, không sửa file | Thiếu vòng thực thi → đo → tìm nguyên nhân → sửa để tạo tiền; các lượt trước có báo cáo sai | Có container hoặc prompt/lịch là có agent đang tự tạo tiền |

Lúc kiểm tra, cả `5080`, `8000`, `8888`, `3210`, `8899` đều không lắng nghe. Dịch vụ ngoài máy như `winkhere.com` chưa được xác minh trong lần kiểm tra này.

## Việc kế tiếp theo quan hệ nhân quả

1. Bản Thảo: hoàn thiện sản phẩm số thật hoặc nhận một sản phẩm số khác đã có file/quyền sử dụng. Không tự viết thay tác giả rồi gọi là sách hoàn chỉnh.
2. Kiểm thử đường nhận đơn → xác nhận chuyển khoản thủ công → giao file riêng tư → ghi tiền thật; chỉ mở thanh toán sau khi đủ điều kiện.
3. Thử một kênh phân phối hợp lệ, có giới hạn thời gian/chi phí và cách ghi phản hồi. Nếu không có tín hiệu mua, chẩn đoán, sửa và thử lại trước khi chuyển hướng.
4. Song song trong phần việc tự làm được, kiểm định và sửa MT5 ở demo nếu có giả thuyết cụ thể. Không coi việc này là tiền thật hay quyền giao dịch thật.
5. Mỗi vòng AI phải ghi thay đổi cụ thể, bằng chứng, chi phí, nguyên nhân thất bại và lần sửa tiếp theo. Không báo `healthy` chỉ vì test xanh hay cổng mở.

## Cách đọc các hồ sơ cũ

[`PROJECT_FLIGHT_RECORDER.md`](PROJECT_FLIGHT_RECORDER.md) mô tả các nhánh cũ: EXP-03 trắc nghiệm/chẩn đoán từng bị khai tử; bản web Bản Thảo hiện tại là hướng **sản phẩm số khác** và vẫn chưa được xác nhận bán được. Các báo cáo cũ gọi năm dự án “live 100%” hoặc nói đã có checkout là không phù hợp với trạng thái này. Xem [bản đồ tài liệu](docs/DOCUMENT_STATUS.md).
