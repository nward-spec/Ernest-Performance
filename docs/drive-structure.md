# Multi-account Drive structure

Single-window setup: work from **nward@ernestperformance.com.au**, with the
other two Drives shared in. Files stay owned by the account they belong to —
nothing is migrated between accounts.

| Workstream | Google account | Owns |
|---|---|---|
| Ernest Performance | nward@ernestperformance.com.au | `Ernest Performance/` |
| Dialled In (podcast) | dialledin@gmail.com | `Dialled In/` |
| NW Personal | nicholasernestward@gmail.com | `NW Personal/` |

Each tree must be created **while signed into its owning account**. Building
them from the Ernest Performance account would make that account the owner,
which is the thing this design avoids.

---

## Job 5 — Dialled In (`dialledin@gmail.com`)

```
Dialled In/
  00 - Claude Workspace
  01 - Episodes/
        Ep 01   Ep 05   Ep 09   Ep 13
        Ep 02   Ep 06   Ep 10   Ep 14
        Ep 03   Ep 07   Ep 11   Ep 15
        Ep 04   Ep 08   Ep 12   Ep 16
  02 - Audio & Video Assets
  03 - Artwork & Thumbnails
  04 - Guests
  05 - Distribution & Scheduling
  06 - Admin
```

Episode subfolders are `Ep 01` … `Ep 16`, zero-padded so they sort correctly.

## Job 6 — NW Personal (`nicholasernestward@gmail.com`)

```
NW Personal/
  00 - Claude Workspace
  01 - Personal Brand & Content
  02 - Golf (Peninsula Kingswood, Box Hill Pennant)
  03 - Training & Health
  04 - Finance & Admin
  05 - Family
```

## Job 7 — Ernest Performance (`nward@ernestperformance.com.au`)

Existing structure is correct and stays as is. **Add one folder only:**

```
Ernest Performance/
  00 - Claude Workspace     <-- ADD THIS
  01 - Admin & Legal
  02 - Finance
  03 - Operations
  04 - Marketing & Content
  05 - Inventory & Suppliers
  06 - Members & Fitting
  07 - Shareholders
```

`00 - Claude Workspace` is scratch space for anything Claude produces before
it is filed into the right numbered folder. Not a permanent home.

Verified folder IDs (Ernest Performance Drive):

| Folder | ID |
|---|---|
| `Ernest Performance` (root) | `1QFeYQGJtDGo3COmrV_VVd_cxYr6B4X40` |
| `01 - Admin & Legal` | `1yqcNsr9lEYRsfIaqKFwfniJztEEcOuPv` |
| `02 - Finance` | `10daBE8uk_Z1BbJLile9nvA5Y96_1EKy3` |
| `03 - Operations` | `1Se3ZSQzwi-GzZYVHGhZKMLBvsXZHRJvZ` |
| `04 - Marketing & Content` | `12p2f4grpl7DxNQ2nZrghfNfhdeEumtS9` |
| `05 - Inventory & Suppliers` | `1dv5W_baWgbRM2g1z6GHQonJWhWjo64er` |
| `06 - Members & Fitting` | `1YdoruIHeq1SRbsYIt7eIV12tCtvHZujk` |
| `07 - Shareholders` | `11LOlihmx4h6wV4kI8EG_KN2CaQ73Gbop` |

---

## Job 8 — Share and shortcut

Share the **top-level folder only**. Drive permissions are inherited, so one
share carries the whole tree including anything added later. One share per
account — not one per subfolder.

| From account | Share | With | Role |
|---|---|---|---|
| dialledin@gmail.com | `Dialled In` | nward@ernestperformance.com.au | Editor |
| nicholasernestward@gmail.com | `NW Personal` | nward@ernestperformance.com.au | Editor |

Then, signed in as **nward@ernestperformance.com.au**, add a shortcut to each
shared folder at the top level of My Drive, so all three sit side by side
instead of one being buried in *Shared with me*:

> Right-click the folder in *Shared with me* → **Organise** → **Add shortcut**
> → **My Drive** → *Add*.

Result:

```
My Drive (nward@ernestperformance.com.au)
  Ernest Performance/          (owned)
  Dialled In/                  (shortcut -> dialledin@gmail.com)
  NW Personal/                 (shortcut -> nicholasernestward@gmail.com)
```

A shortcut is a pointer, not a copy — ownership does not change.

---

## Job 9 — Decisions outstanding

Audited from the Ernest Performance Drive on 2026-08-18.

**1. `Personal/` (top level, 11 subfolders)** — move into `NW Personal`, or keep?

```
Health          Finances        Fitness         Home Loan
Employment      Misc Files      Personal Golf   Spark Email
Photo Archive - old iPhone      Other Golf Business  *   Sportsbet:BetEasy  *
```

`*` — these two read as business, not personal. Flagged for a decision before
anything moves. Note that moving files out of this account changes nothing
about ownership: they would still be owned by the Ernest Performance account
unless separately transferred.

**2. `The Open - Driving Irons/` (top level)** — 4 files, all raw DJI capture
(2× MP4, largest 629 MB; 2× JPG; 13 July 2026). Unedited content footage, not
supplier material → recommend **`04 - Marketing & Content`**.

**3. `Saved from Chrome/`** — one file: `Titleist Price List - May 2026.pdf`.
Supplier pricing → recommend **`05 - Inventory & Suppliers`**, then delete the
empty folder.

**4. `Archive/`** — left alone, as instructed.
