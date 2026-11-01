# Cost Optimization Program & Spending Policy — Money HQ

**Program Status:** ACTIVE (Effective 2026-11-01)  
**Objective:** Maximize verified net profit (`L4` cash minus incremental cost) per unit of owner time and incremental operating cost.  
**Hard Experimental Budget Cap:** **500,000 VND** (Total cumulative incremental spend allowed without a new explicit owner sign-off).  
**Current Incremental Spend:** **0 VND** (100% of current budget remaining).

---

## 1. Audit of Existing Cost-Saving Measures (Verified State)

Before launching new optimizations, the repository and Agent Zero installation were audited on `2026-11-01`:

1. **Subscription OAuth Reuse (`ACTIVE`):** Agent Zero (`usr/plugins/_model_config/presets.yaml` & `usr/plugins/_oauth`) is configured to authenticate via existing `codex` OAuth rather than incurring pay-per-token OpenAI API billing.
2. **Model Tier Presets (`ACTIVE`):** Three presets exist in `presets.yaml`:
   - `Efficiency`: Uses `gpt-5.4-mini` (`reasoning_effort: low`) for utility calls and `gpt-5.4` (`low`) for main chat.
   - `Default`: Uses `gpt-5.4` (`medium`) for main chat and `gpt-5.4-mini` (`low`) for utility.
   - `Power`: Reserved only for complex troubleshooting (`high` reasoning).
3. **Zero-Cost Local Embeddings & Search (`ACTIVE`):** Agent Zero uses local CPU embeddings (`sentence-transformers/all-MiniLM-L6-v2`) and local SearxNG search inside the container (`0 VND` marginal API cost).
4. **Deterministic Engines Instead of LLM Token Burn (`ACTIVE`):**
   - Catalogue SKU QA (`assets/catalogue_qa_engine/catalogue_qa.py`) audits 120+ SKUs in `<0.1s` using deterministic Python rules (`0` LLM tokens).
   - Client Executive HTML Report (`assets/catalogue_qa_engine/report_generator.py`) renders executive audit reports deterministically (`0` LLM tokens).
   - QA Earnings & Ledger Tracker (`assets/qa_workflow_toolkit/qa_earnings_tracker.py` & `tools/money_hq_dashboard.py`) computes ROI and P&L deterministically (`0` LLM tokens).

---

## 2. Mandatory Evaluation Formula for Any Paid Tool or API

No paid API, SaaS subscription, domain, proxy, or paid listing may be purchased unless a written proposal in `operations/OWNER_ACTIONS.md` answers all 7 criteria below and passes the **3x Break-Even Rule**:

1. **Task Performed:** Exact bottleneck the paid tool solves.
2. **Why Free/Current Tools Are Insufficient:** Concrete evidence showing Python scripts, Playwright, SearxNG, GitHub Pages, and existing subscriptions failed.
3. **Incremental Cost (VND):** One-time vs. recurring cost in VND (must fit within the remaining `500,000 VND` cap; recurring charges are blocked by default).
4. **Expected Owner/Operator Time Saved:** Hours saved per week.
5. **Expected Verified Revenue Impact (`L4`):** Realistic 30-day net cash impact.
6. **Break-Even Requirement:**
   $$\text{Break-Even Units} = \frac{\text{Incremental Cost (VND)}}{\text{Net Contribution per Unit (VND)}}$$
   *Rule:* Expected 30-day probability-weighted revenue must be **$\ge 3\times$ Incremental Cost**.
7. **Cheaper Alternatives Evaluated:** At least 2 free or open-source alternatives tested first.

---

## 3. Cost-Optimization Rules for Daily Operations

1. **Deterministic Script First:** Never use an LLM to validate CSV rows, sum ledgers, format HTML reports, or check git status. Run the repository Python scripts.
2. **Context & Token Diet:**
   - Read targeted line ranges or summaries instead of dumping entire files or `node_modules` into prompts.
   - Store reusable SOPs, buyer outreach templates, and audit checklists in repository markdown files so agents read a 50-line SOP instead of regenerating strategy from scratch.
3. **Browser Automation Discipline:**
   - Use headless Playwright only when DOM interaction is required (e.g., syncing the Google Sheet `Money HQ` tab).
   - Avoid repeated full-page screenshots or polling loops once a selector is verified.
4. **Scheduled Polling vs. Constant Loops:**
   - Agent Zero runs **at most 2 scheduled daily jobs** (`08:30` and `20:30` Asia/Saigon). Continuous background polling is prohibited.
5. **Artifact & Research Caching:**
   - Every market or technical finding is logged once in `portfolio/OPPORTUNITY_REGISTER.md` or `experiments/` and reused across sessions.

---

## 4. Ranked Cost-Saving Backlog (Prioritized by ROI)

| Rank | Initiative ID | Optimization Measure | Replaces / Avoids | Est. Monthly Savings | Implementation Status |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | `COST-01` | **Deterministic Catalogue QA & HTML Report Generator** (`catalogue_qa.py` + `report_generator.py`) | Calling GPT-5.4 / Claude per SKU row during client audits (saves ~150k–500k tokens per 1,000-SKU audit) | ~350,000 – 1,200,000 VND/mo in avoided API token burn | **IMPLEMENTED & VERIFIED** |
| **2** | `COST-02` | **Deterministic Financial & Google Sheet Sync Script** (`tools/money_hq_dashboard.py`) | Manual owner spreadsheet entry or multi-step LLM browser reasoning | ~200,000 VND/mo + ~4 hrs/mo Owner Time | **IMPLEMENTED & VERIFIED** |
| **3** | `COST-03` | **OAuth Subscription Routing + `Efficiency` Preset Default for Scheduled Jobs** | Separate pay-as-you-go OpenAI/Anthropic API keys for Agent Zero cron tasks | ~500,000+ VND/mo in avoided API keys | **IMPLEMENTED & VERIFIED** |
| **4** | `COST-04` | **Zero-Cost Hosting & Portfolio Distribution** (GitHub repo + local HTML proof packs + direct outreach) | Paid landing page builders (Webflow/Framer/Carrd Pro) or custom domain before first `L4` sale | ~250,000 – 500,000 VND/mo | **ACTIVE POLICY** |
| **5** | `COST-05` | **Incremental Delta Check in Daily Briefs** (Hash-check `CASH_LEDGER.csv` & `COST_LEDGER.csv` before invoking LLM analysis) | Redundant daily LLM summarization when ledgers have zero new rows | ~50% reduction in Agent Zero scheduled job tokens | **IMPLEMENTED IN SKILL (`financial-reporting`)** |
