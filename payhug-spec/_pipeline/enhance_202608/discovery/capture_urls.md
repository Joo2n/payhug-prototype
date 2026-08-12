# 화면설계서 보강 — 캡처 URL 목록 (검증 완료)

최신 develop 코드(run-admin 9e2741b / run-merchant e083af8)를 목데이터로 렌더하는 로컬 환경.
모든 URL은 헤드리스 크롬 DOM 덤프로 마커 텍스트 검증 통과 (2026-08-12, `discovery/verify_urls.sh`, 덤프본 `discovery/dom/*.html`).

## 서버

| 앱 | 포트 | 기동 명령 (MOCK_API 필수) | 로그 |
|---|---|---|---|
| 어드민 | 3001 | `cd scratchpad/run-admin && MOCK_API=1 nohup npm run dev` | `scratchpad/npm_run_admin.log` |
| 가맹점 | 3000 | `cd scratchpad/run-merchant && MOCK_API=1 nohup npm run dev` | `scratchpad/npm_run_merchant.log` |

현재 두 서버 모두 기동 중.

## 검증 통과 URL (11)

| # | 화면 | URL | 기대 마커 | 비고 |
|---|---|---|---|---|
| 1 | 어드민 총판 홈 | `http://localhost:3001/?__devuser=PARTNER` | "소속 가맹점" | PARTNER 시드 → participantNavGroups(가맹점/정산/관리)만 노출 |
| 2 | 어드민 관리자 홈 | `http://localhost:3001/?__devuser=ADMIN` | "총 가맹점" | ADMIN 시드 사니티 체크용 |
| 3 | 정산 현황 (총판) | `http://localhost:3001/settlement/overview?__devuser=PARTNER` | 탭 버튼 3개: 선정산 결과·차액 정산·이체 내역 | admin 전용 탭(정산 상세·계산서 발행·VOC 대응) 버튼 비노출 확인. 선정산 결과 탭 일별 표 7개 × 가맹점 6행 렌더 |
| 4 | 가맹점 상세 (총판 readOnly) | `http://localhost:3001/merchants/101?__devuser=PARTNER` | "김성호떡볶이 본점" + "테헤란로"(상세 고유 주소) | title="수정" 버튼 2개 모두 `hidden` 클래스 → readOnly 확인 |
| 5 | 계약 프로세스 초기화 모달 | `http://localhost:3001/__preview/contract-reset` | "계약 프로세스 초기화" / "전체 데이터 삭제 경고" | merchants/[id] 인라인 JSX 사본, 흰 배경 |
| 6 | 사업자 정보 수정 모달 | `http://localhost:3001/__preview/business-edit` | "사업자 정보"+"수정"(JSX 보간으로 텍스트 분리) / "재업로드 (선택" | 실제 BusinessEditModal import, 개인사업자 픽스처(김성호떡볶이) |
| 7 | 수기매출 결과 요약 모달 | `http://localhost:3001/__preview/manual-sales-result` | "업로드 완료 (일부 실패)" / "이미 매입취소 (되돌림 방지)" | 실제 ManualSalesResultSummary + ExcelUploadModal 크롬 사본. DELIVERY 픽스처: 성공19/중복3/실패2 + 기타(취소참조·선정산보호·매입취소스킵·미처리취소) + 경고 1건 |
| 8 | 매출 연동 게이트 모달 | `http://localhost:3000/__preview/sign-gate` | "매출 연동을 먼저 완료해주세요" | contract/terms의 CommonModal 동일 props, 흰 배경 |
| 9 | 사업자 유형 확인 모달 | `http://localhost:3000/__preview/biz-typefix` | "사업자 유형 확인" | upload-business의 자동 교정 CommonModal, 개인사업자 분기 |
| 10 | 배달 정산 상세 (환급액 그룹) | `http://localhost:3000/settlement/delivery?bizNo=1234567890&source=BM&__devuser=1` | "환급액" "+12,000원" / "배달의 민족 환급액" / "미리 받는 돈" | 환급액 그룹+하위 행 양수 렌더. 산식 정합: 428,000−88,700+12,000=351,300 |
| 11 | (참고) 배달 주문 단건 | `http://localhost:3000/settlement/delivery/order?bizNo=1234567890&id=90611&__devuser=1` | — | 목 존재, 마커 검증은 안 함 |
| 12 | 미승인(계약 전) 대시보드 | `http://localhost:3000/dashboard?__devuser=1&__devstate=unapproved&__inquired=2150000` | "미리 받을 수 있는 금액" / '예상' 배지(`>예상</span>`) / "1,998,300"(원장 기준 예상 선정산액) / "어제 매출액(2,150,000원)에서" / "조회된 어제 매출액" + 2,150,000원 / 배지 "계약진행" | AmountSummaryCard 렌더. 매출 조회 카드는 접힘(max-h-0) |
| 13 | 미승인 대시보드 + 매출 조회 카드 펼침 | `http://localhost:3000/dashboard?__devuser=1&__devstate=unapproved&__open=inquiry&__inquired=2150000` | "배달앱 또는 카드 매출이 있으신가요?" / `max-h-[3000px] opacity-100`(펼침) / "카드 매출 조회"·"여신금융협회 바로가기"·"배달앱 계정" / `placeholder="사장님 아이디"`·`placeholder="비밀번호"` / 조회 버튼 | 계정 입력 폼 4종(카드·배민·요기요·쿠팡이츠) 노출, 목 계정 아이디 프리필 |

캡처 폭 기준: 1574px (`--window-size=1574,...`).

## 인증 우회 (개발용, 쿼리 없으면 기존 동작 그대로)

- 어드민: `?__devuser=ADMIN` 또는 `?__devuser=PARTNER` → root layout 인라인 스크립트가 하이드레이션 전에 `localStorage.admin_user` + `admin_access_token` 쿠키 시드. 서버측 proxy.ts 가드도 `MOCK_API=1` + 해당 쿼리(또는 `/__preview`)면 통과.
- 가맹점: `?__devuser=1` → `access_token` 쿠키·sessionStorage + `user_data`/`user` 시드 (authStorage.ts 규약 그대로).
- 가맹점 상태 변형: `?__devstate=unapproved` → `__devstate` 쿠키 시드(max-age 24h) → 목 응답 변형(user/businesses 첫 사업자 PENDING, user/process-status 계약서작성 전). **쿠키가 남으면 이후 접속도 미승인으로 보이니, 승인 상태로 되돌릴 땐 `?__devstate=approved`(변형 미매칭 → 기본 목)로 덮어쓰거나 쿠키 삭제.** 헤드리스 캡처는 매번 새 프로필이라 무관.
- 가맹점 대시보드 캡처 플래그: `?__open=inquiry`(매출 조회 카드 최초 렌더부터 펼침), `?__inquired=<금액>`("조회된 어제 매출액" 행 시드). 쿼리 없으면 기존 동작 그대로.
- 어드민 딥링크: 탭 셸(TabContext)이 URL을 무시하고 홈 탭만 열던 구조 → `__devuser` 쿼리 진입 시 현재 pathname을 탭으로 여는 mount effect 추가. **`__devuser` 쿼리 없이는 딥링크가 홈으로 렌더되니 캡처 URL에 반드시 쿼리를 붙일 것.**

## 이식·수정한 파일

run-admin (develop 9e2741b):
- `lib/devMockData.ts` — 01 사본에서 복사 (8,611줄, 그대로)
- `lib/devMock.ts` — 01 사본에서 복사 + **pre-settlement-summary 어댑터 추가**: develop 신규 필드(preSettlementExcludedAmt/TargetAmt, directTransferAmt, recordOnlyAmt, adDeduction·refundAddition·cpcRefund)를 0 기본값으로 채움. 대상액 = 지급액+수수료−반영차액(검증차이 0 유지)
- `app/api/spring/[...path]/route.ts`, `app/api/fastapi/[...path]/route.ts` — MOCK_API=1 분기 이식
- `app/layout.tsx` — `__devuser` 시드 인라인 스크립트
- `proxy.ts` — MOCK_API=1 + (`__devuser` 쿼리 또는 `/__preview`) 서버 가드 통과
- `components/TabContext.tsx` — `__devuser` 진입 시 pathname 탭 오픈 effect
- `app/%5F_preview/{contract-reset,business-edit,manual-sales-result}/page.tsx` — 프리뷰 하네스 3종 (폴더명 `%5F_preview` = Next 프라이빗 폴더 언더스코어 이스케이프 → URL `/__preview/*`)

run-merchant (develop e083af8):
- `lib/devMockData.ts` — 02 사본에서 복사 + **delivery 목에 `refundAmount: 12000` 추가, `transferAmount` 339300→351300 정합 수정** + **settlement/today 목에 `estimatedPayout: 1998300`·`isEstimated`·`hasLedgerData`·`isLedgerFeeSettled` 추가** (PreSettlementCard는 transferAmount만 읽어 승인 화면 영향 없음)
- `lib/devMock.ts` — 02 사본에서 복사 + **`__devstate=unapproved` 변형 리졸버 추가** (user/businesses·user/process-status 클론 변형)
- `app/api/spring/[...path]/route.ts` — MOCK_API=1 분기 이식 + `__devstate` 쿠키를 리졸버에 전달
- `app/api/fastapi/[...path]/route.ts` — MOCK_API=1 분기 이식
- `app/layout.tsx` — `__devuser=1` 시드 + `__devstate` 쿠키 미러링 인라인 스크립트
- `app/dashboard/page.tsx` — 캡처 플래그 2줄: `isInquiryExpanded` 초기값 `__open=inquiry`, `inquiredSalesTotal` 초기값 `__inquired`(숫자). 쿼리 없으면 기존값(false/0) 그대로
- `app/%5F_preview/{sign-gate,biz-typefix}/page.tsx` — 프리뷰 하네스 2종

## 남은 제약

1. **어드민 선정산 결과 탭의 신규 카드 값이 0**: 선정산 제외액 0 / 바로이체 0 / 이미지급 0 / 플랫폼 차감·환급 0 (어댑터 합성 기본값). 선정산 대상액은 지급액+수수료로 합성. 표 구조·합계는 정상.
2. **배달 정산 목은 배민 단일 픽스처**: `source=YO/CPE`로 호출해도 같은 응답(플랫폼명 "배달의 민족")이 온다. 요기요·쿠팡이츠 변형 캡처가 필요하면 목 분기 추가 필요.
3. **가맹점 상세(/merchants/101) 헤드리스 덤프가 60초 소요**: 페이지가 계속 폴링/추가 fetch를 해 DOM 안정화가 늦다(실브라우저에선 정상 렌더). 알 수 없는 GET은 `{success:true,data:null}` 폴백이라 일부 신규 섹션(플랫폼 동기화 제어 등)은 빈 상태로 보일 수 있다.
4. **이 맥의 헤드리스 크롬은 `--dump-dom` 완료 후 종료되지 않음** (macOS 26 + Chrome 151): `verify_urls.sh`의 dump() 래퍼(백그라운드 실행 + `</html>` 폴링 + kill)를 재사용할 것.
5. **미승인 대시보드(#12·13)에 부수 문구 2개가 함께 노출**: 목 계정 픽스처에 오류 계정 2개(요기요 인증실패·쿠팡 일시오류)가 있어 "연동에 문제가 있는 계정이 2개…" 경고 줄이 뜨고, 계약 현황 카드는 "계약 현황을 확인해보세요"(계약서작성 전) 상태로 렌더된다. 캡처에서 빼려면 크롭 또는 목 계정 상태 조정 필요.
6. git commit 안 함 (지시대로). fresh-admin/fresh-merchant는 건드리지 않음.
