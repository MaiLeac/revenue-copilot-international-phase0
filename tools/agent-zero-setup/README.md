# Agent Zero (Local WSL2 Docker Setup by Codex)

> **Current check:** Port `5080` was not listening at 08:55 ICT on 2026-11-05. Setup files below show how it was configured, not that the container or scheduler is running now. See [`PROJECT_STATE.md`](../../PROJECT_STATE.md).

## Capability catalog sync — 2026-11-05

All agents should read root `AGENTS.md` and use `python tools/capability_lookup.py "task words"` for relevant repository candidates. Agent Zero's local `money-coo` prompt was updated with this route using `tools/agent-zero-setup/sync_capability_profile.ps1`; the script stores a local backup beside the prompt. This is a prompt/configuration update, not proof that a listed repository was installed or that Agent Zero completed a task. Docker was unavailable during the update, so in-container behavior was not verified. EXP-03 is digital-only and the book is still being written.

Thư mục này lưu toàn bộ bộ script cài đặt, khởi chạy và cấu hình **Agent Zero** (`frdel/agent-zero`) mà Codex đã dựng trên máy:

- **URL chạy local**: `http://localhost:5080` (Container chạy qua WSL2 Docker proxy cổng `5080 -> 80`).
- **Thư mục dữ liệu gốc trên máy**: `<LOCAL_USER_HOME>\agent-zero\agent-zero\usr` (chứa `.env`, `presets.yaml`, `scheduler/tasks.json`).
- **Thư mục mã nguồn Codex clone**: `<LOCAL_USER_HOME>\Documents\Codex\2026-09-30\stop-rebuilding-the-agent-from-scratch-2\agent-zero`.
- **Các script vận hành chính**:
  - `Agent Zero.cmd` / `start-agent-zero.ps1`: Khởi động WSL2 Docker daemon và bật container Agent Zero ở cổng `5080`.
  - `agent-zero-install.ps1`: Script cài đặt image và mount volume.
  - `agent_zero_smoke.py`: Script kiểm tra kết nối UI và health check của Agent Zero.
  - `allow-ollama-wsl.ps1` & `ollama-install.ps1`: Kết nối Ollama local vào WSL cho Agent Zero.
