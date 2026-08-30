#!/bin/bash
# 투자자 어드민 스테이징 사본(_fig)을 헤드리스로 열어 capture.js가 Figma로 전송하게 함.
# 사용: figcap_ia.sh <file(확장자 제외)> <captureId> <viewportHeight> [figmadelay]
#
# 주의 1 — --window-size 는 macOS 헤드리스에서 실제 뷰포트보다 87px 크다(3점 실측 재확인
#          2026-08-28: 1601→1514 · 590→503 · 717→630). 87을 더해 보정한다.
#          --screenshot 플래그를 붙이면 이 편차가 사라지므로 점검 시 오판 주의.
# 주의 2 — 모노 폰트는 구글폰트 CDN에서 받는다(prep_fig.py 가 링크를 주입). 로드 전에
#          캡처하면 Menlo 로 대체 측정되어 숫자 셀이 말줄임된다. figmadelay 기본값을
#          2500으로 잡아 여유를 둔다. 배치 직전 prep_fig.py fontgate 로 확인할 것.
PAGE="$1"; CID="$2"; VH="${3:-1000}"; DELAY="${4:-2500}"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
EP="https%3A%2F%2Fmcp.figma.com%2Fmcp%2Fcapture%2F${CID}%2Fsubmit%3FbindVariables%3Dtrue"
URL="http://localhost:8903/${PAGE}.html#figmacapture=${CID}&figmaendpoint=${EP}&figmadelay=${DELAY}"
PROF="/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/_fc_${CID}"
rm -rf "$PROF" 2>/dev/null
"$CH" --headless=new --disable-gpu --no-first-run --no-default-browser-check --hide-scrollbars --lang=ko-KR \
  --user-data-dir="$PROF" --window-size=1440,$((VH+87)) "$URL" >/dev/null 2>&1 &
PID=$!
WAIT=$(( DELAY/1000 + 16 ))
S=$SECONDS; until [ $((SECONDS-S)) -ge $WAIT ]; do sleep 2; done
kill -9 "$PID" 2>/dev/null
rm -rf "$PROF" 2>/dev/null
echo "captured ${PAGE} (cid ${CID}, vh ${VH}, delay ${DELAY})"
