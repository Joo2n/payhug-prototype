#!/bin/bash
# 회원관리 TO-BE 목업을 헤드리스로 열어 capture.js가 Figma로 전송하게 함.
# 사용: figcap_mock.sh <mock_name(확장자 제외)> <captureId> [viewportHeight(기본 1600)]   (서버: http.server 8901 --directory mockups_fig)
# 주의: macOS 헤드리스 Chrome은 --window-size 보다 실제 뷰포트가 87px 낮다.
#       폭 1922 기준 1280·1367·1600·1687 네 지점에서 편차 87px 고정을 실측했다.
#       (실측표: investor_admin/figma_import_result.md §5-2)
#       보정하지 않으면 position:fixed 요소가 프레임 바닥에서 87px 떠서 임포트된다.
PAGE="$1"; CID="$2"; VH="${3:-1600}"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
EP="https%3A%2F%2Fmcp.figma.com%2Fmcp%2Fcapture%2F${CID}%2Fsubmit%3FbindVariables%3Dtrue"
URL="http://localhost:8901/${PAGE}.html#figmacapture=${CID}&figmaendpoint=${EP}&figmadelay=1200"
PROF="/private/tmp/claude-501/-Users-semi-cursor-payhug/1ac085d1-d765-4e8c-98f1-012bcafd2c37/scratchpad/_fc_${CID}"
rm -rf "$PROF" 2>/dev/null
"$CH" --headless=new --disable-gpu --no-first-run --no-default-browser-check --hide-scrollbars \
  --user-data-dir="$PROF" --window-size=1922,$((VH+87)) "$URL" >/dev/null 2>&1 &
PID=$!
S=$SECONDS; until [ $((SECONDS-S)) -ge 16 ]; do sleep 2; done
kill -9 "$PID" 2>/dev/null
rm -rf "$PROF" 2>/dev/null
echo "captured ${PAGE} (cid ${CID}, vh ${VH})"
