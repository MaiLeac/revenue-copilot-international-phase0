# AI Workforce & Routing Policy — Money HQ

**Owner / Capital Allocator / Final Approver:** Mai (`MaiLeac`)  
**Last Verified:** 2026-11-01  
**Primary Metric:** Verified Net Cash Received (`L4`) and Level 3 Asset Autonomy per unit of Owner Time and Incremental Operating Cost.

---

## 1. Actual AI Workforce & Verified Execution Capabilities

Do not invent multi-agent orchestration or assume every model has local machine access. Each AI system has a distinct operational boundary based on its actual environment access:

| System | Role | Local Machine / Repo Execution Access? | Actual Responsibilities & Boundaries |
| :--- | :--- | :--- | :--- |
| **Antigravity** | **Primary Local Operator (With Hands)** | **YES (Direct Local Access)** | • Inspects and modifies the local repository (`C:\Users\ACER\Documents\Codex\revenue-copilot-international-phase0`) and environment within granted permissions<br>• Runs local Python tools, `pytest`, Docker/WSL commands, browser verification, and GitHub CLI (`gh`) commits<br>• Executes end-to-end implementation and verification tasks assigned by the owner |
| **ChatGPT** | **Strategic Advisor, Prompt Architect & Independent Auditor** | **NO (Advisory / Browser Context Only)** | • High-level strategy, Level 3 autonomous asset design, and prompt architecture<br>• Independent economic auditing and challenging assumptions<br>• Does **not** directly edit local files or run local commands |
| **OpenAI Codex** | **Coding & Implementation Agent (When Assigned)** | **When Invoked Locally / via CLI** | • Scoped repository code changes, deterministic scripts, unit tests, and technical debugging when explicitly assigned<br>• Also provides OAuth model backend (`gpt-5.4` / `gpt-5.4-mini`) for Agent Zero |
| **Claude Code** | **Independent Reviewer & Specialist Coding Agent (When Assigned)** | **When Invoked Locally / via Review** | • Independent architectural, security, privacy, and failure-mode audits<br>• Challenging fragile economic or technical claims<br>• Executing bounded implementation or review tasks when assigned |
| **Gemini & DeepSeek** | **Independent Advisory Models** | **NO (Advisory Only)** | • Second-opinion ideation, translation, or research cross-checks when queried by the owner<br>• Never assumed to have repository or local execution access |
| **Agent Zero (`v2.13`)** | **Persistent Local Operations Runtime (`money-coo`)** | **YES (Inside Docker Container `agent-zero` at `http://localhost:5080`)** | • **Verified active:** Docker container running on port `5080`, repo bind-mounted at `/a0/usr/projects/money-hq`, `money-coo` profile and 6 local skills installed<br>• **Configured but unverified in live cron execution:** 2 daily scheduled tasks (`08:30` and `20:30` Asia/Saigon in `/a0/usr/scheduler/tasks.json`, currently `last_run: null`)<br>• **Not connected:** Telegram/Email/WhatsApp notification channels are **not** linked |

---

## 2. Non-Negotiable Routing & Cost Discipline Rules

1. **One Task, One Accountable Operator:** Every implementation task is executed by one primary local operator (Antigravity or Codex when assigned). Never send identical implementation tasks to multiple paid models simultaneously.
2. **Deterministic Python First (`0 VND` Marginal Cost):** Whenever a task can be performed by an existing local script (`catalogue_qa.py`, `report_generator.py`, `constitution_engine.py`, `handbook_generator.py`, `qa_earnings_tracker.py`, `money_hq_dashboard.py`, `pytest`), run the deterministic script instead of invoking an LLM.
3. **Separate Advisory from Execution:** ChatGPT, Claude, Gemini, and DeepSeek provide strategy, prompts, and audits; Antigravity (or Codex when invoked) verifies facts against the actual filesystem before making changes.
4. **Evidence Before Claims:** No agent may claim a feature works, a test passes, or a scheduled job ran without inspecting the actual output (`pytest`, `git status`, `tasks.json`, or `CASH_LEDGER.csv`).
5. **Proportional Independent Review:** Use Claude Code or ChatGPT to audit changes that affect:
   - Strategic direction or portfolio ranking (`README.md`, `OPERATING_SYSTEM.md`, `portfolio/OPPORTUNITY_REGISTER.md`),
   - Financial ledgers (`finance/*.csv`),
   - Security, privacy, or public repository exposure,
   - Any proposal requiring incremental cash spend (`> 0 VND`).
6. **Loop Prevention:** Agent Zero scheduled tasks must use `dedicated_context: true`, run deterministic scripts first, and never spawn recursive sub-tasks.

---

## 3. Practical Task Routing Flow

```text
Incoming Need
 ├── Can an existing deterministic Python script or test suite run it?
 │     └── YES -> Execute local Python script / pytest (0 VND marginal cost)
 └── NO -> Requires AI work:
       ├── Needs strategic direction, prompt architecture, or economic critique?
       │     └── ChatGPT (Strategic Advisor & Auditor)
       ├── Needs local repo inspection, code/doc implementation, testing, or deployment?
       │     └── Antigravity (Primary Local Operator) or Codex (when assigned)
       ├── Needs independent security, privacy, or architecture audit?
       │     └── Claude Code (Independent Reviewer)
       └── Needs recurring local status check inside Docker container?
             └── Agent Zero (`money-coo` at localhost:5080, once scheduler runs are verified)
```

---

## 4. Mandatory 8-Step Frontend Development & Anti-AI-Slop Protocol

Whenever any agent (Antigravity, Codex, Claude Code, or Agent Zero) builds or modifies any web page, component, or user interface, it **MUST** follow this non-negotiable 8-step protocol before delivering:

1. **Search the Capability Library First:** Query [`assets/web_capability_library/catalog.json`](../assets/web_capability_library/catalog.json) via `search_capabilities()` or inspection before implementing any UI pattern. Reuse approved dependencies (`lucide-react`, `motion`, `tokens.css`) rather than generating generic substitutes.
2. **Inspect Reference Implementations:** Check existing high-performing implementations in the owner's portfolio (e.g., `Sisan/src/components/RoomCard.tsx` for touch carousel & OSRM routing; `Nutlope/hallmark` for material themes; `eternity4719/HowToLiveBetter` for evidence cards).
3. **Compare Against Real Products:** Compare the intended design against genuine market-leading products in the same category (e.g., Airbnb/Booking for rental search; Gumroad/Substack for digital products; Shopify for B2B tools).
4. **Choose a Coherent Visual Direction Before Coding:** Select one material theme (`tokens.css` Swiss Ledger, Apothecary Paper, or Hospitality Warm) and declare exact CSS custom properties at `:root`. Never write literal colors or ad-hoc font families.
5. **Enforce the Hallmark Floor Gates (Non-Waivable):**
   - No `transition: all` or `transition-all` (specify exact animating properties).
   - No `100vw` (use `overflow-x: clip` on `html` and `body`).
   - Every interactive element has instant `:focus-visible`.
   - Reduced motion fallback: `@media (prefers-reduced-motion: reduce)`.
   - Grid tracks use `minmax(0, 1fr)`; display headings use `overflow-wrap: break-word; min-width: 0`.
6. **Actively Remove Obvious AI-Generated Design Clichés:**
   - **NO** purple-to-blue neon gradients.
   - **NO** tracked-capital/uppercase eyebrows or small caps above headings.
   - **NO** emojis inside buttons, headings, or badge tags (use SVG icons from `lucide-react`).
   - **NO** arrows glued to CTA link text (e.g., `Buy →`).
   - **NO** cards inside cards or decorative pulsing status dots.
7. **Verify Flow-Scout UX Patterns:** Ensure zero dead placeholder links (`<a href="#">`), zero unrecoverable empty states, and accurate tabular prices (`font-variant-numeric: tabular-nums`).
8. **Run Browser-Based Visual Inspection Before Declaring Done:** Execute `python tools/web_quality_gate.py <file> --browser-render` using headless Chromium. Never claim a UI is complete unless it scores 100/100 with zero Floor violations and zero horizontal overflow.
