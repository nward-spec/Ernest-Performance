# Working files — Ernest-Performance

Working files for this project live here.

## WITB "Winner's Bag" Instagram carousel

The weekly PGA Tour "Winner's Bag" carousel (a collab published with the
Dialled In Pod) lives here. Start with [`CLAUDE.md`](./CLAUDE.md) before touching
the build — it documents the render workflow and the layout gotchas.

- `Winners Bag Carousel.html` — the carousel skeleton
- `builds/` — per-week builds (copy the latest, swap the winner data)
- `tools/` — `render_frames.js` (screenshots frames) and `compose_club_stack.py`
- `assets/` — product images and manifest
- `out/` — rendered PNG artifacts (gitignored)

See [`../ORGANIZATION.md`](../ORGANIZATION.md) for how this project stays uniform
across GitHub, the Claude app, and the web.
