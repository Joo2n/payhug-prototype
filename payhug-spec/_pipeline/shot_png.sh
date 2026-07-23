#!/bin/bash
# 로컬 화면을 헤드리스로 PNG 저장 (Figma 제출 아님).
# 사용: shot_png.sh <out.png> <route> <devClick> <delay_ms> <width> <host> <height> <devHover>
set -u
OUT="$1"; ROUTE="$2"; DEVCLICK="${3:-}"; DELAY="${4:-6500}"; W="${5:-2240}"; HOST="${6:-http://localhost:3001}"; H="${7:-1500}"; DEVHOVER="${8:-}"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
enc(){ node -e 'process.stdout.write(encodeURIComponent(process.argv[1]||""))' -- "$1"; }
ENCC=$(enc "$DEVCLICK"); ENCH=$(enc "$DEVHOVER")
Q=""
if [ -n "$ENCC" ] || [ -n "$ENCH" ]; then
  case "$ROUTE" in *\?*) SEP="&";; *) SEP="?";; esac
  P=""
  [ -n "$ENCC" ] && P="devClick=$ENCC"
  [ -n "$ENCH" ] && { [ -n "$P" ] && P="$P&"; P="${P}devHover=$ENCH"; }
  Q="$SEP$P"
fi
URL="${HOST}${ROUTE}${Q}"
PROF="/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/shotprof_$$_$(basename "$OUT" .png)"
rm -rf "$PROF" 2>/dev/null
"$CH" --headless=new --disable-gpu --no-first-run --no-default-browser-check --hide-scrollbars \
  --user-data-dir="$PROF" --window-size=${W},${H} --virtual-time-budget=${DELAY} --screenshot="$OUT" "$URL" >/dev/null 2>&1 &
PID=$!
SLEEP=$(node -e 'process.stdout.write(String(Math.ceil((+process.argv[1]||6500)/1000)+4))' "$DELAY")
sleep "$SLEEP"
kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null
rm -rf "$PROF" 2>/dev/null
if [ -f "$OUT" ]; then echo "OK $(basename "$OUT") $(du -h "$OUT" | cut -f1)"; else echo "FAIL $OUT"; fi
