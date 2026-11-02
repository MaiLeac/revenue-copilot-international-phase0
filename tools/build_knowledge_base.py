"""Synthesis and knowledge base builder for Telegram channels.
Parses 1,857 posts from Vuong To Linh and Dong Chi Long, organizes into structured markdown dossiers.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0/data/scraped_telegram")
DOCS_DIR = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0/docs/knowledge_base")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

vuong_posts = json.loads((DATA_DIR / "khoahoctaichinh_Vuongtolinh.json").read_text(encoding="utf-8"))
long_posts = json.loads((DATA_DIR / "nhatlongtc.json").read_text(encoding="utf-8"))

print(f"Loaded {len(vuong_posts)} posts from Vuong To Linh and {len(long_posts)} posts from Dong Chi Long.")


# -------------------------------------------------------------
# 1. PROCESS DONG CHI LONG (NHAT LONG TAI CHINH)
# -------------------------------------------------------------
long_categories = {
    "1_Tien_Te_Va_Cung_Tien": {
        "title": "1. Bản chất Tiền Tệ, In Tiền & Phương Trình Cân Bằng Giá Cả",
        "keywords": ["phương trình", "in tiền", "tiền máy tính", "tiền giấy", "nhà cái", "ngân hàng trung ương", "nhtm", "tổng tiền", "cung tiền", "lạm phát", "lãi suất"],
        "posts": [],
    },
    "2_Bat_Dong_San": {
        "title": "2. Bản chất Bất Động Sản & Chu Kỳ Thổi Giá / Siết Nợ",
        "keywords": ["bđs", "bất động sản", "nhà đất", "vay", "cutloss", "ông chủ", "thổi giá", "bong bóng", "cầm cố"],
        "posts": [],
    },
    "3_Chung_Khoan_Va_Doi_Lai": {
        "title": "3. Bản chất Chứng Khoán, Đội Lái & Chiêu Trò Của Chủ Doanh Nghiệp",
        "keywords": ["cổ phiếu", "chứng khoán", "lái", "đội lái", "gom hàng", "đè giá", "giải chấp", "phát hành", "trái phiếu", "nhóm a", "nhóm b"],
        "posts": [],
    },
    "4_Crypto_Va_Tai_Chinh_Quoc_Te": {
        "title": "4. Góc nhìn Crypto, Vàng, Dầu & Rửa Tiền Quốc Tế",
        "keywords": ["crypto", "bitcoin", "btc", "vàng", "dầu", "binance", "cz", "rửa tiền", "hongkong", "singapore", "fed"],
        "posts": [],
    },
    "5_Tam_Ly_Va_Phan_Bo_Von": {
        "title": "5. Tâm Lý Đám Đông, Tư Duy Quản Trị Vốn & Triết Lý Đời",
        "keywords": ["tâm lý", "đám đông", "quản trị vốn", "thua lỗ", "tầm nhìn", "kiến thức", "reset não", "lòng tham", "sợ hãi"],
        "posts": [],
    },
}

for p in long_posts:
    txt = p.get("text", "").lower()
    matched = False
    for cat_key, cat_data in long_categories.items():
        if any(kw in txt for kw in cat_data["keywords"]):
            cat_data["posts"].append(p)
            matched = True
            break
    if not matched:
        long_categories["5_Tam_Ly_Va_Phan_Bo_Von"]["posts"].append(p)

# Build DONG_CHI_LONG_NHAT_LONG_TAI_CHINH.md
long_md = []
long_md.append("# 📚 TỔNG HỢP KIẾN THỨC TOÀN TẬP: ĐỒNG CHÍ LONG (NHẬT LONG TÀI CHÍNH)")
long_md.append("\n> **Nguồn dữ liệu:** Kênh Telegram `t.me/nhatlongtc` (Kiến Thức - ĐỒNG CHÍ LONG)")
long_md.append(f"> **Quy mô dữ liệu:** Đã trích xuất & làm sạch **{len(long_posts)} bài viết chuyên sâu** từ 2023 đến nay.")
long_md.append("> **Mục đích:** Đúc kết nguyên bản tư duy, công thức, bài học và luận điểm thực chiến phục vụ phân tích đa AI (ChatGPT, DeepSeek, Claude) và hệ thống hóa kiến thức đầu tư.\n")
long_md.append("---\n")

for cat_key, cat_data in long_categories.items():
    long_md.append(f"## {cat_data['title']}")
    long_md.append(f"*Tổng số bài viết cốt lõi thuộc chủ đề này: {len(cat_data['posts'])} bài.*\n")
    # Sort posts by length or significance, take top 15 most substantive
    top_posts = sorted(cat_data["posts"], key=lambda x: len(x.get("text", "")), reverse=True)[:15]
    for idx, p in enumerate(top_posts, 1):
        dt = p.get("datetime", "")[:10]
        link = p.get("link", "")
        text = p.get("text", "").strip()
        long_md.append(f"### Bài {idx} [{dt}] - {link}")
        long_md.append(f"```text\n{text}\n```\n")

(DOCS_DIR / "DONG_CHI_LONG_NHAT_LONG_TAI_CHINH.md").write_text("\n".join(long_md), encoding="utf-8")
print("Saved DONG_CHI_LONG_NHAT_LONG_TAI_CHINH.md")


# -------------------------------------------------------------
# 2. PROCESS VUONG TO LINH (KHOA HOC TAI CHINH)
# -------------------------------------------------------------
vuong_categories = {
    "1_Vi_Mo_Tin_Dung_Ty_Gia": {
        "title": "1. Khoa Học Vĩ Mô, Cung Tiền, Tỷ Giá & Bộ Ba Bất Khả Thi",
        "keywords": ["lãi suất", "cung tiền", "tỷ giá", "dxy", "sbv", "usd", "bộ ba bất khả thi", "đình lạm", "lạm phát", "nội địa hoá"],
        "posts": [],
    },
    "2_Ban_Chat_Von_Va_Du_An": {
        "title": "2. Bản Chất Dòng Vốn, Metro, Trái Phiếu Đô Thị & Đầu Tư Công",
        "keywords": ["trái phiếu", "đô thị", "metro", "vốn", "đầu tư công", "hút vốn", "chi tiêu", "phát hành"],
        "posts": [],
    },
    "3_Bat_Dong_San_Va_Luat_Dat_Dai": {
        "title": "3. Thị Trường Bất Động Sản, Nhà Ở Tương Lai & Thuế Đất Bỏ Hoang",
        "keywords": ["bđs", "bất động sản", "nhà ở hình thành trong tương lai", "góp vốn", "thuế", "đầu cơ đất"],
        "posts": [],
    },
    "4_Chung_Khoan_Va_Co_Phieu": {
        "title": "4. Thị Trường Chứng Khoán VN, Phân Hóa Cổ Phiếu & Dòng Tiền Ngoại (Tây Bán Ròng)",
        "keywords": ["chứng khoán", "cổ phiếu", "vn-index", "tây bán", "bẫy", "sóng thần", "sập"],
        "posts": [],
    },
    "5_Triet_Ly_Loi_Ich_Va_Con_Nguoi": {
        "title": "5. Quy Luật Lợi Ích Dẫn Lối, Bẫy Lợn Rừng & Tâm Lý Đám Đông",
        "keywords": ["lợi ích", "lợn rừng", "tham lam", "ngu ngốc", "con ruột", "con ghẻ", "loài người", "chu kỳ"],
        "posts": [],
    },
}

for p in vuong_posts:
    txt = p.get("text", "").lower()
    matched = False
    for cat_key, cat_data in vuong_categories.items():
        if any(kw in txt for kw in cat_data["keywords"]):
            cat_data["posts"].append(p)
            matched = True
            break
    if not matched:
        vuong_categories["5_Triet_Ly_Loi_Ich_Va_Con_Nguoi"]["posts"].append(p)

vuong_md = []
vuong_md.append("# 📚 TỔNG HỢP KIẾN THỨC TOÀN TẬP: KHOA HỌC TÀI CHÍNH (VƯƠNG TỐ LINH)")
vuong_md.append("\n> **Nguồn dữ liệu:** Kênh Telegram `t.me/khoahoctaichinh_Vuongtolinh` (Khoa Học Tài Chính - Vuongtolinh)")
vuong_md.append(f"> **Quy mô dữ liệu:** Đã trích xuất & làm sạch **{len(vuong_posts)} bài viết chuyên sâu**.")
vuong_md.append("> **Mục đích:** Hệ thống hóa toàn bộ các luận điểm về khoa học dòng vốn, vĩ mô tiền tệ, chu kỳ lợi ích và phân bổ tài sản.\n")
vuong_md.append("---\n")

for cat_key, cat_data in vuong_categories.items():
    vuong_md.append(f"## {cat_data['title']}")
    vuong_md.append(f"*Tổng số bài viết cốt lõi thuộc chủ đề này: {len(cat_data['posts'])} bài.*\n")
    top_posts = sorted(cat_data["posts"], key=lambda x: len(x.get("text", "")), reverse=True)[:15]
    for idx, p in enumerate(top_posts, 1):
        dt = p.get("datetime", "")[:10]
        link = p.get("link", "")
        text = p.get("text", "").strip()
        vuong_md.append(f"### Bài {idx} [{dt}] - {link}")
        vuong_md.append(f"```text\n{text}\n```\n")

(DOCS_DIR / "KHOA_HOC_TAI_CHINH_VUONG_TO_LINH.md").write_text("\n".join(vuong_md), encoding="utf-8")
print("Saved KHOA_HOC_TAI_CHINH_VUONG_TO_LINH.md")
