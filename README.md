# MaiLeac Money HQ — Autonomous Asset Portfolio & Revenue Operations

> **MANDATORY RULE FOR ALL AI AGENTS:**  
> Before proposing plans, editing code, or making claims, you **must** inspect the actual files, git status, test outputs (`python -m pytest`), and financial ledgers ([`finance/CASH_LEDGER.csv`](./finance/CASH_LEDGER.csv), [`finance/COST_LEDGER.csv`](./finance/COST_LEDGER.csv)) in this repository. Never describe a planned or unverified feature as operational. Never claim tests pass unless you have just executed them.

---

## 1. Quick Orientation: 10 Questions Every Agent Must Understand Immediately

1. **What is Money HQ?**  
   Money HQ is the single monorepo and operating system for building, testing, measuring, and operating legitimate revenue-generating digital assets and cash-flow experiments for **Mai (`MaiLeac`)**.
2. **What is its ultimate objective?**  
   To build a **Level 3 Autonomous Asset Portfolio** — a collection of validated digital assets and automated revenue systems that generate repeatable or recurring net cash flow with near-zero marginal cost and minimal ongoing human labor. Money HQ is **not** a conventional small business, freelance agency, or AI-assisted manual labor platform.
3. **What does Level 3 autonomy mean?**  
   We distinguish three levels of autonomy:
   - **Level 1 — AI-Assisted Labor:** The owner still performs manual work (e.g., testing cycles, hourly transcription, manual client servicing) using AI tools to work faster.
   - **Level 2 — Automated Business:** AI handles most day-to-day execution, while the owner manages exceptions, approvals, and occasional operational bottlenecks.
   - **Level 3 — Autonomous Asset Portfolio (Strategic Destination):** AI agents research demand, create and maintain digital assets, and run automated acquisition, payment, and fulfillment pipelines. Multiple validated assets operate as a portfolio while the owner acts strictly as **capital allocator, risk controller, and exception handler**. *(Lower levels are acceptable only as temporary cash-flow bridges or validation stepping stones.)*
4. **What is the current primary priority?**  
   Validating automated acquisition, payment, and fulfillment for **Tier 1–2 Digital Assets** ([`experiments/exp03-duong-nhan-ai-mvp/`](./experiments/exp03-duong-nhan-ai-mvp) and [`experiments/exp02-catalogue-qa-pilot/`](./experiments/exp02-catalogue-qa-pilot)) while collecting the already-approved `L3` crowdtesting payout ([`experiments/exp01-qa-cashflow/`](./experiments/exp01-qa-cashflow)).
5. **What is currently generating real money (`L4`), if anything?**  
   - **Realized Usable Cash (`L4` in [`finance/CASH_LEDGER.csv`](./finance/CASH_LEDGER.csv)):** **`0 VND`** (no cash has settled into a bank/Payoneer/PayPal account yet).
   - **Approved Pending Payouts (`L3`):** **`0 VND`** (`platform.utest.com/account/payments` currently shows `VND 0.00 Pending Payout` despite `3/3` approved bugs on Cycle 562706).
   - **Digital Asset Sales (`EXP-03` & `EXP-02`):** **`0 VND` (`L2` commercial storefronts deployed; `0` paid customer orders to date).**
6. **Which projects are revenue experiments, capital engines, or infrastructure?**  
   - **Pillar 1 (Digital Wellness):** `EXP-03` ([`experiments/exp03-duong-nhan-ai-mvp/`](./experiments/exp03-duong-nhan-ai-mvp)) — Dưỡng Nhan 7-Constitution Web App & Handbook (69k retail cashflow).
   - **Pillar 2 (Micro-SaaS & Data Utility):** `EXP-02` ([`experiments/exp02-catalogue-qa-pilot/`](./experiments/exp02-catalogue-qa-pilot)) — Catalogue QA Engine & Self-Serve CSV Web Tool (199k / $9 B2B utility).
   - **Pillar 3 (Media & Content Infrastructure):** [`awesome-ai-video-code`](https://github.com/MaiLeac/awesome-ai-video-code) — Directory of 8 code-driven video generation skills for audience & traffic.
   - **Pillar 4 (Treasury & Quantitative Compounding):** `TRD-01` ([`trading-agent-exness-demo/`](./trading-agent-exness-demo)) — Milestone M2 Exness MT5 Quantitative Trading Agent connected to verified Demo account `#464160066` ($100k capital), running statistical trend + ATR stops with zero LLM order execution.
   - **Operating Infrastructure:** [`assets/superagent_control_plane/`](./assets/superagent_control_plane), [`tools/superagent_runner.py`](./tools/superagent_runner.py), [`operations/ATTENTION_PANEL.md`](./operations/ATTENTION_PANEL.md), and [`tools/agent-zero-setup/`](./tools/agent-zero-setup).
7. **What can each AI agent actually do?**  
   - **Money HQ Superagent Control Plane (`tools/superagent_runner.py`):** Deterministic Python operations engine (`0 VND` LLM cost) implementing DeepSeek Superagent's `Source -> Trigger -> Eval -> Mandate -> Ticket -> Isolated Worker -> Watchdog Recovery -> Attention Panel`.
   - **Antigravity:** Primary local operator with direct hands on the repository, shell, browser, and Docker environment.
   - **ChatGPT:** Strategic advisor, prompt architect, and independent auditor (no direct local machine execution).
   - **OpenAI Codex:** Coding and implementation agent when assigned locally/CLI; also provides the OAuth model backend for Agent Zero.
   - **Claude Code:** Independent architectural, security, and economic reviewer / specialist coding agent when assigned.
   - **Gemini & DeepSeek:** Independent advisory models (`dsh-superagent-prototype` domain architecture adapted into Money HQ).
   - **Agent Zero (`v2.13`):** Local Docker runtime (`http://localhost:5080`) with repo bind-mounted at `/a0/usr/projects/money-hq` (supervised and recovered by the Superagent Watchdog).
8. **What must agents prioritize and what must they avoid?**  
   - **Prioritize:** Repeatable digital assets, automated payment/fulfillment, compounding distribution, deterministic local Python scripts (`0 VND` marginal cost), and factual verification.
   - **Avoid:** Turning the owner into a daily manual laborer/salesperson, building complex infrastructure without a validated offer, spending money without approval (`500,000 VND` hard cap), fabricating metrics, or running redundant multi-agent loops.
9. **How is success measured?**  
   By **realized net profit (`L4` cash received minus all incremental costs), minimal owner hours, incremental capital efficiency, repeatability, and degree of operational independence** — never by lines of code, number of agents, or unverified revenue projections.
10. **Where should an agent look for detailed instructions and current status?**  
    Start here in `README.md`, then read [`OPERATING_SYSTEM.md`](./OPERATING_SYSTEM.md), [`portfolio/OPPORTUNITY_REGISTER.md`](./portfolio/OPPORTUNITY_REGISTER.md), [`operations/DAILY_BRIEF.md`](./operations/DAILY_BRIEF.md), [`operations/OWNER_ACTIONS.md`](./operations/OWNER_ACTIONS.md), and [`agents/AI_ROUTING_POLICY.md`](./agents/AI_ROUTING_POLICY.md).

---

## 2. Strategic Priorities & Opportunity Evaluation Rules

### Priority Order (Highest to Lowest)

1. **Assets created once and sold repeatedly** (digital handbooks, interactive diagnostic tools, templates, audio bundles).
2. **Products with automated acquisition, payment, and fulfillment** (static web funnels, VietQR/SePay webhooks, instant browser delivery).
3. **Compounding content, search, audience, and distribution assets** (programmatic SEO pages, searchable symptom/SKU tools, KOC affiliate links).
4. **Software, templates, data products, and reusable workflows** with near-zero marginal costs.
5. **Automated services requiring minimal human intervention** (where >95% of fulfillment is executed by deterministic scripts).
6. **Labor-based income (Lowest Priority)** — used **only** when collecting already-earned payouts (`uTest`) or providing an optional short-term cash bridge to fund scalable assets.

### Strategic Guardrails (What Not to Assume)

- **Do not assume** SaaS is inherently superior to digital products, content, affiliate websites, or micro-tools.
- **Do not assume** B2B is always superior to B2C.
- **Do not assume** the owner must personally perform cold outreach, sales calls, manual fulfillment, or customer support if an automated or affiliate model is viable.
- **Do not assume** more AI agents, Docker containers, or automation scripts equal business value. **Never confuse automation infrastructure with revenue-producing assets.**

### Mandatory 8-Factor Asset Evaluation

Every opportunity in [`portfolio/OPPORTUNITY_REGISTER.md`](./portfolio/OPPORTUNITY_REGISTER.md) must be evaluated honestly on:
1. **Demand Evidence (`L0–L4`):** Is there verified buyer/competitor payment proof?
2. **AI Asset Creation:** Can AI create and maintain the asset?
3. **Compliant Distribution:** How does traffic reach the asset without spam or rule violations?
4. **Automated Payment & Fulfillment:** Can checkout and delivery run without manual owner intervention?
5. **Support Minimization:** Does the product UX prevent repetitive support tickets?
6. **Marginal Cost & Unit Economics:** What is the incremental cost per additional sale (target: `0 VND`)?
7. **Compounding Value:** What accumulates over time (search index, affiliate links, rule libraries)?
8. **Unavoidable Human Intervention:** What legal, KYC, payout-rail, or capital-allocation tasks strictly require the owner?

---

## 3. System Inventory: Strategy vs. Actual Implementation Status

Every module in this repository carries an explicit verification label:
- `Implemented and verified` — Code/artifact exists and has been verified by automated tests or live execution.
- `Implemented but not verified` — Code/config exists, but end-to-end production execution or real buyer conversion is unverified.
- `In progress` — Actively being configured or tested.
- `Planned` — Proposed on the roadmap; **not** built yet.
- `Research only` — Market/competitor analysis or static dossiers only.
- `Paused or deprecated` — Explicitly halted or archived due to negative economics or strategic pivot.

### A. Strategic Destination

| Component | Target State | Current Status |
| :--- | :--- | :--- |
| **Level 3 Autonomous Asset Portfolio** | Multiple validated digital assets generating recurring/repeatable `L4` net cash flow with automated acquisition, payment, and fulfillment | **`In progress` (`L2` assets deployed; `L4` cash = `0 VND`)** |

### B. Current Operating System & Infrastructure

| Component | Path | Actual Capability & Verification Evidence | Status |
| :--- | :--- | :--- | :--- |
| **Control Plane & Governance** | [`OPERATING_SYSTEM.md`](./OPERATING_SYSTEM.md), [`agents/AI_ROUTING_POLICY.md`](./agents/AI_ROUTING_POLICY.md), [`agents/COST_OPTIMIZATION_POLICY.md`](./agents/COST_OPTIMIZATION_POLICY.md), [`agents/ROLE_CHARTER.md`](./agents/ROLE_CHARTER.md) | Defines Level 3 asset hierarchy, `500,000 VND` hard budget cap, 3x ROI gate, and actual AI agent responsibilities. | **`Implemented and verified`** |
| **Financial Ledgers & Dashboard Generator** | [`finance/CASH_LEDGER.csv`](./finance/CASH_LEDGER.csv), [`finance/COST_LEDGER.csv`](./finance/COST_LEDGER.csv), [`tools/money_hq_dashboard.py`](./tools/money_hq_dashboard.py) | Tracks `L4` cash (`0 VND`), `L3` pending payouts (`3` uTest bugs), incremental spend (`0 VND`), and exports [`finance/MONEY_HQ_DASHBOARD.md`](./finance/MONEY_HQ_DASHBOARD.md). Covered by `tests/test_money_hq_dashboard.py`. | **`Implemented and verified`** |
| **Google Sheet `Money HQ` Tab** | `Money HQ` tab (`gid=66015035`) | Synced from `MONEY_HQ_DASHBOARD.csv` with verified `0 VND` (`L4 = 0 ₫`, `L3 = 0 ₫`, `Spend = 0 ₫`) and clickable product links. | **`Implemented and verified`** |
| **GitHub Pages Commercial Storefront Hub & SEO Sitemap** | [`index.html`](./index.html), [`sitemap.xml`](./sitemap.xml), [`robots.txt`](./robots.txt) | Root commercial storefront (`https://maileac.github.io/revenue-copilot-international-phase0/`) with JSON-LD product schema, sitemap, and direct links to `EXP-03` (`299k / $12`) and `EXP-02` (`199k / $9`). | **`Implemented and verified`** |
| **Money HQ Superagent Control Plane (Adapted from DeepSeek Superagent)** | [`assets/superagent_control_plane/`](./assets/superagent_control_plane), [`tools/superagent_runner.py`](./tools/superagent_runner.py), [`operations/ATTENTION_PANEL.md`](./operations/ATTENTION_PANEL.md) | Persistent SQLite registry (`operations/superagent_store.db`), proactive `Sources` & `Triggers`, Revenue-First `Eval` & `Mandate` gate, idempotent `Tickets`, isolated per-ticket worker directories (`operations/superagent_work/`), step-level checkpointing, Watchdog crash recovery, and minimal Owner `Attention Panel`. Verified by 4 end-to-end tests in `tests/test_superagent_control_plane.py`. | **`Implemented and verified`** |
| **Web Capability Library & Independent Visual Quality Gate** | [`assets/web_capability_library/`](./assets/web_capability_library), [`tools/web_quality_gate.py`](./tools/web_quality_gate.py) | Queryable catalog of 13 capabilities synthesized from MaiLeac's GitHub stars (`Nutlope/hallmark`, `alchaincyf/huashu-design`, `eternity4719/HowToLiveBetter`, `browser-use`) and owned repos (`flow-scout-core`, `Sisan`, `vuong-quoc-loser`). Includes `tokens.css` multi-material design tokens, approved dependencies list, decision guide, and real Chromium Playwright visual QA testing. Verified by 5 tests in `tests/test_web_capability_library.py`. | **`Implemented and verified`** |
| **Telegram Two-Way Bridge & Quiet-by-Default Escalation Alerts** | [`tools/telegram_notify.py`](./tools/telegram_notify.py), [`tools/telegram_listener.py`](./tools/telegram_listener.py) | Loads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` strictly from non-Git `.env`; supports two-way owner commands (`báo cáo`, `test`, `link`) and quiet-by-default Superagent escalation alerts. | **`Implemented and verified`** |
| **Agent Zero (`v2.13`) Container & Repo Mount** | [`tools/agent-zero-setup/`](./tools/agent-zero-setup) (`http://localhost:5080`) | Docker container `agent-zero` running; repo bind-mounted read/write at `/a0/usr/projects/money-hq`; custom profile `money-coo` installed. | **`Implemented and verified`** |
| **Agent Zero Internal LLM Scheduler (`tasks.json`)** | [`tools/agent-zero-setup/tasks.json`](./tools/agent-zero-setup/tasks.json) (`/a0/usr/scheduler/tasks.json`) | Cron tasks configured, but Agent Zero's internal LLM scheduler failed at `20:30` with `litellm.AuthenticationError (401 Clerk/OpenRouter)`. Automatically detected and recovered deterministically by our Superagent Control Plane (`TKT-CA4F99B8`). Direct LLM execution inside Agent Zero remains blocked until a non-OpenRouter model provider is set in Agent Zero UI. | **`Blocked` (Agent Zero LLM Auth) / `Implemented and verified` (Deterministic Superagent Recovery)** |

### C. Revenue Experiments & Digital Assets

| ID & Name | Path | What Actually Exists vs. Market Validation | Status |
| :--- | :--- | :--- | :--- |
| **`EXP-03` (`PROD-01` / `ASSET-01`): Dưỡng Nhan 7-Constitution Web App, Digital Handbook & Audio** | [`experiments/exp03-duong-nhan-ai-mvp/`](./experiments/exp03-duong-nhan-ai-mvp), [`assets/duong_nhan_engine/`](./assets/duong_nhan_engine) | **Built:** Deterministic 7-constitution quiz engine (`constitution_engine.py`), 21-recipe handbook + Web Speech audio + printable 28-day tracker (`handbook.html`), dual international (`Payoneer: lethanhmaicombo@gmail.com`) + domestic (`VietQR`) checkout, commercial footer, and organic distribution kit (`distribution_kit.json` staged in `observe` mode). Covered by 6 unit tests.<br>**Unverified:** VietQR uses placeholder account `MB-0000000000` (no live SePay webhook bound yet); `0` live paid orders (`L4 = 0 VND`). | **`Implemented and verified` (Code, UI & Observe Distribution Kit) / `Implemented but not verified` (Live Payment & Sales)** |
| **`EXP-02` (`TOOL-01` / `SVC-01`): Catalogue QA Engine & Self-Serve CSV Web App** | [`experiments/exp02-catalogue-qa-pilot/`](./experiments/exp02-catalogue-qa-pilot), [`assets/catalogue_qa_engine/`](./assets/catalogue_qa_engine) | **Built:** Python SKU normalization & PII redaction engine (`catalogue_qa.py`), executive HTML report generator (`report_generator.py`), client-side browser CSV cleaner (`index.html`) with dual `Payoneer ($9)` + `VietQR (199k)` checkout, commercial footer, `distribution_kit.json` (`observe` mode), and a **120-row synthetic dataset** (`sample_portfolio/`). Covered by 5 unit tests.<br>**Unverified:** Tested on synthetic data; `0` paying customers (`L4 = 0 VND`). | **`Implemented and verified` (Engine, UI & Observe Distribution Kit) / `Implemented but not verified` (Customer Validation)** |
| **`EXP-01` (`CASH-01`): Crowdtesting (`uTest` Cycle 562706)** | [`experiments/exp01-qa-cashflow/`](./experiments/exp01-qa-cashflow), [`assets/qa_workflow_toolkit/`](./assets/qa_workflow_toolkit) | **Built:** Pre-flight bug report validator (`bug_report_preflight.py`) and net-hourly VND tracker (`qa_earnings_tracker.py`). Covered by 3 unit tests.<br>**Market Evidence (`L3`):** `3/3` approved bugs on uTest Cycle 562706, but `platform.utest.com/account/payments` currently shows `VND 0.00 Pending Payout` (`0 VND` realized or queued payout). | **`Implemented and verified` (Toolkit) / `Planned` (Awaiting uTest Cycle Settlement)** |
| **`JOB-01`: Remote Hourly QA / Transcription Applications (`Lionbridge`, `RWS`, `Welo`)** | [`experiments/exp01-qa-cashflow/APPLICATION_DOSSIER.md`](./experiments/exp01-qa-cashflow/APPLICATION_DOSSIER.md) | Static copy-paste application dossier. Demoted because hourly labor does not build an autonomous asset. | **`Planned` (Optional Standby Only)** |
| **Competitor & Gate 0 Research** | [`research/`](./research) | Evidence logs (`EVIDENCE_LOG.csv`), Gate 0 memos, and teardown of `biquyetduongnhan.vn`. | **`Implemented and verified` (Research Baseline)** |

### D. Pillar 4: Systematic Treasury & Quantitative Compounding

| ID & Name | Path | Relationship to Money HQ & Verification Status | Status |
| :--- | :--- | :--- | :--- |
| **`TRD-01`: Exness MT5 Quantitative Trading Agent** | [`trading-agent-exness-demo/`](./trading-agent-exness-demo) | Milestone M2 Quantitative Treasury Engine. Connected via live IPC to verified Exness MT5 Demo account (`#464160066`, server `Exness-MT5Trial17`, balance `$100,000 USD`). Features 2-tier architecture (pure mathematical EMA 20/50 + ATR stops, zero LLM execution), fail-closed safety (`block_live_accounts: true`), Conway Automaton-inspired survival tiers (max 1.2% DD in walk-forward tests, hard Kill Switch at 3%), and 22/22 unit tests passing offline. | **`Implemented and verified` (Live Demo Engine M2 — Capital Compounding Wing)** |
| **`TRD-02`: SOL-USDT Spot EMA50/200 Backtest** | [`experiments/sol-backtest/`](./experiments/sol-backtest) | Reproducible offline backtest on 2,096 daily OKX `SOL-USDT` bars (`2021–2026`). Verified by `tests/test_sol_backtest_audit.py`. Proved **negative Out-of-Sample returns from 2025 onward (`-35.76%` Buy & Hold, `-38.65%` EMA50/200)** — validated why Money HQ rejected crypto spot trend-following. | **`Implemented and verified` (Closed Audit Benchmark)** |

### E. Future Roadmap

1. **Programmatic SEO Symptom & E-Commerce Error Pages (`Planned`):** Next autonomous revenue-producing task queued for the Superagent Control Plane — generate static high-intent SEO symptom pages (`experiments/exp03-duong-nhan-ai-mvp/pages/`) and Shopify/Shopee CSV error landing pages (`experiments/exp02-catalogue-qa-pilot/pages/`) linked from `sitemap.xml` at `0 VND` cost.
2. **Live VietQR Bank Account / SePay Webhook Binding (`Blocked` on Owner Input):** Replace placeholder VietQR account (`MB-0000000000`) when owner wishes to receive domestic automatic QR transfers (international Payoneer `lethanhmaicombo@gmail.com` is already embedded).
3. **External Community Syndication Promotion from `observe` to `live` (`Planned`):** Keep external community posts (`distribution_kit.json`) in `observe_dry_run` mode until owner reviews and approves public posting.

---

## 4. AI Workforce & Routing Summary

Full policy: [`agents/AI_ROUTING_POLICY.md`](./agents/AI_ROUTING_POLICY.md) | Cost policy: [`agents/COST_OPTIMIZATION_POLICY.md`](./agents/COST_OPTIMIZATION_POLICY.md)

| Agent / Model | Role in Money HQ | Can Directly Edit Local Repo / Run Commands? |
| :--- | :--- | :--- |
| **Money HQ Superagent Control Plane (`tools/superagent_runner.py`)** | **Deterministic Autonomous Operations Engine (`0 VND` LLM Cost):** Runs `Source -> Trigger -> Eval -> Mandate -> Ticket -> Isolated Worker -> Watchdog Recovery -> Attention Panel`. | **YES (Deterministic Python)** |
| **Antigravity** | **Primary Local Operator (With Hands):** Inspects files, edits code/docs, runs `pytest`, manages Docker/Agent Zero, and pushes commits via `gh`. | **YES** |
| **ChatGPT** | **Strategic Advisor, Prompt Architect & Independent Auditor:** Defines Level 3 strategy, critiques unit economics, and audits agent output. | **NO** |
| **OpenAI Codex** | **Coding & Implementation Agent (When Assigned):** Executes scoped code/test implementation when invoked; provides OAuth model backend (`gpt-5.4` / `gpt-5.4-mini`). | **When invoked locally** |
| **Claude Code** | **Independent Reviewer & Specialist Agent (When Assigned):** Audits architecture, security/privacy exposures, and hidden failure modes. | **When invoked locally** |
| **Gemini & DeepSeek** | **Independent Advisory Models:** Used for secondary research or cross-checking assumptions (`dsh-superagent-prototype` domain architecture adapted here). | **NO** |
| **Agent Zero (`v2.13`)** | **Local Container Runtime (`http://localhost:5080`):** Runs `money-coo` profile with `/a0/usr/projects/money-hq` bind-mounted; supervised by Superagent Watchdog. | **Inside `/a0/usr/projects/money-hq`** |

---

## 5. Security, Privacy & Repository Visibility Notice

- **Repository Visibility:** This GitHub repository (`MaiLeac/revenue-copilot-international-phase0`) is currently **PUBLIC** (which enables free GitHub Pages hosting for `index.html`, `EXP-03`, and `EXP-02`).
- **No Raw Credentials Committed:** There are zero API keys, Telegram tokens, passwords, `.env` secrets, or real bank account numbers committed in this repository (verified by `test_no_hardcoded_credentials_in_telegram_tools`).
- **Spreadsheet Link Separation Rule:** Keep Money HQ business metrics strictly inside [`finance/MONEY_HQ_DASHBOARD.md`](./finance/MONEY_HQ_DASHBOARD.md) and [`finance/MONEY_HQ_DASHBOARD.csv`](./finance/MONEY_HQ_DASHBOARD.csv).

---

## 6. Running Automated Verification (`49/49 Tests Passing`)

Always run the test suite and Superagent Control Plane pass from the repository root before claiming any module works:

```powershell
python -m pytest -v
python tools/superagent_runner.py --run-pass
python tools/web_quality_gate.py index.html experiments/exp03-duong-nhan-ai-mvp/index.html experiments/exp02-catalogue-qa-pilot/index.html --browser-render
```

- **Root test suite (`tests/`):** `27` unit & integration tests covering `catalogue_qa_engine`, `duong_nhan_engine`, `money_hq_dashboard`, `qa_workflow_toolkit`, `sol_backtest_audit`, `superagent_control_plane`, and `web_capability_library` (catalog querying, Hallmark Floor gate audits, Playwright DOM geometry verification).
- **Trading R&D test suite (`trading-agent-exness-demo/tests/`):** `22` unit tests covering demo-only config locks, data quality gates, execution blockers, risk kill-switch, and IS/OOS backtest evaluation.
