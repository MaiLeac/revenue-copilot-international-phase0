# Shared capability map — 2026-11-05

This is the quick index for Codex, Antigravity, Agent Zero and any other agent working on Money HQ. The machine-readable list is [`catalog.json`](./catalog.json); use `python tools/capability_lookup.py "task words"` from repository root. Entries are candidates, not installed software. Recheck licenses, maintenance, cost and local availability before code reuse.

| Task | Start here | Practical use | Limit |
|---|---|---|---|
| Landing page structure and comparison | `JCodesMore/ai-website-cloner-template` (`EXT-01`) | Map reference sections, inspect desktop/mobile, implement and visually compare | Workflow only for EXP-03; do not copy third-party assets or migrate to Next.js without need |
| Design quality and typography | `Nutlope/hallmark` (`STAR-01`), `alchaincyf/huashu-design` (`STAR-02`), local `tokens.css` | Choose a coherent visual system and run local quality gate | Star counts and maintenance labels in catalog are historical snapshots |
| Trustworthy informational layout | `eternity4719/HowToLiveBetter` (`STAR-03`) | Study evidence presentation and plain language | Code/content licenses differ; no medical claims without independent support |
| UX bug checks | `MaiLeac/flow-scout-core` (`OWN-01`), `tools/web_quality_gate.py` | Check dead links, overflow, state and visual layout | Verify local path exists before importing; gate is available in this repo |
| Forms and marketplace patterns | `MaiLeac/Sisan` (`OWN-03`) | Reuse a relevant interaction pattern if the project stack matches | Do not copy a whole app to make a static page |
| Promotional video concepts | `Vincentwei1021/video-shotcraft` (`STAR-04`), `MaiLeac/awesome-ai-video-code` (`OWN-02`) | Storyboard or adapt a visual sequence after a real product exists | Video does not prove demand; no paid rendering assumed |
| Browser automation | `browser-use/browser-use` (`STAR-05`) | Consider for authorized, repeatable QA work | Requires dependencies/model access; not needed for simple static QA |
| Trading research | `HKUDS/Vibe-Trading` (`STAR-06`) | Separate demo research only | No real-money trading or implied profitability |
| Autonomous agent ideas | `Conway-Research/automaton` (`STAR-07`) | Read architecture patterns only | Do not deploy wallet/spending/autonomy runtime |

## Selection procedure

1. State the concrete task and expected output.
2. Look up at most a few relevant candidates using the CLI or JSON catalog.
3. Verify the repository's current source and license; check installed status and incremental cost.
4. Use an existing local component or a small pattern; make the task deliverable work without the candidate if it adds weight.
5. Test the actual result and record the source used in the change note. Never report "integrated" solely because a repo is starred.

For EXP-03 the current choice is **EXT-01's comparison workflow plus the existing static HTML and local QA gate**. No third-party clone was installed. The site content and visual assets are original to this repo.
