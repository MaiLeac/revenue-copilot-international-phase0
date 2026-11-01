# Catalogue QA Pilot — Offer Spec, SOP & Opt-In Outreach Templates (`EXP-02`)

> **Governance Gate:** Do NOT send any outreach or quote a binding price without owner approval and verified payment rail readiness. All portfolio attachments use the **100% Synthetic 120-Row Sample** (`sample_portfolio/SYNTHETIC_CASE_STUDY_REPORT.md`).

---

## 1. Fixed-Scope Pilot Specification ("200-Row Catalogue Rescue")

- **Deliverable:**
  1. `cleaned_catalogue.csv` — Normalized handles, trimmed titles, restored leading-zero SKUs, standardized option names/statuses, and formatted prices.
  2. `issue_log.csv` — Exact row and column numbers for every auto-fixed defect (`AUTO_FIXED`), warning (`WARNING`), and critical blocker (`CRITICAL` such as duplicate/missing SKUs or `$0.00` prices that require merchant confirmation rather than guessing).
  3. `AUDIT_SUMMARY_REPORT.md` — 100% row-count reconciliation before vs. after.
- **Hard Boundaries (What We Never Do):**
  - Never guess or invent missing business prices, missing SKUs, or missing variant options.
  - Never log into a client's production Shopify/WooCommerce admin to run destructive imports.
  - Never accept files containing customer names, addresses, phones, or payment data (any accidental email/phone in product descriptions is automatically flagged and redacted).
- **Turnaround:** 24–48 hours from receipt of PII-free CSV and schema confirmation.
- **Pricing Hypothesis:**
  - **International:** `100 USD` per batch (`<= 200 variant rows`, 50% upfront / 50% upon delivery review).
  - **Domestic (VN):** `500,000 VND` per batch (`<= 200 variant rows`, 50% upfront / 50% upon delivery review).

---

## 2. Standard Operating Procedure (SOP) — 15-Minute Delivery Pipeline

1. **Intake & Privacy Check (3 mins):** Verify the file has `<= 200 rows`, no customer PII columns, and a locked target header schema.
2. **Automated Pass (1 min):** Run `CatalogueQAEngine.process_files()` on the local CSV.
3. **Human QA Review (8 mins):** Inspect `issue_log.csv` and `AUDIT_SUMMARY_REPORT.md`, verify every `CRITICAL` row is clearly explained for the merchant, and confirm row counts match 100%.
4. **Delivery & Sign-off (3 mins):** Send the report + cleaned file + issue log; perform at most 1 scoped revision round after the client supplies missing SKU/price decisions.

---

## 3. Compliant Opt-In Reply Templates (For Owner Review Only)

### Template A — English (For Public Merchant/Agency Request Seeking CSV/Variant Cleanup)
> Hi [Name],
>
> Saw your post regarding the CSV variant/SKU import issues. Typically when Shopify/WooCommerce skips lines or overwrites fields, it comes down to leading zeros stripped from numeric SKUs, duplicate option combinations under the same handle, or blank `Option1 Value` cells.
>
> I run a deterministic Catalogue QA workflow for batches up to 200 variant rows (48h turnaround). Instead of guessing missing business prices or SKUs, I deliver:
> 1. A cleaned, import-ready CSV (handles, casing, leading zeros, and price formatting fixed).
> 2. A row-by-row `issue_log.csv` isolating every duplicate/missing SKU or price conflict for your final call.
> 3. A 100% before/after row reconciliation summary.
>
> I've attached a **synthetic 120-row sample audit** showing the exact output format. If helpful, happy to run a scoped batch (`$100` for up to 200 rows, no store admin access or customer PII needed).

### Template B — Vietnamese (Cho Chủ Shop / Agency TMĐT đăng bài cần chuẩn hóa file sản phẩm)
> Chào anh/chị [Tên],
>
> Mình thấy bên mình đang cần rà soát và chuẩn hóa file danh mục sản phẩm/SKU trước khi import. Các lỗi lệch dòng variant, mất số `0` ở đầu mã SKU khi mở bằng Excel, hoặc trùng tổ hợp thuộc tính thường làm hệ thống báo lỗi hoặc ghi đè nhầm giá.
>
> Bên mình chuyên xử lý chuẩn hóa & đối soát dữ liệu Catalogue theo lô (tối đa 200 dòng variant / lô, bàn giao trong 24–48h, không cần cấp quyền admin web và không nhận dữ liệu cá nhân khách hàng). Đầu ra gồm:
> 1. File CSV đã làm sạch định dạng (chuẩn hóa Handle, Option, khôi phục số 0 đầu mã SKU, định dạng giá).
> 2. Bảng `issue_log.csv` chỉ rõ từng dòng bị trùng/thiếu SKU hoặc lệch giá gốc/giá giảm để anh/chị chốt (tuyệt đối không tự ý đoán giá kinh doanh).
> 3. Báo cáo đối chiếu 100% số dòng trước và sau khi xử lý.
>
> Mình gửi kèm **bộ mẫu giả lập 120 dòng (Synthetic Sample)** để anh/chị xem trước cấu trúc bàn giao. Nếu phù hợp với file hiện tại của bên mình (`500.000đ / lô <= 200 dòng`), anh/chị nhắn mình nhé!
