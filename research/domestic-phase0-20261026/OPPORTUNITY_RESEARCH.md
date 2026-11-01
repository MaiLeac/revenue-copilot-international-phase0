# Phase 0 — nghiên cứu và chuẩn bị quyết định

Ngày quan sát: 26/10/2026, Asia/Bangkok. Không liên hệ, đăng ký, tải dữ liệu khách, cài phần mềm, chi tiền hay chạy experiment. Chỉ đọc web công khai và tạo tài liệu cục bộ. Không xác minh thanh toán thực tế; L3=0, L4=0. Không dùng điểm số trọng số.

## 1. Phương pháp và bằng chứng

Trình tự: hồ sơ → vấn đề → tín hiệu → đối thủ → offer → kênh → kinh tế → thử nghiệm → công cụ. Tìm bằng tiếng Việt và Anh; ưu tiên yêu cầu của người mua và tài liệu chính thức. Không coi kết quả tìm kiếm là trang đã mở; ghi 403/timeout. Không dùng số lượng job của trang tổng hợp làm số khách độc lập. Ngày “vừa đăng” của marketplace không được suy ngược thành ngày lịch đáng tin cậy.

EVIDENCE_LOG.csv ghi 10 tín hiệu thị trường có giới hạn và các nguồn hỗ trợ riêng. E01/E02 là hai yêu cầu thuê khác Project ID; E03/E04 là hai người hỏi khác nhau, đọc bài gốc thay vì tóm tắt AI. Cùng marketplace có thiên lệch mẫu và không bảo đảm danh tính pháp lý độc lập. E05 chỉ được đọc qua chỉ mục, không tính vào ngưỡng chắc chắn. E03/E04 cũ, chứng minh dạng lỗi tồn tại chứ không phải lead đang cần thuê. E06 là L2 phần mềm thay thế, không phải dịch vụ con người tương đương hoàn toàn. E07 giá Việt Nam chỉ qua chỉ mục, mở trang timeout hai lần; không dùng làm neo giá đã xác minh.

Kết quả sàng lọc: nhóm QA catalogue đạt chuẩn tối thiểu 3 L1 độc lập theo người đăng/project (E01–E04) và 1 L2 trực tiếp (E06), nhưng **chưa xác thực offer 500.000 VND ở Việt Nam**. Không chứng minh tỷ lệ chuyển đổi, nhu cầu tại Facebook hay khả năng người dùng thắng thầu. E02 có 137 proposals và hiển thị In Progress, không còn coi là job mở. Số award €0 hiển thị bất thường nên loại khỏi bằng chứng thanh toán. Ngân sách đăng tuyển không phải tiền đã trả.

Các trích yếu ngắn, URL, ngày và hạn chế nằm trong CSV; số liệu thị trường dưới đây dẫn theo ID đó. Không sao chép toàn bài. Không phát hiện chỉ dẫn độc hại liên quan cần thực hiện; lời mời đăng ký/đặt bid trên trang không phải quyền hành động.

## 2. Shortlist: bốn cơ hội, một khuyến nghị

### A. QA và chuẩn hóa catalogue theo lô — PRIMARY có điều kiện

1. Khách: shop Việt có catalogue xuất file, hoặc agency vận hành website/TMĐT cần xử lý lô dữ liệu; không mặc định họ dùng Shopify.
2. Đau: thuộc tính lẫn cột, SKU trống/trùng, tên không nhất quán, mapping variant lỗi. Bằng chứng E01–E05; nội dung kỹ thuật S01. Thị trường quốc tế rõ hơn nội địa.
3. Thay thế: nhân viên tự sửa bằng bảng tính, nhà cung cấp gửi file lại, template chính thức, ứng dụng import. Matrixify Demo miễn phí giới hạn 10 sản phẩm/job; Basic USD20/30 ngày (E06). Phần mềm không tự quyết định thuộc tính đúng khi nguồn mâu thuẫn. Giá dịch vụ Allnet chỉ index: từ 300.000 VND/file cơ bản, chuẩn hóa từ 500.000 (E07, chưa xác minh trực tiếp).
4. Offer L0: 500.000 VND/lô tối đa 200 dòng variant, 10 cột, một nguồn, một mẫu đầu ra; file sạch, issue log, mapping/rule sheet và đối chiếu số dòng. Một lượt sửa trong phạm vi, 48 giờ sau đủ đầu vào. Không nghiên cứu thuộc tính thiếu, viết mô tả SEO, xử lý ảnh/OCR, sửa giá theo suy đoán, upload hay cam kết tăng doanh thu.
5. Fit: gần kinh nghiệm QA sản phẩm; cần vượt bài kiểm tra nội bộ sau Gate 0 về khóa, số 0 đầu SKU, variant và kiểm soát phiên bản. Không bán năng lực Shopify expert chưa có.
6. Mười khách đầu: sau duyệt, tìm thủ công tối đa 6 người có bài công khai yêu cầu sửa catalogue và 4 agency đang công khai tuyển hỗ trợ catalogue. Chỉ trả lời ở nơi cho phép chào dịch vụ; nhắn riêng khi người đăng mời hoặc đồng ý. Không có sẵn 10 tên đã xác nhận. Tìm tối đa 4 giờ; thiếu ứng viên là kết quả thất bại kênh, không chuyển sang spam. Không mang khách marketplace ra ngoài trả tiền.
7. Thời gian nhận khoản đầu L0: ngày 7–14 nếu có một brief phù hợp và đồng ý đặt trước; hoàn tất tiền ngày 10–21. Có thể không thu được gì trong 30 ngày.
8. Giá là giả thuyết từ phạm vi và công sức, không phải suy ra trực tiếp từ USD400/E05. Chỉ nhận sau xem mẫu đã loại dữ liệu cá nhân; scope quá lớn thì không báo cùng giá.
9. Giao hàng 4 giờ + QA/sửa/admin 2 giờ. Chi phí biến đổi dự phòng 25.000 VND/đơn; thực tế có thể 0, phí ngân hàng chưa rõ.
10. Contribution trước công 475.000; sau công giao 6 giờ ×50.000 còn 175.000, chưa acquisition. Đơn đầu 16 giờ tổng → -325.000. Bảng chi tiết bên dưới.
11. Nút thắt: niềm tin và tiếp cận người mua; giả định rủi ro nhất là họ trả 500.000 cho một người chưa có portfolio, thay vì tự làm.
12. Test rẻ: một mẫu giả lập rõ nhãn, trả lời tối đa 10 yêu cầu phù hợp, đề nghị pilot có trả tiền; không làm miễn phí cả file. Mọi thứ chờ Gate 0.
13. Loại nếu không có 3 cuộc trao đổi đủ điều kiện sau 10 tiếp cận, không có cam kết trả tiền, file đòi quyền production hoặc >6 giờ giao.
14. Tài sản lặp lại: taxonomy lỗi, checklist, rule library theo schema và gói QA lô tiếp theo. Chỉ tự động hóa bước ổn định sau ít nhất 2 khách thanh toán; không tái sử dụng dữ liệu khách làm tài sản.

### B. Cập nhật catalogue định kỳ từ file nhà cung cấp — BACKUP có điều kiện

1–3. Khách shop/agency có bảng giá theo đợt; đau là ghép SKU và giữ tên/variant. E02/E03 và E06; tự VLOOKUP/XLOOKUP, nhập lại hoặc dùng bulk editor là thay thế. Chia sẻ bằng chứng với A, không tính thêm tín hiệu độc lập.
4–5. Offer L0: 750.000 VND/đợt, hai file cấu trúc rõ, ≤300 dòng, ≤5 trường thay đổi; bảng matched/unmatched và change log, không import. Hợp sales ops và QA; kỹ năng join dữ liệu phải kiểm tra trước.
6. Mười khách giả định: 5 người công khai hỏi cập nhật theo SKU, 5 agency công khai tìm trợ lý vận hành; cùng quy tắc opt-in và giới hạn thời gian như A, chưa có danh sách xác nhận.
7–10. Khoản đầu giả định ngày 10–21, phụ thuộc file mẫu và quyền dùng dữ liệu. Giao 7 giờ, chi biến đổi 25.000, contribution 725.000; trừ 350.000 công giao còn 375.000; thêm 8 giờ acquisition và 2 giờ setup → -125.000 đơn đầu. Giá cao hơn A do ghép hai nguồn và xử lý ngoại lệ; chưa ai đồng ý giá.
11–13. Bottleneck: khóa SKU không ổn định, sai giá ảnh hưởng bán hàng; giả định lịch cập nhật lặp lại. Test một đợt trả tiền, khách tự import 5 dòng rồi quyết định. Loại nếu phải đoán khóa, sửa giá tự động, hoặc không có đợt tiếp theo trong 30 ngày. Không test backup đồng thời primary.
14. Có thể chuyển thành gói QA tháng khi đã có nhu cầu thật; chưa gọi là subscription revenue. Dùng mapping tái sử dụng, mỗi thay đổi quy tắc vẫn cần duyệt.

### C. Đối chiếu đơn và danh sách ngoại lệ — HOLD

1–3. Khách shop có hai bản xuất đơn/giao hàng cần tìm dòng thiếu/trùng; E08 chỉ là đối chiếu receipt gần kề, chưa chứng minh nhu cầu chính xác này. Không có 3 L1 hoặc L2 đúng offer đã xác minh. Thay thế: nhân viên lọc Excel hoặc báo cáo phần mềm sẵn có; giá chưa xác minh. E09 yêu cầu nghiệp vụ tài chính cao, không phù hợp.
4–5. Offer L0: 600.000 VND, hai CSV đã bỏ tên/điện thoại/địa chỉ, ≤500 dòng, join theo mã đơn, bảng ngoại lệ; không sổ sách kế toán, thuế hay kiểm toán. Fit xử lý đơn nhưng rủi ro dữ liệu cá nhân.
6. Mười khách giả định: người đăng tìm hỗ trợ vận hành/đối soát thuộc 2–3 cộng đồng có luật rõ; chỉ phản hồi nhu cầu công khai, không thu thập đơn hay số điện thoại để tìm khách.
7–10. 10–25 ngày L0; giao 7 giờ, chi 25.000; contribution 575.000; sau công giao còn 225.000; tổng17 giờ gồm10 giờ setup/acquisition → -275.000.
11–13. Thiếu buyer proof, quyền xử lý dữ liệu và quy tắc hoàn/huỷ. Test rẻ nhất sau duyệt: phỏng vấn có đồng ý, chỉ dùng mô tả/quy tắc và dữ liệu giả. Không bán trước khi hiểu ngoại lệ. Loại nếu đòi dữ liệu cá nhân hoặc nghiệp vụ kế toán ngoài năng lực.
14. Có thể thành checklist đối chiếu và báo cáo theo kỳ; vẫn phụ thuộc người kiểm ngoại lệ. Không chọn làm backup hiện tại.

### D. Nghiên cứu danh sách doanh nghiệp từ nguồn được phép — HOLD

1–3. Khách agency/sales cần thông tin doanh nghiệp có nguồn; E10 chỉ trang category Upwork trong index, thiếu kiểm chứng brief riêng và mức độ độc lập. Thay thế: tự tìm, thư mục công khai, VA; giá đối thủ đúng phạm vi chưa xác minh. Không gộp lead-mining dữ liệu cá nhân vào dịch vụ này.
4–5. Offer L0: 500.000 VND/30 tổ chức ×5 trường (tên, website, ngành, vùng hoạt động, nguồn/ngày); không email/số điện thoại cá nhân, không gửi outreach. Fit đọc hiểu và tổ chức dữ liệu, chưa có kỹ năng market research chuyên sâu.
6. Mười khách giả định: phản hồi 10 brief công khai yêu cầu company research không đòi scraping riêng tư, qua kênh được cho phép. Tài khoản marketplace và phí chưa xác minh, nên đường này có thể bị chặn.
7–10. 14–30 ngày L0; giao 6 giờ, chi 25.000; contribution 475.000; sau công giao175.000; tổng16 giờ → -325.000. Giá theo scope, chưa có buyer validation.
11–13. Bottleneck: buyer thường muốn liên hệ cá nhân, khó chứng minh giá trị hơn tự tìm. Test rẻ nhất là xác nhận brief và ngân sách với người đã mời nhận proposal, không xây database trước. Loại nếu đòi scraping social, dữ liệu riêng tư, hoặc nguồn không cho phép.
14. Có thể tích luỹ taxonomy và workflow kiểm nguồn, không mặc nhiên được bán lại dữ liệu hoặc biến thành tài sản có IP độc quyền.

## 3. Kinh tế primary — VND; toàn bộ dự báo là L0

Không chuyển USD/EUR sang VND: giá ngoại tệ chỉ giữ nguyên để so sánh cấu trúc thị trường, không nằm trong ngân sách đề xuất; vì vậy không cần tỷ giá giả. Nếu chọn marketplace phải lấy tỷ giá nhận tiền thực tế và phí trước một phê duyệt riêng.

P=500.000/đơn; C=25.000/đơn dự phòng tiền mặt, gồm mọi chi tăng thêm nhỏ và phí nhận tiền chưa rõ; không coi đây là biểu phí. Labor v=50.000/giờ. Chi API, hosting, quảng cáo, thuê bao mới =0 theo thiết kế. Gói thuê bao hiện có chỉ là chi cam kết nếu thật sự còn hiệu lực; chưa phân bổ chúng thành chi tăng thêm hoặc coi miễn phí vô hạn.

| Tình huống giả định | Doanh thu khi hoàn tất | Chi biến đổi | Contribution trước công | Giờ | Công quy đổi | Sau công, trước thuế/chi cố định |
|---|---:|---:|---:|---:|---:|---:|
| Không bán được, dừng sau 10h | 0 | 0 | 0 | 10 | 500.000 | -500.000 |
| Một pilot đầu | 500.000 | 25.000 | 475.000 | 16 | 800.000 | -325.000 |
| Một đơn lặp lại, acquisition 1h | 500.000 | 25.000 | 475.000 | 7 | 350.000 | 125.000 |
| Ba đơn dùng chung10h setup/acquisition | 1.500.000 | 75.000 | 1.425.000 | 28 | 1.400.000 | 25.000 |

Đơn đầu: 2h setup +8h tìm khách/trao đổi +4h xử lý +2h QA/sửa/admin =16h. Chưa cộng thời gian người dùng đọc nghiên cứu Phase 0; không có số đo nên không bịa số giờ đã bỏ ra. Ghi thực tế từ Phase1; điều này làm kết quả sau công kém hơn nếu cộng đầy đủ.

Contribution cash = doanh thu thực hiện -chi biến đổi, không phải net profit. Tiền đặt trước 250.000 là cash collected nhưng còn nghĩa vụ giao/hoàn; không tự coi toàn bộ doanh thu đã thực hiện. 250.000 còn lại chỉ ghi thu khi tiền thực nhận. Tiền escrow/pending, ảnh chuyển khoản, promise và số trong log không phải xác nhận tiền vào ngân hàng. Operator tự đối chiếu; agent không truy cập hay lưu chứng từ chứa thông tin ngân hàng; nhật ký dùng mã nội bộ/ngày/số tiền/trạng thái do người dùng xác nhận, nêu rõ mức kiểm chứng.

Hòa vốn tiền mặt nếu thu đủ P và C≤25.000: một đơn đủ bù C; không đồng nghĩa hoà vốn công. Ngưỡng tổng giờ cho đơn 500.000 là (500.000-25.000)/50.000=9,5h. Với 10h acquisition/setup chung, 6h giao/đơn: n≥500.000/175.000, làm tròn 3 đơn; nếu acquisition lặp lại8h/đơn thì không đạt bằng cách tăng số đơn cùng giá. Đơn đầu để bù16h cần825.000 VND (giả thuyết, chưa chứng minh khách mua). Ở25k/h đơn đầu +75k, 50k/h -325k, 100k/h -1.125k. Rework +4h làm đơn lặp lại từ +125k thành -75k.

Ngân sách đề nghị: 0 trước khách; sau đồng ý scope chỉ dự phòng ≤50.000 tổng cho pilot, từng khoản phải duyệt. 450.000 còn lại không phân bổ và không được tự tiêu. Trần500k gồm API, công cụ, hạ tầng, phí, compliance nếu phát sinh; chi pháp lý ngoài trần → dừng. Không chi paid usage Phase0.

## 4. Công cụ và repository — sau sàng lọc

Không repository nào cần thiết cho việc kiểm chứng người mua trả tiền cho200 dòng. **0 repo audit**, không suy luận license hay maintenance. Danh sách ứng viên chỉ được loại theo phạm vi nhiệm vụ: browser-use không cần cho bảng tính thủ công; Vibe-Trading không phục vụ offer và trading bị cấm; huashu-design không cần cho catalogue QA; HowToLiveBetter chưa chứng minh nhu cầu, không tái sử dụng/biên dịch vì license chưa kiểm tra; automaton không triển khai, không ví/spend/spawn/self-modify. Đây không phải đánh giá an toàn code của các repo.

Tối thiểu: ứng dụng bảng tính đang được phép dùng, bản sao file cục bộ, checklist và change log. Chưa xác nhận Excel có license hoặc phần mềm bảng tính hiện hữu; nếu thiếu thì pause, không cài mới. Không cần đưa dữ liệu khách lên AI. Có thể viết công thức/script sau Gate0 nếu cần, chưa viết prototype trong Phase0. Các subscription tự khai không cần cho test nên entitlement chưa được kiểm tra tài khoản; giới hạn an toàn là không gọi API hay mua thêm.

## 5. Pháp lý, platform, privacy, payment

S02–S09 là nguồn chính thức, không phải L1/L2. Nguồn thuế cũ tháng3/2026 nói500 triệu đã được NĐ141 sửa thành1 tỷ tại các điều khoản liên quan (S02). Không suy ra bạn miễn đăng ký, miễn mọi thuế, miễn báo cáo hoặc có quyền xuất hóa đơn. Cần xác định tư cách hoạt động, tổng doanh thu năm, loại dịch vụ, khách đòi chứng từ gì, điều kiện đăng ký theo NĐ168 (S03), kê khai và hóa đơn với cơ quan thuế/chuyên gia phù hợp trước nhận đơn. Không dùng tư vấn này thay kết luận cho hồ sơ cá nhân.

Luật91/2025/QH15 có hiệu lực01/01/2026 (S04); nghiên cứu chỉ xác nhận metadata, chưa phân tích toàn luật/hướng dẫn/chuyển dữ liệu xuyên biên giới. Thiết kế giảm rủi ro: chỉ catalogue đã bỏ thông tin cá nhân; khách xác nhận quyền sử dụng/ủy quyền, nơi lưu/ai truy cập, thời hạn giữ và cách xóa phải thống nhất trước giao. Nếu phát hiện thông tin người mua/nhân viên, dừng và yêu cầu khách tự loại bỏ. Không upload AI; muốn đổi phải phê duyệt riêng cả đích nhận, dữ liệu và điều kiện.

Ngân hàng Việt Nam: chưa biết ngân hàng/gói tài khoản/phí/điều kiện nhận tiền dịch vụ; không khẳng định miễn phí. Operator tự kiểm tra, chỉ báo đạt/chưa đạt và phí không kèm số tài khoản. Wise/PayPal không phải đường dự phòng đã hoạt động. Upwork có service fee0–15%, Connects USD0,15, rút local bank USD0,99 và có thời gian chờ (S05–S07); không mặc định eligibility Việt Nam/cá nhân này hoặc mọi phí đã gồm. Marketplace không chọn cho pilot đầu. Không tìm buyer trên Upwork rồi chuyển bank ngoài nền tảng (S08).

Meta phản đối automated scraping không được phép (S09). Chưa xác minh rules từng Facebook group hay quyền self-promotion; phải đọc trước từng hành động, manual không tự động làm outreach hợp lệ. Không mass DM, follow-up chỉ khi đã được mời, không nhắn lại người im lặng. GitHub access không phải bằng chứng có người mua; không chào hàng trong issue không liên quan.

IP: khách phải có quyền dùng catalogue/ảnh/mô tả nhà cung cấp; không mặc định public=được sao chép. Pilot chỉ biến đổi file khách cung cấp, không dịch/repackage repo/content. Sở hữu đầu ra, bảo mật, quyền dùng rule template chung và cấm public case study khi chưa cho phép cần ghi trong brief.

## 6. Quyết định

Chọn A để xin phép thử có giới hạn; B chỉ dự phòng sau đánh giá lại. Không đủ bằng chứng để cam kết thu tiền30 ngày hoặc tự động hoá kiếm tiền. Nếu không đạt điều kiện trước bán, bước rẻ nhất là 3 cuộc trao đổi opt-in về brief/ngân sách sau duyệt, không xây sản phẩm. EXPERIMENT_PLAN.md định nghĩa thử; ACTION_REQUIRED.md liệt kê quyền cần cấp. **STOP tại Gate0.**
