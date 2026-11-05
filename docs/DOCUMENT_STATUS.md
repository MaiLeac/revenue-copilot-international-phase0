# Bản đồ tài liệu Money HQ — 05/11/2026

Mục đích: agent không được lấy một mô tả cũ, file cấu hình hay báo cáo sinh tự động làm sự thật hiện hành. **Thứ tự:** yêu cầu mới nhất của chủ dự án → bằng chứng trực tiếp ở thời điểm làm → `README.md`/`PROJECT_STATE.md`/sổ tiền → tài liệu vận hành hiện hành → hồ sơ lịch sử. Khi hai nguồn mâu thuẫn, kiểm tra dữ liệu gốc rồi sửa nguồn hiện hành; giữ lịch sử bằng Git và nhãn rõ ràng.

Đã rà tên và tìm các tuyên bố trạng thái/giá/thanh toán trên **54 tài liệu Markdown hiện không nằm trong `archive/`, `engine-runs/` hoặc kho tri thức nguồn**. Các file sinh từ backtest và kho tri thức được xếp vào nhóm dữ liệu, không dùng làm chỉ dẫn vận hành.

| Nhóm | File/phạm vi | Cách dùng |
|---|---|---|
| Hiện hành, ưu tiên cao | `README.md`, `AGENTS.md`, `AI_MANDATE_CONSTITUTION.md`, `OPERATING_SYSTEM.md`, `PROJECT_STATE.md`, `portfolio/OPPORTUNITY_REGISTER.md`, `portfolio/WINK_ECOSYSTEM_CHARTER.md` | Mục tiêu, trạng thái, thứ tự làm việc. `PROJECT_STATE.md` là ảnh chụp có ngày, phải kiểm tra lại trước khi kết luận dịch vụ đang chạy. |
| Vận hành hiện hành | `agents/AI_ROUTING_POLICY.md`, `agents/COST_OPTIMIZATION_POLICY.md`, `agents/ROLE_CHARTER.md`, `operations/ATTENTION_PANEL.md`, `operations/DAILY_BRIEF.md`, `operations/OWNER_ACTIONS.md`, `operations/EXECUTION_HANDOFF.md` | Dùng để chọn và ghi việc. Brief/handoff có ngày; không biến report của agent thành bằng chứng thanh toán. |
| Tiền và sản phẩm | `finance/CASH_LEDGER.csv`, `finance/COST_LEDGER.csv`, `finance/AI_USAGE_AND_COST_LOG.csv`, `finance/MONEY_HQ_DASHBOARD.*`, `experiments/exp03-duong-nhan-ai-mvp/products.json`, `CATALOG_OPERATIONS.md` | Ledger là bản ghi, dashboard là phép tính từ bản ghi, không phải xác nhận ngân hàng. Catalog hiện chỉ có sách `draft`. |
| Danh mục công cụ | `assets/web_capability_library/catalog.json`, `CAPABILITY_ROUTING.md`, `tools/capability_lookup.py` | Repo ứng viên; phải kiểm tra cài đặt, license, chi phí trước khi dùng. `CAPABILITY_LIBRARY.md`, `assets/web_design_framework/*`, `assets/getlayers_library/*` là tài liệu tham khảo, không chứng minh tích hợp. |
| Hồ sơ lịch sử/pivot | `PROJECT_FLIGHT_RECORDER.md`, `operations/QA_RISK_AUDIT_CYCLE1.md`, `docs/REVENUE_REFORM_2026-11-04.md`, `research/**`, `archive/**`, `experiments/exp02-*/EXPERIMENT_SPEC.md`, `OFFER_AND_OUTREACH_KIT.md`, `experiments/exp03-*/EXPERIMENT_SPEC.md`, `distribution_kit.json` | Giữ để hiểu quyết định cũ. Giá, trà/quà, job thủ công, quiz sức khỏe, checkout tự động, nhận định pháp lý hoặc status “live” trong đó **không phải kế hoạch hiện hành**. |
| Kỹ thuật/demo/đầu ra máy | `trading-agent-exness-demo/**`, `AUDIT_PACK_TRADING_AGENT.md`, `experiments/sol-backtest/**`, `docs/knowledge_base/**`, `assets/knowledge_mining_engine/**`, `tools/vibe-trading-launchers/**` | Code, thử nghiệm và dữ liệu. Backtest/demo không là L4, `run_state.json` có thể cũ. Kiểm tra timestamp, nguồn dữ liệu và lệnh thật trước khi tuyên bố running/profit. |
| Agent Zero setup | `tools/agent-zero-setup/README.md`, `TELEGRAM_AND_SCHEDULER_SETUP.md`, `tasks.json`, `usr_config/scheduler/tasks.json` | Cấu hình/hướng dẫn. `tasks.json` cũ đã gắn nhãn obsolete; cổng runtime và lịch thật phải xác minh trực tiếp. |

## Những mâu thuẫn đã xử lý

1. README, hiến chương, charter và opportunity board từng gọi Bản Thảo là offer 199k–389k kèm trà, VietQR/MoMo hoạt động. Hiện sản phẩm số đang viết, checkout đóng; các file hiện hành đã sửa. Bản kế hoạch cũ được gắn nhãn lịch sử.
2. `PROJECT_STATE.md` từng gọi EXP-03 “khai tử” đồng thời các bảng khác gọi nó “flagship live”. Đã tách **quiz/chẩn đoán cũ đã dừng** khỏi **web sách số mới chưa mở bán**.
3. Báo cáo từng ghi “zero traffic”, “100% ready”, mọi dịch vụ chạy và Agent Zero tự kiếm tiền mà không có số đo. Nay ghi `chưa biết`; cổng local được kiểm tra tại một thời điểm, không suy ra uptime dài hạn.
4. Dashboard từng có giá cũ, quà vật chất, khoản tiết kiệm giả định, 0 giờ chủ dự án và tên “net profit” cho tiền sau một phần chi phí. Generator và artifact đã đổi sang số ghi trong ledger, chỉ rõ chi phí/giờ còn thiếu.
5. MT5 từng được mô tả như đường tiền đầu tiên và hai tuần demo đủ thi quỹ. Nay tách thành demo/nghiên cứu; không tính kết quả trading ảo vào L4.
6. Lịch Agent Zero trong template cũ bắt đầu bằng pytest/báo cáo. Tài liệu setup đã gắn nhãn template obsolete; vòng làm việc hiện hành đòi thay đổi cụ thể trên một đường tạo tiền có thể kiểm chứng.
7. Quy tắc cũ dễ hiểu thành bỏ hướng làm sau một thử nghiệm thất bại và chỉ tìm khách mua sản phẩm. README, chỉ dẫn agent và tài liệu vận hành hiện yêu cầu chẩn đoán → sửa → thử lại; chỉ chuyển nguồn lực theo bằng chứng, chi phí và rủi ro. Mục tiêu 15 tỷ là đích chưa được định nghĩa thành thước đo tài chính cụ thể.

Các file trong nhóm lịch sử không được chỉnh lại kết luận ngày xưa như thể chúng chưa từng tồn tại. Khi phát hiện mâu thuẫn mới, ghi nó tại đây cùng nguồn và ngày kiểm tra.
