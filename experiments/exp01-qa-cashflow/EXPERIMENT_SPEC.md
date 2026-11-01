# EXP-01 (Primary Cashflow Experiment) — Crowdtesting Throughput & Remote QA Expansion (`CASH-01` + `JOB-01`)

**Lane:** Cashflow  
**Status:** Active (Primary #1)  
**Evidence Level:** `L3` on `CASH-01` (uTest Cycle 562706 Rank #1 Leader, 3/3 bugs approved: 1 Very Valuable, 2 Somewhat Valuable, 0% rejection); `L1` on `JOB-01` (`I01` Lionbridge $15–$20/hr, `I02` RWS up to $6/hr, `I03` Welo ~$5/hr).

---

## 1. Revenue Discipline Parameters

| Dimension | Specification |
|---|---|
| **Specific Buyer / Payer** | Global crowdtesting & AI/QA platforms with verified payout rails (`uTest / Applause`, `Testlio`, `Test IO / EPAM`, `Lionbridge`, `RWS TrainAI`, `Welo Global`). |
| **Specific Pain** | Post-release functional/checkout defects on live e-commerce/travel web apps (`uTest`/`Testlio`/`Test IO`) and Vietnamese language transcription/search/ads evaluation quality (`Lionbridge`/`RWS`/`Welo`). |
| **Concrete Monetization Mechanism** | Per-approved-bug bounty ($2–$50+/bug on uTest/Test IO) + hourly paid test runs ($10–$18/hr on Testlio; $5–$20/hr on Lionbridge/RWS/Welo). |
| **Distribution Channel** | Direct platform cycle invitations & official Lever/platform application portals (`I01–I03`, Testlio). Zero cold outreach or ad spend required. |
| **Measurable Conversion Event** | **Interim (`L3`):** Bug report marked `Approved` on scorecard or paid contract/run assigned with clear pay rate. **Final (`L4`):** Usable cash settled into the owner's bank/PayPal/Payoneer account and logged in `finance/CASH_LEDGER.csv`. |
| **Cost & Owner-Time Budget** | **Cash spend:** `0 VND` (cap `<= 500,000 VND` strictly for payment withdrawal/FX fees upon receipt). **Unpaid prep/application/test cap:** `<= 12 hours` total across `JOB-01` onboarding. |
| **Stop Condition** | 1. Halt any platform that requests application/training fees, deposits, or VPN/identity spoofing. 2. Halt `JOB-01` onboarding if no paid task/contract with a <30-day payout schedule is confirmed by Day 7 (`<=12h` unpaid). 3. Drop any cycle/project whose realized net payout after fees falls below `50,000 VND/hour` (`~$2.00/hr` net) after initial onboarding. |

---

## 2. Deployed Autonomous Assets in This Experiment

1. **[`assets/qa_workflow_toolkit/bug_report_preflight.py`](../../assets/qa_workflow_toolkit/bug_report_preflight.py)**:
   - Pre-submission validator checking draft bug reports against the 8 acceptance rules from `BUG_LESSONS.md` (title structure, environment completeness, >=3 atomic reproduction steps, expected vs actual distinction, video/screenshot attachment check, WAD/WNF trap warnings, and PII leak blocking).
2. **[`assets/qa_workflow_toolkit/qa_earnings_tracker.py`](../../assets/qa_workflow_toolkit/qa_earnings_tracker.py)**:
   - Reconciles unpaid prep hours vs active hours, calculates net VND/hour after PayPal/FX fees and the `50,000 VND/hr` shadow wage, and enforces the strict separation between `L3_APPROVED_PENDING` and `L4_COLLECTED_CASH`.
3. **[`APPLICATION_DOSSIER.md`](./APPLICATION_DOSSIER.md)**:
   - Ready-to-paste factual profile, device matrix template, and pre-application verification questions for Lionbridge (`I01`), RWS (`I02`), Welo (`I03`), and Testlio.
