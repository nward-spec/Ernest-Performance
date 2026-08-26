# Workshop Pro — Architecture

Base44 app **EP Workshop Pro** (`69d85d24a19d92f61a853c2e`, config name "SwingCraft Pro").
Staff-facing one-stop shop for quoting club-fitting builds, invoicing them via
Shopify, building the clubs with staged customer notifications via Klaviyo, and
hosting customer specs. Deliberately **not** connected to the live
bookings/membership app (`69d83a90aa7a27a33cd3b77a`) yet — same brand, separate
apps, integration is a later phase.

This document is the source of truth for how the app is shaped. The point of
the architecture is that day-to-day changes are **data edits, not code edits**:
a new brand, a new loft, a price change, a new notification, a house-standard
tweak — none of those should require touching a React component again.

## Decision log (locked 2026-08-26)

| Decision | Choice |
|---|---|
| Brand data ingestion | **Live portal scraping** — per-brand adapters run where the dealer-portal logins live (Nathan's Mac, same pattern as the existing Shopify "Mac sync" and `tools/labgolf_refresh.py`), push normalized rows to the app's `ingest-catalog` backend function. Clean syncs auto-apply; anomalies hold for review. |
| Quote → payment | **Shopify draft order** — an approved quote creates a draft order (components + labour + build fee as line items); the customer pays through the Shopify checkout link; the existing Shopify→Xero accounting flow does the books. The manual "paste Xero link" path stays only as fallback until this ships. |
| Customer notifications | **Key milestones via Klaviyo** — the app fires a Klaviyo event on *every* stage change; Klaviyo flows email only the milestones (Order Confirmed, In Build, Ready for Collection). Adding/removing a customer touchpoint is a Klaviyo flow edit, not app code. |
| Migration style | **Staged** — new catalog engine grows alongside the existing entities; pages repoint one at a time (Spec Sheet first); nothing live breaks mid-migration. |

The separate **BillFlow** Base44 app is not part of this flow and stays untouched.

## Principles (the "foolproof" rules)

1. **Nothing is ever guessed.** A spec value exists because a manufacturer
   source published it, or it is empty. (Already the house style — see the
   HeadModelSpec `lies` description and `labgolf_refresh.py` guards. This is
   now a system-wide invariant.)
2. **Cascades derive from concrete variants, never parallel arrays.** "GT2 in
   left hand comes in 9° and 10° only" is true because those two variant rows
   exist, not because two arrays happen to line up. Parallel-array entities
   (HeadModelSpec lofts/lies/labels, IronStockSpec) are migration sources, not
   the destination.
3. **Every quotable product has confirmed wholesale AND retail pricing.** A
   variant missing either is `price_status: needs_review` and the quoting UI
   refuses to add it silently — it shows the gap instead. No margin is ever
   computed from a missing cost (InventoryItem already states this; it
   generalises).
4. **Quoted prices are frozen.** What a job was quoted at is stored on the job
   and never re-derived from the live catalog (the `club_count` rule, applied
   everywhere money is stored).
5. **Side-effectful transitions go through backend functions.** Stage changes,
   quote approval, draft-order creation, Klaviyo events — one function per
   transition, idempotent, with a ledger row. Pages never fire external calls
   directly.
6. **Sources are ranked.** For any one field: portal feed > manual staff entry
   > Shopify mirror. A sync never overwrites a manually-confirmed price
   without flagging it.

## System map

```
Titleist / PING / Callaway / Mizuno / Srixon / Cobra dealer portals   LAB Golf public configurator
        │ (logins live in the browser on the Mac)                            │
        ▼                                                                    ▼
  Per-brand adapter scripts (Mac, scheduled)  ◄── one shared contract ── labgolf adapter
        │  normalized JSON rows, chunked
        ▼
  ingest-catalog  (Base44 backend fn, shared-secret auth)
        │  diff vs live catalog
        ├── clean ────────────► CatalogVariant   (single source of truth)
        └── anomalies ───────► IngestBatch: pending_review ──(staff approve on Catalog page)──► CatalogVariant
                                                                    │
                          ┌─────────────────────────────────────────┤
                          ▼                                         ▼
                 Spec Sheet cascade engine                  Catalog Health view
                 (filter variants by selection)             (missing prices, stale syncs)
                          │
                          ▼
                    BuildJob (quote → build stages, prices frozen at quote)
                          │ quote approved                        │ stage change
                          ▼                                       ▼
             create-draft-order fn ──► Shopify draft order   advance-stage fn ──► NotificationEvent ledger
                          │ customer pays                              │
                          ▼                                            ▼
             Shopify order (→ Xero via existing flow)        Klaviyo event "WP Build Stage Changed"
                                                                       │ (flows pick milestones)
                                                                       ▼
                                                          Customer email: Order Confirmed /
                                                          In Build / Ready for Collection
```

## Data model

### New entities (created 2026-08-26)

**CatalogVariant** — one row per orderable combination, all component types.
Key fields: `component_type` (Head/Shaft/Grip), `brand`, `model`, `family`,
`variant_label`, `category`, axis fields (`hand`, `club_label`, `loft`, `lie`,
`length`, `flex`, `bounce`, `grind`, `finish`, `weight`, `grip_size`,
`tip_size`), `sku`, `wholesale_price`, `retail_price`, `price_status`
(confirmed / needs_review / missing), `availability` (available /
special_order / discontinued / unknown), `source`, `source_ref`,
`ingest_batch_id`, `synced_at`, `shopify_product_id`, `shopify_variant_id`.
Identity key for diffing: `source + sku`, falling back to
`brand|model|variant_label|axes` when a portal publishes no SKU.

**IngestBatch** — provenance + staging for every sync run. `source`,
`adapter_version`, `status` (received / applied / pending_review / rejected /
failed), row/added/updated/removed/price-change counts, `anomalies[]`
(severity, code, message, sku), `pending_rows` (held rows for review),
`auto_apply`.

**AppSetting** — key/JSON-value settings with a `category`. First residents:
the EP house standard block currently hard-coded in `specCatalog.js`
(`EP_HOUSE_STANDARD`: lie/length at 7i, steps, hold-below-PW flag), the $35
build fee (`clubPricing.js BUILD_FEE_DEFAULT`), price-anomaly thresholds, and
notification toggles. Admin page edits these; code reads them.

**NotificationEvent** — the idempotency ledger. `job_id`, `event_type`,
`stage`, `channel`, `metric`, `recipient`, `dedupe_key`
(`job_id|event_type|stage`), `status` (queued / sent / failed / suppressed),
`error`, `sent_at`, `properties`. A stage change that already has a sent row
for its dedupe_key does not fire Klaviyo again.

### Existing entities and their fate

| Entity | Fate |
|---|---|
| `BuildJob` | **Keeps its role** as the job aggregate. Gains nothing structural now; later gains `shopify_draft_order_id` + per-line `catalog_variant_id` references (prices stay frozen copies). |
| `Customer` | Unchanged. |
| `HeadModelSpec` | Migration **source** for head CatalogVariants (its parallel arrays expand to one row per hand×loft). Stays live until Spec Sheet reads the catalog service; then read-only, then retired. |
| `IronStockSpec` | Same — expands to per-club-label variant rows. |
| `InventoryItem` | Narrows to what it truly is: the **Shopify/stock mirror** (quantities, Shopify IDs, unit cost). Spec/cascade duties move to CatalogVariant; the two link via `shopify_variant_id`. |
| `src/data/labPutters.js` | `labgolf_refresh.py` gets a second output mode: emit adapter rows to `ingest-catalog` instead of writing a JS file. Until then the file remains the LAB source behind the catalog service facade. |
| `User` | Unchanged. |

### The catalog service facade

`src/lib/catalog.js` — the **only** module pages may import for catalog data:

```
getModels({component_type, category, brand?})        → distinct models
getVariants({model, hand?, ...axis filters})         → matching variant rows
cascade(axes, selection)                             → for each axis: values still available
priceFor(variant)                                    → {wholesale, retail, status}
health()                                             → missing prices, stale sources, pending batches
```

During migration the facade reads the old entities + `labPutters.js` behind
the same signatures; sources swap to CatalogVariant per component type with
zero page edits. That is the mechanism that makes the staged migration safe.

## Ingestion layer

### Adapter contract (Mac-side runners)

One adapter per brand, any language, one obligation: POST normalized rows to
`/functions/ingest-catalog` with header `x-ingest-key: <INGEST_API_KEY>`.
Full row schema + rules live in the app repo at `tools/ADAPTERS.md`. The rules
that make it foolproof:

- Every value verbatim from the portal — no derivation, no interpolation
  (the two `labgolf_refresh.py` guards, generalised).
- Chunked ≤500 rows per call; chunks share a `batch_ref`; final chunk sets
  `complete: true` so removals are only computed against a full feed.
- `wholesale_price` and `retail_price` (RRP) both required where the portal
  publishes them; a row missing either arrives as `needs_review`, never
  invented.
- Adapters are scheduled on the Mac (launchd/cron or a recurring Claude
  session) because that is where the portal logins live; the app never stores
  portal credentials.

### Anomaly gates (server-side, in `ingest-catalog`)

Auto-apply only when a sync is clean. Held for review when:
- any price moves more than the threshold (AppSetting, default 20%),
- more than 10% of a source's variants vanish from a complete feed,
- a row fails validation (unknown component_type, malformed price),
- first-ever sync of a new source (everything is "new" — a human should look).

Held batches surface on the Catalog page with a diff (added / changed /
removed / price moves); one click applies or rejects. Applied or not, every
run leaves an IngestBatch row, so "when did Titleist last sync and what
changed" is always answerable.

## Pricing policy

- Wholesale comes from the dealer portal (or Shopify `unitCost` for
  shop-stocked odds and ends). Retail is the published RRP where one exists.
- Where a brand publishes no RRP, retail may be proposed by a per-brand markup
  rule (AppSetting) but lands as `needs_review` until a human confirms it.
- A manual price confirmation wins over a sync until the portal price itself
  changes, which re-flags rather than silently overwrites (source ranking).
- The quoting UI treats `needs_review`/`missing` as a visible blocker on the
  line, not a zero.

## Quote → payment (Shopify draft order)

1. Staff build the quote (existing NewJob/QuotePage flow, prices frozen on the
   job). Customer approves via the hosted quote link.
2. Approval calls `create-draft-order` (new backend fn): line items = each
   club's components at quoted retail × club_count, labour, build fee;
   customer attached by email; job gets `shopify_draft_order_id` and the
   invoice URL becomes the draft order's checkout link (replacing the manual
   Xero paste).
3. Customer pays through Shopify checkout. A scheduled poll (or webhook via a
   Shopify app proxy, later) marks the job paid → auto-advance to Order
   Confirmed → milestone email fires.
4. Xero stays downstream of Shopify exactly as it is today for retail sales.

## Build stages & notifications

Stage ladder (unchanged): Quote → Order Confirmed → Components Pulled →
Assembly → Quality Check → Ready for Collection → Delivered (+ Cancelled).

- `advance-stage` backend fn is the only writer of `stage`: validates the
  transition, appends `stage_history`, writes the NotificationEvent ledger
  row, fires Klaviyo metric **"WP Build Stage Changed"** with properties
  `{job_number, stage, first_name, due_date}`.
- Klaviyo flows filter on `stage`: emails exist for **Order Confirmed**,
  **Components Pulled** (customer-facing copy: "Your build has started"), and
  **Ready for Collection**. Assembly/QC stay internal. Changing cadence or
  copy = Klaviyo edit only.
- Ledger dedupe means a mis-click or retry can never double-email a customer.
- SMS for Ready for Collection is a Klaviyo flow addition later; the event
  already carries everything it needs.

## UI architecture

- **Design tokens only.** `src/index.css` holds the shadcn/Tailwind variables,
  now aligned to the live main app's compiled CSS (near-black `20 4% 4%`
  background, Soft Sand foreground, Bunker Brown `28 20% 57%` primary, slate
  `200 27% 18%` secondary/border, radius .75rem, Aeonik Pro / Conthrax type).
  Re-skinning ever again is a variable edit in one file.
- **One cascade component.** `ShaftCascade` / `GripCascade` / head pickers
  (~60KB of near-duplicate logic) converge on a generic `CascadeSelect` driven
  by `catalog.cascade()` — an axis list + selection in, valid options out.
  Per-club-type differences become config (which axes, in what order), not
  components. This is the direct fix for "too long on individual toggles".
- **House standards read from AppSetting**, edited on Admin — already flagged
  as intended in the `EP_HOUSE_STANDARD` comment.
- Print/spec-sheet views keep their current structure; they read the same
  facade.

## Migration plan

| Phase | Work | Done when |
|---|---|---|
| **0. Foundation** *(this change)* | Entities (CatalogVariant, IngestBatch, AppSetting, NotificationEvent), `ingest-catalog` fn scaffold, adapter contract, design tokens aligned, this document. | Entities visible in app; tokens match main site; doc merged. |
| **1. First feeds** | LAB adapter emits to `ingest-catalog`; Titleist adapter built against the portal on the Mac; Catalog page gains batch review + health view; `INGEST_API_KEY` secret set. | Two sources syncing on schedule; every LAB/Titleist variant priced or flagged. |
| **2. Facade** | `src/lib/catalog.js` over old entities; Spec Sheet + NewJob repointed; `CascadeSelect` replaces first cascade. | Spec Sheet renders identically from the facade. |
| **3. Backfill + swap** | HeadModelSpec/IronStockSpec expanded into CatalogVariant; remaining brands' adapters; facade flips source; old spec entities read-only. | Cascades served entirely by CatalogVariant. |
| **4. Money** | `create-draft-order` fn + paid-poll; quote approval wires to it; manual Xero paste demoted to fallback. | A real build quoted → approved → paid in Shopify end-to-end. |
| **5. Stages** | `advance-stage` fn + ledger + Klaviyo metric; three milestone flows built; UI stage buttons call the fn. | Stage click sends exactly one correct customer email. |
| **6. Retire** | Delete parallel-array entities, hard-coded data files, dead toggles. | No page imports anything but the facade. |

Each phase is independently shippable; the app works throughout.
