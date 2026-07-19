# Build note — Ryan Fox / The 154th Open Championship (2026-07-19)

Photo-mode WITB carousel (real product hero shots, not SVG). Egress was **Full**
this week, so the pipeline web-sourced manufacturer photos.

## Winner (confirmed)
- **Ryan Fox** — 154th Open Championship, Royal Birkdale, 16–19 Jul 2026.
- Winning score **270 (−10)**, by 1 stroke over Cameron Young. Maiden major.
- Rounds 72-68-62-68 (the 62 was Saturday/round 3).

## WITB (cross-checked: GolfWRX, Golf Monthly, Today's Golfer, 2nd Swing)
- Driver — Srixon ZXi LS, 10.5° · Fujikura Ventus Black 7 TX
- 3-wood — Srixon ZXi, 15° · Fujikura Ventus Black
- Driving iron — Srixon ZXi5+ 3-iron (20°)
- Irons — Srixon ZXi5 (4–5), ZXi7 (6–PW) · True Temper Dynamic Gold Tour Issue X100
- Wedges — Cleveland RTZ 50°/56°/60° · True Temper DG Tour Issue
- Putter — Ping Anser 2D · SuperStroke Zenergy grip
- Ball — Srixon Z-Star XV (Pure White)

## Image sources (manufacturer CDNs)
- Driver / 3-wood / irons / ball — us.dunlopsports.com (Srixon `large/` catalog shots)
- Wedge — us.dunlopsports.com (Cleveland RTZ Tour Satin `large/` shot)
- Putter — api.next.ping.com (PLD Milled Anser 2D, transparent PNG)
Raw downloads in `assets/products/raw/`, cleaned versions in `assets/products/stack/`.

## Processing
`raw → flatten-on-white → (driver: paint out Golf Digest badge) → trim → 5% pad →
resize → JPEG` then embedded as base64 data URIs so the build HTML is self-contained
(also required for the Claude Artifact CSP). Reprocess with the same steps if
re-sourcing.

## Build + render
- Carousel: `builds/2026-07-19-the-open-fox.html` (self-contained; 6 × 1080×1350)
- Render: `node tools/render_frames.js builds/2026-07-19-the-open-fox.html out/the-open-fox`
- Approval proof-sheet (source): `builds/2026-07-19-the-open-fox.artifact.html`
- Claude Artifact: https://claude.ai/code/artifact/f08e0143-274d-4b08-abeb-2fdf7f7a9329

## Status
Draft posted to Slack `#ernest-performance` for approval. **Not scheduled** — awaiting
go-ahead before Metricool `createScheduledPost`.
