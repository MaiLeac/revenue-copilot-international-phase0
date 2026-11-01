"""TikTok Knowledge Mining System — Batched Knowledge Extractor & Synthesizer.

Extracts structured claims per video batch, then synthesizes into:
1. KNOWLEDGE_BASE.md (Structured claim register with timestamps & URLs)
2. THINKING_FRAMEWORK.md (Comprehensive analytical worldview & mental models)
3. TRADING_RESEARCH.md (Quantitative hypotheses for MT5 Demo backtesting)
"""

from __future__ import annotations

import json
import logging
import os
import socket
import urllib.request
from pathlib import Path
from typing import Any

# Force IPv4 resolution to prevent IPv6 timeouts on Windows
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


BATCH_PROMPT_TEMPLATE = """Bạn là Chuyên gia Khai phá Tri thức Tài chính.
Dưới đây là một nhóm video transcript ({batch_count} video) từ một chuyên gia đầu tư/xác suất.

Hãy trích xuất TẤT CẢ các luận điểm quan trọng và định dạng thành JSON list các object có schema sau:
[
  {{
    "video_id": "id của video",
    "url": "link video",
    "topic": "Chủ đề (VD: Xác suất, Quản trị vốn, Tâm lý, Chu kỳ, Lựa chọn cổ phiếu)",
    "claim": "Luận điểm cốt lõi",
    "reasoning": "Lập luận và nguyên lý giải thích",
    "conditions": "Điều kiện áp dụng",
    "example": "Ví dụ cụ thể (nếu có)",
    "timestamp_marker": "Thời điểm trong video",
    "tier": "Kiến thức nền | Phương pháp cá nhân | Kinh nghiệm thực chiến | Quan điểm chưa kiểm chứng"
  }}
]

DỮ LIỆU TRANSCRIPT NHÓM NÀY:
{batch_content}

Chỉ trả về JSON thuần túy, không bọc markdown.
"""

SYNTHESIS_PROMPT_TEMPLATE = """Bạn là Giám đốc Nghiên cứu Định lượng (Chief Quant & Research Officer).
Dưới đây là TOÀN BỘ danh sách {total_claims} luận điểm đã được trích xuất từ kênh của tác giả:

{all_claims_json}

Nhiệm vụ của bạn là tổng hợp thành 3 tài sản nghiên cứu độc lập:

### PHẦN 1: BẢN ĐỒ TƯ DUY (THINKING FRAMEWORK)
1. Thế giới quan đầu tư của tác giả (Họ coi thị trường là gì? Xác suất được hiểu thế nào?).
2. 5-7 Nguyên lý cốt lõi bất biến được lặp lại nhiều nhất.
3. Ma trận ra quyết định và quy trình chọn lọc cơ hội.
4. Những mâu thuẫn hoặc sự thay đổi quan điểm theo thời gian.

### PHẦN 2: ĐÁNH GIÁ 4 TẦNG TRI THỨC (EPISTEMIC AUDIT)
- Tầng 1 (Kiến thức nền vững chắc): Những gì đã được khoa học/toán học kiểm chứng.
- Tầng 2 (Phương pháp riêng): Điểm mạnh và điểm yếu.
- Tầng 3 (Kinh nghiệm thực chiến): Bài học xương máu giá trị nhất.
- Tầng 4 (Quan điểm chưa kiểm chứng): Những cảnh báo về thiên kiến sống sót (survivorship bias) hoặc nhận định cảm tính.

### PHẦN 3: GIẢ THUYẾT ĐỊNH LƯỢNG CHO MT5 BOT (TRADING RESEARCH HYPOTHESES)
- 3 giả thuyết định lượng cụ thể có thể code và backtest được trên dữ liệu nến thật.
- Các quy tắc quản lý vốn hoặc lọc tín hiệu đáng thử nghiệm.
"""


def call_gemini(prompt: str, model_name: str = "gemini-flash-lite-latest") -> str:
    api_key = get_gemini_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["candidates"][0]["content"]["parts"][0]["text"]


def process_channel_corpus(data_dir: Path, batch_size: int = 5) -> dict[str, Any]:
    """Process all transcripts in batches and synthesize into target assets."""
    manifest_file = data_dir / "videos_manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_file}")

    manifest: list[dict[str, Any]] = json.loads(manifest_file.read_text(encoding="utf-8"))
    logger.info(f"Loaded manifest with {len(manifest)} videos. Beginning batched extraction...")

    all_extracted_claims: list[dict[str, Any]] = []

    # Process in batches of batch_size
    for i in range(0, len(manifest), batch_size):
        batch = manifest[i : i + batch_size]
        batch_text_blocks = []
        for v in batch:
            v_info = f"VIDEO ID: {v.get('id')} | URL: {v.get('url')} | Title: {v.get('title')}\n"
            sub_file = v.get("subtitle_file")
            transcript_text = ""
            if sub_file and Path(sub_file).exists():
                transcript_text = Path(sub_file).read_text(encoding="utf-8", errors="ignore")[:3000]
            else:
                transcript_text = f"[Caption / Description]: {v.get('description', '')}"
            batch_text_blocks.append(v_info + transcript_text)

        batch_prompt = BATCH_PROMPT_TEMPLATE.format(
            batch_count=len(batch),
            batch_content="\n\n---\n\n".join(batch_text_blocks),
        )
        try:
            logger.info(f"Extracting batch {i // batch_size + 1} ({len(batch)} videos)...")
            res_raw = call_gemini(batch_prompt)
            # Try to parse json
            clean_json = res_raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            claims = json.loads(clean_json)
            if isinstance(claims, list):
                all_extracted_claims.extend(claims)
        except Exception as err:
            logger.warning(f"Error extracting batch {i // batch_size + 1}: {err}")

    # Save structured claims
    claims_path = data_dir / "extracted_claims.json"
    claims_path.write_text(json.dumps(all_extracted_claims, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Extracted {len(all_extracted_claims)} structured claims. Synthesizing full dossier...")

    # Synthesis pass
    synth_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        total_claims=len(all_extracted_claims),
        all_claims_json=json.dumps(all_extracted_claims[:80], indent=1, ensure_ascii=False),
    )
    dossier_text = call_gemini(synth_prompt)

    dossier_file = data_dir / "RESEARCH_DOSSIER.md"
    dossier_file.write_text(dossier_text, encoding="utf-8")
    logger.info(f"Final dossier saved to {dossier_file}")
    return {"claims_count": len(all_extracted_claims), "dossier_path": str(dossier_file)}
