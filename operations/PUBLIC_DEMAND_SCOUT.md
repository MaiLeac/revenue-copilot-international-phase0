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
