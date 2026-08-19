# Dispatch toolkit

Scripts for auditing and preparing the studio MacBook as the Dispatch engine.

**These must run on the MacBook itself.** Claude Code sessions started from
the Claude Desktop app run in an Anthropic cloud container (`environment_kind:
anthropic_cloud`) with only this repo cloned into it — no access to the Mac's
filesystem. To run them, open **Terminal on the MacBook**:

```bash
cd ~/Ernest-Performance          # wherever this repo is cloned
claude                           # optional: Claude Code CLI, runs locally
```

Or run the scripts directly. Jobs 1 and 2 are read-only.

| Script | Job | Writes? |
|---|---|---|
| `01-audit-local.sh` | 1 — repo, Drive, config, power audit | no |
| `02-scan-secrets.sh` | 2 — credential scan, tree + history | no |
| `10-dispatch-power.sh` | 10 — keep-awake settings | yes (sudo) |
| `gitignore.template` | 2 — .gitignore for the pipeline repos | — |
| `env.example.template` | 2 — .env.example placeholders | — |

## Job 1 — audit

```bash
bash tools/dispatch/01-audit-local.sh | tee ~/Desktop/audit-$(date +%F).txt
```

Searches `$HOME` by default; pass paths to narrow or widen it. Reports every
git repo with its remote, uncommitted changes, and unpushed commits, and flags
any repo inside a Google Drive sync path.

**Repos inside Drive must be moved to a local path.** Drive syncs `.git`
internals as ordinary files; concurrent writes during a sync corrupt the
object store. Move with the repo closed and Drive paused:

```bash
mv "~/Library/CloudStorage/GoogleDrive-.../My Drive/some-repo" ~/Code/some-repo
git -C ~/Code/some-repo fsck          # verify nothing was already damaged
```

## Job 2 — credential audit

```bash
bash tools/dispatch/02-scan-secrets.sh ~/Code/bill-automation ~/Code/amortisation
```

Matches are redacted to a 4-character prefix, so the output is safe to paste
back into a chat. Add `SKIP_HISTORY=1` to scan the working tree only.

Sections **D** and **E** cover git history. A secret committed months ago and
deleted since is still in the history and still leaked — for anything found
there, **rotate the credential**; removing the file is not enough. Then:

```bash
cp tools/dispatch/gitignore.template   <repo>/.gitignore
cp tools/dispatch/env.example.template <repo>/.env.example
```

Move real values into `.env` (gitignored) and rewrite history with
`git filter-repo` before the first push. This is the gate before Job 3.

## Job 10 — keep the machine awake

```bash
bash tools/dispatch/10-dispatch-power.sh --check   # inspect
bash tools/dispatch/10-dispatch-power.sh           # apply (sudo)
```

Sets `displaysleep`, `sleep` and `disksleep` to never **on AC power only** —
on battery the machine still sleeps. Re-reads the values afterwards and fails
loudly if a configuration profile overrode them.

Closing the lid still sleeps the machine. Leave it open.
