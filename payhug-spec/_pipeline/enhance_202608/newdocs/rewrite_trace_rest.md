# 대응표 — rewrite_settle_rest.md 코드 추적 · 영문 원어 매핑 (2/2)

- 기준 코드: `fresh-admin` develop `9e2741b` (2026-08-10, PAYHUG-162 포함). 줄번호는 이 커밋 기준.
- 파일 약어: OV = `app/settlement/overview/page.tsx` / TY = `types/settlement.ts` / LB = `lib/settlementLabels.ts` / LG = `lib/settlementLedger.ts` / HK = `hooks/useSettlementOverview.ts`. 탭 컴포넌트(TransferRecordsTab·VocExportTab·PreSettlementTab·BatchDetailTab)는 `app/settlement/overview/` 하위.
- 본문(rewrite_settle_rest.md)은 순한글 원고 — 개발 식별자·코드 근거는 전부 이 표에서만 관리.

## 0. 공통 — 쟁점 번호 · 원고 전반 매핑

| 본문 표기 | 원어(레지스터/코드) | 비고 |
|---|---|---|
| 쟁점 1 (수수료율) | 충돌 레지스터 C1 | `analysis/00_종합.md` |
| 쟁점 2 (지급 캘린더) | C2 (계약 "매일" vs 운영 D+1 vs DB D+2) | 〃 |
| 쟁점 4 (예상 지급 차액) | C4 | 〃 |
| 쟁점 5 (매출 회수 ≠ 과지급 회수) | C5 | 〃 |
| (확정)/(가설)/(확인 필요) | [확정]/[가설]/[확인 필요] | 원원고 표기 계승 |
| 총판 5역할 (파트너·영업조직·영업·제휴·투자자) | PARTNER / SALES_ORG / SALES / AFFILIATE / INVESTOR | — |
| 관리자 게이트 | isAdmin | 탭·배너 노출 조건 |

## 1. 주제 ① 차액 정산 탭

### 화면·조회
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 화면 주소·탭 | `/settlement/overview` 3번째 탭 | OV:282-291(게이트 없음) |
| 진입 시 1회 자동 조회 | — | OV:176-178 |
| 조회 통신 | `GET /admin/settlement/fee-adjustment-dashboard?dateFrom&dateTo(&cardCorp&salesSource)` | HK:292-310 |
| 카드사 선택지(전체 기준) | `availableCardCorps` | HK:303 |
| 매출 유형·카드사 단추 | salesSource / cardCorp 복수 선택 | OV:366-408, 413-453 |
| 매출 유형 안내 문구 | — | OV:374-377 |
| 필터 가드(카드 해제→카드사 초기화) | — | OV:187-190 |
| 서버 반영 필터 즉시 재조회 | — | OV:192-202 |
| 에이전시·가맹점명 = 목록만 필터 | 클라이언트 필터 | OV:610-616 |
| 요약 지표 카드(1+대분류 수, 주석 "4개") | KPI 카드 | OV:682-720 |
| 일별 추이 차트(3계열·2일 이상) | — | OV:723-750 |
| 하위 탭 6종 | 전체/FEE_DIFF/DELIVERY_DIFF/CANCEL_CLAWBACK/ESTIMATED_DIFF/CARRY_FORWARD | OV:756-772, TY:457, OV:544-550 |
| 상세 목록 항목 | — | OV:794-867 |
| 정렬(거래일→등록 순번) | date → id 2차 정렬 | OV:621-624 |
| 엑셀 "차액정산" 12항목·부호 부여 | — | OV:626-663 |
| 미회수 이월 규칙 문구 | — | BatchDetailTab.tsx:459-468, `settlements/[id]/fee-adjustments/page.tsx`:239-244 |

### 용어·산식
| 본문 용어 | 원어/필드 | 코드 근거 |
|---|---|---|
| 전체 차액(순액) | `summary.netAmount = totalRefundAmt − totalDeductAmt` (서버) | TY:468-475 |
| 대분류 순액 | `cat.netAmount` (서버, `summary.categories`) | TY:459-466 |
| 건별 차액 | `AdjustmentDetail.adjustmentAmt` (절댓값), `estimatedFee` vs `actualFee` | TY:485-503, 496-498 |
| 표시 부호(환급 +) | `isRefund ? "+" : "-"` | OV:814, 841-845 |
| 유형 8종 | REFUND/DEDUCT 계열 8종 정의 | OV:552-561 |
| 대기 중 / 반영 완료 | PENDING / APPLIED | OV 상태 표기 |
| 거래 수수료 차액 | `PreSettlementTransaction.feeDiffAmt` | TY:356-363 |
| 정산 반영 수수료 차액 | `PreSettlementMerchant.adjustmentAmt` | TY:323-324 |
| 배분 수수료 차액 | `Payout.feeAdjustment` | TY:70, BatchDetailTab.tsx:628 |
| 차액 대상 수수료(표식 "차액대상") | `adjMarginFeeAmt` / feeType `FEE_ADJUSTMENT` | TY:226, LB:22 |

## 2. 주제 ② 이체 내역 · VOC 대응 탭

### 이체 내역
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 화면 주소·탭 | `/settlement/overview` 4번째 탭 | OV:292-301(게이트 없음), 자동 조회 OV:179-181 |
| 조회 통신 | `GET /admin/settlement/transfer-records?dateFrom&dateTo` | HK:312-327 |
| 정렬·엑셀 | — | TransferRecordsTab.tsx:284-288 |
| 요약 지표 4카드 | KPI | :291-316 |
| 날짜별 카드·0원 숨김 | — | :319-346 |
| 짝 매칭(가맹점+금액, 선점) | merchantId + amount, 쿠콘 출금이체 API 02003700 + 입금이체 02001110 | :24-87 (선점 :55-68) |
| 짝 대표 금액=출금액 | `group.withdrawal.amount` | :89-91 |
| 짝 대표 상태 규칙 | SUCCESS/CONFIRMED→성공, 실패 우선, 그 외 출금 상태 | :93-100 |
| 이체 유형 3종 | DISBURSEMENT / COLLECTION / ADMIN_MANUAL | :106-109 (수동 지급 라벨 :21) |
| 요약 지표 재계산(짝 묶음 후) | 서버 집계 미사용 | :131-164 |
| 전체 실패 = 실패 상태만 | `totalFailedCount/totalFailedAmount`, FAILED만 | :144, 160-161 |
| 날짜 머리글 실패 = 비성공 잔여 | `bucket.failed` | :117-129 (낡은 주석 :116) |
| 상태 5종 | SUCCESS/CONFIRMED/FAILED/요청중/타임아웃 | :10-16 |
| 실패 행 오류 문구(20자 말줄임) | 쿠콘 오류 메시지 | :420-426 |
| 회수 2단계 펼침(락계좌→미지급계정→모계좌) | — | :432-535 (계정 라벨 :300, 494-517) |
| 엑셀 원천 11항목(짝 미묶음) | — | :229-263 |
| 화면 필터(지표도 재계산) | 에이전시·가맹점명·ID·사업자번호 | :211-223 |
| 지급/회수 성공 금액 | `disbursement.amount` / `collection.amount` 합 | :146-152 |
| 전체 성공 | `totalSuccess` / `totalSuccessAmount` | :143, 158-159 |

### VOC 대응
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 탭 위치(공용 필터 미사용·관리자 전용) | isAdmin 게이트 | OV:329, 314-325, 455 |
| 조회·다운로드 | `checkVocData` / `downloadVocExcel` (`services/settlementService`), 가맹점 목록 `fetchMerchants` | VocExportTab.tsx:43-75 |
| 카드 구성 | — | :87-139 |
| 가맹점 후보(승인+사업자번호) | APPROVED && bizNo | :26-31 |
| 조회 결과 상자·다운로드 완료 안내 | `hasData`, 결과 표시 | :147-180, 181-185 |
| 오류 빨간 상자 | — | :141-145 |
| 상태 초기화 | — | :37-41, 92, 111, 120 |
| 무음 실패(가맹점 목록) | `catch(() => {})` | :33 |
| 실지급 합계 | `checkResult.totalPayout` | 정의 서버 확인 |
| 라벨 3곳 동기화 | 프론트 `PLATFORM_ADJUSTMENT_TYPES` / 서버 `MerchantPlatformAdjustment.ITEM_*` / 보고서 `VocExcelService.platformAdjLabel` | LB:29-35 주석 |
| 표시 전용 항목 3종 | display_only — "광고비 보전"의 원어 = CPE 광고비 | LB:45-49 |
| 보고서 산식 | 서버 `VocExcelService` 소관 | — |

## 3. 주제 ③ 미정산 누락 추적

| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 배너 위치·펼침 | PreSettlementTab 상단 | PreSettlementTab.tsx:1008-1160 |
| 관리자 전용 조회·표시 | `enableMissedSettlements: isAdmin` | OV:131-133(사유 주석 :131), 표시 OV:474 |
| 조회 통신(기간 없음 = 전 기간) | `GET /admin/settlement/missed-settlements` | HK:349 |
| 처리·미리보기 | `POST …/resolve` / `POST …/resolve/preview`, `uplIds`, action=TRANSFER\|RECORD_ONLY | HK:360-410 |
| 배너 머리글 | — | :1010-1033 |
| 고지 문구(이틀 규칙·입금 추정) | — | :1035-1039 (이틀 문구 :1036) |
| 실행 줄(선택·3버튼) | — | :1044-1080 |
| 3단 목록 | — | :1082-1150 |
| 미리보기 창(무부작용 고지·3지표·가맹점별 카드) | preview | :1162-1249 (묶음 문구 :1212), 타입 주석 TY:588 |
| 확인 창 2종 문구 | — | :981-1006 |
| 처리 흐름(재조회·부분 실패 문구·선택 유지) | — | HK:373, 376-381, :998-1003 |
| 이체 묶음 규칙(합산 1회·원장 거래일별) | `transferAmount` / `transferCount` | TY:596-608 (금액 :600-601, 횟수 :602-603) |
| 선택 합계 | `Σ tx.netPayoutAmt` | :966-967 |
| 처리 2경로 배치 유형 | DIRECT_PAYOUT / DIRECT_PAYOUT_RECORD | BatchDetailTab.tsx:19-22, 표시 TY:229-245 |
| 엑셀 5번째 시트 "미정산누락" 13항목 | — | :335-353 |
| 입금 추정 | `likelyDeposited` | 화면 고지 있음 |
| 미정산 누락 건 데이터 단위 | upl (uplIds) | — |

## 4. 주제 ④ 수수료 원장 · 전달금 재귀속 · 시뮬레이션

### 정산 상세 — 수수료 원장 상세
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 정산 상세 탭 관리자 전용 | isAdmin | OV:270-281 |
| 원장 카드 위치 | "수수료 원장 상세" | BatchDetailTab.tsx:677-690 |
| 2단 조회(배분→원장) | `…/batches/{id}/payouts` → `…/batches/{id}/ledgers` | HK:221, 257 |
| 엑셀 기간 일괄 조회 | `batch-payouts` / `batch-ledgers` | HK:276, 285 |
| 펼침 3계층 | (a):756-782 / (b):783-815 / (c):816-841 | 건별=MARGIN·SYSTEM_FEE, 배치=TRANSFER_FEE |
| 원장 표·소계·배분액 색 | — | :864-928 |
| 납부자 판정("납부 → OOO") | payout<0 && (SYSTEM_FEE\|TRANSFER_FEE) | :851-863 |
| 전달금 표식("{OOO} 지급 N원") | passthrough+VAT>0, excluded 참여자명, 기본 "영업조직" | :859-863, 890-894 |
| 시스템 이용료 합산(수취인+역할 키) | payee+role 합산 | :715-742 |
| 엑셀 "수수료 원장 상세" 18항목 | — | :268-291 (재귀속 적용 :150-175, 전달금 합산 :171) |
| 렌더 직전 재귀속 적용 | `reattributeSalesPassthrough` | :847 |
| 기록용 줄 제외·하단 정렬 | RECORD_ONLY / excluded | :32-37 |
| 유형 항목 조건부 숨김 | — | :848-850 |
| 수수료 4종 명칭 일원화 | MARGIN/SYSTEM_FEE/TRANSFER_FEE/FEE_ADJUSTMENT | LB:9-23 (차액대상 LB:22) |
| 역할 8종 | INVESTOR·PAYHUG·UPPER·LOWER·SALES 3분리·MERCHANT — roleLabel 맵 | OV:242-245 (1/2편 원고에서 7종→8종 정정 반영) |
| 예상 표식 | `isEstimated` | — |
| 구획 배분 합계·소계 | `Σ l.payout` / `Σ rows.payout` | :760, 786, 819 / :917-923 |
| 수익(=매출−원가 가설) | `profit` | TY:75-92 |

### 전달금 재귀속 (공통 모듈)
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 공통 규칙 파일(2026-08-07 신설) | `lib/settlementLedger.ts` | LG 전체 (표시 보정 한정 LG:1) |
| 함수 | `reattributeSalesPassthrough(entries, groupKey)` | LG:67-68(대상 없으면 원본) |
| 적용 3곳 | BatchDetailTab.tsx:847 / 엑셀 :152 / simulation/page.tsx:533 | — |
| 적용 유형(폭포수) | `WATERFALL_FEE_TYPES` = MARGIN, FEE_ADJUSTMENT | LG:15 |
| 묶음 식별 | 수수료 유형 + groupKey (`transactionId ?? "batch"`) | — |
| 발동 3조건 | LOWER·UPPER 존재 / passthrough+VAT≠0 / 하위 profit=0 | LG:43-51 |
| 보정 내용·배분액 불변 | — | LG:53-64, 불변 LG:24 |
| 필요 사유 주석 | — | LG:17-23 |
| 순수익 항등식 | `netProfit = profit + profitVat − passthrough − passthroughVat` | LG:53-64 (57, 63 재계산) |

### 정산 시뮬레이션
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 화면 주소 | `/settlement/simulation` | — |
| 총판 메뉴 비노출 | participantNavGroups에 없음(홈+4항목) | 직접 접근 가드 없음 |
| 계산 전용 통신 | `POST /admin/settlement/simulate` (저장 없음) | simulation/page.tsx:132-162, 안내 :203-206 |
| 요약 4카드 | — | :330-351 (부과 분해 :343, 지급액 `summary.merchantPayout` :345-349) |
| 건별 원장 카드(정책명 `ruleType`·스킵) | — | :354-398 (스킵 :366-369) |
| 시스템 이용료 합산 | — | :401-408 (합산 로직 :167-193) |
| 이체 수수료 "배치당 1회" | — | :411-418 (제목 :414) |
| 원장 표 10항목 | — | :539-592 (전달금 표식 :569-573, 재귀속 :533) |
| 이해관계자 배분 요약 | 기록용=PASSTHROUGH(주황·기울임)/직접배분(파랑) | :421-497 |
| 부과액 산식 | `ledgers.filter(!excluded && payout>0).Σ payout` | :196-197 |
| 채권매입 부과(스킵 제외) | `Σ tx.fee` | :323-324 |
| 총 수수료 분해 | 채권매입 + `chargedSum(SYSTEM_FEE)` + `chargedSum(TRANSFER_FEE)` | :323-326, 343 |
| 차액 수수료 부재 | FEE_ADJUSTMENT 결과 없음 | — |

## 5. 주제 ⑤ 차액 정산 내역 화면 2종

### 선정산 축
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 화면 주소 | `/settlements/[id]/fee-adjustments` | — |
| 진입 연결 0건(고아) | 어드민 전 화면 grep 인바운드 0건 | (확정) |
| 조회 통신 | `GET /admin/pre-settlement-payouts/{payoutId}/fee-adjustments` | page.tsx:44-57 |
| 머리글(돌아가기) | history.back | :106-117 |
| 통계 4카드(서버 집계) | `totalRefund` / `totalDeduct` / `netAdjustment` | :119-146 (산식 :24-30) |
| 목록 8항목·원래 선정산 연결 | `#originalPayoutId` → `/settlements/{originalPayoutId}` | :148-224 |
| 깨진 연결(404) | `/settlements`는 overview로 재이동, `/settlements/[id]/page.tsx` 부재 | 라우트 구조 (확정) |
| 유형 안내 상자 문구 | — | :226-246 (차액 정의 :226-233) |
| 빈 데이터 문구 | — | :85-101 |
| 차액 부호 | `TYPE_CONFIG`의 sign | :59-71, 198-203 |

### 가맹점 축
| 본문 항목 | 원어/식별자 | 코드 근거 |
|---|---|---|
| 진입 카드 | `FeeAdjustmentSummary` | `app/merchants/[id]/page.tsx`:1760, components/FeeAdjustmentSummary.tsx:180-196, TabContent.tsx:47-49 |
| 카드 요약(서버 집계) | `GET /admin/merchants/{id}/fee-adjustment-summary`, `pendingCount/thisMonth*/total*` | FeeAdjustmentSummary.tsx:15-24 |
| 이력 0건 시 카드 숨김 | — | FeeAdjustmentSummary.tsx:60-62 |
| 총판 열람 가능 | readOnly prop 없음·조회 전용 | (확정) |
| 이력 화면 주소·조회 | `/merchants/[id]/fee-adjustments`, `GET /admin/merchants/{id}/fee-adjustments?status=` | page.tsx:67-88 |
| 머리글 | — | :151-157 |
| 통계 4카드 | — | :159-192 |
| 상태 필터 3종(서버 재조회) | 전체/APPLIED/PENDING | :194-211 |
| 목록 9항목(정산일 = `appliedAt`) | — | :213-302 |
| 필터 연동 통계(재계산) | — | :38-43, 122-132 |
| 통계 모집단 한정(왜곡 가능성) | adjustmentType이 정확히 REFUND/DEDUCT만 집계 | :122-132 (확정) |
| 순 차액(화면 계산) | `totalRefundAmt − totalDeductAmt` | :126-132, 183-191 |
| 차액 부호 | TYPE_CONFIG 방식 | :90-102 |
| 3단계 수명주기 문구 | — | :304-321 |
| 상태 3종 | PENDING/APPLIED/CANCELLED | — |
| 개발용 기록 출력 잔존 | console.log | :49, 52, 58, 134 |
| 정산적용 수수료 = 예상수수료 | 동일 필드 `estimatedFee`의 라벨 상이 | — |

## 6. 화면 시트 번호(한글 화면명 ↔ 설계서 시트) 대응

| 본문 한글 화면명 | 시트 번호 |
|---|---|
| 차액 정산 탭 (+하위 탭·필터 변형) | AD_SETTLE_DIFF + _CARD/_DELIVERY/_CLAWBACK/_ESTIMATED/_CARRY/_CARDFILTER |
| 선정산 결과 탭 / 가맹점 펼침 | AD_SETTLE / AD_SETTLE_EXPAND |
| 이체 내역 탭 / 회수 2단계 펼침 | AD_SETTLE_TRANSFER / AD_SETTLE_TRANSFER_COLLECT |
| VOC 대응 탭 | AD_SETTLE_VOC |
| 1:1 문의(정산) | AD_INQUIRY_SETTLEMENT |
| 미정산 누락 배너/미리보기/바로이체/이미지급 | AD_SETTLE_MISSED / _PREVIEW / _DIRECT / _RECORD |
| 정산 상세 탭 / 배치 상세 | AD_SETTLE_DETAIL / AD_SETTLE_DETAIL_BATCH |
| 정산 시뮬레이션(단건/다건) | AD_SIM / AD_SIM_MULTI |
| 정산 상품관리 계열 | AD_PRODUCT 계열 |
| 계산서 발행 | AD_SETTLE_BILL |
| 선정산 차액 정산 내역(선정산 축) | AD_SETTLE_DIFFLIST |
| 가맹점 차액 이력(+상태 필터 변형) | AD_MERCHANT_DT_ADJUST / _DONE / _PENDING |
| 가맹점 상세 차액 정산 현황 카드 | AD_MERCHANT_DT_ADJSTAT |
| 가맹점 상세 수동 이체 | AD_MERCHANT_DT_TRANSFER |
| 가맹점 정산 상품 배정 | AD_MERCHANT_DT |
| 카드사별 수수료 관리 계열 | AD_MERCHANT_DT_FEE 계열 |
| 매출 조회 차액 펼침 | AD_SALES_DT_ADJUST |
| 모계좌 잔액 조회 | AD_BALANCE |
| 가맹점 웹 예상 지급 차액 계열 | ST_DIFF · ST_DIFF_TIP_* |
| 가맹점 웹 입금 내역·선정산 제외 | ST_AC / ST_AC_EX |
| 가맹점 웹 정산 화면 계열 | ST_MA 계열 |

## 7. 영문 → 순한글 치환 일람 (본문에서 사용한 번역)

| 본문 표기 | 원어 |
|---|---|
| 핵심 지표(요약 지표) 카드 | KPI 카드 |
| 실패 상태 | FAILED |
| 성공 / 확인 완료 | SUCCESS / CONFIRMED |
| 시간 초과 | 타임아웃(TIMEOUT) |
| 대기 중 / 반영 완료(완료) / 취소 | PENDING / APPLIED / CANCELLED |
| 지급 / 회수 / 수동 지급 | DISBURSEMENT / COLLECTION / ADMIN_MANUAL |
| 채권매입 수수료 / 시스템 이용료 / 이체 수수료 / 차액 수수료 | MARGIN / SYSTEM_FEE / TRANSFER_FEE / FEE_ADJUSTMENT |
| 전달금 | passthrough |
| 기록용 (참여자) | RECORD_ONLY / excluded / PASSTHROUGH(배분 요약 유형) |
| 재귀속 | reattributeSalesPassthrough |
| 바로이체 배치 / 이미지급 기록 배치 | DIRECT_PAYOUT / DIRECT_PAYOUT_RECORD |
| 부가세 | VAT |
| 순지급액 | netPayoutAmt |
| 예상수수료(정산적용 수수료) / 실제 수수료 | estimatedFee / actualFee |
| 차액 | adjustmentAmt |
| 원래 선정산 (번호) | originalPayoutId |
| 입금 추정 | likelyDeposited |
| 표시 전용 항목 | display_only |
| 광고비 보전 | CPE 광고비 |
| 상위·하위 (파트너) | UPPER / LOWER |
| 배분액 | payout |
| 원장 | Ledger |
| 이체 대행 | 쿠콘(Coocon) 연동 |
| 하위 탭 대분류 | FEE_DIFF / DELIVERY_DIFF / CANCEL_CLAWBACK / ESTIMATED_DIFF / CARRY_FORWARD |
| 정책명 | ruleType |
| 미정산 누락 건 (데이터 단위) | upl / uplIds |
| 화면 주소 | URL / 라우트 |
| 개발용 기록 출력 | console.log |
