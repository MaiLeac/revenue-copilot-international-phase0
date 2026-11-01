"""Generates a 120-row synthetic e-commerce catalogue and runs the CatalogueQAEngine on it.

NOTE: 100% synthetic data created for portfolio demonstration (SVC-01 / EXP-02).
Contains zero real merchant or customer data.
"""

from __future__ import annotations

import csv
from pathlib import Path

from assets.catalogue_qa_engine.catalogue_qa import CatalogueQAEngine

FIELDNAMES = [
    "Handle",
    "Title",
    "Body (HTML)",
    "Vendor",
    "Product Category",
    "Type",
    "Tags",
    "Published",
    "Option1 Name",
    "Option1 Value",
    "Variant SKU",
    "Variant Grams",
    "Variant Inventory Tracker",
    "Variant Inventory Qty",
    "Variant Inventory Policy",
    "Variant Fulfillment Service",
    "Variant Price",
    "Variant Compare At Price",
    "Status",
]


def build_synthetic_dirty_rows() -> list[dict[str, str]]:
    products = [
        ("linen-resort-shirt", "Linen Resort Shirt", "Apparel", "Shirts", "29.00", "39.00"),
        ("bamboo-lounge-set", "Bamboo Lounge Set", "Apparel", "Loungewear", "45.00", "59.00"),
        ("ceramic-pour-over-mug", "Ceramic Pour Over Mug", "Home & Kitchen", "Drinkware", "18.50", "24.00"),
        ("merino-travel-hoodie", "Merino Travel Hoodie", "Apparel", "Outerwear", "78.00", "95.00"),
        ("canvas-weekender-tote", "Canvas Weekender Tote", "Accessories", "Bags", "54.00", "68.00"),
        ("organic-cotton-tee", "Organic Cotton Tee", "Apparel", "Shirts", "22.00", "28.00"),
        ("pleated-wide-leg-pant", "Pleated Wide Leg Pant", "Apparel", "Pants", "62.00", "79.00"),
        ("minimalist-card-holder", "Minimalist Card Holder", "Accessories", "Wallets", "26.00", "34.00"),
        ("ribbed-knit-cardigan", "Ribbed Knit Cardigan", "Apparel", "Knitwear", "68.00", "85.00"),
        ("stainless-thermal-flask", "Stainless Thermal Flask", "Home & Kitchen", "Drinkware", "31.00", "40.00"),
        ("woven-market-basket", "Woven Market Basket", "Home & Kitchen", "Storage", "36.00", "45.00"),
        ("silk-sleep-eye-mask", "Silk Sleep Eye Mask", "Accessories", "Sleep", "19.00", "25.00"),
        ("tailored-linen-shorts", "Tailored Linen Shorts", "Apparel", "Shorts", "42.00", "52.00"),
        ("stoneware-salad-bowl", "Stoneware Salad Bowl", "Home & Kitchen", "Tableware", "48.00", "60.00"),
        ("recycled-nylon-backpack", "Recycled Nylon Backpack", "Accessories", "Bags", "84.00", "110.00"),
        ("waffle-weave-bath-towel", "Waffle Weave Bath Towel", "Home & Kitchen", "Bath", "27.00", "35.00"),
        ("brushed-fleece-jogger", "Brushed Fleece Jogger", "Apparel", "Pants", "52.00", "65.00"),
        ("brass-desk-organizer", "Brass Desk Organizer", "Home & Kitchen", "Office", "34.00", "44.00"),
        ("suede-loafer-mule", "Suede Loafer Mule", "Footwear", "Shoes", "92.00", "120.00"),
        ("cashmere-rib-beanie", "Cashmere Rib Beanie", "Accessories", "Hats", "44.00", "58.00"),
    ]
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]

    rows: list[dict[str, str]] = []
    sku_counter = 4100

    for p_idx, (handle, title, cat, ptype, price, compare) in enumerate(products):
        for s_idx, size in enumerate(sizes):
            sku_counter += 1
            row_idx = len(rows) + 1  # 1..120
            sku_str = f"{sku_counter:06d}"  # e.g. 004101

            row_handle = handle
            row_title = title if s_idx == 0 else f"  {title}  "
            row_opt_name = "Size"
            row_opt_val = size
            row_price = price
            row_compare = compare
            row_status = "active"
            row_body = f"<p>Synthetic portfolio item: {title} ({size}).</p>"

            # Inject realistic merchant catalogue defects (E01-E04 patterns):
            if row_idx in {1, 7, 13, 19, 25, 31, 37, 43}:
                # Leading zeros stripped by spreadsheet export (e.g. "4101" instead of "004101")
                sku_str = str(sku_counter)
            if row_idx in {5, 18}:
                # Unnormalized handle with spaces and uppercase
                row_handle = f"  {handle.upper().replace('-', ' ')} "
            if row_idx in {10, 22, 35}:
                # Currency symbol & spaces in price
                row_price = f" ${price} "
            if row_idx in {14, 28}:
                # Lowercase/messy option name
                row_opt_name = "  size "
            if row_idx in {20, 40}:
                # Uppercase status
                row_status = "ACTIVE"
            if row_idx == 12:
                # Duplicate SKU collision with row 11
                sku_str = f"{sku_counter - 1:06d}"
            if row_idx == 27:
                # Missing SKU
                sku_str = ""
            if row_idx == 33:
                # Missing Option1 Value (causes Shopify CSV import line failure E04)
                row_opt_val = ""
            if row_idx == 48:
                # Invalid negative/zero price
                row_price = "0.00"
            if row_idx == 55:
                # Compare-at price accidentally lower than selling price
                row_compare = "15.00"
            if row_idx == 64:
                # Accidental supplier contact PII left in product description
                row_body = "<p>Supplier contact: warehouse-ops@example-supplier.com or +1-415-555-0199 before reorder.</p>"

            rows.append(
                {
                    "Handle": row_handle,
                    "Title": row_title,
                    "Body (HTML)": row_body,
                    "Vendor": "Avenue Synthetic Lab",
                    "Product Category": cat,
                    "Type": ptype,
                    "Tags": "synthetic-sample, Resort-2026",
                    "Published": "TRUE",
                    "Option1 Name": row_opt_name,
                    "Option1 Value": row_opt_val,
                    "Variant SKU": sku_str,
                    "Variant Grams": "350",
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": "25",
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Price": row_price,
                    "Variant Compare At Price": row_compare,
                    "Status": row_status,
                }
            )
    return rows


def generate_portfolio_sample(output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    dirty_csv = out / "synthetic_dirty_catalogue_120rows.csv"
    cleaned_csv = out / "synthetic_cleaned_catalogue_120rows.csv"
    issues_csv = out / "synthetic_issue_log.csv"
    report_md = out / "SYNTHETIC_CASE_STUDY_REPORT.md"

    dirty_rows = build_synthetic_dirty_rows()
    with dirty_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(dirty_rows)

    engine = CatalogueQAEngine(expected_sku_digits=6, max_rows=200)
    engine.process_files(
        input_csv=dirty_csv,
        output_cleaned_csv=cleaned_csv,
        output_issue_log_csv=issues_csv,
        output_report_md=report_md,
    )


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    sample_dir = repo_root / "experiments" / "exp02-catalogue-qa-pilot" / "sample_portfolio"
    generate_portfolio_sample(sample_dir)
