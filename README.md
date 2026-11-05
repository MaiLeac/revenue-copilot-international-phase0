# Money HQ — nhiệm vụ cho mọi AI

**Đích của Mai: 15 tỷ VND càng sớm càng khả thi.** Đây là mục tiêu, không phải dự báo hay cam kết. Chưa chốt 15 tỷ là tổng tiền thu, lợi nhuận tích lũy hay tài sản ròng. Mốc đầu tiên: **tiền đã thực nhận và dùng được**. Tối ưu tiền ròng, tính lặp lại, giờ của Mai, chi phí, token và rủi ro.

**KPI vận hành trước mắt:** tiến tới 500.000 VND/ngày **tiền ròng thực nhận** sau phí và chi phí AI tăng thêm. Báo đúng số 0 khi chưa thu được; mỗi ngày phải có việc cụ thể, kết quả kiểm chứng và lần sửa tiếp theo. Không dùng tiền thật để ép trading đạt chỉ tiêu.

**Không mặc định phải bán hàng.** Xét mọi cơ chế thu tiền hợp pháp có thể kiểm chứng: sản phẩm, dịch vụ, cấp phép, hoa hồng, nền tảng hoặc đầu tư/trading. Không tính demo, backtest, lượt xem, đơn chưa trả hay báo cáo là tiền kiếm được. Không có việc nào chắc chắn làm là có tiền ngay.

**Tôn chỉ khác biệt:** một web hay đống code AI giống thứ người khác đã có không phải lợi thế. Trước khi mở rộng, chứng minh điều Mai làm tốt hơn hoặc khó sao chép hơn: dữ liệu, nội dung, quy trình, kết quả cho người dùng hoặc kênh tiếp cận. Tham vọng thành “kỳ lân” phải đi qua bằng chứng sử dụng, tiền thu và khả năng nhân rộng; không mua quảng cáo để che một offer yếu.

**Tiền lẻ vẫn làm:** ưu tiên cách thu nhỏ nhưng lặp lại được. Với từng việc, tiền thực thu phải lớn hơn phí nền tảng, chi phí giao và **chi phí AI tăng thêm**; tính riêng giờ của Mai. Khi chưa thu tiền, chỉ dùng tài nguyên AI đã có mà không phát sinh thêm phí. Không lấy doanh thu dự kiến để biện minh cho quota/API tính tiền.

**An toàn của Mai đứng trước KPI.** Mai là người có thể gánh trách nhiệm pháp lý, tài chính và mất dữ liệu; AI không được lấy mục tiêu doanh thu để đẩy rủi ro đó sang Mai. Trước khi xuất bản, nhận tiền, nhận dữ liệu thật, liên hệ người khác hoặc giao dịch, kiểm tra luật hiện hành, quy định nền tảng, quyền nội dung, bảo mật và khả năng thực hiện lời hứa. Không dùng câu “miễn mọi trách nhiệm” như lá chắn pháp lý; không bịa chứng nhận, chuyên gia hay bảo đảm kết quả. Nếu chưa rõ, giữ hành động rủi ro ở trạng thái chưa mở, tự hoàn thành phần nội bộ an toàn và đưa Mai quyết định cụ thể cần thiết.

## Vòng tự làm hằng ngày

1. **Chọn một đường tạo tiền cụ thể** và điểm nghẽn lớn nhất dựa trên dữ liệu gốc. Dùng nguồn công khai được phép, công cụ và repo sẵn có; không suy diễn từ lời hứa trong README hay báo cáo cũ.
2. **Thực thi một thay đổi kiểm chứng được.** Ghi đầu ra, nguồn, giờ, chi phí, rủi ro và tín hiệu dẫn tới tiền. Báo cáo, test và bot online chỉ là hỗ trợ.
3. **Nếu thất bại: tái hiện → tìm nguyên nhân → sửa → thử lại.** Không bỏ hướng làm sau một lần thử, không chỉ đi nghiên cứu ngách mới. Chỉ chuyển nguồn lực sau khi đã thử cách sửa hợp lý mà vẫn không hiệu quả, chi phí/rủi ro quá cao, hoặc hướng khác có bằng chứng tốt hơn. Ghi bài học để không lặp lỗi.
4. **Nếu bị chặn:** AI tự làm hết phần nội bộ có thể làm; chuẩn bị phương án, chi phí và quyết định cụ thể cần Mai khi thiếu quyền, tiền, dữ liệu hoặc việc chỉ Mai làm được. Không để việc nằm im rồi chờ Mai hỏi.
5. **Đo tiền thật.** Ghi tiền đã nhận, phí, chi phí, giờ Mai và khả năng lặp lại. Không nhận là có lợi nhuận nếu chưa tính đủ chi phí hoặc chưa đối soát giao dịch.

## Hiện trạng kiểm tra 05/11/2026

- [Sổ thu](finance/CASH_LEDGER.csv) và [sổ chi](finance/COST_LEDGER.csv) chỉ có tiêu đề: chưa **ghi nhận** tiền; chưa đối soát độc lập ngân hàng.
- [Bản Thảo](experiments/exp03-duong-nhan-ai-mvp/) là web sản phẩm số; sách đang viết, checkout đóng. Không bán trà hay sản phẩm vật chất. [CatalogueQA](experiments/exp02-catalogue-qa-pilot/) là nguyên mẫu, chưa có khách trả tiền được ghi nhận.
- MT5 đang ở mức nghiên cứu/demo. Tiếp tục tìm lỗi và kiểm định lợi thế sau phí, ngoài mẫu và rủi ro; không tự nâng lên giao dịch tiền thật hay thi quỹ chỉ vì hai tuần demo.
- Kiểm tra 12:37 ICT: container Agent Zero chạy trong WSL nhưng cả ba lịch runtime đều tắt. Lượt thử CatalogueQA chỉ chạy test cũ, không sửa file; chưa có AI tự thực thi hằng ngày.
- Bộ rà rủi ro không dùng AI chạy bằng Windows Task Scheduler mỗi ngày 09:00 (`MoneyHQ-RiskReview`); lượt chạy thử 05/11 thành công, kết quả cục bộ ở `operations/risk_review_latest.json`. Bộ này chỉ phát hiện một số lỗi có thể kiểm tra tự động; không cấp quyền hành động đối ngoại. [Cách vận hành](OPERATING_SYSTEM.md).

**Mỗi AI vào repo:** đọc [AGENTS.md](AGENTS.md), [trạng thái có bằng chứng](PROJECT_STATE.md), [bản đồ tài liệu](docs/DOCUMENT_STATUS.md); tra [công cụ/repo](assets/web_capability_library/CAPABILITY_ROUTING.md) khi có việc cụ thể. Tự làm việc nội bộ đã được giao. Với chi tiền, giao dịch tài chính, liên hệ người khác, xuất bản hoặc dùng dữ liệu khách, kiểm tra quyền đã cấp và giới hạn; chỉ xin quyền mới khi vượt phạm vi. Không bịa kết quả hoặc coi im lặng là phê duyệt.
