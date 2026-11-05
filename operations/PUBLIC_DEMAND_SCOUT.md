# Public Demand Scout

`python tools/public_demand_scout.py` runs one bounded pass over recent public
Hacker News comments and GitHub issues. It makes at most six searches, reads at
most 15 results per search, needs no credentials or paid API, and never contacts
anyone. Register the Windows task with
`powershell -File tools/register_public_demand_scout.ps1`; it runs at 08:35,
14:35 and 20:35 local time while the signed-in computer is available.

The local `operations/public_demand_scout/latest.json` contains the last run and
new signals; `signals.jsonl` is the cumulative source-linked evidence; `state.json`
prevents duplicate processing. These runtime files are ignored by git. A signal
is not proof of a buyer, payment, or unmet market. For any candidate, verify the
source post, current need, buyer/payer, existing alternatives, why they fail, and
whether a response is permitted. If cheap existing products solve it, reject the
copycat offer unless a specific buyer proves a remaining gap.

## From signal to work

The scheduled script only collects candidates; **it does not evaluate competitors or execute work by itself**. An AI working from this repo must take one source-linked candidate at a time:

1. Reopen the original request and record an absolute last-check time, current availability, buyer outcome, and budget/payment conditions. Reject stale or inaccessible listings.
2. Compare the exact request with at least the obvious free/native tool and visible competing bids or products. State the buyer's remaining gap; do not invent a moat. Verify platform fees, required deposits, payout path, privacy and permitted response channel.
3. If the economics and access pass, perform the smallest safe **internal** part of delivery now on synthetic/public data and test it. Record artifact, result, time and cash cost. Do not stop at an idea card.
4. If a real customer response, account, customer data, or commercial commitment is needed, prepare the exact next action and follow the repo's authorization rules. Record submitted/accepted/paid only after evidence exists. If blocked, state the concrete blocker and switch to the next candidate; do not count preparation as revenue.

[05 Nov execution example](ACTION_2026-11-05_DATA_CLEANUP.md): a real listing was checked against competing bids and native tools, a cleanup sample was built and tested, then the bid was stopped because the platform requires a minimum account balance. No money was collected.
