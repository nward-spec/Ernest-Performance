#!/usr/bin/env bash
# Job 10 — Keep this MacBook awake as the Dispatch engine.
# Applies AC-power settings, then re-reads them to prove they held.
# Battery settings are left ALONE: unplugged, the machine still sleeps.
#
# Usage:  bash 10-dispatch-power.sh          (show current, then apply)
#         bash 10-dispatch-power.sh --check  (show current only)

set -u

show() {
  printf '\n--- Current AC ("Wall Adapter") settings ---\n'
  # pmset prints AC and battery blocks; take AC through to the next header.
  pmset -g custom 2>/dev/null | awk '/AC Power/{f=1} /Battery Power/{f=0} f' | sed 's/^/  /'
}

verify() {
  local block ok=1
  block="$(pmset -g custom 2>/dev/null | awk '/AC Power/{f=1} /Battery Power/{f=0} f')"
  for k in sleep displaysleep disksleep; do
    v="$(printf '%s\n' "$block" | awk -v k="$k" '$1==k{print $2; exit}')"
    if [ "${v:-x}" = "0" ]; then
      printf '  %-13s = 0   OK (never)\n' "$k"
    else
      printf '  %-13s = %s   NOT APPLIED\n' "$k" "${v:-unset}"; ok=0
    fi
  done
  return $ok
}

if [ "${1:-}" = "--check" ]; then
  show; printf '\n--- Verification ---\n'; verify; exit 0
fi

show

printf '\n--- Applying (sudo required) ---\n'
# -c targets AC power only. 0 means never.
sudo pmset -c displaysleep 0 || { echo "  FAILED: displaysleep" >&2; exit 1; }
sudo pmset -c sleep 0        || { echo "  FAILED: sleep" >&2; exit 1; }
sudo pmset -c disksleep 0    || { echo "  FAILED: disksleep" >&2; exit 1; }
printf '  applied.\n'

printf '\n--- Verification (re-read from the system) ---\n'
if verify; then
  printf '\nAll three held. On the adapter with the lid open this machine\n'
  printf 'will stay awake and reachable.\n'
else
  printf '\nAt least one setting did not stick. Check for a configuration\n'
  printf 'profile or MDM policy overriding Energy Saver.\n'; exit 1
fi

printf '\n--- Anything currently holding sleep off ---\n'
pmset -g assertions 2>/dev/null | grep -E 'PreventUserIdle' | sed 's/^/  /'

printf '\nNOTE: closing the lid still sleeps the machine unless an external\n'
printf 'display and power are attached. Leave the lid open.\n\n'
