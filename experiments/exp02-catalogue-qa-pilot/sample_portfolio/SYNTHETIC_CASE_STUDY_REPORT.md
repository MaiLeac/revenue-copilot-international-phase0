# Catalogue QA & Reconciliation Report — `synthetic_dirty_catalogue_120rows.csv`

**Import Gate Status:** `REQUIRES CLIENT DECISION ON CRITICAL ROWS BEFORE IMPORT`

## 1. Before / After Reconciliation Metrics

| Metric | Count | Notes |
|---|---:|---|
| Total Input Variant Rows | 120 | Scoped batch cap: <=200 rows |
| Total Output Variant Rows | 120 | 100% row reconciliation preserved |
| Unique Product Handles | 20 | Normalized slug format |
| Unique Validated SKUs | 118 | Post leading-zero restoration |
| Auto-Fixed Formatting Issues | 117 | Deterministic rule fixes applied |
| Warnings (Review Recommended) | 2 | Compare-at-price or PII flags |
| Critical Unresolved Issues | 4 | Missing/duplicate SKUs or invalid prices (never guessed) |
| PII Leakage Flags | 1 | Emails/phones redacted in Body HTML |

## 2. Breakdown by Issue Code

| Issue Code | Occurrences |
|---|---:|
| `COMPARE_AT_LOWER_THAN_PRICE` | 1 |
| `DUPLICATE_SKU` | 1 |
| `HANDLE_NORMALIZED` | 2 |
| `INVALID_OR_NON_POSITIVE_PRICE` | 1 |
| `MISSING_OPTION_VALUE` | 1 |
| `MISSING_SKU` | 1 |
| `OPTION_NAME_NORMALIZED` | 2 |
| `PII_DETECTED_IN_DESCRIPTION` | 1 |
| `PRICE_NUMBER_FORMATTED` | 3 |
| `SKU_LEADING_ZERO_RESTORED` | 8 |
| `STATUS_CASED_LOWER` | 2 |
| `WHITESPACE_CLEANED` | 100 |

## 3. Critical Unresolved Rows (Requires Client Confirmation)

> Per operating policy, the QA engine **never guesses business prices, missing SKUs, or missing variant options**.

| Row | Handle | SKU | Field | Issue Code | Detail |
|---:|---|---|---|---|---|
| 13 | `bamboo-lounge-set` | `004111` | `Variant SKU` | `DUPLICATE_SKU` | Duplicate Variant SKU '004111' (first seen on row 12). |
| 28 | `canvas-weekender-tote` | `` | `Variant SKU` | `MISSING_SKU` | Variant SKU is empty; never invent missing SKUs without client mapping. |
| 34 | `organic-cotton-tee` | `004133` | `Option1 Value` | `MISSING_OPTION_VALUE` | Option1 Value is empty; Shopify/WooCommerce imports fail when variant option is blank. |
| 49 | `minimalist-card-holder` | `004148` | `Variant Price` | `INVALID_OR_NON_POSITIVE_PRICE` | Variant Price is missing, non-numeric, or <= 0. Business prices are never guessed. |
