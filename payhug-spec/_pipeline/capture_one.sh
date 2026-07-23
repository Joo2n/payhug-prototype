#!/bin/bash
# 한 화면(상태)을 헤드리스로 캡처. Figma 제출은 capture.js가 수행.
# 사용: capture_one.sh <captureId> <route> <devClickRaw> <figmadelay_ms> <width> <host>
# 예:   capture_one.sh <id> /manage 심사대기 4000 2240 http://localhost:3001
set -u
CID="$1"; ROUTE="$2"; DEVCLICK="${3:-}"; DELAY="${4:-3500}"; WIDTH="${5:-2240}"; HOST="${6:-http://localhost:3001}"; HEIGHT="${7:-1300}"; DEVHOVER="${8:-}"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FE="figmaendpoint=https%3A%2F%2Fmcp.figma.com%2Fmcp%2Fcapture%2F"
SUF="%2Fsubmit%3FbindVariables%3Dtrue"
ENCC=$(node -e 'process.stdout.write(encodeURIComponent(process.argv[1]||""))' -- "$DEVCLICK")
ENCH=$(node -e 'process.stdout.write(encodeURIComponent(process.argv[1]||""))' -- "$DEVHOVER")
Q=""
addp() { local k="$1" v="$2"; [ -z "$v" ] && return; if [ -z "$Q" ]; then case "$ROUTE" in *\?*) Q="&";; *) Q="?";; esac; else Q="${Q}&"; fi; Q="${Q}${k}=${v}"; }
addp devClick "$ENCC"
addp devHover "$ENCH"
URL="${HOST}${ROUTE}${Q}#figmacapture=${CID}&${FE}${CID}${SUF}&figmadelay=${DELAY}"
PROFILE="/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/figprof_${CID}"
rm -rf "$PROFILE" 2>/dev/null
"$CH" --headless=new --disable-gpu --no-first-run --no-default-browser-check \
  --user-data-dir="$PROFILE" --window-size=${WIDTH},${HEIGHT} "$URL" >/dev/null 2>&1 &
PID=$!
SLEEP=$(node -e 'process.stdout.write(String(Math.ceil((+process.argv[1]||3500)/1000)+7))' "$DELAY")
sleep "$SLEEP"
kill "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
rm -rf "$PROFILE" 2>/dev/null
echo "captured route=${ROUTE} devClick='${DEVCLICK}' width=${WIDTH} (slept ${SLEEP}s)"
