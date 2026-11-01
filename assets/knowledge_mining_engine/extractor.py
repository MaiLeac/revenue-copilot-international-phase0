"""TikTok Knowledge Mining System — Knowledge Extractor & Synthesizer.

Uses Gemini API (Free Tier) to reconstruct the author's Thinking Framework & Knowledge Base.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import urllib.request
from pathlib import Path
from typing import Any

# Force IPv4 resolution
_orig_getaddrinfo = socket.getaddrinfo


def _getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _getaddrinfo_ipv4_only

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tiktok_extractor")


def get_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key and (key.startswith("AQ.") or key.startswith("AIza")):
        return key
    env_file = Path.home() / "agent-zero" / "agent-zero" / "usr" / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise ValueError("GEMINI_API_KEY is required to run knowledge extraction.")


EXTRACTION_PROMPT = """Bạn là Chuyên gia Nghiên cứu Tri thức & Định lượng Tài chính Cấp cao (Senior Knowledge Mining & Quant Researcher).
Dưới đây là tập hợp toàn bộ lời nói/transcript của một tác giả trên TikTok chuyên về đầu tư chứng khoán, kinh tế và xác suất.

NHIỆM VỤ:
Tái dựng hoàn chỉnh HỆ THỐNG TƯ DUY (Thinking Framework) của tác giả, thay vì tóm tắt từng video rời rạc.

YÊU CẦU PHÂN LOẠI TRI THỨC VÀO 4 TẦNG:
1. Kiến thức nền: Những nguyên lý toán học, tài chính, kinh tế học, xác suất có thể kiểm chứng độc lập.
2. Phương pháp cá nhân: Cách tác giả phân tích thị trường, lựa chọn cổ phiếu, quản trị vốn và ra quyết định.
3. Kinh nghiệm thực chiến: Những bài học từ các giao dịch, sai lầm, chu kỳ thị trường mà tác giả từng trải qua.
4. Quan điểm chưa kiểm chứng: Những nhận định chủ quan, dự đoán tương lai hoặc giai thoại chưa có số liệu chứng minh.

HÃY XUẤT RA BÁO CÁO GỒM 3 PHẦN CHÍNH:

### PHẦN 1: BẢN ĐỒ TƯ DUY (THINKING FRAMEWORK)
- Thế giới quan đầu tư của tác giả: Họ coi thị trường là gì (sòng bạc, cỗ máy bỏ phiếu, hay hệ thống xác suất)?
- Các nguyên lý cốt lõi được lặp đi lặp lại nhiều nhất.
- Cách tác giả định nghĩa và ứng dụng xác suất (Expected Value, Risk-Reward, kích thước vị thế).
- Sự tiến hóa hoặc mâu thuẫn quan điểm theo thời gian (nếu có).

### PHẦN 2: CƠ SỞ DỮ LIỆU LUẬN ĐIỂM (STRUCTURED KNOWLEDGE BASE)
Bảng tổng hợp chi tiết các luận điểm quan trọng nhất:
| Chủ đề | Luận điểm cốt lõi | Lập luận & Luận cứ | Điều kiện áp dụng | Ví dụ thực tế | Phân tầng kiểm chứng |

### PHẦN 3: GIẢ THUYẾT ĐỊNH LƯỢNG CHO BOT TRADING (TRADING RESEARCH)
- Những nguyên tắc/quy luật nào của tác giả có thể biến thành thuật toán hoặc kiểm chứng trên dữ liệu quá khứ?
- Cảnh báo bẫy tâm lý và những điểm tác giả có thể sai lầm hoặc bị thiên kiến sống sót (Survivorship bias).

---
NỘI DUNG TRANSCRIPT THU THẬP ĐƯỢC:
{corpus_text}
"""


def extract_and_synthesize(corpus_text: str, model_name: str = "gemini-flash-lite-latest") -> str:
    api_key = get_gemini_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": EXTRACTION_PROMPT.format(corpus_text=corpus_text)}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    logger.info(f"Sending corpus ({len(corpus_text)} chars) to Gemini {model_name}...")
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        result_text = res["candidates"][0]["content"]["parts"][0]["text"]
        logger.info("Knowledge synthesis completed successfully!")
        return result_text
