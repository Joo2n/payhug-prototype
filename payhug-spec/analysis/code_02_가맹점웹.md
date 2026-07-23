# 코드 분석 — PayHug 가맹점 웹 (`02_payhug-merchant-web-main`)

> 작성: 2026-07-18, 실제 프론트 코드 서브에이전트 분석 결과.
> 레포 루트: `/Users/semi/cursor/payhug/02_payhug-merchant-web-main`
> 로컬 실행: `npm ci && npm run dev` → **http://localhost:3000** (확인: 정상 기동, 랜딩 렌더링 OK)

---

## 0. 한 줄 결론 (기획자용)

Next.js 16 App Router 기반 가맹점(사용자) 웹. **랜딩/로그인/회원가입/비밀번호찾기/알림은 백엔드 없이 그대로 렌더링**된다. 대시보드·정산·계약·내정보는 클라이언트 `AuthGuard`가 막지만 **토큰 존재 여부만 검사**하므로 쿠키 `access_token=dummy` 주입으로 우회 가능(데이터는 빈 상태). 서버 미들웨어(`proxy.ts`)는 인증 차단을 하지 않는다(어드민과 다른 점).

## 1. 기술 스택

| 항목 | 내용 |
|---|---|
| 프레임워크 | **Next.js 16.1.6** (App Router, `output: "standalone"`, serverActions bodySizeLimit 50mb) |
| 언어 | TypeScript ~5 (strict), alias `@/* → ./*` |
| UI 런타임 | React 19.2.0 |
| 상태관리 | 라이브러리 없음 — React 훅 + 쿠키/세션스토리지 + 커스텀 훅(`hooks/*`) |
| 스타일링 | **Tailwind CSS v4** (커스텀 클래스, UI 라이브러리 없음) |
| 특수 의존성 | **react-signature-canvas** — 계약서 전자서명 패드 (`components/SignaturePad.tsx`) |
| 인증 저장 | js-cookie + sessionStorage/localStorage 병행 (`lib/authStorage.ts`) |
| 폰트 | `next/font/google` Noto Sans KR |
| 패키지 매니저 | **npm** (`package-lock.json`), 공개 레지스트리만 |
| Node 버전 | 명시 없음, 사실상 Node 20.9+/22 (로컬 v26.3.1 기동 확인) |

## 2. 실행 방법

| script | 명령 | 설명 |
|---|---|---|
| `dev` | `next dev -H localhost` | 개발 서버, **포트 3000(기본)** |
| `build` | `next build` | 프로덕션 빌드 |
| `start` | `next start` | 빌드본 실행 |
| `lint` | `eslint` | 린트 |

```bash
cd /Users/semi/cursor/payhug/02_payhug-merchant-web-main
npm ci
cp .env.example .env.local   # (완료됨)
npm run dev                  # → http://localhost:3000
```

## 3. 환경변수 · 백엔드 의존성 · 로그인 게이트

### 3-1. 환경변수 (전부 fallback 있음 — env 없어도 뜸)

| 변수 | 기본값 | 사용처 |
|---|---|---|
| `SPRING_API_URL` | `http://localhost:8080` | `app/api/spring/[...path]/route.ts:11` |
| `FASTAPI_API_URL` | `http://localhost:8000` | `app/api/fastapi/[...path]/route.ts:11` |
| `NEXT_PUBLIC_SPRING_API_URL` | `http://localhost:8080` | `lib/config.ts:13` (KCB 콜백 등) |
| `NEXT_PUBLIC_FASTAPI_API_URL` | `http://localhost:8000` | `lib/config.ts:14` |

### 3-2. API 아키텍처
- 백엔드 2개: **Spring(핵심 API, 8080) + FastAPI(OCR/AI, 8000)**.
- 클라이언트는 상대경로 `/api/spring/*`, `/api/fastapi/*`만 호출(`lib/config.ts`) → Next API Route가 프록시(`→ ${...}/api/v1/...`).
- 단일 진입점: **`lib/apiClient.ts`(`springApi`/`fastApi`) + `lib/api.ts`(`fetchWithAuth`)**. 예외: 멀티파트 업로드만 `services/contractService.ts`에서 직접 fetch. → 목킹 붙이기 쉬움. **MSW 등 기존 목 인프라 없음.**

### 3-3. 인증
- `POST /auth/login` → JWT + user 반환 (`services/authService.ts`).
- 저장: 쿠키 `access_token`(SameSite=None, Secure, 만료 150분) + sessionStorage, 유저는 `user_data` 쿠키/`user` localStorage (`lib/authStorage.ts`).
- `Authorization: Bearer` 자동 첨부, 401 시 `/login?reason=expired`.
- 회원가입 3단계: 약관동의 → **KCB 본인인증(팝업 + postMessage `KCB_AUTH_SUCCESS`)** → 비밀번호 설정 (`app/signup/page.tsx`).

### 3-4. 게이트 구조 (어드민과 다름!)
- **미들웨어 `proxy.ts`는 차단 안 함** — protected path에서도 `NextResponse.next()` 통과.
- 실제 차단은 클라이언트 **`components/AuthGuard.tsx`** — 토큰 없으면 `router.replace("/login")`. 적용: `app/dashboard/layout.tsx`, `app/settlement/layout.tsx`, `app/contract/layout.tsx`(+`ApprovedContractGuard`), `app/my-info/layout.tsx`.

| 화면군 | 백엔드 없이 접근 | 비고 |
|---|---|---|
| `/`, `/login`, `/signup`, `/signup/complete`, `/find-password`, `/notifications` | **가능** | 제출 동작만 백엔드 필요 |
| `/dashboard`, `/settlement/**`, `/contract/**`, `/my-info/**` | 쿠키 주입 시 가능 | AuthGuard는 truthy 검사만 |

### 3-5. 우회 방법
- DevTools에서 쿠키 `access_token=dummy` (+ `user_data={"id":1,"name":"테스트"}` 또는 localStorage `user`) 주입 → 가드 통과.
- 백엔드 없으면 프록시가 **502** 반환(401 아님) → 강제 로그아웃 없이 레이아웃/빈 상태("정산 정보를 불러올 수 없어요" 등) 확인 가능.
- 실데이터 화면은 `lib/apiClient.ts`/`lib/api.ts` 스텁 필요(코드 수정 영역).

## 4. 화면(라우트) 인벤토리 — 총 32 라우트

### 4-1. 공개/인증 진입 (6)

| 경로 | 파일 (`app/` 이하) | 화면 이름 | 주요 기능 |
|---|---|---|---|
| `/` | `page.tsx` | 랜딩(메인) | 히어로 + 3스텝 + 매출 조회로 선정산 가능액 미리보기 + FAQ + 1:1문의 |
| `/login` | `login/page.tsx` | 사장님 로그인 | 사업자번호/휴대폰 + 비밀번호 |
| `/signup` | `signup/page.tsx` | 회원가입 | 약관동의 → KCB 본인인증 → 비밀번호 |
| `/signup/complete` | `signup/complete/page.tsx` | 가입 완료 | 선정산 신청 유도 |
| `/find-password` | `find-password/page.tsx` | 비밀번호 찾기 | 본인인증 → 재설정 |
| `/notifications` | `notifications/page.tsx` | 알림 목록 | 알림 리스트 (AuthGuard 미적용) |

### 4-2. 대시보드 (1)

| 경로 | 파일 | 화면 이름 | 주요 기능 |
|---|---|---|---|
| `/dashboard` | `dashboard/page.tsx` | 가맹점 메인 | 사업자 선택+계약상태 배지, 계약 CTA, **"미리 받은 돈" 카드**, 매출조회, 1:1문의 |

### 4-3. 계약(선정산 온보딩) 플로우 (12) — `AuthGuard`+`ApprovedContractGuard`

| 경로 | 화면 이름 | 주요 기능 |
|---|---|---|
| `/contract` | 계약 준비/서류 체크리스트 | 필요 서류 6종 안내, 단계 허브 |
| `/contract/terms` | 약관동의·계약서 서명 | 4스텝: 약관→미리보기→전자서명+수수료율→PDF 합성 |
| `/contract/upload-business` | 사업자등록증 업로드 | 첨부 + OCR(FastAPI) |
| `/contract/confirm-business` | 사업자 정보 확인 | 국세청 진위확인 + 등록 |
| `/contract/upload-identity` | 신분증 업로드 | 주민증/면허증 + OCR |
| `/contract/confirm-identity` | 신분증 정보 확인 | 확인/등록 |
| `/contract/apply-pre-payment` | 전용계좌 개설 안내 | 하나은행 락계좌+입출금 개설 유도 |
| `/contract/upload-pre-payment` | 락계좌 통장 업로드 | 통장 이미지 + OCR |
| `/contract/confirm-pre-payment` | 락계좌 인증/등록 | 1원 인증 + 출금 비번 + 빠른조회 |
| `/contract/upload-settlement` | 입금 계좌 통장 업로드 | 일반 계좌 통장 첨부 |
| `/contract/confirm-settlement` | 입금 계좌 인증/등록 | 1원 인증 후 등록 |
| `/contract/register-accounts` | 플랫폼 계정 등록 | 카드/배민/요기요/쿠팡이츠 연동 |

### 4-4. 정산("미리 받은 돈") 상세 (8) — `AuthGuard`

| 경로 | 화면 이름 | 주요 기능 |
|---|---|---|
| `/settlement` | 미리 받는 돈(정산 상세) | 입금일별 카드/배달앱/페이허그 분해 |
| `/settlement/card` | 카드사별 상세 | 카드사별 내역(페이징) |
| `/settlement/card/transaction` | 카드 거래 단위 상세 | 승인번호 단위 수수료/지급액 |
| `/settlement/delivery` | 배달앱별 상세 | 플랫폼별(만나서결제 차감 표기) |
| `/settlement/delivery/order` | 배달 주문 단위 상세 | 주문번호 단위 분해 |
| `/settlement/adjustments` | 예상 지급 차액 | 예상↔실제 차액(다음 정산 반영) |
| `/settlement/account` | 계좌 입금 내역 | 정산계좌 실입금 이력(하나은행) |
| `/settlement/account/excluded` | 선정산 제외액 내역 | 바로지급(제외분) 상세 |

### 4-5. 내 정보 (5) — `AuthGuard`

| 경로 | 화면 이름 | 주요 기능 |
|---|---|---|
| `/my-info` | 내 정보 관리(허브) | 기본정보/계약/연동계정/고객지원/보안 |
| `/my-info/contract` | 계약 정보 조회 | 계좌·증빙·계약서·약관 조회, 상태배지 |
| `/my-info/accounts` | 연동 계정 관리 | 플랫폼 계정 재검증/저장 |
| `/my-info/inquiries` | 1:1 문의 | 문의 등록/조회 |
| `/my-info/change-password` | 비밀번호 변경 | 변경 후 재로그인 |

### 4-6. 시스템: `/api/spring/[...path]`, `/api/fastapi/[...path]` 프록시, `layout/loading/error/robots/sitemap`

### 4-7. 오버레이 컴포넌트

| 파일 | 종류 | 용도 |
|---|---|---|
| `components/CommonModal.tsx` | 중앙 모달 | 공통 확인/안내(전 화면 재사용) |
| `components/CommonToast.tsx` | 토스트 | `useToast` 연동 |
| `components/CommonTooltip.tsx` | 툴팁 | 수수료/차액 설명 |
| `components/TermsModal.tsx` | 모달 | 약관 전문 |
| `components/dashboard/InquiryModal.tsx` | 모달 | 1:1 문의 작성 |
| `components/SignatureCreator.tsx`/`SignaturePad.tsx` | 서명 패드 | 전자서명 입력 |
| `components/ContractSignInput/View/DirectSign/SignatureOnPdf` | PDF 오버레이 | 계약서 서명 배치·표시 |
| `components/Header.tsx` 내부 | 드로어/드롭다운/모달 | 햄버거 드로어, 알림·프로필 드롭다운, 로그아웃 확인 |
| `components/CommonLoading.tsx` | 로딩 오버레이 | 페이지/버튼 로딩 |

## 5. 도메인 로직 관찰

### 5-1. 계약 상태 — `"PENDING"|"APPROVED"|"REJECTED"` (`types/user.ts`, `types/myContract.ts`)
- 라벨: 승인완료/심사반려/심사중. PENDING은 사업자 등록 기본값이라 계약완료로 간주 안 함 (`dashboard/page.tsx:91-127`).

### 5-2. 플랫폼 코드
- `PlatformType = "CARD"|"BAEMIN"|"YOGIYO"|"COUPANG"` (`types/user.ts:40-47`)
- 정산 API 코드: **CARD / BM / YO / CPE** (`services/salesService.ts:477-481`)
- 연동 상태: `ACTIVE/INACTIVE/AUTH_FAILED/SCRAPING_ERROR/ERROR`

### 5-3. 수수료 체계 (`services/salesService.ts`)
- `preSettlementFeeTotal`(선정산 수수료 합), `marginFeeTotal`(채권매입, VAT 포함), `systemFeeTotal`(시스템 이용료), `transferFeeTotal`(이체 수수료)
- `SettlementPayhug`: `feeExempt`(면제), `offlineDeduction`(현장결제 차감), `adDeduction`(광고비 차감, 배민 우리가게클릭)
- 원장 컬럼: `cardFeeAmt, deliveryFeeAmt, preSettlementFee, marginFee, systemFee, netPayoutAmt, preSettlementAmt` (`components/sales/LedgerTable.tsx`)

### 5-4. 상태값 (`components/sales/LedgerTable.tsx`)
- 거래: 승인/승인취소/성공/취소/매입완료/매입취소/선정산 대상/대기
- 정산: `READY / SETTLED(정산완료) / ADJUSTED(차액정산완료)`
- 이체: `PENDING(이체대기)/PROCESSING(이체중)/COMPLETED(이체완료)/FAILED(이체실패)`
- 계좌 용도: `PRE_PAYMENT`(선정산 전용 락계좌) / `SETTLEMENT`(입금받을 정산계좌) (`types/myContract.ts:44`)
- 문의: `PENDING(대기)/IN_PROGRESS(처리중)`

### 5-5. 코드에 명시된 비즈니스 규칙
- 예상 카드 수수료율 기준 선지급 → **실제 정산 차액은 다음 선정산에 자동 반영** (`settlement/page.tsx:36-42`)
- **매일 오전 11:30 정산 완료 후 수집분은 "미리 받는 돈"에서 제외**(=선정산 제외액/바로지급) (`settlement/account/excluded/page.tsx:16`)
- **만나서 결제(현장결제)는 선정산 제외/차감**(음수 지급) (`settlement/delivery/order/page.tsx:132`)
- 랜딩 FAQ: 최소 매출 5만원 이상, 현금매출 제외 등 (`app/page.tsx:379-414`)

## 6. 리스크

| 리스크 | 영향도 | 대응 |
|---|---|---|
| 핵심 화면 AuthGuard | 높음 | 쿠키 주입 우회(위 3-5), 실데이터는 목킹 필요 |
| 백엔드 2종 의존 | 중 | 조회/제출 실패(502), 로그인 자체 불가 → 우회 필요 |
| Node 버전 | 중 | 20.9+ 필요 (로컬 v26 확인 완료) |
| 구글 폰트 다운로드 | 중 | 최초 실행은 인터넷 연결 필요 |
| 사설 레지스트리 | 없음 | 공개 npm만 사용 |

## 정책 문서 대조 메모 (payhug-spec 연계)

- 코드의 `선정산 제외액(바로지급)`·`예상 지급 차액`·`미회수 이월` 개념이 02(용어)·07(미확정질문)의 6대 개념과 어떻게 매핑되는지 확인 필요 — 특히 C4(예상 지급 차액 정의 미확정)의 실제 구현이 `/settlement/adjustments` 화면에 존재.
- 11:30 정산 컷오프가 코드 문구로 확인됨(가맹점 웹) — C2(지급 캘린더) 검토 시 근거로 사용 가능(단, 이것은 "구현 사실"이지 "정책 확정"은 아님).
