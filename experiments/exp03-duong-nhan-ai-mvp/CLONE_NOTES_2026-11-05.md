# EXP-03 web reference and rebuild notes — 2026-11-05

## Sources and limits

- `https://biquyetduongnhan.vn/ebook/duong-nhan` was inspected in the owner's open Chrome tab on 2026-11-05. The repo also preserves a 2026-11-01 HTML snapshot in `research/competitors/biquyetduongnhan/landing_page.html`.
- The owner's MotionSites Bloom screenshots are visual references only. No MotionSites prompt, source code, or asset was purchased or copied.
- `JCodesMore/ai-website-cloner-template` (MIT) supplied the map → observe → build → compare workflow. Its Next.js 16 scaffold was not installed: this experiment is already a small static site, and its current bottleneck is a finished product rather than a framework migration.
- Competitor copy, brand, book images, medical assertions, and checkout code were not reused. The botanical hero in this project was generated for this project.

## Observed source → local route

| Source behavior | Local implementation | Status |
|---|---|---|
| Offer hero and book cover | `index.html` hero and illustrative cover | Rebuilt with original copy and image; full book still in editing |
| Actual book-page gallery | `index.html#trang-mau` and `handbook.html` | Three excerpts from the existing seven-day sample; no invented finished pages |
| Problem/method explanation | `index.html#ve-sach` and `#xem-truoc` | Original non-diagnostic habit-journal framing |
| How buyer receives the book | `index.html#cach-nhan` | Future manual bank check and file delivery are disclosed; payment is closed |
| FAQ | `index.html#hoi-dap` | Native keyboard-accessible `<details>` controls |
| Payment modal / web reader | `checkout.html` / `handbook.html` | Payment closed; free sample readable now. No live paid access flow |

## Checks

- Chrome desktop preview: hero, sample cards, FAQ rendered.
- Chrome at 390 × 844: hero image visible; no horizontal overflow (`scrollWidth` 375 vs viewport 390); FAQ opened.
- Local anchor targets resolve; `tools/web_quality_gate.py` passed the three EXP-03 HTML pages.
- No buyer payment, download delivery, conversion, or traffic test has occurred. The source site's advertised automated confirmation was not tested either.

## Product gate

The page may invite people to read the free sample. It must not display a price or accept a transfer until there is a complete, rights-cleared digital file and an exact fulfillment procedure. A larger digital catalogue needs additional finished files, not empty product cards.
