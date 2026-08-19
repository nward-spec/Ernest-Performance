# Local session brief

Everything a fresh Claude Code session running **on the studio MacBook** needs
to finish this work. Written 2026-08-19. Read this file in full before acting.

## Why this file exists

The earlier session ran in an Anthropic cloud container, not on the Mac. It
could reach Google Drive (one account) and GitHub, but never the local
filesystem — so the local audit, the credential scan and the power settings
were specified and scripted but never run. You are the session that runs them.

## Context

Three parallel workstreams, each with its own Google account:

| Workstream | Google account | Drive status |
|---|---|---|
| Ernest Performance | nward@ernestperformance.com.au | structured, folders 01–07 |
| Dialled In (podcast) | dialledin@gmail.com | unstructured |
| NW Personal | nicholasernestward@gmail.com | unstructured |

Goal: one window. Nick works from the Ernest Performance account with the other
two Drives shared in, reachable from iPad and iPhone, nothing living only on a
local machine. **Files stay owned by the account they belong to. Nothing is
migrated between accounts.**

The wider objective: Nick can leave this MacBook at the studio and still work
from iPad and iPhone. Everything below serves that.

## State of the machine

- `~/Ernest-Performance` **exists but is NOT a git repository.** Contents
  unknown. Inspect it, report what it is, do not modify or delete it. It may
  hold unbacked work, or be a Drive-synced copy.
- The repo should be cloned fresh to `~/Code/Ernest-Performance`.
- Node/npm state unknown. Claude Code CLI was being installed.

## Already done — do not redo

- **Job 9 filing.** `The Open - Driving Irons/` moved to `04 - Marketing &
  Content`; `Titleist Price List - May 2026.pdf` moved to `05 - Inventory &
  Suppliers`. Both verified. `Saved from Chrome/` is now empty and can be
  deleted. `Archive/` untouched, as instructed.
- **Job 7 declined.** `00 - Claude Workspace` was deliberately not created in
  the Ernest Performance Drive. Do not create it unless Nick asks.
- **`Personal/` is OUT OF SCOPE.** Nick relocates those 11 subfolders himself,
  by hand, from the personal account. Do not move, copy or plan anything for
  them. (Reason: a Drive move does not transfer ownership — see
  `docs/drive-structure.md`.)

## Jobs to run, in order

### Job 1 — Local audit (read-only)

```bash
bash tools/dispatch/01-audit-local.sh | tee ~/Desktop/audit.txt
```

Report: every git repo with full path, remote, uncommitted changes, unpushed
state. Include the Gmail→Xero bill automation and the amortisation calculator.

**Flag any repo inside a Google Drive for Desktop synced folder.** Git
internals syncing through Drive corrupts the object store. Report which ones —
**do not move them yet.** Also report Drive for Desktop status (installed,
running, account, streaming vs mirroring) and Claude Code's directory access.

**CHECK IN with Nick. Wait for his go-ahead before Job 2.**

### Job 2 — Credential audit (read-only scan, then changes)

The bill pipeline touches live Gmail and live Xero. **This is the blocking gate
before anything goes near GitHub.**

```bash
bash tools/dispatch/02-scan-secrets.sh <each repo path from Job 1>
```

Scan for credentials, API keys, OAuth tokens, client secrets, refresh tokens,
and the Xero and Gmail configuration. **Scan git history, not just the working
tree** — a secret committed three months ago and deleted since is still in the
history and still a leak. Sections D and E of the scanner cover history.

Then:
- Install `tools/dispatch/gitignore.template` as `.gitignore` in each repo,
  merging with anything already there.
- Install `tools/dispatch/env.example.template` as `.env.example`, adjusted to
  the variable names each repo actually uses. **Placeholder values only.**
- Move hardcoded secrets to environment variables.
- For anything found in history: tell Nick to **rotate the credential**.
  Deleting the file is not enough. Offer `git filter-repo` to scrub history.

**CHECK IN. Report exactly what was found and what was changed, before a
single push.**

### Job 3 — Push to GitHub

Only after Nick approves Job 2. Create **private** repos and push. Repos live
in GitHub, not Drive.

This is a fallback, not the primary path: if the MacBook drops offline Nick
reaches the code through Claude Code on the web. Actual pipeline runs against
live Gmail and Xero stay on this machine.

Do **not** open pull requests.

### Job 10 — Prepare the machine as the Dispatch engine

```bash
bash tools/dispatch/10-dispatch-power.sh --check   # inspect first
bash tools/dispatch/10-dispatch-power.sh           # apply, needs sudo
```

Sets display sleep, system sleep and disk sleep to never **on AC only**, then
re-reads them to confirm they held. Also:
- Confirm Claude Desktop is on the current version.
- Confirm no energy saver setting suspends the machine while plugged in with
  the lid open.
- Re-report Claude Code's directory access after any repo moves from Job 1, so
  Nick knows the paths are still valid.

Dispatch pairing needs Nick's phone in hand — leave that to him.

## Jobs that need Google Drive access

Jobs 4, 5, 6 and 8 need OAuth for `dialledin@gmail.com` and
`nicholasernestward@gmail.com`. A local CLI session probably does **not** have
Drive connectors either — check before promising anything.

If Drive tools are unavailable, say so and suggest the practical path: create
the folders directly in the Drive web UI while signed into each account. It is
roughly 25 folders. Full trees, share instructions and verified folder IDs are
in `docs/drive-structure.md`.

- **Job 5** — build the `Dialled In` tree in dialledin@gmail.com
- **Job 6** — build the `NW Personal` tree in nicholasernestward@gmail.com
  (empty structure only — Nick populates it himself)
- **Job 8** — from each Gmail account, share the top-level folder with
  nward@ernestperformance.com.au as **Editor**. One share per account at the
  top level, which carries the whole tree including anything added later. Then,
  in the Ernest Performance Drive, add shortcuts to both shared folders at the
  top level so all three projects sit side by side.

## Job 11 — Final report

Finish with:
- The three project trees, printed
- Every share and shortcut created
- Every repo pushed, and its GitHub URL
- **Anything still tied to this MacBook that will not work if it goes offline**
- **Anything you could not complete and why**

Be specific about the last two. Nick is deciding whether to leave the laptop at
the studio based on this.

## Working rules

- Branch: `claude/multi-account-drive-git-audit-eywwlh`. Commit and push there.
- Never open a pull request unless asked.
- Stop at every CHECK IN and wait.
- Jobs 1 and 2 are read-only scans. Report before changing anything.
- If something cannot be done, say so plainly and say why. Do not report a job
  complete when it is partial.
