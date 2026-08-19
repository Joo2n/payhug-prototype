#!/bin/bash
# 프로토타입 상태를 헤드리스로 열어 capture.js가 Figma로 전송하게 함.
# 사용: figcap_state.sh <state_id> <captureId>   (서버: http.server 8902 --directory proto_fig)
ST="$1"; CID="$2"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
EP="https%3A%2F%2Fmcp.figma.com%2Fmcp%2Fcapture%2F${CID}%2Fsubmit%3FbindVariables%3Dtrue"
URL="http://localhost:8902/index.html?state=${ST}#figmacapture=${CID}&figmaendpoint=${EP}&figmadelay=1800"
PROF="/private/tmp/claude-501/-Users-semi-cursor-payhug/1ac085d1-d765-4e8c-98f1-012bcafd2c37/scratchpad/_fcs_${CID}"
rm -rf "$PROF" 2>/dev/null
"$CH" --headless=new --disable-gpu --no-first-run --no-default-browser-check --hide-scrollbars \
  --user-data-dir="$PROF" --window-size=1922,1600 "$URL" >/dev/null 2>&1 &
PID=$!
S=$SECONDS; until [ $((SECONDS-S)) -ge 18 ]; do sleep 2; done
kill -9 "$PID" 2>/dev/null
rm -rf "$PROF" 2>/dev/null
echo "captured state=${ST} (cid ${CID})"
