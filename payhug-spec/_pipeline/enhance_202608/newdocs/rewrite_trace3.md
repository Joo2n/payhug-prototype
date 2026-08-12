# 부록(비노출) — rewrite_settle3.md 한글 개념 ↔ 원 근거 대응표

본 파일은 문서 비노출용. `rewrite_settle3.md` 본문에서 제거한 개발 식별자·코드 추적 정보(파일:줄)·화면 ID·캡처 파일명을 보존한다.

- 기준 코드: payhug-admin-web develop `9e2741b` (2026-08-10, PAYHUG-162 계열 머지 포함)
- 파일 경로 축약: `PreSettlementTab` = `app/settlement/overview/PreSettlementTab.tsx`, `BatchDetailTab` = `app/settlement/overview/BatchDetailTab.tsx`, `TaxInvoiceTab` = `app/settlement/overview/TaxInvoiceTab.tsx`, `page` = `app/settlement/overview/page.tsx`, `hook` = `hooks/useSettlementOverview.ts`, `types` = `types/settlement.ts`, `labels` = `lib/settlementLabels.ts`, `ledgerLib` = `lib/settlementLedger.ts`
- 원 원고: 같은 폴더 `settle3_content.md` (사실관계 원본)

## 0. 캡처 번호 ↔ 파일·노드

| 본문 표기 | 파일 | Figma 노드 | 내용 |
|---|---|---|---|
| 캡처 3907 | `newdocs/scr_3907.png` | `3907:2` | 선정산 결과 탭 전체 |
| 캡처 3905 | `newdocs/scr_3905.png` | `3905:2` | 정산 상세 탭(배치 미선택) |
| 캡처 3906 | `newdocs/scr_3906.png` | `3906:2` | 계산서 발행 탭 |
| (참고) | `scr_3911.png` / `scr_3910.png` / `scr_3909.png` | `3911:2` / `3910:2` / `3909:2` | 차액 정산 / 이체 내역 / VOC 대응 (2/2 원고 범위) |

## 1. 화면 한글명 ↔ 화면 ID

| 본문 한글명 | 화면 ID |
|---|---|
| 정산 현황 > 선정산 결과 탭 | AD_SETTLE |
| 정산 현황 > 정산 상세 탭 (묶음 선택 상태) | AD_SETTLE_DETAIL (AD_SETTLE_DETAIL_BATCH) |
| 정산 현황 > 차액 정산 탭 | AD_SETTLE_DIFF |
| 정산 현황 > 이체 내역 탭(매출 회수 포함) | AD_SETTLE_TRANSFER / AD_SETTLE_COLLECT |
| 정산 현황 > 계산서 발행 탭 | AD_SETTLE_BILL |
| 건별 펼침 / 미정산 누락 / 바로이체 미리보기 / 바로이체 확인 / 이미지급 확인 | AD_SETTLE_EXPAND / _MISSED / _PREVIEW / _DIRECT / _RECORD |
| 매출 조회 상세 | AD_SALES_DT |
| 가맹점 상세 > 차액 정산 현황 · 이력 / 차액 정산 목록 | AD_MERCHANT_DT_ADJSTAT / _ADJUST, AD_SETTLE_DIFFLIST |
| 어드민 홈 | AD_HOME |
| 정산 상품 관리(일반 · 다우) | AD_PRODUCT (_GENERAL/_DAOU) |
| 정산 시뮬레이션(단건 · 복수) | AD_SIM / AD_SIM_MULTI |
| 파트너 관리(소개 정보 포함) | AD_PARTNER (_PROFILE) |
| 모계좌 잔액 | AD_BALANCE |
| 가맹점 앱 > 미리 받는 돈(카드 · 배달 상세 포함) | ST_MA (+_CARD/_CARD_DT/_DELIV/_DELIV_DT) |
| 가맹점 앱 > 예상 지급 차액(말풍선 안내 세 종 포함) | ST_DIFF (+툴팁 3종) |
| 가맹점 앱 > 계좌 입금 내역 · 선정산 제외액 내역 | ST_AC / ST_AC_EX |
| 가맹점 전자계약(채권 매입 계약) | MC_CONTRACT_SIGN 계열 |
| 충돌 대장 1번 / 2번 / 4번, '회수' 구분 | C1 / C2 / C4, C5 (`analysis/00_종합.md`) |

## 2. 탭 1(선정산 결과) — 개념 ↔ 필드 ↔ 근거

### 용어·산식 항

| 한글 개념 | 원 식별자 | 근거 |
|---|---|---|
| 선정산 대상액 | `preSettlementTargetAmt` | types:237-238 |
| 선정산 제외액 | `preSettlementExcludedAmt` | types:229-245 |
| 바로이체 | `DIRECT_PAYOUT`, `directTransferAmt` | types:239-245 |
| 이미지급 | `DIRECT_PAYOUT_RECORD`, `recordOnlyAmt` | types:239-245 |
| 선정산 수수료 | `preSettlementFeeAmt` | PreSettlementTab:471 |
| 채권매입 수수료 / 시스템 이용료 / 이체 수수료 / 차액 대상 수수료 | `marginFeeAmt` / `systemFeeAmt` / `transferFeeAmt` / `adjMarginFeeAmt` | labels:9-23, PreSettlementTab:674-688 |
| 정산 반영 수수료 차액 | `adjustmentAmt` (지급일 기준) | types:323-324 |
| 거래 수수료 차액 | `feeDiffAmt` (거래일 기준) | types:356-363 |
| 배분 수수료 차액 | `payout.feeAdjustment` | BatchDetailTab:628 |
| 오프라인 차감 | `offlineDeductionAmt` | PreSettlementTab:698-700 |
| 플랫폼 차감 / 환급 | `adDeductionAmt` / `refundAdditionAmt`+`cpcRefundAmt` (`adCharges`/`adRefunds`) | types:308-314, PreSettlementTab:57-59 |
| 검증 차이 | `unexplainedDiffAmt` | types:321-322, PreSettlementTab:714-724 |
| 수수료 면제 | `feeExempt` | types:319-320, PreSettlementTab:682-686 |
| 미정산 누락 | `missed-settlements` | hook:346-358 |
| 정책 요율 자리(미사용) | `policyRate` | types:304 |
| 카드 원장 수수료 차액(부호 반대) | `fee_adjustment_amt` (예상−실제) | types:356-363 |

### 산식 근거

| 본문 산식 | 근거 |
|---|---|
| 산식 1 선정산 지급액(6항, 0항 생략, 카드 부제=검증 차이 안내 공유 상수 `PAYOUT_TERMS`) | PreSettlementTab:63-71, 413-420 |
| 산식 2 순 지급액(취소 차감 안내) | PreSettlementTab:445-455 |
| 산식 3 제외액 부호 규약·잔차 안내·엑셀 머리글 "(-제외/+확인 필요)" | types:229-245, PreSettlementTab:456-469, 754-763, 259 |
| 산식 4 수수료 4종·면제 | PreSettlementTab:471, 674-688; labels:9-23 |
| 산식 5 거래 수수료 차액·배달 원장 부재 | types:356-363 |
| 산식 6 검증 차이 | types:321-322, PreSettlementTab:714-724 |
| 규약 1 플랫폼 차감 구성=원금, '구성 미상' | PreSettlementTab:801-928, types:310-314 |

### 정책·케이스·구성 근거

| 본문 서술 | 근거 |
|---|---|
| 6탭 구성·내부 전용 3탭 | page.tsx:270-325 |
| 진입 자동 조회(이번 달 1일~오늘) | page.tsx:106-112, hook:413-422 |
| 총판 노출·미정산 누락 내부 전용 (`enableMissedSettlements: isAdmin`, `showMissedSettlements`) | page.tsx:127-133, 474 |
| 이전 주소 리다이렉트 (`/settlement`·`/settlements`→`/settlement/overview`) | discovery/code_inventory.md ② |
| 공통 필터 바·동적 에이전시 | page.tsx:328-364 |
| 필터 재집계(`aggregateDayOverview`, 차액 건수 0 처리·Σ`adjustmentAmt` 복원) | page.tsx:33-89, 223-238 |
| 정렬·엑셀 버튼 | PreSettlementTab:430-438 |
| 요약 카드 8장 | PreSettlementTab:442-481 |
| 차액 배너·필터 시 숨김 | PreSettlementTab:484-517, page.tsx:82-87 |
| 미정산 누락 배너·3단 목록 | PreSettlementTab:1008-1160 |
| 날짜 아코디언·9단 분해 | PreSettlementTab:525-583 |
| 가맹점 행 10컬럼 | PreSettlementTab:588-728 |
| 건별 12컬럼+플랫폼 차감·환급+대기 차액 | PreSettlementTab:1251-1402 |
| 조회 1회(`GET /admin/settlement/pre-settlement-summary`) | hook:155-174 |
| 펼침 재조회(`GET pre-settlement-detail/{bizNo}`, 1행만) | page.tsx:135-144, hook:176-205 |
| 응답 전체 보존 원칙(`adRefunds` 소실 전력) | hook:190-199 |
| 누락 처리(`POST missed-settlements/resolve`, TRANSFER/RECORD_ONLY, preview) | hook:360-410 |
| 합산 1회 이체·거래일별 기록 | PreSettlementTab:1211-1232 |
| 엑셀 5시트 | PreSettlementTab:152-363 |
| 상태 3종·6종 배지 | PreSettlementTab:36-50 |
| '정산 미반영' 배지=`eligible === false`만(리터럴 비교 폐기) | PreSettlementTab:868-875 |
| case2 잔차 상쇄(가맹점별 OR 판정) | PreSettlementTab:564-566, 754-763 |
| case4 이월 사례(민속보쌈 0원+372,300) | 원 원고 ⑥ |
| case5 이틀 규칙 문구 | PreSettlementTab:1035-1039 |
| case6 예정일 경과=추정 | PreSettlementTab:1038 |
| case7 부분 실패 상태 | hook:373-385 |
| 모집단 3쌍 | PreSettlementTab:183-186, 1268 |
| 동명 필드 반대 부호(`AdDeduction.adAmount` 절댓값 vs `PreSettlementAdCharge.adAmount` 부호) | types:127-133 vs 422-428 |
| C2 정산일/매출일 표기 | PreSettlementTab:542-551 |
| C5 '회수' 3종 | labels:57-66 |

## 3. 탭 2(정산 상세) — 개념 ↔ 필드 ↔ 근거

| 한글 개념 | 원 식별자 | 근거 |
|---|---|---|
| 정산 묶음 | `Batch` (COMPLETED/OPEN/PENDING), `closedAt` | BatchDetailTab:330-413 |
| 배분 | `payout` (margin/systemFee/transferFee/feeAdjustment/totalPayout) | types:75-92 |
| 수수료 장부 | `ledger` (revenue/cost/profit/profitVat/passthrough/passthroughVat/netProfit/payout) | types:75-92 |
| 실 지급 | `payout.totalPayout` (즉석 계산 폐기) | BatchDetailTab:311-316, 449-453 |
| 전달금 | `passthrough` (+`passthroughVat`) | types:75-92 |
| 재귀속 | `ledgerLib` 표시 보정, MARGIN·FEE_ADJUSTMENT만, payout 불변 | ledgerLib:14-69 (조건 41-68, 유형 15) |
| 납부자/전달금 배지 | payout<0 SYSTEM_FEE/TRANSFER_FEE, passthrough>0 | BatchDetailTab:850-894 |
| 차감액(조정 원금) | `adAmount` (서버 .abs) | types:126-146 |
| 정산 묶음 회수액 | `recoveredAmount` (회수 원장 take), Σ=`adDeductionAmount`는 V57 배포 이후만 | types:126-146, BatchDetailTab:77-80, 559-603 |
| 미회수 차액 이월 | `CARRY_FORWARD` | BatchDetailTab:458-469, hook:265 |
| 부채상계 | `DEBT_OFFSET` (발동 조건 코드 없음) | BatchDetailTab:28 |
| 기록용 | `RECORD_ONLY` | BatchDetailTab:32-37, 663-671 |
| 역할 8종 | `roleLabel` 맵 (INVESTOR/PAYHUG/UPPER/LOWER/SALES 3종/MERCHANT) | page.tsx:242-245 |
| 배분 상태 5종 | 이체완료·이체대기·이체실패·부채상계·기록용 | BatchDetailTab:24-37 |

### 구성·로직·케이스 근거

| 본문 서술 | 근거 |
|---|---|
| 내부 전용·탭 미렌더 | page.tsx:270-281, 497; 총판 3탭 = code_inventory ②-9 |
| 진입 자동 조회·클릭 로드 | page.tsx:172-185, 512-515 |
| 좌 목록 그룹핑·"(미정산)" | BatchDetailTab:330-413, 344-346, 12-22 |
| 우 헤더 병기 | BatchDetailTab:418-456 |
| 조건부 3구역 | BatchDetailTab:458-607 |
| 배분 요약 표 | BatchDetailTab:609-675, 24-37 |
| 장부 아코디언 3층 | BatchDetailTab:744-928 |
| 정렬·엑셀 4시트 | BatchDetailTab:216-292 |
| 2단 조회(`GET batches` → `batches/{id}/payouts` → `/ledgers`) | hook:232-272 |
| 필터(가맹점명·`merchantId`·사업자번호) | BatchDetailTab:70-75 |
| 시스템 이용료 건별 합산(payee+role) | BatchDetailTab:716-742 |
| 엑셀 일괄(`GET batch-payouts`/`batch-ledgers`, 부분 실패 내성) | BatchDetailTab:98-109, hook:274-290 |
| 산식 4 Σ(role=MERCHANT feeAdjustment) | BatchDetailTab:311-314, 441-448 |
| 산식 5 백필 사유 표시·회수액<차감액 상태 무관·차감액 열 합계 없음 | BatchDetailTab:559-603, 560-566, 582-586, 596-601 |
| case7 엑셀 재귀속 반영(감사 차이) | BatchDetailTab:150-175 |
| "계산서는 가맹점 단위 발행" 주석 | BatchDetailTab:177 |
| C2 마감 시각(mock closedAt 04:30대) | 원 원고 ⑤ |

## 4. 탭 3(계산서 발행) — 개념 ↔ 필드 ↔ 근거

| 한글 개념 | 원 식별자 | 근거 |
|---|---|---|
| 발행 단위 | 가맹점 × `payeeUserId` × `feeType` | types:180-205 |
| 항목 | `feeType` = MARGIN / SYSTEM_FEE / TRANSFER_FEE | types:180-205 |
| 면세/과세 판정 | `taxType` = TAX_FREE / TAXABLE (서버 판정) | types:189-193, hook:329-344 |
| 기준액 | `baseAmount` (이체 수수료는 null) | types:180-205 |
| 머리글 선정산 대상 합계 | `totalSalesAmount` (행 `baseAmount`와 별개 — 일치 여부 확인 필요) | types:237-238 주석, 원 원고 ④(6) |
| 공급가액/세액/합계 | `supply` / `vat` / `total` | types:180-205 |
| 이체 횟수 | `batchCount` | TaxInvoiceTab:24-29 |
| 발행 주체 배지 | `isBusiness` (법인/사업자) | 원 원고 ⑤·⑥ |

### 구성·로직·케이스 근거

| 본문 서술 | 근거 |
|---|---|
| 내부 전용·탭/콘텐츠 미노출 | page.tsx:302-313, 477-486 |
| 자동 조회(fetchTaxInvoiceSummary) | page.tsx:151, 182-184; hook:329-344 |
| 발행 실행 없음·탭 라벨 '계산서 발행' | page.tsx:311 |
| 안내문·엑셀 버튼 | TaxInvoiceTab:156-164 |
| 가맹점 펼침 카드 | TaxInvoiceTab:166-190 |
| 매출유형 요약 표(이체 수수료 rowSpan) | TaxInvoiceTab:194-227 |
| 발행 내역 표·정렬·tfoot | TaxInvoiceTab:20-39, 229-281 |
| 비고 배지 2종(emerald/blue) | TaxInvoiceTab:15-18 |
| 단일 호출(`GET /admin/settlement/tax-invoice-summary`)·표시 전용 | hook:329-344, types:180-209 |
| 클라이언트 필터 | TaxInvoiceTab:76-83 |
| 엑셀 2시트 | TaxInvoiceTab:93-154 |
| 산식 2 요율 역산·반올림·"-" | TaxInvoiceTab:22-33 (인용 금지 캐비엇 30-33) |
| 산식 3 단가×N회/정액 | TaxInvoiceTab:24-29 |
| 산식 5 발행 합계 Σ`invoiceRows.total` | TaxInvoiceTab:168, 273-279 |
| 이체 수수료 단가 불일치(300원/배치 vs 500원/일 — mock 내) | 원 원고 ⑤ |
| 요율 실값 사례(1.004%·0.402%)·mock seed(0.6/0.3/0.1%+300원) | 원 원고 ⑤ |

## 5. 본문에 잔존시킨 라틴 문자 표기

- `VOC` — 탭 이름 고유명사(지시서 허용).
- 그 외 화면 ID·필드명·상수·파일:줄·API 경로·`C1` 등 충돌 번호는 본문에서 전량 제거("충돌 대장 1·2·4번"으로 표기), 본 부록에만 보존.
