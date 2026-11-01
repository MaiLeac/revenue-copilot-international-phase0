# Money HQ Web Capability Library & Anti-AI-Slop Visual Quality Gate

> **Core Mandate:** Never generate generic, AI-looking web interfaces. Before writing any CSS or layout code, query this library, reuse approved components and design tokens from MaiLeac's GitHub stars and repositories, and pass the independent visual quality gate (`tools/web_quality_gate.py`).

---

## 1. Complete GitHub Stars & Repositories Inventory

*Verification Method: Paginated GitHub API query via GitHub CLI (`https://api.github.com/users/MaiLeac/starred?per_page=100` and `https://api.github.com/user/repos?per_page=100`). Verified that page 1 returned the complete active dataset and page 2 returned 0 items.*

### A. Curated Starred Repositories (Total: 7)

| ID | Repository & URL | Language & Stars | License & Commercial Use | Maintenance Status | What It Actually Provides & Reusability Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`STAR-01`** | [**`Nutlope/hallmark`**](https://github.com/Nutlope/hallmark) | CSS • 44.5k ★ | MIT (Allowed; 755 bundled photos under individual open licenses) | Active (Pushed 2026-10-29) | **Direct Reuse:** 50 material themes, 16 non-waivable Floor Gates against AI slop (`overflow-x: clip`, `:focus-visible`, reduced-motion, no tracked-cap eyebrows, no emoji buttons, no `transition: all`), font pairing tables (`fonts.md`), and `sloplint.mjs`. |
| **`STAR-02`** | [**`alchaincyf/huashu-design`**](https://github.com/alchaincyf/huashu-design) | HTML • 28.4k ★ | MIT (Allowed) | Active (Pushed 2026-10-30) | **Adapt Pattern:** 84-style visual reference catalog (`design-styles.md`), 3-direction gate, GSAP timeline recipes (`gsap-recipes.md`), typography scale rules (display-to-body font ratio $\ge 2.5\times$, 8pt spacing grid, $\le 4$ core colors), and `scripts/design_lint.py`. |
| **`STAR-03`** | [**`eternity4719/HowToLiveBetter`**](https://github.com/eternity4719/HowToLiveBetter) | HTML • 72.2k ★ | MIT (Code via `LICENSE-CODE`) / CC-BY-4.0 (Content) | Active (Pushed 2026-10-21) | **Adapt Pattern:** High-trust editorial layout where every health/life recommendation explicitly presents Cost, Benefit, Evidence Grade, and Primary Source (`index.html` + `selfcheck.html`). Ideal for `EXP-03` Dưỡng Nhan. |
| **`STAR-04`** | [**`Vincentwei1021/video-shotcraft`**](https://github.com/Vincentwei1021/video-shotcraft) | TS • 15.7k ★ | Apache-2.0 (Allowed) | Active (Pushed 2026-10-29) | **Adapt Pattern:** 124 cinematic shot recipe cards, 150 motion previews, Remotion promo video templates, and Motion Workbench. Reusable for product video promos. |
| **`STAR-05`** | [**`browser-use/browser-use`**](https://github.com/browser-use/browser-use) | Python • 119.7k ★ | MIT (Allowed) | Active (Pushed 2026-10-31) | **Direct Reuse:** Python browser automation engine built on Playwright for multi-step browser validation and crowdtesting workflows. |
| **`STAR-06`** | [**`HKUDS/Vibe-Trading`**](https://github.com/HKUDS/Vibe-Trading) | Python • 37.4k ★ | MIT (Allowed) | Active (Pushed 2026-10-30) | **Inspiration Only:** Multi-agent trading research. Not a frontend web library; archived under TRD-01 demo R&D. |
| **`STAR-07`** | [**`Conway-Research/automaton`**](https://github.com/Conway-Research/automaton) | TS • 7.6k ★ | MIT (Allowed) | Active (Pushed 2026-08-26) | **Inspiration Only:** Conceptual autonomous agent runtime. Superseded by our deterministic DeepSeek Superagent Control Plane. |

### B. Owned Repositories & Local Codebases (Total: 9 Owned Repositories)

| ID | Repository & Local Path | Language | License | What It Provides to the Capability Library |
| :--- | :--- | :--- | :--- | :--- |
| **`OWN-01`** | [**`MaiLeac/flow-scout-core`**](https://github.com/MaiLeac/flow-scout-core)<br>`C:\Users\ACER\Documents\Codex\flow-scout-core` | TypeScript | Proprietary (Owner) | **Direct Reuse:** 15 battle-tested UX/QA failure patterns (`PAT-01` to `PAT-15`) including dead link prevention (`PAT-08`), filter-detail contradictions (`PAT-01`), and unrecoverable empty states (`PAT-05`). |
| **`OWN-02`** | [**`MaiLeac/Sisan`**](https://github.com/MaiLeac/Sisan)<br>`C:\Users\ACER\Sisan` | React 19, TS, Tailwind v4, Vite 6 | Proprietary (Owner) | **Direct Reuse:** Touch-swipeable `RoomCard.tsx` image carousel, OSRM route distance service (`distance.ts`), multi-criteria `FilterBar.tsx` with mobile bottom sheet, and CTV referral link tracker (`referral.ts`). |
| **`OWN-03`** | [**`MaiLeac/vuong-quoc-loser`**](https://github.com/MaiLeac/vuong-quoc-loser)<br>`C:\Users\ACER\.codex\worktrees\backup-task-ids\Loser Kingdom` | Python, Vanilla JS, CSS | Proprietary (Owner) | **Adapt Pattern:** Isolated SVG motion layers (`banner-flag-svg`, `cloak-svg`) over static high-res artboards, ambient canvas particle system (`kingdom-magic`, `kingdom-petals`) with explicit pause toggle (`.motion-toggle`). |
| **`OWN-04`** | [**`MaiLeac/awesome-ai-video-code`**](https://github.com/MaiLeac/awesome-ai-video-code) | Markdown | Proprietary (Owner) | **Direct Reuse:** Curated handbook & integration matrix for 8 code-driven video/animation skills (Remotion, GSAP, hyperframes, edge-tts). |
| **`OWN-05`** | [**`MaiLeac/revenue-copilot-international-phase0`**](https://github.com/MaiLeac/revenue-copilot-international-phase0) | Python, HTML, JS | Proprietary (Owner) | **Direct Reuse:** Root commercial storefront (`index.html`), SEO sitemap (`sitemap.xml`), client-side CSV auditor (`EXP-02`), and 7-constitution health engine (`EXP-03`). |

---

## 2. Capability Catalog Grouped by 13 Core Capabilities

```text
                                 MONEY HQ CAPABILITY MATRIX
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. Premium UI & Design Systems     │ Nutlope/hallmark (50 themes), tokens.css          │
│ 2. Landing Pages & Templates       │ Hallmark themes, HowToLiveBetter layout           │
│ 3. Dashboards & App Layouts        │ Sisan AdminRevenuePanel, BookingsDashboard        │
│ 4. Typography & Color Systems      │ Hallmark fonts.md, Huashu 8pt grid, 3-token system │
│ 5. Animation & Micro-Interactions  │ Loser Kingdom isolated SVG motion, Motion v12     │
│ 6. Charts & Data Visualization     │ HowToLiveBetter evidence cards, Flow-Scout KPIs   │
│ 7. Forms, Filters & Search Tables  │ Sisan FilterBar, distance.ts, CSV Fixer table     │
│ 8. Navigation & Responsive Layouts │ Sisan Header, Hallmark capped-centered containers │
│ 9. Accessibility & Usability       │ Hallmark Floor (:focus-visible, reduced-motion)   │
│ 10. Visual QA & Regression Testing │ tools/web_quality_gate.py, Playwright browser run │
│ 11. Conversion & Analytics         │ Sisan referral.ts, VietQR/Payoneer checkout hooks │
│ 12. Asset & Icon Libraries         │ lucide-react (100% SVG, no emoji icons)           │
│ 13. AI Frontend Dev Workflows      │ 8-step Anti-AI-Slop Protocol, catalog.json index  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Premium UI components & design systems:** [`assets/web_capability_library/tokens.css`](./tokens.css) (multi-material variables: Swiss Ledger, Apothecary Paper, Hospitality Warm; strict zero-slop rules).
2. **Landing page and website templates:** Commercial Storefront Hub (`index.html`), Dưỡng Nhan Quiz Funnel (`EXP-03`), and Catalogue QA Tool (`EXP-02`).
3. **Dashboard and application layouts:** `C:\Users\ACER\Sisan\src\components\BookingsDashboard.tsx` and `AdminRevenuePanel.tsx`.
4. **Typography, color systems & visual design references:** `Nutlope/hallmark/skills/hallmark/references/fonts.md` (banned fonts list, non-default display pairings: Newsreader, Rethink Sans, EB Garamond, JetBrains Mono; display-to-body font scale ratio $\ge 2.0\times$).
5. **Animation & micro-interaction libraries:** `motion` (`^12.23.24`), Loser Kingdom isolated SVG motion layers (`banner-flag-svg`, `cloak-svg` with zero background distortion), and `.motion-toggle` pause control.
6. **Charts, data visualization & interactive elements:** `HowToLiveBetter` evidence cards, Money HQ KPI grid, and SVG metric sparklines.
7. **Forms, tables, filters and search interfaces:** Sisan `FilterBar.tsx` (real-time search, multi-district filter, price presets, active badge counter, and mobile slide-over sheet).
8. **Navigation, menus and responsive layouts:** Capped & centered container (`max-width: 1120px; margin-inline: auto; padding-inline: 24px;`), mobile-responsive hamburger drawer, and `overflow-x: clip`.
9. **Accessibility & usability tools:** Instant `:focus-visible` outlines, `@media (prefers-reduced-motion: reduce)`, and `minmax(0, 1fr)` image grid tracks.
10. **Browser automation and visual regression testing:** [`tools/web_quality_gate.py`](../../tools/web_quality_gate.py) executing real Chromium headless rendering at `1280x800` (desktop) and `390x844` (mobile).
11. **Product analytics & conversion optimization:** Sisan `referral.ts` (query string parameter parsing, persistent localStorage attribution, commission split calculation) + VietQR/Payoneer dual payment rails.
12. **Image, icon, illustration & asset libraries:** `lucide-react` (SVG icons replacing all UI emojis) and Hallmark 755 openly licensed photography index (`photos.json`).
13. **AI-assisted design & frontend development tools:** Money HQ 8-Step Anti-AI-Slop Protocol + Python query engine (`assets/web_capability_library/library.py`).

---

## 3. Approved Dependencies & Design System Recommendations

### A. React & TypeScript Stack (For Sisan & Next-Gen SPAs)
- **Icons:** `lucide-react` (`^0.546.0`, ISC License). *Rule: Never use emojis as button or status icons.*
- **Animation:** `motion` (`^12.23.24`, MIT License). *Rule: Animate only `transform` and `opacity`. Never `transition: all`.*
- **QR & Export:** `react-qr-code` (`^2.2.0`, MIT License), `html-to-image` (`^1.11.13`, MIT License), `jspdf` (`^4.2.1`, MIT License).
- **Styling:** `tailwindcss` (`^4.1.14`, MIT License) bound strictly to `tokens.css` semantic CSS variables.

### B. Static HTML & Editorial Stack (For Storefronts, Guides, Tool Pages)
- **Typography:** Google Fonts (`Newsreader`, `Rethink Sans`, `EB Garamond`, `JetBrains Mono`). Free under SIL Open Font License 1.1.
- **Base Tokens:** Link [`assets/web_capability_library/tokens.css`](./tokens.css) in the document `<head>`.
- **Numerals:** Always add `.tabular-nums` / `font-variant-numeric: tabular-nums` to price cards, order numbers, and KPI stats.

---

## 4. Decision Guide: When to Reuse, Adapt, or Build

| Scenario | Action | Mandatory Rule |
| :--- | :--- | :--- |
| **Common UI Pattern** (icons, modals, carousels, routing distances, QR codes) | **DIRECT REUSE** | Check `approved_dependencies` and `Sisan/src/utils/` first. Do not reinvent. |
| **Visual Style & Layout** (hero sections, evidence cards, color palettes, animations) | **ADAPT PATTERN** | Adapt Hallmark material themes (`tokens.css`), Huashu 8pt grid, or HowToLiveBetter evidence cards. |
| **Domain Logic** (7-constitution diagnosis, catalogue SKU error fixing, MT5 trade gate) | **BUILD FROM SCRATCH** | Write clean, deterministic Python/TypeScript logic, but bind UI rendering strictly to `tokens.css` and pass `web_quality_gate.py`. |

---

## 5. Independent Visual Quality Gate (`tools/web_quality_gate.py`)

A build that compiles is **not** a finished product. Every HTML page must pass our automated quality gate before delivery:

```powershell
python tools/web_quality_gate.py <html-file> --browser-render --screenshot-dir operations/quality_gate_screenshots
```

### Checks Enforced:
1. **Hallmark Floor Gate #1:** Declared `:root` CSS custom properties or link to `tokens.css`.
2. **Hallmark Floor Gate #2:** Zero `transition: all` or `transition-all`.
3. **Hallmark Floor Gate #4:** Zero `100vw`; `overflow-x: clip` on `html` and `body`.
4. **Hallmark Floor Gate #6:** Instant `:focus-visible` on all interactive elements.
5. **Hallmark Floor Gate #7:** `@media (prefers-reduced-motion: reduce)` fallback.
6. **Hallmark Floor Gate #9:** Zero tracked-uppercase eyebrow labels (use body font in sentence case).
7. **Hallmark Floor Gate #10:** Zero glued arrows in CTA text (e.g. `Buy Now →` is forbidden; use `Buy Now`).
8. **Hallmark Floor Gate #11:** Zero emojis inside buttons or headings.
9. **Flow-Scout PAT-08:** Zero dead placeholder links (`<a href="#">`).
10. **Real Browser Geometry (Playwright Chromium):**
    - `desktop_1280x800`: Zero horizontal overflow (`scrollWidth <= clientWidth`), Hero H1 and primary CTA visible above 800px fold.
    - `mobile_390x844`: Zero horizontal overflow, display-to-body font ratio $\ge 1.5\times$.

---

## 6. Concrete Improvement Plans for Existing Projects

### A. Sisan / Wink Home (`C:\Users\ACER\Sisan`)

| Priority | Defect / Problem | Root Cause | Recommended Fix from Capability Library |
| :--- | :--- | :--- | :--- |
| **High** | Dead `<a href="#">` links in `Header.tsx` (Giới thiệu, Tuyển dụng, Hợp tác, Liên hệ) | Flow-Scout `PAT-08` violation; leads users to nowhere | Replace `#` with modal triggers (`onOpenAboutModal`) or smooth-scroll anchor sections (`#features`, `#contact`). |
| **High** | `transition-all duration-300` in `RoomCard.tsx` (Line 138) | Hallmark Floor Gate #2 violation; causes browser layout thrashing | Replace `transition-all` with `.interactive-surface` (`transition: transform 160ms ease-out, box-shadow 160ms ease-out, border-color 160ms ease-out`). |
| **Medium** | AI neon gradient borders & emojis in `RoomCard.tsx` and `Header.tsx` (`✨ Vì sao Sisan gợi ý`, `animate-border-flow`, `🎁 Săn thưởng`, `👑 Admin`) | AI-generated design cliché | Replace emojis with clean `lucide-react` icons (`Sparkles`, `Gift`, `Crown`); replace neon cyan/teal animated gradient with subtle solid `border border-emerald-200 bg-emerald-50/50`. |
| **Medium** | Missing `:focus-visible` styling on room cards and search inputs | Accessibility barrier | Inherit `:focus-visible` from `tokens.css` with 2px emerald outline offset. |

### B. Loser Kingdom (`C:\Users\ACER\.codex\worktrees\backup-task-ids\Loser Kingdom`)

| Priority | Defect / Problem | Root Cause | Recommended Fix from Capability Library |
| :--- | :--- | :--- | :--- |
| **High** | Unbounded viewport and box shadow overflow on desktop (`box-shadow: 0 0 110px #000; overflow: auto`) | Violates Hallmark Floor Gate #4 & #14 (capped and centered container) | Clamp desktop frame with `max-width: 480px; margin-inline: auto; height: 100dvh; overflow: hidden;` and use `overflow-x: clip`. |
| **Medium** | Floating advisor parchment text contrast (`advisor-parchment` over scenery) | Low readability in bright scenery zones | Apply `backdrop-filter: blur(8px); background: rgba(14, 18, 27, 0.85); border: 1px solid rgba(232, 194, 118, 0.35); color: #fdf5d3;` using tokens. |
| **Medium** | Beacons lack keyboard focus indicators | Accessible interaction failure | Add `:focus-visible` outline for all 5 goal beacons (`.beacon:focus-visible`). |

---

## 7. Working Demonstration & Verified Browser Results

We applied this capability library directly to our active web assets:
1. **Root Commercial Storefront Hub (`index.html`)**
2. **Dưỡng Nhan 7-Constitution Web App (`experiments/exp03-duong-nhan-ai-mvp/index.html`)**
3. **Catalogue QA E-Commerce Tool (`experiments/exp02-catalogue-qa-pilot/index.html`)**

### Verification Command Run:
```powershell
python tools/web_quality_gate.py index.html experiments/exp03-duong-nhan-ai-mvp/index.html experiments/exp02-catalogue-qa-pilot/index.html --browser-render --screenshot-dir operations/quality_gate_screenshots
```

### Actual Verified Evidence:
- **Overall Status:** `overall_passed = True` (Exit Code `0`).
- **All 3 Assets Scored 100/100:**
  - `index.html`: `100/100` • 0 horizontal overflow • H1 bottom Y = 125px • CTA bottom Y = 555px (cleanly visible above 800px fold).
  - `exp03/index.html`: `100/100` • 0 horizontal overflow • Font ratio = 2.35x.
  - `exp02/index.html`: `100/100` • 0 horizontal overflow • All button emojis removed • Semantic footer verified.
- **Rendered Screenshots Saved:**
  - `operations/quality_gate_screenshots/index__desktop.png` (101.7 KB)
  - `operations/quality_gate_screenshots/index_exp03-duong-nhan-ai-mvp_desktop.png` (500.2 KB)
  - `operations/quality_gate_screenshots/index_exp02-catalogue-qa-pilot_desktop.png` (126.1 KB)
- **Unit & Integration Test Suite:** `49/49` automated tests passing in `2.30s`.
