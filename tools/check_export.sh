#!/usr/bin/env bash
# Export a PCK and run it outside the project directory.
# Asserts the travel map spawns place nodes from packed resources.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-godot}"
OUT="$(mktemp -d)"
cleanup() { rm -rf "$OUT"; }
trap cleanup EXIT

"$GODOT" --headless --path "$ROOT" --export-pack Linux "$OUT/game.pck"

LOG="$OUT/check.log"
set +e
(
	cd "$OUT"
	xvfb-run -a -s "-screen 0 900x1600x24" "$GODOT" --main-pack "$OUT/game.pck" -- --export-check
) | tee "$LOG"
code=${PIPESTATUS[0]}
set -e

nodes="$(sed -n 's/^EXPORT_MAP_NODES //p' "$LOG" | tail -n 1)"
echo "export check exit=$code nodes=${nodes:-missing}"
if [[ "$code" -ne 0 ]]; then
	exit "$code"
fi
if [[ -z "${nodes}" || "$nodes" -le 0 ]]; then
	echo "map spawned ${nodes:-0} nodes" >&2
	exit 1
fi
grep -q "EXPORT_CHECK_OK" "$LOG"

TOUCH_LOG="$OUT/touch.log"
set +e
(
	cd "$OUT"
	xvfb-run -a -s "-screen 0 900x1600x24" "$GODOT" --main-pack "$OUT/game.pck" -- --touch-check
) | tee "$TOUCH_LOG"
touch_code=${PIPESTATUS[0]}
set -e
echo "touch check exit=$touch_code"
if [[ "$touch_code" -ne 0 ]]; then
	exit "$touch_code"
fi
grep -q "TOUCH_CHECK_OK" "$TOUCH_LOG"
