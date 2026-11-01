# Agent Zero (Local WSL2 Docker Setup by Codex)

Thư mục này lưu toàn bộ bộ script cài đặt, khởi chạy và cấu hình **Agent Zero** (`frdel/agent-zero`) mà Codex đã dựng trên máy:

- **URL chạy local**: `http://localhost:5080` (Container chạy qua WSL2 Docker proxy cổng `5080 -> 80`).
- **Thư mục dữ liệu gốc trên máy**: `C:\Users\ACER\agent-zero\agent-zero\usr` (chứa `.env`, `presets.yaml`, `scheduler/tasks.json`).
- **Thư mục mã nguồn Codex clone**: `C:\Users\ACER\Documents\Codex\2026-09-30\stop-rebuilding-the-agent-from-scratch-2\agent-zero`.
- **Các script vận hành chính**:
  - `Agent Zero.cmd` / `start-agent-zero.ps1`: Khởi động WSL2 Docker daemon và bật container Agent Zero ở cổng `5080`.
  - `agent-zero-install.ps1`: Script cài đặt image và mount volume.
  - `agent_zero_smoke.py`: Script kiểm tra kết nối UI và health check của Agent Zero.
  - `allow-ollama-wsl.ps1` & `ollama-install.ps1`: Kết nối Ollama local vào WSL cho Agent Zero.
