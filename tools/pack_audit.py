"""Audit Packager for External AI Reviewers (ChatGPT, Claude, Grok, DeepSeek).

Consolidates all critical trading agent code, configs, test outputs, and architecture
into a single structured Markdown file and a lightweight ZIP archive.
Allows the user to easily drag-and-drop or copy-paste the entire codebase into any AI.
"""

from __future__ import annotations

import os
import subprocess
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRADING_DIR = REPO_ROOT / "trading-agent-exness-demo"
OUTPUT_MD = REPO_ROOT / "AUDIT_PACK_TRADING_AGENT.md"
OUTPUT_ZIP = REPO_ROOT / "AUDIT_PACK_TRADING_AGENT.zip"

CORE_FILES = [
    "config/demo.yaml",
    "app/daemon.py",
    "app/mt5/execution.py",
    "app/risk/manager.py",
    "app/risk/kill_switch.py",
    "app/mt5/connection.py",
    "app/strategies/trend_pullback.py",
    "app/strategies/base.py",
    "app/data/quality_gate.py",
    "app/evaluation/performance.py",
    "tests/test_execution.py",
    "tests/test_risk.py",
    "tests/test_strategy_backtest.py",
    "research/STRATEGY_SPEC.md",
]


def generate_tree(dir_path: Path, prefix: str = "") -> str:
    lines = []
    items = sorted(
        [p for p in dir_path.iterdir() if not p.name.startswith(".") and p.name != "__pycache__"],
        key=lambda p: (p.is_file(), p.name.lower()),
    )
    for idx, item in enumerate(items):
        is_last = idx == len(items) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{item.name}")
        if item.is_dir():
            sub_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(generate_tree(item, sub_prefix))
    return "\n".join(lines)


def get_test_output() -> str:
    try:
        res = subprocess.run(
            ["python", "-m", "pytest", "-v", "tests/"],
            cwd=str(TRADING_DIR),
            capture_output=True,
            text=True,
            timeout=20,
        )
        return res.stdout.strip() or res.stderr.strip()
    except Exception as e:
        return f"Error running tests: {e}"


def main() -> None:
    print("Generating AUDIT_PACK_TRADING_AGENT.md...")
    tree_str = generate_tree(TRADING_DIR)
    test_str = get_test_output()

    md_parts = [
        "# MT5 AUTONOMOUS TRADING AGENT (EXNESS DEMO) — AUDIT DOSSIER",
        "\n> **Mục đích:** Tài liệu kỹ thuật tổng hợp toàn bộ mã nguồn, cấu hình và kiểm thử của hệ thống MT5 trading bot để gửi cho AI độc lập (ChatGPT / Claude / Grok) thực hiện adversarial audit phản biện đa chiều.",
        "\n## 1. THÔNG TIN HỆ THỐNG & NGUYÊN TẮC BẤT BIẾN (INVARIANTS)",
        "- **Môi trường hoạt động:** DEMO ONLY (`Exness-MT5Trial17`, Login `#464160066`, Balance `$100,000 USD`).",
        "- **Chặn Live Account:** Khóa cứng ở tầng Execution Adapter, kiểm tra `trade_mode == DEMO`, `trade_allowed`, `trade_expert`, chặn tên server chứa 'real/live'.",
        "- **Quản trị rủi ro cố định:** 0.25%/lệnh, SL cứng bắt buộc mọi lệnh, làm tròn lot XUỐNG (`math.floor`), từ chối lệnh nếu `min_vol` vượt ngân sách rủi ro.",
        "- **Cross-check MT5 Native:** Gọi `order_calc_profit()` đối soát với broker trước khi gửi lệnh.",
        "- **Tách quyền hạn:** Strategy chỉ sinh Signal(entry, sl, tp, reason), KHÔNG có quyền đặt lệnh hay tính volume.",
        "- **Bảo toàn trạng thái qua Restart:** KillSwitch và RiskManager ghi trạng thái ra file đĩa nguyên tử.",
        "\n## 2. CẤU TRÚC THƯ MỤC DỰ ÁN",
        "```text",
        f"trading-agent-exness-demo/\n{tree_str}",
        "```",
        "\n## 3. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (PYTEST TEST SUITE)",
        "```text",
        test_str,
        "```",
        "\n## 4. MÃ NGUỒN CÁC MODULE TRỌNG YẾU",
    ]

    # Zip packaging
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in CORE_FILES:
            fpath = TRADING_DIR / rel
            if fpath.exists():
                zf.write(fpath, arcname=f"trading-agent-exness-demo/{rel}")
                content = fpath.read_text(encoding="utf-8")
                github_raw_url = f"https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/{rel.replace('\\', '/')}"
                md_parts.extend([
                    f"\n### File: `{rel}`",
                    f"- **GitHub Raw:** [{rel}]({github_raw_url})",
                    "```python" if rel.endswith(".py") else ("```yaml" if rel.endswith(".yaml") else "```markdown"),
                    content,
                    "```",
                ])

    OUTPUT_MD.write_text("\n".join(md_parts), encoding="utf-8")
    print(f"Pack created successfully:\n- Markdown: {OUTPUT_MD} ({OUTPUT_MD.stat().st_size / 1024:.1f} KB)\n- ZIP: {OUTPUT_ZIP} ({OUTPUT_ZIP.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
