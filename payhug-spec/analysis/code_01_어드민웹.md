# 코드 분석 — PayHug Admin Web (`01_payhug-admin-web-main`)

> 작성: 2026-07-18, 실제 프론트 코드 서브에이전트 분석 결과.
> 레포 루트: `/Users/semi/cursor/payhug/01_payhug-admin-web-main`
> 로컬 실행: `npm ci && npm run dev` → **http://localhost:3001** (확인: 정상 기동, 미로그인 시 `/login` 리다이렉트)

---

## 0. 한 줄 결론 (기획자용)

Next.js 16 App Router 기반 어드민. **로그인 게이트가 이중**(미들웨어 + 클라이언트 가드)이고 로그인은 Spring 백엔드 의존 → 백엔드 없이 "정상 로그인"으로는 진입 불가. 다만 **게이트가 토큰 "존재 여부"만 검사**하므로 가짜 쿠키/로컬스토리지를 심으면 각 화면의 레이아웃(껍데기)은 볼 수 있다(데이터는 502로 빈 상태). 화면 인벤토리 확보 목적에는 충분.

## 1. 기술 스택

| 항목 | 내용 |
|---|---|
| 프레임워크 | **Next.js 16.1.6** (App Router, `output: "standalone"`) |
| 언어 | TypeScript 5 (strict) |
| UI 런타임 | React 19.2.0 |
| 상태관리 | 라이브러리 없음 — React 훅 + Context(`components/TabContext.tsx`) + 커스텀 훅 |
| 스타일링 | **Tailwind CSS v4** (PostCSS 플러그인, config 파일 없음) |
| 차트 | recharts 3.7.0 (dynamic import, SSR off) — `app/page.tsx` |
| 엑셀 | exceljs 4.4.0 + xlsx 0.18.5 — `lib/excel.ts` |
| 마크다운 | react-markdown 10 + remark-gfm — AI 로그분석 화면 |
| 인증 저장 | js-cookie — `lib/apiClient.ts` |
| 폰트 | `next/font/google` Noto Sans KR (최초 실행 시 인터넷 필요) |
| 패키지 매니저 | **npm** (`package-lock.json`), 공개 레지스트리만 사용 |
| Node 버전 | 명시 없음. Next 16 요구사항상 **Node ≥ 20.9** (Dockerfile은 node:20-alpine, 로컬 v26.3.1로 기동 확인) |

## 2. 실행 방법

| script | 명령 | 설명 |
|---|---|---|
| `dev` | `next dev -H localhost -p 3001` | 개발 서버, **포트 3001** |
| `build` | `next build` | 프로덕션 빌드(standalone) |
| `start` | `next start -p 3001` | 빌드본 실행 |
| `lint` | `eslint` | 린트 |

```bash
cd /Users/semi/cursor/payhug/01_payhug-admin-web-main
npm ci
cp .env.example .env.local   # 없어도 기본값으로 뜸 (완료됨)
npm run dev                  # → http://localhost:3001
```

## 3. 환경변수 · 백엔드 의존성 · 로그인 게이트

### 3-1. 환경변수 (서버사이드 전용 2개)

| 변수 | 기본값 | 용도 | 참조 위치 |
|---|---|---|---|
| `SPRING_API_URL` | `http://localhost:8080` | Spring(메인 API) 프록시 타깃 | `app/api/spring/[...path]/route.ts` |
| `FASTAPI_URL` | `http://localhost:8000` | FastAPI(OCR·AI 로그분석) 프록시 타깃 | `app/api/fastapi/[...path]/route.ts` |

`NEXT_PUBLIC_*`는 의도적으로 미사용(런타임 주입 목적). Dockerfile의 `NEXT_PUBLIC_*` ARG는 잔재.

### 3-2. API 아키텍처
- 클라이언트는 백엔드 직접 호출 없음. 자기 자신의 Next API Route로 프록시.
  - `getApiUrl(path)` → `/api/spring{path}` → `${SPRING_API_URL}/api/v1/{path}` — 설정: `lib/config.ts`
  - `getFastApiUrl(path)` → `/api/fastapi/api/v1{path}`
- 공용 클라이언트: `lib/apiClient.ts` (401 시 자동 로그아웃)
- 서비스 계층: `services/` — `authService, merchantService, settlementService, partnerService, batchService, termsService, manualSalesService, logAnalysisService, cooconService`

### 3-3. 인증
- `POST /api/spring/auth/login` → 토큰을 쿠키 `admin_access_token`(만료 150분), user 객체를 localStorage `admin_user`에 저장.
- 모든 요청에 `Authorization: Bearer <token>`. 401이면 세션 클리어 후 `/login`.
- 허용 userType: `ADMIN, PAYHUG, PARTNER, SALES_ORG, SALES, AFFILIATE, INVESTOR`

### 3-4. 로그인 게이트 (이중)
1. **미들웨어**: `proxy.ts` — ⚠️ Next.js 16에서 `middleware.ts`가 `proxy.ts`로 개명된 것. `/login` 외 모든 경로에서 쿠키 `admin_access_token` **존재 여부만** 검사, 없으면 `/login?redirect=...`.
2. **클라이언트 가드**: `components/AdminLayout.tsx` — 쿠키 없으면 `/login` 강제 이동. `admin_user.userType`으로 사이드바 메뉴 필터(ADMIN/PAYHUG=전체, 그 외=축소).

### 3-5. 백엔드 없이 화면 보는 우회 (코드 수정 불필요)
- 브라우저 DevTools에서:
  - Cookie: `admin_access_token = dummy` (domain: localhost)
  - localStorage: `admin_user = {"name":"기획","userType":"ADMIN"}`
- 이후 원하는 경로 진입 → 레이아웃/사이드바/탭/빈 테이블 렌더. 데이터 API는 502(빈 상태).
- **MSW 등 목 인프라 없음.** 데이터까지 보려면 목킹 지점: `app/api/spring/[...path]/route.ts`(프록시에서 고정 JSON) 또는 `lib/apiClient.ts`. 응답 스키마는 `types/`에 정의돼 있어 목 데이터 작성 용이.

## 4. 화면(라우트) 인벤토리 — 총 20 페이지 라우트 (+오버레이)

### 4-1. 페이지 라우트

| 경로 | 파일 (`app/` 이하) | 화면 이름 | 주요 기능 |
|---|---|---|---|
| `/login` | `login/page.tsx` | 관리자 로그인 | 휴대폰/사업자번호 + 비밀번호, 세션만료 안내 |
| `/` | `page.tsx` | 관리자 대시보드 | 선정산 KPI, 일별 차트(recharts), 상위 가맹점, 시스템 상태 |
| `/manage` | `manage/page.tsx` | 가맹점 관리 | 리스트·계약상태 필터(심사대기/승인/반려)·정렬 |
| `/merchants/[id]` | `merchants/[id]/page.tsx` | 가맹점 상세 (2,296줄 최대) | 계약/서류/외부계좌/카드수수료/채무관리/메모/문의/평균매출 |
| `/merchants/[id]/fee-adjustments` | `merchants/[id]/fee-adjustments/page.tsx` | 가맹점 수수료 차액 조정 | 카드수수료 환급/차감 |
| `/sales` | `sales/page.tsx` | 매출 조회 | 가맹점 매출 목록·상태 필터 |
| `/sales/[bizNo]` | `sales/[bizNo]/page.tsx` | 매출 상세 (1,279줄) | 건별 매출·이체상태·광고차감·예상/실매출 대사 |
| `/inquiries` | `inquiries/page.tsx` | 1:1 문의 관리 | 문의 목록/상태/답변 |
| `/settlement` | `settlement/page.tsx` | (리다이렉트) | → `/settlement/overview` |
| `/settlements` | `settlements/page.tsx` | (리다이렉트, 레거시) | → `/settlement/overview` |
| `/settlement/overview` | `settlement/overview/page.tsx` | 정산 현황 (809줄, **6탭 허브**) | 아래 4-3 |
| `/settlement/policies` | `settlement/policies/page.tsx` | 정산 상품 관리 | 수수료 정책/요율(bps) CRUD |
| `/settlement/simulation` | `settlement/simulation/page.tsx` | 정산 시뮬레이션 | 채권매입/시스템/이체 수수료 계산 |
| `/settlements/[id]/fee-adjustments` | `settlements/[id]/fee-adjustments/page.tsx` | 정산 배치 수수료 차액 | 배치 단위 환급/차감 |
| `/account-balance` | `account-balance/page.tsx` | 모(母) 계좌 잔액 조회 | 마스터 계좌 잔액·이체 확인 |
| `/partners` | `partners/page.tsx` | 회원 관리 (1,513줄) | 파트너/영업조직/영업사원/제휴/투자자/페이허그 회원 |
| `/terms` | `terms/page.tsx` | 약관 관리 | 약관 CRUD |
| `/scraping-incidents` | `scraping-incidents/page.tsx` | 스크래핑 장애 이력 | 카드/배민/요기요/쿠팡이츠 수집 장애 |
| `/activity-logs` | `activity-logs/page.tsx` | 활동 로그 | 관리자/사용자 감사 로그 |
| `/log-analysis` | `log-analysis/page.tsx` | AI 모니터링 어시스턴트 | FastAPI 로그 분석(markdown), 기간 프리셋 |

### 4-2. API 라우트(프록시): `/api/spring/[...path]`, `/api/fastapi/[...path]`

### 4-3. `/settlement/overview` 내부 6탭 (사실상 6개 하위 화면)

| 탭 값 | 라벨 | 파일 |
|---|---|---|
| `pre-settlement` | 선정산 결과 | `PreSettlementTab.tsx` |
| `batch-detail` | 정산 상세 | `BatchDetailTab.tsx` |
| `fee-adjustment` | 차액 정산 | (page.tsx 인라인) |
| `transfer-records` | 이체 내역 | `TransferRecordsTab.tsx` |
| `tax-invoice` | 계산서 발행 | `TaxInvoiceTab.tsx` |
| `voc` | VOC 대응 | `VocExportTab.tsx` |

### 4-4. 오버레이(모달/다이얼로그/토스트)

| 컴포넌트 | 파일 | 성격 |
|---|---|---|
| 확인 다이얼로그 | `components/ConfirmDialog.tsx` | 공용 confirm |
| 토스트 | `components/Toast.tsx` | 성공/실패/정보 |
| 첨부 미리보기 | `components/AttachmentPreviewModal.tsx` | 이미지/PDF |
| 수동 이체 | `components/ManualTransferModal.tsx` | 수기 이체 실행 |
| 가맹점 서류 편집 | `components/MerchantDocumentEditModals.tsx` | 복수 모달 |
| 락계좌 상세 | `components/PlatformLockAccountDetailDialog.tsx` | 플랫폼 락계좌 |
| 엑셀 업로드 | `components/sales/ExcelUploadModal.tsx` | 매출 엑셀 |
| 수동 매출 입력 | `components/sales/ManualSalesModal.tsx` | 수기 매출 등록 |
| 정산 상품 폼 | `app/settlement/policies/PolicyFormModal.tsx` | 정책 생성/수정 |
| 인라인 다이얼로그 | `MerchantCardFees/MerchantDebtManagement/MerchantExternalAccounts/PreSettlementTab/partners/inquiries/terms/account-balance` 각 화면 내장 | fixed/z-50 오버레이 |

### 4-5. 네비게이션 프레임
- **탭 기반 MDI**: `components/TabContext.tsx`, `TabBar.tsx`, `TabContent.tsx` — `isTabMode`면 사이드바 클릭이 상단 탭으로 열림.
- 사이드바 그룹(ADMIN 기준): **가맹점**(가맹점 관리/매출 조회/1:1 문의) · **정산**(정산 현황/상품관리/시뮬레이션) · **관리자**(모 계좌 잔액/회원/약관/스크래핑 장애/활동 로그/AI 모니터링). 참여자 계정은 축소 메뉴. (`components/AdminLayout.tsx`)

## 5. 도메인 로직 관찰

### 5-1. 수수료 유형 (`lib/settlementLabels.ts`)
```
MARGIN / MARGIN_FEE  = 채권매입 수수료
SYSTEM_FEE           = 시스템 이용료
TRANSFER_FEE         = 이체 수수료
FEE_ADJUSTMENT       = 차액 수수료
```
- 요율은 `rateBps`(bps), VAT 구분(`vatType`), 면세/과세(`TAX_FREE`/`TAXABLE`).
- 채권매입=면세계산서, 시스템·이체=세금계산서 (`TaxInvoiceTab.tsx`).

### 5-2. 차액 정산 카테고리 `AdjustmentCategory` (`types/settlement.ts`)
```
FEE_DIFF        = 수수료 차액
DELIVERY_DIFF   = 배달 차액
CANCEL_CLAWBACK = 취소 환수     ← 결제 취소 시 선지급금 회수
ESTIMATED_DIFF  = 예상매출 대사
CARRY_FORWARD   = 미회수 이월    ← 미회수 차액 다음 정산 차감
```
- 대사 상태: `ESTIMATED`(대사 대기) / `RECONCILED`(대사 완료) / `ADJUSTED`(차액 정산 완료) — `sales/[bizNo]/page.tsx`
- 수수료 확정: `feeType: "ESTIMATED"|"ACTUAL"`

### 5-3. 회수·미수
- 이체 유형에 `COLLECTION=회수`. 쿠콘 회수는 출금+입금 2건 페어 표시 (`TransferRecordsTab.tsx`).
- `CARRY_FORWARD`: "회수하지 못한 X원은 다음 정산에서 차감" (`BatchDetailTab.tsx`).
- 광고비 미수: `PreSettlementAdCharge` — `adAmount/recoveredAmount/outstandingAmount/status`.

### 5-4. 상태값
- 이체: `PENDING/COMPLETED/FAILED`
- 백필 배치: `RUNNING/COMPLETED/FAILED/UNKNOWN`, 소스 `CARD/BM/YO/CPE/ALL`
- 락계좌 검증: `NORMAL/ANOMALY/FAULT/SKIPPED/EXCLUDED` (`lib/platformSettlementConstants.ts`)
- 계약: `PENDING`(심사대기)/`APPROVED`·`ACTIVE`(승인)/`REJECTED`(반려)
- 계약 진행 6단계: 선지급계좌/정산계좌/사업자등록/신분증/외부계좌/계약서 (`types/merchant.ts` `ContractProgressSteps`)

> enum 값은 대부분 백엔드가 문자열로 내려주고 프론트는 `Record<string,{label,cls}>` 라벨 맵으로 매핑. 값의 원천은 Spring.

## 6. 리스크

| 리스크 | 영향도 | 대응 |
|---|---|---|
| 로그인 게이트 + 백엔드 의존 | 높음 | 쿠키 주입 우회로 레이아웃 확인, 데이터는 목킹 필요 |
| Node 버전 미고정 | 중 | Node ≥ 20.9 필요 (로컬 v26 확인 완료) |
| 구글 폰트 네트워크 의존 | 중 | 최초 실행은 인터넷 연결 상태에서 (캐시됨) |
| 사설 레지스트리/사내 패키지 | 없음 | 공개 npm만 사용 |
| 레거시 중복 경로 | 낮음 | `/settlement`,`/settlements`는 리다이렉트 껍데기 |

## 부록: 참고 파일 인덱스
- 설정: `next.config.ts`, `proxy.ts`(=미들웨어), `Dockerfile`, `.env.example`
- API/인증: `lib/config.ts`, `lib/apiClient.ts`, `services/authService.ts`, `app/api/spring/[...path]/route.ts`
- 네비/레이아웃: `components/AdminLayout.tsx`, `components/TabContext.tsx`
- 도메인: `types/settlement.ts`, `types/merchant.ts`, `lib/settlementLabels.ts`, `lib/platformSettlementConstants.ts`
