#!/bin/bash
# 투자자 어드민 Figma 갱신 — 실행 스크립트.
# 동결 신호가 오면 preflight 부터 순서대로. 쓰기 단계(6~10)는 MCP 도구라 여기서 안 돈다.
#
#   run_import_0828.sh preflight        0~5단계. 로컬에서 끝나는 전량
#   run_import_0828.sh serve            8903 캡처 서버 기동(_fig 루트). 캡처 내내 떠 있어야 함
#   run_import_0828.sh cap <file> <cid> 단건 캡처. vh 는 fig_heights.json 에서 자동
#   run_import_0828.sh plan             쓰기 단계 체크리스트 출력
#   run_import_0828.sh stop             서버 종료
set -u
D="$(cd "$(dirname "$0")" && pwd)"
SRC=/Users/semi/cursor/payhug-investor-admin
cd "$D"

case "${1:-plan}" in

preflight)
  echo "── 0. 동결 지점"
  git -C "$SRC" rev-parse --short HEAD
  N=$(git -C "$SRC" status --porcelain | grep -cE '\.(html|css|js)$' || true)
  echo "   워킹트리 html/css/js 변경 $N건"
  [ "$N" -gt 0 ] && echo "   경고 — 미커밋 변경이 있다. 동결 신호를 받은 상태인지 확인할 것"
  echo
  echo "── 1. Figma 폰트 목록 확인 (수동)"
  echo "   listAvailableFontsAsync() 로 'Roboto Mono' 존재 확인. 없으면 여기서 중단하고 보고"
  echo
  echo "── 2~3. 스테이징 동기화 + CSS 패치"
  python3 prep_fig.py sync || exit 1
  echo
  echo "── 4. value 필드 기하 측정 + 치환"
  python3 prep_fig.py measure || exit 1
  python3 prep_fig.py apply || exit 1
  echo
  echo "── 4b. 스테이징 검증"
  python3 prep_fig.py verify || exit 1
  echo
  echo "── 4c. 폰트 게이트"
  python3 prep_fig.py fontgate || { echo "폰트 미로드 — 캡처 금지"; exit 1; }
  echo
  echo "── 5. 프레임 높이 산출"
  python3 prep_fig.py heights || exit 1
  echo
  echo "── 5b. op 목록 생성"
  python3 build_ops.py || exit 1
  echo
  echo "preflight 통과. 다음: run_import_0828.sh serve → 쓰기 단계(plan 참조)"
  ;;

serve)
  pkill -f "http.server 8903" 2>/dev/null
  sleep 1
  cd "$D/_fig" && nohup python3 -m http.server 8903 >/tmp/figcap_srv.log 2>&1 &
  sleep 2
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8903/invest-assets.html)
  echo "8903 서버 (_fig 루트) status=$code"
  [ "$code" = "200" ] || { echo "기동 실패"; exit 1; }
  ;;

cap)
  F="${2:?파일명}"; CID="${3:?captureId}"
  VH=$(python3 -c "import json,sys;print(json.load(open('$D/fig_heights.json'))['$F']['vh'])") || exit 1
  echo "캡처 $F vh=$VH"
  "$D/figcap_ia.sh" "$F" "$CID" "$VH"
  ;;

plan)
  cat <<'TXT'
쓰기 단계 — MCP 도구로 수행. figma_ops_0828.json 이 대상 목록.

 6. Figma 현재 선택 해제. 잔여 8프레임(delete_orphans, x=-6797) 삭제
    선택이 3189:15662 Sidebar 안에 있던 이력이 있어 해제부터 한다
 7. 폐기 1건 삭제 — 3216:2 (04-a 쿠콘 이동 확인)
 8. 교체 23건 캡처·임포트 — 3건 이하 청크. serve 를 띄운 채로
      run_import_0828.sh cap <file> <captureId>
 9. 신규 1건 임포트 — acquisition--doc → (4800, 13065)
10. 구 노드 23건 삭제 (replace[].old_node_id)
11. 검사 — 클립 이탈 0 · textTruncation:ENDING 0 · hasMissingFont 0 · 프레임 폭 1440 전건
12. figma_map_investor.json 갱신 + 결과서 작성

보류 8건은 손대지 않는다 — 투자 수익 4(03·03-a·03-b·03-c) · 비밀번호 4
TXT
  ;;

stop)
  pkill -f "http.server 8903" 2>/dev/null && echo "8903 종료" || echo "떠 있지 않음"
  ;;

*) echo "preflight | serve | cap <file> <cid> | plan | stop"; exit 1;;
esac
