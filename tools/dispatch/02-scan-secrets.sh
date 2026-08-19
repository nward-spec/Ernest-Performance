#!/usr/bin/env bash
# Job 2 — Credential audit. Read-only: finds secrets, changes nothing.
# Usage:  bash 02-scan-secrets.sh /path/to/repo [/path/to/repo ...]
#         SKIP_HISTORY=1 bash 02-scan-secrets.sh ...   (working tree only, faster)
#
# Matches are REDACTED — you get file, line and a 4-char prefix, never the
# secret itself, so the report is safe to paste back into a chat.

REPOS=("$@")
if [ ${#REPOS[@]} -eq 0 ]; then
  echo "usage: bash 02-scan-secrets.sh <repo-path> [repo-path ...]" >&2
  exit 2
fi

# Content patterns. Google OAuth, Xero, and generic key material.
PATTERNS='(client_secret|client_id|refresh_token|access_token|api[_-]?key|apikey|secret[_-]?key|password|passwd|auth[_-]?token|bearer [A-Za-z0-9._-]{20,})'
PATTERNS+='|AIza[0-9A-Za-z_-]{35}'
PATTERNS+='|ya29\.[0-9A-Za-z_-]+'
PATTERNS+='|[0-9]+-[0-9a-z]{32}\.apps\.googleusercontent\.com'
PATTERNS+='|XERO_[A-Z_]+'
PATTERNS+='|-----BEGIN [A-Z ]*PRIVATE KEY-----'
PATTERNS+='|AKIA[0-9A-Z]{16}'
PATTERNS+='|gh[pousr]_[A-Za-z0-9]{36}'

# Filenames that are secrets by nature, regardless of content.
FILE_PATTERNS='(^|/)(\.env(\..*)?|token\.json|tokens\.json|credentials\.json|client_secret.*\.json|service[_-]account.*\.json|.*\.pem|.*\.p12|.*\.pfx|.*\.key)$'
# Local stores that must never be committed (the SQLite idempotency store).
DB_PATTERNS='(^|/).*\.(sqlite3?|db)$'

redact() {
  # Keep enough to identify the finding, not enough to use it.
  sed -E 's/([A-Za-z0-9_\-]{4})[A-Za-z0-9_\/+=\.\-]{8,}/\1<REDACTED>/g'
}

for REPO in "${REPOS[@]}"; do
  if [ ! -d "$REPO/.git" ]; then
    printf '\n!! %s is not a git repository — skipping\n' "$REPO"; continue
  fi

  printf '\n\n########################################################\n'
  printf '# %s\n' "$REPO"
  printf '########################################################\n'

  printf '\n--- A. Tracked files whose NAME indicates a secret ---\n'
  hits="$(git -C "$REPO" ls-files | grep -iE "$FILE_PATTERNS")"
  if [ -n "$hits" ]; then
    printf '%s\n' "$hits" | sed 's/^/  COMMITTED: /'
    printf '  >> These are tracked in git. They need removing from history.\n'
  else
    printf '  none tracked\n'
  fi

  printf '\n--- B. Tracked local databases ---\n'
  hits="$(git -C "$REPO" ls-files | grep -iE "$DB_PATTERNS")"
  [ -n "$hits" ] && printf '%s\n' "$hits" | sed 's/^/  COMMITTED: /' || printf '  none tracked\n'

  printf '\n--- C. Secret-shaped content in the WORKING TREE ---\n'
  found=$(git -C "$REPO" grep -I -n -iE "$PATTERNS" -- \
      ':!*.lock' ':!package-lock.json' ':!*.min.js' 2>/dev/null | head -40)
  if [ -n "$found" ]; then
    printf '%s\n' "$found" | redact | sed 's/^/  /'
  else
    printf '  no matches\n'
  fi

  printf '\n--- D. Files with secret NAMES ever added in HISTORY ---\n'
  printf '    (deleted since still counts — the blob is still in the repo)\n'
  hist="$(git -C "$REPO" log --all --diff-filter=A --name-only --pretty=format: 2>/dev/null \
          | sort -u | grep -iE "$FILE_PATTERNS")"
  if [ -n "$hist" ]; then
    printf '%s\n' "$hist" | sed 's/^/  IN HISTORY: /'
    printf '  >> Rewrite history (git filter-repo) AND rotate these credentials.\n'
  else
    printf '  none\n'
  fi

  if [ "${SKIP_HISTORY:-0}" = "1" ]; then
    printf '\n--- E. History content scan: SKIPPED (SKIP_HISTORY=1) ---\n'
  else
    printf '\n--- E. Secret-shaped content in HISTORY ---\n'
    commits="$(git -C "$REPO" rev-list --all 2>/dev/null | wc -l | tr -d ' ')"
    printf '    scanning %s commits...\n' "$commits"
    ghits="$(git -C "$REPO" grep -I -n -iE "$PATTERNS" $(git -C "$REPO" rev-list --all) \
             -- ':!*.lock' ':!package-lock.json' 2>/dev/null | head -40)"
    if [ -n "$ghits" ]; then
      printf '%s\n' "$ghits" | redact | sed 's/^/  /'
      printf '  >> Present in history. Rotate anything real that appears here.\n'
    else
      printf '  no matches\n'
    fi
  fi

  printf '\n--- F. .gitignore status ---\n'
  if [ -f "$REPO/.gitignore" ]; then
    for need in '.env' 'token' 'credentials' '*.sqlite' '*.db'; do
      grep -qF -- "$need" "$REPO/.gitignore" && printf '  covers %-14s yes\n' "$need:" \
                                             || printf '  covers %-14s NO\n'  "$need:"
    done
  else
    printf '  NO .gitignore — install the template alongside this script.\n'
  fi
done

printf '\n\nSCAN COMPLETE. Nothing was modified.\n'
printf 'Anything under D or E means the credential is compromised: rotate it,\n'
printf 'do not just delete the file.\n\n'
