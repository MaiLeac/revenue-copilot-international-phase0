# EXP-02 (Supporting Asset-Building Experiment) — E-Commerce SKU / Catalogue QA Pilot (`SVC-01`)

**Lane:** Service-to-Asset  
**Status:** Active (Supporting #1 — Synthetic Sample & Engine Ready)  
**Evidence Level:** `L1` buyer pain (`E01`–`E05` independent merchant/buyer requests) + `L2` software alternative (`E06` Matrixify $20/30 days). `L3/L4 = 0` (no paid client yet).

---

## 1. Revenue Discipline Parameters

| Dimension | Specification |
|---|---|
| **Specific Buyer** | Small-to-mid Shopify/WooCommerce merchants and e-commerce agencies dealing with messy supplier spreadsheets or failing CSV product imports. |
| **Specific Pain** | Variant import failures (`E04`), accidental field overwrites during price updates (`E03`), stripped leading zeros on SKUs (`004101 -> 4101`), duplicate SKUs, and inconsistent option names (`E01`, `E02`). |
| **Concrete Offer** | **Fixed-Scope Catalogue Audit & Cleanup Pilot:** Up to `200 variant rows` (1 CSV/XLSX source, <=10 columns), delivering: (1) cleaned import-ready CSV, (2) row-by-row `issue_log.csv` flagging missing/duplicate SKUs and price anomalies without guessing business data, and (3) `AUDIT_SUMMARY_REPORT.md` with before/after reconciliation counts + 1 revision round within 48 hours. **Price Hypothesis:** `100 USD` (international, 50% deposit / 50% on delivery) or `500,000 VND` (domestic). |
| **Distribution Channel** | Opt-in replies to **at most 10 active public buyer requests** (<=5 merchants posting live CSV/catalogue errors, <=5 agencies requesting overflow data QA) in communities/marketplaces where service replies are explicitly permitted. Zero cold scraping or mass DMing. |
| **Measurable Conversion Event** | **Interim (`L2`):** >=3 qualified buyer replies confirming scope & budget. **Validation (`L3`):** Signed pilot scope + 50% deposit commitment. **Success (`L4`):** Usable cash net of fees received in bank before Day 30. |
| **Cost & Owner-Time Budget** | **Cash spend:** `0 VND` upfront. **Owner time cap:** `<= 5 hours` for finding/replying to <=10 qualified requests; `<= 2 hours` per pilot delivery using `CatalogueQAEngine`. |
| **Stop Condition** | Stop outreach after 10 compliant replies if `< 3` qualified conversations or `0` paid pilots result. Reject any prospect requiring production store admin credentials, raw customer PII, or uncompensated full-file free trials. |

---

## 2. Built & Verified Assets in This Experiment

- **Automated QA Engine:** [`assets/catalogue_qa_engine/catalogue_qa.py`](../../assets/catalogue_qa_engine/catalogue_qa.py)
- **Synthetic 120-Row Case Study Portfolio:** [`sample_portfolio/`](./sample_portfolio/)
  - Input with 7 realistic defect types: [`synthetic_dirty_catalogue_120rows.csv`](./sample_portfolio/synthetic_dirty_catalogue_120rows.csv)
  - Cleaned output: [`synthetic_cleaned_catalogue_120rows.csv`](./sample_portfolio/synthetic_cleaned_catalogue_120rows.csv)
  - Detailed issue log: [`synthetic_issue_log.csv`](./sample_portfolio/synthetic_issue_log.csv)
  - Reconciliation report: [`SYNTHETIC_CASE_STUDY_REPORT.md`](./sample_portfolio/SYNTHETIC_CASE_STUDY_REPORT.md)
- **Offer & Opt-In Outreach Kit:** [`OFFER_AND_OUTREACH_KIT.md`](./OFFER_AND_OUTREACH_KIT.md)
