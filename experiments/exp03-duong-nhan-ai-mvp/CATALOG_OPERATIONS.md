# Bản Thảo product catalog

**Current state, 2026-11-05:** One book is being written. Seven free web exercises are illustrative and not author-approved excerpts from the finished book. No product is on sale. `products.json` is the source for the public `catalog.html` listing. There are no physical goods.

## Adding the next real digital product

1. Get the actual title, file or working preview, description, format, rights to use all text and art, and delivery method. Do not invent a product to fill the grid.
2. Add one object to `products.json` with a unique `id`, `name`, `format`, `summary`, `status`, `price_vnd`, `detail_url`, and optional `sample_url`. Use `draft` while incomplete, `preview` when only a real sample is available, and `available` only after the full deliverable and fulfillment path are verified.
3. Make a detail page that accurately shows the deliverable and sample. Never place a paid file in the public repository or a public web path.
4. Before a product becomes `available`, verify the final file opens on phone and desktop, the author approves its contents, the price and receiving account are correct, the bank transfer reference is understandable, and a manual order can be matched to a received payment and delivered. Test a zero-cost dry run without paying or publishing buyer data.
5. Only after those checks, enable a real order route. A static HTML page cannot itself verify receipt of a bank transfer or privately deliver a paid file. `checkout.html` intentionally remains closed until the manual process and contact channel are configured and tested.
6. Run `python tools/web_quality_gate.py experiments/exp03-duong-nhan-ai-mvp/index.html experiments/exp03-duong-nhan-ai-mvp/catalog.html experiments/exp03-duong-nhan-ai-mvp/handbook.html experiments/exp03-duong-nhan-ai-mvp/checkout.html --browser-render`, inspect both viewports, and check every link.

## What is still needed to sell

- The author's finished, approved book or another finished digital product.
- Confirmed product name, format, license/usage terms, price, and preview.
- A chosen customer contact channel and delivery process. Do not display account details or ask for payment until they are verified and the order process works.
- The owner's explicit go-live decision for public sale.

No subscription, paid API or hosting dependency was added for the catalog.
