# WINK private asset workflow · 06/11/2026

- Windows task `FamilyAssets_AutoPriceUpdater` runs `tools/auto_update_family_assets.py --telegram-prices-only` daily at 20:00 ICT. Python fetches public reference prices, writes to local SQLite, then sends a per-owner Telegram report. The flag is a compatibility alias; running without it does the same thing.
- The private database is `C:/Users/ACER/Documents/Codex/wink-private/wink.db`, outside the public Git repository. Initial data was imported once from local `holdings.json` and `prices.json`. Edits from the WINK dashboard are audited in the `asset_edits` table.
- Each successful scheduled refresh saves the observed portfolio in `daily_snapshots` for its ICT date. A manual holding edit updates that day's snapshot. WINK can filter the recorded dates and show the last snapshot per week, month or year. It does not manufacture historical values for dates before recording started; the first trusted snapshot is 06/11/2026.
- Phantom screenshot provided 06/11/2026 confirms **19.65951 PSOL**. The 21 SOL transaction shown in the same app is the initial stake, not a current PSOL balance. WINK displays PSOL to five decimal places and records the screenshot date for the quantity.
- The WINK dashboard runs on `http://127.0.0.1:8000` only. It shows Mai, Mẹ and Bầu (Việt) separately, with quantity, original cost, estimated market value, and estimated change. No debt is counted. Exness equity and quantities need manual updates; the dashboard does not connect to brokerage accounts.
- KNP silver page does not expose a verified quote date to this parser. Exness equity was last manually recorded 07/10/2026. These limits must remain visible in the report and dashboard.
- This script no longer requests Google Sheets access or writes to the Sheet. The old Codex Sheet automation remains paused. Do not revive it without a new owner decision.
- Agent Zero is shown as read-only status plus a local launch link. WINK does not send financial data or commands to Agent Zero and does not claim its scheduled jobs are active.
- Telegram delivery counts as verified only when `send_telegram_alert` returns `ok=True` without `dry_run`.
