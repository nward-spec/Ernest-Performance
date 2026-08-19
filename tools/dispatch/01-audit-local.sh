#!/usr/bin/env bash
# Job 1 — Local audit. Read-only: reports state, changes nothing.
# Usage:  bash 01-audit-local.sh [search-root ...]     (default: $HOME)
# Output: human-readable report on stdout. Tee it to a file to keep it.

shopt -s nullglob
ROOTS=("$@")
[ ${#ROOTS[@]} -eq 0 ] && ROOTS=("$HOME")

rule() { printf '\n%s\n%s\n' "$1" "$(printf '=%.0s' $(seq 1 ${#1}))"; }

# Google Drive for Desktop mount points, in the order Google has used them.
DRIVE_PATHS=(
  "$HOME/Library/CloudStorage"
  "$HOME/Google Drive"
  "/Volumes/GoogleDrive"
)

is_in_drive() {
  local p; p="$(cd "$1" 2>/dev/null && pwd -P)" || return 1
  for d in "${DRIVE_PATHS[@]}"; do
    [ -e "$d" ] || continue
    local rp; rp="$(cd "$d" 2>/dev/null && pwd -P)" || continue
    case "$p" in "$rp"/*|"$rp") return 0 ;; esac
  done
  return 1
}

rule "1. GIT REPOSITORIES"
# -prune stops descent into a repo, so nested vendor checkouts don't spam.
while IFS= read -r gitdir; do
  repo="$(dirname "$gitdir")"
  printf '\n  %s\n' "$repo"

  remote="$(git -C "$repo" remote -v 2>/dev/null | awk '/\(fetch\)/{print $2; exit}')"
  printf '    remote        : %s\n' "${remote:-NONE CONFIGURED}"
  printf '    branch        : %s\n' "$(git -C "$repo" branch --show-current 2>/dev/null || echo '(detached)')"

  dirty="$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$dirty" -gt 0 ]; then
    printf '    uncommitted   : YES (%s files)\n' "$dirty"
    git -C "$repo" status --porcelain 2>/dev/null | head -10 | sed 's/^/                    /'
    [ "$dirty" -gt 10 ] && printf '                    ... and %s more\n' "$((dirty - 10))"
  else
    printf '    uncommitted   : no\n'
  fi

  # Unpushed work is lost if this machine dies, even with a remote set.
  if [ -n "$remote" ]; then
    if git -C "$repo" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
      ahead="$(git -C "$repo" rev-list --count '@{u}..HEAD' 2>/dev/null)"
      [ "${ahead:-0}" -gt 0 ] 2>/dev/null &&
        printf '    unpushed      : %s commits ahead of upstream\n' "$ahead"
    else
      printf '    unpushed      : NO UPSTREAM TRACKING — this branch has never\n'
      printf '                    been pushed. All of its work is local-only.\n'
    fi
  fi

  if is_in_drive "$repo"; then
    printf '    >> WARNING    : INSIDE GOOGLE DRIVE SYNC PATH — move to a local path.\n'
    printf '                    Drive syncing .git internals corrupts repos.\n'
  fi
done < <(find "${ROOTS[@]}" -type d -name .git -not -path '*/node_modules/*' -prune -print 2>/dev/null)

rule "2. GOOGLE DRIVE FOR DESKTOP"
if [ -d "/Applications/Google Drive.app" ]; then
  ver="$(defaults read "/Applications/Google Drive.app/Contents/Info" CFBundleShortVersionString 2>/dev/null)"
  printf '  installed     : YES (version %s)\n' "${ver:-unknown}"
else
  printf '  installed     : NO\n'
fi

if pgrep -qx "Google Drive" 2>/dev/null; then
  printf '  running       : YES\n'
else
  printf '  running       : no\n'
fi

# Each signed-in account gets a CloudStorage mount named for its address.
printf '  accounts / mounts:\n'
found=0
for m in "$HOME/Library/CloudStorage"/GoogleDrive-*; do
  printf '    %s\n' "$(basename "$m")"; found=1
done
[ $found -eq 0 ] && printf '    (none found under ~/Library/CloudStorage)\n'

# "My Drive" as a real directory inside the mount means mirroring; streaming
# exposes it only through the virtual filesystem.
printf '  mode          : '
if [ -d "$HOME/Library/CloudStorage" ] && [ $found -eq 1 ]; then
  if compgen -G "$HOME/Library/CloudStorage/GoogleDrive-*/My Drive" >/dev/null 2>&1; then
    printf 'STREAMING or MIRRORING (My Drive present — confirm in Drive > Settings)\n'
  else
    printf 'mount present, My Drive not visible — likely STREAMING\n'
  fi
else
  printf 'n/a\n'
fi

rule "3. CLAUDE CODE / CLAUDE DESKTOP CONFIG"
printf '  ~/.claude exists     : %s\n' "$([ -d "$HOME/.claude" ] && echo yes || echo no)"
printf '  ~/.claude.json exists: %s\n' "$([ -f "$HOME/.claude.json" ] && echo yes || echo no)"

if [ -f "$HOME/.claude.json" ]; then
  printf '  project directories Claude Code has been used in:\n'
  /usr/bin/python3 - "$HOME/.claude.json" <<'PY'
import json, sys
try:
    with open(sys.argv[1]) as fh:
        cfg = json.load(fh)
except Exception as exc:
    print(f"    (could not parse: {exc})"); sys.exit()
projects = cfg.get("projects", {})
if not projects:
    print("    (none)")
for path, meta in projects.items():
    extra = meta.get("additionalDirectories") or []
    print(f"    {path}")
    if extra:
        print(f"        + additional dirs: {extra}")
PY
fi

for f in "$HOME/.claude/settings.json" "$HOME/.claude/settings.local.json"; do
  [ -f "$f" ] && { printf '  --- %s ---\n' "$f"; sed 's/^/    /' "$f"; }
done

if [ -d "/Applications/Claude.app" ]; then
  printf '  Claude Desktop       : %s\n' \
    "$(defaults read /Applications/Claude.app/Contents/Info CFBundleShortVersionString 2>/dev/null || echo unknown)"
else
  printf '  Claude Desktop       : not installed in /Applications\n'
fi

rule "4. POWER SETTINGS (Job 10 baseline — read-only)"
pmset -g custom 2>/dev/null | sed 's/^/  /' || printf '  (pmset unavailable)\n'
printf '\n  Currently preventing sleep:\n'
pmset -g assertions 2>/dev/null | grep -E 'PreventUserIdleSystemSleep|PreventUserIdleDisplaySleep' | sed 's/^/    /'

rule "AUDIT COMPLETE"
printf 'Nothing was modified. Review section 1 for repos flagged INSIDE GOOGLE DRIVE.\n\n'
