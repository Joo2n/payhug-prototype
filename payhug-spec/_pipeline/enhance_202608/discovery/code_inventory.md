# 페이허그 어드민 웹 — 코드 기반 화면 인벤토리

- 기준: `scratchpad/fresh-admin` develop HEAD `9e2741b` (2026-08-10, PR #13 머지 포함)
- 목적: Figma 화면설계서(AD_* 117시트, ~7/24 빌드 기준) 커버리지 대조
- 시트 목록: `scratchpad/sheet_list.json` (총 209, AD_* 117)

---

## ① 메뉴 트리 (역할 분기 포함)

출처: `components/AdminLayout.tsx` (navGroups L28–152, participantNavGroups L154–206, 분기 L351–357)

### 역할 분기 방식 (확정)
- 로그인 허용 userType 7종: `ADMIN, PAYHUG, PARTNER, SALES_ORG, SALES, AFFILIATE, INVESTOR` (`app/login/page.tsx` L53)
- **isAdmin** = `ADMIN | PAYHUG` → 전체 메뉴(navGroups)
- **isParticipant**(총판/참여자) = `PARTNER | SALES_ORG | SALES | AFFILIATE | INVESTOR` → 축소 메뉴(participantNavGroups)
- 별도 레이아웃/별도 라우트 없음. **같은 라우트를 공유**하고 페이지 내부에서 `getAdminUser().userType`으로 기능·탭·버튼을 가림
  - `readOnly` prop 전파: 가맹점 상세의 모든 카드 컴포넌트 (`canEdit = isAdmin`, `app/merchants/[id]/page.tsx` L152–155)
  - `lib/platformSettlementConstants.ts` L11: "readOnly(총판) 화면" 안내 문구 상수(PARTNER_CONTACT_HINT)
  - `/account-balance`는 비관리자 접근 시 차단 뷰 (L133)
  - 홈 대시보드: 총판이면 "총 가맹점"→"소속 가맹점", 시스템 상태 카드 숨김 (`app/page.tsx` L35, 53–71)
  - 정산 현황: 총판은 6탭 중 3탭만 (아래 ② 참고)
- 총판 어드민 UX 정비는 PR #9 `fix/partner-admin-merchant-view` (7/28–29 머지): 플랫폼 ID/PW 복사 버튼 제거, 락계좌 검증·빠른조회 확인 버튼 비노출, readOnly 가드 확대
- 참고: PR #13 브랜치명은 `feature/distributor-admin-web`이지만 **실제 내용물은 PAYHUG-162 선정산 결과 탭 개편**(8/6–8/10). 총판 분기 자체(participantNavGroups)는 2026-05-04 `bf5d1b9`부터 존재

### 관리자(ADMIN/PAYHUG) 메뉴 — 홈 + 3그룹 12항목
| 순서 | 그룹 | 라벨 | href |
|---|---|---|---|
| 0 | - | 홈 | `/` |
| 1 | 가맹점 | 가맹점 관리 | `/manage` |
| 2 | 가맹점 | 매출 조회 | `/sales` |
| 3 | 가맹점 | 1:1 문의 | `/inquiries` |
| 4 | 정산 | 정산 현황 | `/settlement/overview` |
| 5 | 정산 | 정산 상품관리 | `/settlement/policies` |
| 6 | 정산 | 정산 시뮬레이션 | `/settlement/simulation` |
| 7 | 관리자 | 모 계좌 잔액 조회 | `/account-balance` |
| 8 | 관리자 | 회원 관리 | `/partners` |
| 9 | 관리자 | 약관 관리 | `/terms` |
| 10 | 관리자 | 스크래핑 장애 이력 | `/scraping-incidents` |
| 11 | 관리자 | 활동 로그 | `/activity-logs` |
| 12 | 관리자 | AI 모니터링 어시스턴트 | `/log-analysis` |

### 총판/참여자 메뉴 — 홈 + 3그룹 4항목
| 순서 | 그룹 | 라벨 | href |
|---|---|---|---|
| 0 | - | 홈 | `/` |
| 1 | 가맹점 | 가맹점 관리 | `/manage` |
| 2 | 가맹점 | 매출 조회 | `/sales` |
| 3 | 정산 | 정산 현황 | `/settlement/overview` |
| 4 | 관리 | 회원 관리 | `/partners` |

### 셸(공통)
- **멀티탭 모드 상시 활성**: `app/layout.tsx` → `TabProviderWrapper` → `TabContext(isTabMode: true)`. 사이드바 클릭 시 페이지 이동 대신 상단 TabBar에 탭 추가(`components/TabBar.tsx`, `TabContent.tsx`)
- 사이드바 접기(72px)/그룹 접기, 모바일 햄버거, 백필(매출 수집) 진행 토스트 폴링(AdminLayout L233–345)

---

## ② 라우트별 화면 해부 (탭/모달/서브뷰)

`/settlement`·`/settlements`는 **`/settlement/overview`로 redirect** (각 page.tsx 12줄) — 시트 불필요.

### 1. `/login` — 관리자 로그인 (`app/login/page.tsx`)
- 폼 + 오류 토스트. 시트: **AD_LOGIN** ✓

### 2. `/` — 관리자 대시보드 (`app/page.tsx`, 491줄)
- 상단: 가맹점 카드(관리자=총 가맹점 / 총판=소속 가맹점) + 시스템 상태 카드(관리자만)
- 선정산 현황: 정산 플로우 KPI 6카드(순지급액→선정산 수수료→선정산 지급액 등) / 일별 선정산 추이 차트 / 하단 3열(매출구성·수수료 산정 현황·가맹점별 선정산 TOP5)
- 시트: **AD_HOME** ✓ (총판 변형은 미시트 — ④)

### 3. `/manage` — 가맹점 관리 (`app/manage/page.tsx`, 531줄)
- 필터 탭 5: 전체/심사대기/승인/반려/미등록 (FILTER_TABS L24)
- 모달: **부채 가맹점 등록**(L383, 관리자만) / **담당자 변경**(L445)
- 시트: AD_MERCHANT, _PENDING, _APPROVED, _REJECT, _NONE, _LEGACY, _ASSIGN ✓ 전부 대응

### 4. `/merchants/[id]` — 가맹점 상세 (`app/merchants/[id]/page.tsx`, 2,297줄) — 최대 화면
**카드 섹션** (탭 없음, 세로 나열 + 우측 설정열):
| 섹션 | 위치/컴포넌트 | 대응 시트 |
|---|---|---|
| 가맹점 기본 정보 | L1012 | AD_MERCHANT_DT ✓ |
| 계약(약관 동의·계약서·이전 계약서 펼침) | L1439~, `showContractHistory` | AD_MERCHANT_DT_OLDCONTRACT ✓ |
| 특이사항/메모 | `components/MerchantMemos.tsx` | AD_MERCHANT_DT ✓(내부) |
| 정산 상품 배정 | L1707 | AD_MERCHANT_DT ✓(내부) |
| 카드사별 수수료 관리 | `components/MerchantCardFees.tsx` | AD_MERCHANT_DT ✓ |
| 요일별 평균 매출 요약(상세 펼침) | `components/MerchantAvgSalesSummary.tsx` | AD_MERCHANT_DT_WEEKDAY ✓ |
| 락계좌 입금내역(빠른조회·엑셀) | `components/LockAccountDeposits.tsx` | **확인 필요** — ④ |
| 플랫폼 계정 관리(+락계좌 연결 상태) | `components/MerchantExternalAccounts.tsx`, `PlatformLockAccountStatus.tsx` | AD_MERCHANT_DT_PLATFORM ✓ |
| 이관 부채 관리 | `components/MerchantDebtManagement.tsx` | AD_MERCHANT_DT_DEBT ✓ |
| 카드 수수료 차액 정산 현황(통계 펼침) | `components/FeeAdjustmentSummary.tsx` | AD_MERCHANT_DT_ADJSTAT ✓ |
| 1:1 문의(가맹점 단위) | `components/MerchantInquiries.tsx` | AD_MERCHANT_DT ✓(내부) |
| 우측: 계약 진행 현황 L2147 / 정산 실행 설정 L2206 / 수수료 면제 L2236 / 회수 전용 L2265 | (관리자만) | AD_MERCHANT_DT ✓(내부) |

**모달/다이얼로그**:
| 모달 | 위치 | 대응 시트 |
|---|---|---|
| 가맹점 반려 | `rejectModalOpen` L113 | AD_MERCHANT_DT_REJECT ✓ |
| 계약 재서명 요청 | `resignModalContractId` L116 | AD_MERCHANT_DT_RESIGN ✓ |
| **계약 프로세스 초기화** | `resetModalOpen` L123, L1863 | **없음 — gap 후보** ④ |
| 유저 하드리셋 | `hardResetModalOpen` L124, L1958 | AD_MERCHANT_DT_HARDRESET ✓ |
| 비밀번호 초기화 | `passwordResetModalOpen` L136, L1920 | AD_MERCHANT_DT_RESET ✓ |
| 매출 데이터 수집(백필) | `backfillDialogOpen` L142 | AD_MERCHANT_DT_SCRAPE ✓ |
| **사업자 정보 등록/수정** | `BusinessEditModal` (`components/MerchantDocumentEditModals.tsx` L61) | **없음 — gap 후보** ④ |
| 신분증 등록/수정 | `IdentityEditModal` (동파일 L275) | AD_MERCHANT_DT_IDCARD ✓ |
| 입출금 계좌 등록/수정 | `BankAccountEditModal` (동파일 L476, purpose 분기) | AD_MERCHANT_DT_BANKACCT ✓ |
| 선정산 전용계좌 등록/수정 | 동일 모달 purpose 분기 | AD_MERCHANT_DT_LOCKACCT ✓ |
| 수동 이체 | `components/ManualTransferModal.tsx` | AD_MERCHANT_DT_TRANSFER ✓ |
| 플랫폼 락계좌 연결 상세 | `components/PlatformLockAccountDetailDialog.tsx` | AD_MERCHANT_DT_LOCKDETAIL ✓ |
| 락계좌 검증 확인(ConfirmDialog) | merchants/[id] 내 | AD_MERCHANT_DT_LOCKVERIFY ✓ |
| 카드 수수료 기본값 초기화(Confirm) | MerchantCardFees L155 | AD_MERCHANT_DT_FEERESET ✓ |
| 첨부 미리보기 | `components/AttachmentPreviewModal.tsx` | 미시트(보조 뷰어) — 낮은 우선순위 |
| 약관 동의 원문 미리보기 | `previewTerms` L112 | **확인 필요** ④ |

- 총판 접속 시 전 카드 `readOnly` + 조치 버튼 비노출 (PR #9)

### 5. `/merchants/[id]/fee-adjustments` — 카드 수수료 차액 정산 이력 (325줄)
- 통계 카드 4 + 상태 필터(대기/완료) 목록. 시트: AD_MERCHANT_DT_ADJUST, _ADJUST_DONE, _ADJUST_PENDING ✓

### 6. `/sales` — 매출 조회 (`app/sales/page.tsx`, 206줄)
- 가맹점 검색 리스트(정렬: 승인+정산활성 우선). 시트: **AD_SALES** ✓

### 7. `/sales/[bizNo]` — 매출 조회 > 가맹점 상세 (1,279줄)
- 필터/서브뷰: 기준일 토글(거래일/지급예정일 L483–484) · 거래상태(전체/정상/취소 L502) · 매출유형 5(전체/카드/배민/요기요/쿠팡이츠) · 카드사 2뎁스 칩(카드 선택 시) · 정렬(최신/오래된순) · 차액정산 내역 펼침(`showAdjDetail`) · 선정산 툴팁
- 모달: **수동 매출 등록**(`components/sales/ManualSalesModal.tsx` — 카드 승인/카드 매입/배달 3유형) / **엑셀 매출 업로드**(`components/sales/ExcelUploadModal.tsx`) / **등록 결과 요약**(`components/sales/ManualSalesResultSummary.tsx`, 두 모달 공용 결과 스텝)
- 시트: AD_SALES_DT + _PAYOUT, _CANCEL, _NORMAL, _BM, _CARD, _OLD, _ADJUST, _ADD_CARD, _ADD_PURCHASE, _ADD_DELIVERY, _EXCEL ✓ / 결과 요약 스텝은 **확인 필요** ④ (요기요·쿠팡이츠 필터 변형은 BM과 동일 패턴이라 gap으로 안 봄)

### 8. `/inquiries` — 1:1 문의 관리 (446줄)
- 상태 탭 5(전체/대기/처리중/답변완료/종료) + 카테고리 칩 5(일반/결제/정산/기술/계정) + 상세 메시지 스레드 드로어
- 시트: AD_INQUIRY + 상태 4종 + 카테고리 5종 + _DT ✓ 전부 대응

### 9. `/settlement/overview` — 정산 현황 (871줄 + 탭 파일 5개) — **탭 6개** (3개 아님)
| # | 탭 | 노출 | 파일 | 대응 시트 |
|---|---|---|---|---|
| 1 | 선정산 결과 | 전체 | `PreSettlementTab.tsx` (1,402줄) | AD_SETTLE (최신판 있음 — gap 아님) |
| 2 | 정산 상세 | **관리자만** | `BatchDetailTab.tsx` (928줄) | AD_SETTLE_DETAIL·_BATCH (최신판 있음) |
| 3 | 차액 정산 | 전체 | overview/page.tsx 내 `FeeAdjustmentTab` | AD_SETTLE_DIFF ✓ |
| 4 | 이체 내역 | 전체 | `TransferRecordsTab.tsx` (535줄) | AD_SETTLE_TRANSFER ✓ |
| 5 | 계산서 발행 | **관리자만** | `TaxInvoiceTab.tsx` (289줄) | AD_SETTLE_BILL (최신판 있음) |
| 6 | VOC 대응 | **관리자만** | `VocExportTab.tsx` (191줄) | AD_SETTLE_VOC ✓ |

→ **총판은 3탭**(선정산 결과·차액 정산·이체 내역)만 노출. 미정산 누락 추적도 관리자만(`enableMissedSettlements: isAdmin`).

- 선정산 결과 탭 내부: 요약 카드(선정산 제외액·대상액 포함, 8월 개편) / 일자별 아코디언 / 가맹점 건별 상세 펼침(AD_SETTLE_EXPAND ✓) / 플랫폼 차감·환급 섹션 / **미정산 누락 추적 배너**(AD_SETTLE_MISSED ✓) → 바로이체 미리보기 모달(AD_SETTLE_PREVIEW ✓)·바로이체 확인(AD_SETTLE_DIRECT ✓)·이미지급(기록만) 확인(AD_SETTLE_RECORD ✓) / 엑셀 다운로드(선정산요약·건별상세·플랫폼차감·플랫폼환급·미정산누락 시트)
- 차액 정산 탭 내부: KPI 4카드 + 일별 추이 차트 + **서브탭 6**(전체/카드 수수료 차액/배달 수수료 차액/취소 환수/예상매출 대사/미회수 이월) + 매출유형·카드사 2뎁스 필터 → AD_SETTLE_DIFF_CARD·_DELIVERY·_CLAWBACK·_ESTIMATED·_CARRY·_CARDFILTER ✓ 전부 대응
- 이체 내역 탭 내부: KPI(지급/회수×성공/실패) + 날짜별 그룹 + 회수(출금+입금) 2단계 페어 펼침 → AD_SETTLE_TRANSFER_COLLECT ✓

### 10. `/settlement/policies` — 정산 상품 관리 (655줄 + PolicyFormModal 469줄)
- 상품 그룹 펼침: 일반(GENERAL)/다우(DAOU) 분리, 참여자·수수료(MARGIN/SYSTEM_FEE/TRANSFER_FEE) 테이블
- 모달: 상품 생성/수정(`PolicyFormModal.tsx`), 비활성화 확인(L188), 완전 삭제 확인(L209)
- 시트: AD_PRODUCT, _GENERAL, _DAOU, _ADD, _EDIT, _DEACT, _DELETE ✓ 전부 대응

### 11. `/settlement/simulation` — 정산 시뮬레이션 (592줄)
- 섹션: 정책 선택 → 거래 입력(다건) → 결과(참여자 지급/건별 원장/SYSTEM_FEE 건별 합산/TRANSFER_FEE)
- 시트: AD_SIM, AD_SIM_MULTI ✓

### 12. `/settlements/[id]/fee-adjustments` — 선정산 #id 차액 정산 내역 (250줄)
- 통계 카드 4 + 내역 테이블. 시트: **AD_SETTLE_DIFFLIST** ✓ (제목 일치 "선정산 차액 정산 내역")

### 13. `/account-balance` — 모 계좌 잔액 조회 (800줄, **관리자 전용** — 비관리자 차단 뷰 L133)
- 잔액 카드 + 입·출금 내역(카테고리 배지) + **외부 입금 등록 모달**(L723)
- 시트: AD_BALANCE, AD_BALANCE_DEPOSIT ✓

### 14. `/partners` — 회원 관리 (1,477줄)
- 유형 필터: 전체 + 7종(투자자/페이허그/파트너/제휴사/영업/영업조직/관리자) → AD_PARTNER + _INVESTOR·_PAYHUG·_PARTNER·_AFFILIATE·_SALES·_SALESORG·_ADMIN ✓
- **가입 링크 생성** 카드(L735, 페이지 하단 상시 노출) — AD_PARTNER 시트에 포함됐는지 확인 필요(경미)
- 모달: 회원 등록/수정(L877, 관리자만 일부 필드), 프로필 관리(L250 — 인감·사업자등록증 첨부), 비활성화/삭제 확인(ConfirmDialog), 첨부 미리보기
- 시트: _ADD, _EDIT, _PROFILE, _DEACT, _DELETE ✓

### 15. `/terms` — 약관 관리 (522줄)
- 목록 + 컨텍스트 필터(`filterCtx` — 서버 컨텍스트: 회원가입/전자계약/마케팅 수신) + 설정 펼침(`showSettings` = 종류·컨텍스트 관리)
- 모달: 약관 개정(종류 선택/고정)·버전 수정(`revModal` L27), 버전 미리보기, 종류 추가/수정(`typeModal`), 컨텍스트 추가/수정(`ctxModal`), 버전 삭제 확인
- 시트: AD_TERMS, _SIGNUP, _CONTRACT, _MARKETING, _REVISE, _REVISE_FIXED, _VER_EDIT, _VER_DEL, _PREVIEW, _TYPE_ADD, _TYPE_EDIT, _CTX, _CTX_ADD, _CTX_EDIT ✓ 전부 대응

### 16. `/scraping-incidents` — 스크래핑 장애 이력 (325줄)
- 플랫폼별 현재 상태 카드(카드/배민/요기요/쿠팡이츠) + 장애 이력 목록(감지/예상 정산 중/해소/대사 완료)
- 시트: AD_SCRAPING ✓ (단일)

### 17. `/activity-logs` — 활동 로그 (365줄)
- 이벤트 유형 셀렉트(신규 회원가입·사업자등록·신분증·전자계약 등) + 행위자 배지(관리자/사용자/시스템)
- 시트: AD_LOG ✓ (단일)

### 18. `/log-analysis` — AI 모니터링 어시스턴트 (439줄)
- 시간범위 프리셋/직접 지정 + 채팅형 질문/스트리밍 응답
- 시트: AD_AI, _CUSTOM, _ANSWER ✓

---

## ③ 7월 초 이후 변경 (화면설계서 7/24 빌드 이후가 gap 최우선)

커밋 84개 (`git log --since=2026-07-01`). 신규 파일 및 화면 영향 변경:

### 신규 파일 (7/1 이후 추가)
| 파일 | 추가일 | 내용 |
|---|---|---|
| `app/settlement/overview/TaxInvoiceTab.tsx` | 7/16 | 계산서 발행 탭 신설 → AD_SETTLE_BILL 최신판 존재 |
| `components/settlement/SortOrderButton.tsx` | 7/16 | 정렬 토글 공통화 |
| `components/PlatformLockAccountStatus.tsx` `PlatformLockAccountDetailDialog.tsx` `lib/platformSettlementConstants.ts` | 7/17 | 플랫폼 락계좌 검증 UI → AD_MERCHANT_DT_LOCKVERIFY/_LOCKDETAIL 존재 |
| `components/sales/ManualSalesResultSummary.tsx` `lib/manualSalesResult.ts` | **7/24** | 수기/엑셀 등록 **결과 화면 공용화** — 시트 미확인 |
| `lib/settlementLedger.ts` | 8/7 | 정산 상세 엑셀 개선(비화면) |

### 7/24 이후 화면 영향 변경 (시트 빌드 이후)
- **7/24–29 매출 수기등록**: 결과 요약 UX 통일(단건=엑셀 동일), 엑셀 업로드 모달 구분 열 추가, 배달(매입취소) 스킵 사유 라벨, 취소 확인 UI (PR #6·#8)
- **7/28–29 총판 어드민 정비** (PR #9): 락계좌 검증·빠른조회 버튼 비노출, ID/PW 복사 버튼 제거, readOnly 가드 확대, ANOMALY/FAULT 색상, SKIPPED 카드 스타일
- **8/1–8/8 정산 상세 탭**: 우리가게클릭비 부호·광고비 회수 상태/회수액 컬럼(8/3 `00b16ac`), 회수액 배치별 값(PAYHUG-152/158/164) → AD_SETTLE_DETAIL 최신판 존재로 gap 아님
- **8/5**: 가맹점 승인 계약 순서 무관 처리(로직만)
- **8/6–8/10 선정산 결과 탭 대개편** (PAYHUG-162, PR #13): 선정산 제외액·대상액 컬럼 신설, 컬럼 재배치, 정산 상태 배지 6종, 플랫폼 차감/환급 펼침 섹션, 엑셀 4시트(+미정산누락) → AD_SETTLE 최신판 존재로 gap 아님

---

## ④ Gap 후보 표

전제: AD_SETTLE / AD_SETTLE_DETAIL / AD_SETTLE_BILL은 최신판 시트 별도 제작됨(정산 현황 3탭) — gap 아님.

| # | 등급 | 항목 | 코드 위치 | 근거 / 매칭 시도 |
|---|---|---|---|---|
| G1 | **gap 유력** | **총판(참여자) 어드민 화면군 전체** | `components/AdminLayout.tsx` L154–206·L351–357, `app/page.tsx` L35, `app/settlement/overview/page.tsx` L101–132, `app/merchants/[id]/page.tsx` L152–155, `lib/platformSettlementConstants.ts` | AD_* 117시트는 전부 관리자 시점. 총판 로그인 시 메뉴 5개·정산현황 3탭·가맹점 상세 readOnly·홈 "소속 가맹점" 변형이 존재하나 대응 시트 없음. 총판 UX 정비(PR #9)는 7/28–29로 시트 빌드 이후 |
| G2 | **gap 유력** | **계약 프로세스 초기화 모달** | `app/merchants/[id]/page.tsx` L790–793(버튼)·L1863–1908(모달) | 초기화 계열 시트 3종(_RESET=비밀번호, _HARDRESET=유저, _FEERESET=카드수수료)과 전부 별개 개념. "계약 프로세스 초기화" 시트 없음 |
| G3 | **gap 유력** | **사업자 정보 등록/수정 모달** | `components/MerchantDocumentEditModals.tsx` L61 `BusinessEditModal` (OCR 오버레이 포함) | 같은 파일의 신분증(_IDCARD)·계좌(_BANKACCT/_LOCKACCT) 모달은 시트가 있는데 사업자 정보만 없음 |
| G4 | 확인 필요 | 수기/엑셀 등록 **결과 요약 스텝** | `components/sales/ManualSalesResultSummary.tsx` (7/24 신규, 7/26–29 보강) | _ADD_CARD/_ADD_PURCHASE/_ADD_DELIVERY/_EXCEL 시트가 입력 스텝만 담았는지 결과 스텝까지 담았는지 시트 이미지 확인 필요. 시트 빌드일과 같은 날 추가라 미반영 가능성 높음 |
| G5 | 확인 필요 | 락계좌 입금내역 카드 (빠른조회 상태·엑셀 다운로드) | `components/LockAccountDeposits.tsx` (가맹점 상세 내 섹션) | 락계좌 시트 3종은 검증/연결/등록만. 입금내역 카드가 AD_MERCHANT_DT 본판 캡처에 포함됐는지 확인 필요 (7/29 엑셀 페이징 보강 있음) |
| G6 | 확인 필요(경미) | 가맹점 상세의 약관 동의 원문 미리보기 모달 | `app/merchants/[id]/page.tsx` L112 `previewTerms` | AD_TERMS_PREVIEW는 약관 관리 메뉴의 버전 미리보기라 다른 화면. 가맹점 상세 쪽 미리보기는 시트 불명 |
| G7 | 확인 필요(경미) | 회원 관리 "가입 링크 생성" 카드 | `app/partners/page.tsx` L735 (7/22 상위 조직 노출 제거) | 별도 시트 없음 — AD_PARTNER 본판에 포함됐는지 확인 필요 |
| G8 | 확인 필요(경미) | 멀티탭 셸(TabBar) — 탭 열기/닫기/전환 | `components/TabBar.tsx`, `TabContext.tsx`, `app/layout.tsx` L28 | 상시 활성인 내비게이션 패러다임인데 시트가 이를 표현하는지 불명 (화면설계서 성격상 생략 가능) |
| G9 | 비대상(참고) | 첨부 미리보기 모달, error/loading 화면 | `components/AttachmentPreviewModal.tsx`, `app/error.tsx`, `app/loading.tsx` | 보조 뷰어/시스템 화면 — 통상 시트화 대상 아님 |
| G10 | 비대상(참고) | 매출 상세 요기요/쿠팡이츠 필터 변형 | `app/sales/[bizNo]/page.tsx` L18–23 | _BM 시트와 동일 패턴의 값 차이 — 변형 시트 불필요 판단 |

### 역방향(시트→코드) 검증
- AD_* 117개 전수 대조 결과 **코드에 없는 시트는 0개** — 모든 시트가 현행 라우트/탭/모달에 대응됨 (AD_SETTLE_DIFFLIST → `/settlements/[id]/fee-adjustments`, AD_SETTLE_RECORD/_DIRECT/_PREVIEW/_MISSED → PreSettlementTab의 MissedSettlementsBanner 계열로 확인)
