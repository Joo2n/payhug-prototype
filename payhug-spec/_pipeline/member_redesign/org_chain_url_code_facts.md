# 조직 다단·가입링크(URL) — 현행 코드 사실관계

조사 레포: `/Users/semi/cursor/payhug-admin-web` (Next.js App Router, main = 5f9297e 2026-07-24; `git diff main origin/develop -- app/partners app/settlement/policies services/partnerService.ts` 0건 — develop 기준 동일). 주의: `/Users/semi/cursor/payhug/01_payhug-admin-web-main`은 3fbc230(7/22) 이전 스냅샷이라 `fetchLinkAncestors`·최상위 자동선택 코드가 남아 있음 — 라인 인용은 payhug-admin-web 기준.

## 1. 탭↔생성기 연동 — 부수효과의 정확한 기전 [사실]

부수효과 경로는 4단계이고, 필터·잠금 로직은 한 줄도 없다.

1. 탭 클릭 → `setFilterType(opt.value)` (`app/partners/page.tsx:1262-1274`)
2. `filterType`이 `loadPartners`의 useCallback 의존성 → 서버 재조회 `fetchPartners(filterType || undefined)` (`page.tsx:1075-1094`, `services/partnerService.ts:52-55` → `GET /admin/partners?userType=…`)
3. 응답이 단일 상태 `partners`에 저장 (`page.tsx:1085`)
4. 생성기에 그 원본 배열이 그대로 주입 (`page.tsx:1438` `<SignupLinkGenerator partners={partners} />`) → 생성기 내부 `partners.filter(...)`로 드롭다운 후보 구성 (`page.tsx:696-699`)

즉 드롭다운 옵션 소스 = 목록 테이블의 서버 응답 그 자체. 전용 fetch 없음. "전체 탭에서만 조합이 된다"는 현상은 사실이며 원인은 소스 공유다.

부수효과의 정확한 동작 3가지 [사실]:
- 잠기는 게 아니라 비는 것: 탭 때문에 disabled가 걸리는 select는 없음. 유일한 disabled는 파트너↔제휴사 상호배타(`:742` `disabled={!!selectedAffiliate}`, `:756` `disabled={!!selectedPartner}` + `:701-709` 상호 초기화). 영업 select에는 disabled 자체가 없음(`:766-776`).
- 선택값 잔존 결함: 생성기는 조건부 렌더 밖(`:1437-1438`)에 상시 마운트되고 key도 없어, 탭을 바꿔도 언마운트되지 않는다. `selectedPartner/Affiliate/Sales`(`:689-691`)가 유지되므로 전체 탭에서 파트너 선택 → 영업 탭 이동 시 드롭다운은 빈 것처럼 보이지만 URL에는 `partnerCode`가 계속 실린다(`:715-722`). 화면-URL 불일치.
- 검색창은 무관: `searchQuery`는 `filtered`(`:1101-1107`)에만 적용되어 테이블에만 쓰인다. 생성기는 `partners` 원본을 받으므로 검색으로는 후보가 좁아지지 않음(탭만 영향).

탭별 후보 표(코드 도출):

| 탭 | 파트너 dd | 제휴사 dd | 영업 dd |
|---|---|---|---|
| 전체 | 조회범위 내 PARTNER 전부 | AFFILIATE 전부 | SALES+SALES_ORG 전부 |
| 파트너 | 파트너만 | 빈 목록 | 빈 목록 |
| 영업 | 빈 목록 | 빈 목록 | SALES만* |
| 영업조직 | 빈 목록 | 빈 목록 | SALES_ORG만* |
| 투자자/페이허그/관리자 | 전부 빈 목록 | | |

\* `?userType=SALES` 응답에 SALES_ORG가 섞이는지는 [불명(서버 확인 필요)] — 프론트는 서버 응답을 그대로 쓴다.

## 2. 드롭다운 구성·필수 여부·URL 형태 [사실]

- 공통 전제 `page.tsx:696`: `partners.filter(p => p.status === "ACTIVE" && p.referralCode)` — 활성 + 추천코드 보유자만 후보.
- 파트너 `:697` `userType === "PARTNER"` / 제휴사 `:698` `=== "AFFILIATE"` / 영업 `:699` `["SALES","SALES_ORG"].includes(...)`.
- 옵션 label = `{p.name} ({p.referralCode})`, value = `p.referralCode` (`:746-748`, `:760-762`, `:773-775`).
- 필수 코드 없음 — `buildUrl()`(`page.tsx:715-722`)은 `partnerCode`/`affiliateCode`/`salesCode` 3개 모두 "있으면 넣는" 조건부. 셋 다 비었을 때만 안내문 "참여자를 1명 이상 선택하면…"(`:799`). → 파트너코드 없이 `?salesCode=XXX` 단독 URL 생성·복사 가능 [사실]. "파트너코드 필수"는 프론트 코드 기준으로 성립하지 않음.
- URL 형태: `window.location.origin.replace("admin.","")` + `?partnerCode=&affiliateCode=&salesCode=` (`:711-713`, `:715-722`). 중간 조직 코드를 담는 파라미터는 없음(3종이 전부).
- 수신 측: `payhug-merchant-web/app/page.tsx:54-74`(sessionStorage 저장) → `app/signup/page.tsx:263-274`(있으면 payload 첨부). 서버가 코드 소유자에서 상위 체인을 재구성하는지는 [불명(서버 확인 필요)] — 3fbc230 커밋 메시지("상위 코드로 링크 생성 시 본인이 계약 체인에서 누락")가 서버 재구성 구조를 시사.
- 배경 이력 [사실]: 3fbc230(2026-07-22) — `fetchLinkAncestors()`(`/admin/partners/link-ancestors`) 호출과 "최상위 파트너 자동 선택" useEffect를 삭제하고 자기+하위만 노출로 변경. 이 때문에 영업·영업조직 계정은 파트너 후보 0명(정상 시나리오).

## 3. 계층 규칙 — 프론트 하드코딩 0건, 전면 서버 위임 [사실]

- 상위 회원 드롭다운 `page.tsx:860-871`: `partners.filter(p => p.status === "ACTIVE" && p.id !== editTargetId)` — 유형 제약·깊이 제약·순환 방지 전부 없음. 라벨은 `${p.name} (${USER_TYPE_LABELS[p.userType]})`(`:865`) 유형 병기만. 수정 시 스코프 밖 기존 상위는 `(현재 상위)` 라벨로 강제 주입(`:867-871`).
- 유형 드롭다운 `page.tsx:872`: `USER_TYPE_OPTIONS.filter(opt => creatableTypes.includes(opt.value))` — 서버 `GET /admin/partners/creatable-types`(`services/partnerService.ts:73-75`) 종속. 빈 배열이면 `+ 등록` 버튼 숨김(`page.tsx:1249-1256`).
- 레포 전체 `SALES_ORG` grep 11곳 — 라벨 맵·탭 옵션·정산 참여자 옵션·로그인 허용목록(`app/login/page.tsx:53`)·참여자 판별(`components/AdminLayout.tsx:352`, `app/merchants/[id]/page.tsx:154`)뿐, "부모 유형 X면 자식 유형 Y 금지" 규칙 0건.
- "SALES 유형은 SALES_ORG 유형의 회원을 생성/변경할 수 없습니다" 문자열은 프론트에 없음 → 서버 메시지를 `submitError`로 표시. 프론트는 사전 검증 없이 제출 후 에러로만 통보.
- "영업 하위에 영업" / "영업조직 상위에 영업조직" → 화면상 선택은 100% 가능 [사실]. 실제 저장 성공 여부·깊이 상한·순환 방지는 [불명(서버 확인 필요)].

## 4. '메타→이로움' 실데이터 케이스 [사실 + 불명]

- 어드민 프론트 코드·목데이터에 '메타플레이'·'이로움' 문자열 0건(grep). 목데이터 최대 체인은 `PAYHUG(2) → PARTNER(10) → SALES_ORG 서초영업조직(12) → SALES 김영업/이영업(13,14)` 4단 — 조직 2중 적층 예시 없음(`01_payhug-admin-web-main/lib/devMockData.ts:46-116`). 이 케이스는 목/테스트 범위 밖.
- 문서 흔적: `decisions_0819.md:145`(B3 정책 판단 대기), `states_catalog.md:145`(상태 미부여), `07_OPEN_QUESTIONS.md:226`.
- 현행 화면 거동(코드 도출):
  - 목록 '상위 회원' 열은 `parentUserName` 한 칸만 렌더(`page.tsx:1353-1354`) — 유형 배지·체인 없음. 2단 조직이어도 화면상 깨지지 않고 "이로움의 상위=메타"로만 보임.
  - 가입링크 '영업' 드롭다운에서 메타(SALES)와 이로움(SALES_ORG)이 같은 '영업' 라벨 아래 혼합 노출(`:699`) → "영업조직이 영업으로 분류됐다"는 인상의 직접 원인.
  - 메타가 SALES로 등록된 상태에서 하위 수정 시 서버 계층 규칙에 걸려 실패, 프론트는 서버 문구만 표시.
  - 이로움 하위 영업 3인은 엔케이(파트너) 계정 조회 범위 밖이면 목록·드롭다운 양쪽 부재 — "파트너를 고르면 영업이 좁혀진다"는 로직은 코드에 없음(파트너 선택이 salesOptions 재계산을 트리거하는 코드 부재).
  - 유형 정정(SALES→SALES_ORG) 경로: 수정 모달 유형 select는 `creatableTypes` 기반이라 서버가 허용해야만 노출 [불명(서버 확인 필요)].

## 5. 수익 배분 폼의 계층 수용력 [사실]

`app/settlement/policies/PolicyFormModal.tsx:204-266` 참여자 슬롯:
- `ruleType === "GENERAL"`: 투자자 / 페이허그 / 상위파트너 / 하위파트너 / 영업조직(단일 슬롯 1개) — `:241-247`, 옵션 소스 `userOptions["SALES_ORG"]`.
- `ruleType === "DAOU"`: 투자자 / 페이허그 / 상위영업 / 하위영업 — `:250-264`, 옵션 `SALES + AFFILIATE` 혼합.
- 즉 조직 슬롯은 1단 1개. 영업조직→영업조직→영업 3단 체인은 배분에 담을 슬롯이 없어 중간 조직이 배분에서 유실. 슬롯 추가 UI 없음(고정 폼).
- 배분 행 가드: `app/settlement/policies/page.tsx:331-335` `isRateVisible` — `targetRole === "SALES"` 요율 행은 `form.salesOrgId`가 비면 숨겨지고 `buildPayload`에서도 제외(`:344`). 조직 슬롯을 못 채우면 조직 몫 요율 자체가 저장되지 않음.
- 옵션 로딩 유형: `page.tsx:241` `["INVESTOR","PAYHUG","PARTNER","SALES","SALES_ORG","AFFILIATE"]`.

## 6. 표기 이슈 [사실]

| # | 지점 | 코드 근거 | 내용 |
|---|---|---|---|
| a | '영업' 드롭다운 유형 혼합 | `page.tsx:699` | URL 파라미터가 `salesCode` 하나뿐이라 SALES+SALES_ORG를 한 select에 병합. 라벨 "영업" 단일 |
| b | 탭 정렬 계층 역순 | `page.tsx:29-37` vs `:1240` 부제 | 같은 페이지 안 순서 불일치. 탭은 배열 순서 그대로 렌더(`:1262`) |
| c | role 코드 SALES 의미 충돌 | `app/settlement/policies/page.tsx:46`(`ROLE_LABELS.SALES="영업조직"`) vs `:78`(`USER_TYPE_LABELS.SALES="영업"`) 동일 파일 공존, `PolicyFormModal.tsx:48` 동일 | 정산 도메인의 SALES = 영업조직 몫 |
| d | 유형 라벨 매핑 자체는 일관 | `page.tsx:39-47`, `:865`, `:1326` | SALES=영업 / SALES_ORG=영업조직. 라벨이 반대로 붙은 코드는 없음 |
| e | 상위 회원 열 정보 부족 | `page.tsx:1353-1354` | 이름만 표시(유형 배지·체인 없음) → 다단 조직 오등록을 목록에서 식별 불가 |

## [불명(서버 확인 필요)] 종합

① `?userType=SALES` 응답의 SALES_ORG 포함 여부 ② `creatable-types`의 로그인 유형별 반환 매트릭스 ③ 유형×상위유형 생성/변경 허용표와 깊이 상한·순환 방지 ④ `salesCode` 단독 링크의 가입 유효성·체인 재구성 규칙 ⑤ 유형 변경(SALES→SALES_ORG)의 서버 허용 여부와 정산 영향
