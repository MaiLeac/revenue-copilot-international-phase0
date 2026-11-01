# Agent Zero v2.13 — Money HQ Runtime, Scheduler & Telegram Setup

**Endpoint:** `http://localhost:5080`  
**Docker Image:** `agent0ai/agent-zero:v2.13`  
**Mounted Persistent State:** `C:\Users\ACER\agent-zero\agent-zero\usr` $\rightarrow$ `/a0/usr`  
**Mounted Repository Project:** `C:\Users\ACER\Documents\Codex\revenue-copilot-international-phase0` $\rightarrow$ `/a0/usr/projects/money-hq`

---

## 1. Activated Agent Profile & Skills

### Profile: `money-coo` (`/a0/usr/agents/money-coo/`)
- **`agent.yaml`**: Defines the **Money HQ COO (`money-coo`)** profile.
- **`prompts/agent.system.main.specifics.md`**: Enforces `OPERATING_SYSTEM.md`, `agents/AI_ROUTING_POLICY.md`, `agents/COST_OPTIMIZATION_POLICY.md`, and the `500,000 VND` experimental budget cap.

### Installed Skills (`/a0/usr/skills/`)
1. **`catalogue-qa-audit`**: Runs `assets/catalogue_qa_engine/catalogue_qa.py` and `assets/catalogue_qa_engine/report_generator.py` (`0 VND` marginal LLM cost).
2. **`qa-earnings-tracker`**: Runs `assets/qa_workflow_toolkit/bug_report_preflight.py` and `assets/qa_workflow_toolkit/qa_earnings_tracker.py`.
3. **`opportunity-scout`**: Enforces `L0–L4` evidence scoring and the `1 Primary + 1 Supporting` anti-fragmentation rule.
4. **`financial-reporting`**: Runs `tools/money_hq_dashboard.py` and monitors the `500,000 VND` budget cap and early-warning triggers.
5. **`repository-qa`**: Runs `python -m pytest -q` and checks secret/PII hygiene.

---

## 2. Scheduled Low-Cost Tasks (`/a0/usr/scheduler/tasks.json`)

Two recurring low-cost daily tasks are configured in `usr/scheduler/tasks.json` (timezone `Asia/Saigon`, `dedicated_context: true`, bounded to deterministic local scripts first):

1. **`Money HQ — Daily Operational & Opportunity Review`**
   - **Schedule:** `30 8 * * *` (`08:30` Asia/Saigon daily)
   - **Project:** `money-hq`
   - **Action:** Runs `python -m pytest -q`, checks `EXP-01` (`uTest` / `JOB-01`) and `EXP-02` (`SVC-01` Catalogue QA) against stop conditions, and updates `operations/DAILY_BRIEF.md` only if actionable changes exist.
2. **`Money HQ — Daily Financial & Blocker Report`**
   - **Schedule:** `30 20 * * *` (`20:30` Asia/Saigon daily)
   - **Project:** `money-hq`
   - **Action:** Runs `python tools/money_hq_dashboard.py`, verifies `L4` realized cash vs `L3` pending payouts and the `500,000 VND` budget cap, and escalates any blocker to `operations/OWNER_ACTIONS.md`.

---

## 3. Non-Blocking Telegram Alert Integration (`/a0/plugins/_telegram_integration`)

Agent Zero v2.13 includes the official `_telegram_integration` plugin (`webui/config.html`). It is pre-installed and ready to activate in **2 minutes** whenever the owner wants mobile push alerts:

1. Open `http://localhost:5080` $\rightarrow$ click **Connect Telegram** on the dashboard (or **Plugins** $\rightarrow$ **Telegram Integration**).
2. Paste a Telegram Bot Token from `@BotFather` (stored in `/a0/usr/plugins/_telegram_integration/config.yaml` locally — **never committed to Git**).
3. Set `allowed_users` to Mai's Telegram `@username` or numeric user ID, and set `default_project` to `money-hq`.
4. Use `/commands` or `/send` in Telegram to receive daily financial briefs and immediate red-flag blocker alerts on mobile.
