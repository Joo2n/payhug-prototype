#!/bin/zsh
# 헤드리스 크롬으로 각 URL DOM을 덤프해 마커 텍스트를 확인한다.
# 이 맥(macOS 26 + Chrome 151)에서는 --dump-dom 완료 후에도 크롬이 종료되지 않으므로,
# 백그라운드로 띄우고 출력 파일 끝의 </html>을 폴링한 뒤 직접 kill 한다.
SC=/private/tmp/claude-501/-Users-semi-cursor-payhug/d845932c-7f84-4039-9996-117da0987331/scratchpad
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=$SC/discovery/dom
mkdir -p "$OUT"

dump() { # $1=name $2=url
  local name=$1 url=$2
  local profile="$SC/chrome-prof-$name"
  rm -rf "$profile"
  "$CHROME" --headless=new --disable-gpu --no-sandbox --no-first-run \
    --user-data-dir="$profile" --window-size=1574,1600 --virtual-time-budget=10000 \
    --dump-dom "$url" > "$OUT/$name.html" 2>"$OUT/$name.err" &
  local pid=$!
  local waited=0
  while (( waited < 60 )); do
    sleep 2; waited=$((waited+2))
    if [[ -s "$OUT/$name.html" ]] && tail -c 200 "$OUT/$name.html" | grep -q '</html>'; then
      break
    fi
    kill -0 $pid 2>/dev/null || break
  done
  pkill -9 -f "chrome-prof-$name" 2>/dev/null
  rm -rf "$profile"
  echo "[dumped] $name ($(wc -c < "$OUT/$name.html" | tr -d ' ') bytes, ${waited}s)"
}

check() { # $1=name $2=marker
  if grep -q "$2" "$OUT/$1.html"; then echo "  PASS: '$2'"; else echo "  FAIL: '$2' not found"; fi
}

check_absent() { # $1=name $2=marker
  if grep -q "$2" "$OUT/$1.html"; then echo "  FAIL: '$2' visible (admin 전용인데 노출)"; else echo "  PASS: '$2' absent"; fi
}

dump admin_home_partner "http://localhost:3001/?__devuser=PARTNER"
check admin_home_partner "소속 가맹점"

dump admin_home_admin "http://localhost:3001/?__devuser=ADMIN"
check admin_home_admin "총 가맹점"

dump admin_overview_partner "http://localhost:3001/settlement/overview?__devuser=PARTNER"
# 탭은 버튼 단위로 확인 — "정산 상세"는 부제 문구에, "계산서 발행"은 카드 캡션에도 등장(오탐 방지)
check admin_overview_partner ">선정산 결과</button>"
check admin_overview_partner ">차액 정산</button>"
check admin_overview_partner ">이체 내역</button>"
check_absent admin_overview_partner ">정산 상세</button>"
check_absent admin_overview_partner ">계산서 발행</button>"
check_absent admin_overview_partner ">VOC 대응</button>"

dump admin_merchant_partner "http://localhost:3001/merchants/101?__devuser=PARTNER"
check admin_merchant_partner "김성호떡볶이 본점"
check admin_merchant_partner "테헤란로"   # 가맹점 상세 고유 값(주소) — 홈 TOP5 오탐 방지
python3 - <<'PY'
import re
h = open("/private/tmp/claude-501/-Users-semi-cursor-payhug/d845932c-7f84-4039-9996-117da0987331/scratchpad/discovery/dom/admin_merchant_partner.html").read()
tags = re.findall(r'<button[^>]*title="수정"[^>]*>', h)
bad = [t for t in tags if "hidden" not in t]
if not tags:
    print("  WARN: title=수정 버튼 자체가 DOM에 없음 (렌더 확인 필요)")
elif bad:
    print(f"  FAIL: readOnly 아님 — 수정 버튼 {len(bad)}/{len(tags)}개 노출")
else:
    print(f"  PASS: readOnly — 수정 버튼 {len(tags)}개 모두 hidden")
PY

dump admin_pv_contract_reset "http://localhost:3001/__preview/contract-reset"
check admin_pv_contract_reset "계약 프로세스 초기화"
check admin_pv_contract_reset "전체 데이터 삭제 경고"

dump admin_pv_business_edit "http://localhost:3001/__preview/business-edit"
check admin_pv_business_edit "사업자 정보"      # 헤더 "사업자 정보 수정" (JSX 보간으로 텍스트 노드 분리됨)
check admin_pv_business_edit "재업로드 (선택"   # 기존 등록건 수정 모드 확인
check admin_pv_business_edit "김성호떡볶이 본점"

dump admin_pv_manual_sales "http://localhost:3001/__preview/manual-sales-result"
check admin_pv_manual_sales "업로드 완료 (일부 실패)"
check admin_pv_manual_sales "이미 매입취소 (되돌림 방지)"

dump mc_pv_sign_gate "http://localhost:3000/__preview/sign-gate"
check mc_pv_sign_gate "매출 연동을 먼저 완료해주세요"

dump mc_pv_biz_typefix "http://localhost:3000/__preview/biz-typefix"
check mc_pv_biz_typefix "사업자 유형 확인"

dump mc_delivery "http://localhost:3000/settlement/delivery?bizNo=1234567890&source=BM&__devuser=1"
check mc_delivery "환급액"
check mc_delivery "+12,000원"
check mc_delivery "배달의 민족 환급액"
check mc_delivery "미리 받는 돈"

# ── 추가 2건: 미승인 대시보드 (예상 선정산액) / 매출 조회 카드 펼침 ──
check_f() { # fixed-string check (클래스명 대괄호 등)
  if grep -qF "$2" "$OUT/$1.html"; then echo "  PASS(f): '$2'"; else echo "  FAIL(f): '$2' not found"; fi
}
check_f_absent() {
  if grep -qF "$2" "$OUT/$1.html"; then echo "  FAIL(f): '$2' visible"; else echo "  PASS(f): '$2' absent"; fi
}

dump mc_dash_unapproved "http://localhost:3000/dashboard?__devuser=1&__devstate=unapproved&__inquired=2150000"
check mc_dash_unapproved "미리 받을 수 있는 금액"
check mc_dash_unapproved ">예상</span>"
check mc_dash_unapproved "1,998,300"
check mc_dash_unapproved "어제 매출액(2,150,000원)에서"
check mc_dash_unapproved "조회된 어제 매출액"
check mc_dash_unapproved ">계약진행</span>"
check_f_absent mc_dash_unapproved "max-h-[3000px]"

dump mc_dash_inquiry_open "http://localhost:3000/dashboard?__devuser=1&__devstate=unapproved&__open=inquiry&__inquired=2150000"
check_f mc_dash_inquiry_open "max-h-[3000px] opacity-100"
check mc_dash_inquiry_open "배달앱 또는 카드 매출이 있으신가요?"
check mc_dash_inquiry_open "카드 매출 조회"
check mc_dash_inquiry_open "여신금융협회 바로가기"
check mc_dash_inquiry_open "배달앱 계정"
check_f mc_dash_inquiry_open 'placeholder="사장님 아이디"'
check_f mc_dash_inquiry_open 'placeholder="비밀번호"'
check mc_dash_inquiry_open ">조회</button>"
check mc_dash_inquiry_open ">예상</span>"
