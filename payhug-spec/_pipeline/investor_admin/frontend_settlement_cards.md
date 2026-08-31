# 어드민 `정산 현황 > 선정산 결과` 요약 카드 8개 — 프론트 코드 실사

대상 화면: 어드민 `정산 현황` 페이지 `선정산 결과` 탭 상단 요약 카드 8개
조회 조건: 기간 `2026-08-01`~`2026-08-31`, 에이전시 `전체`
근거: 출처 B(실제 프론트 `payhug-admin-web`, 읽기 전용). 인용은 전부 원문 그대로.

---

## §1 화면 진입점과 데이터 경로

### 1.1 파일 사슬

| 순번 | 파일 | 역할 |
|---|---|---|
| 1 | `/Users/semi/cursor/payhug-admin-web/app/settlement/overview/page.tsx` | 페이지 컨테이너. 탭 전환·기간·에이전시·가맹점 필터 보유 |
| 2 | `/Users/semi/cursor/payhug-admin-web/hooks/useSettlementOverview.ts` | 조회 훅. `fetchSummary()` 하나로 카드 8개 전량 확보 |
| 3 | `/Users/semi/cursor/payhug-admin-web/lib/apiClient.ts` | `authFetch` — 쿠키 `admin_access_token`을 Bearer로 붙임 |
| 4 | `/Users/semi/cursor/payhug-admin-web/lib/config.ts` | `getApiUrl` — 클라이언트 경로를 `/api/spring/*` 로 만듦 |
| 5 | `/Users/semi/cursor/payhug-admin-web/app/api/spring/[...path]/route.ts` | Next 서버 프록시. `${SPRING_API_URL}/api/v1/${path}` 로 그대로 전달 |
| 6 | `/Users/semi/cursor/payhug-admin-web/app/settlement/overview/PreSettlementTab.tsx` | 카드 8개 렌더 |
| 7 | `/Users/semi/cursor/payhug-admin-web/types/settlement.ts` | `PreSettlementOverview` 필드 정의·JSDoc(산식 서술의 유일한 프론트 문서) |

### 1.2 탭 식별

```tsx
// app/settlement/overview/page.tsx:279-281
          >
            선정산 결과
          </button>
```

```tsx
// app/settlement/overview/page.tsx:469-470
        ) : activeTab === "pre-settlement" ? (
          <PreSettlementTab
```

### 1.3 API 호출 지점 — 카드 8개의 유일한 원천

```ts
// hooks/useSettlementOverview.ts:155-172
  const fetchSummary = useCallback(async () => {
    setLoading(true);
    onFetchSummaryStart?.();
    setDetail(null);
    searchedRange.current = { from: dateFrom, to: dateTo };
    try {
      const res = await authFetch(
        getApiUrl(`/admin/settlement/pre-settlement-summary?dateFrom=${dateFrom}&dateTo=${dateTo}`)
      );
      const json = await res.json();
      const data = json.data || json;
      setTotalOverview(data.totalOverview || null);
      setDailyData(data.dailyData || []);
    } catch (e) {
      console.error("선정산 요약 조회 실패:", e);
    } finally {
      setLoading(false);
      setHasSearched(true);
    }
  }, [dateFrom, dateTo, onFetchSummaryStart]);
```

엔드포인트 `GET /api/v1/admin/settlement/pre-settlement-summary?dateFrom&dateTo` 응답의 `totalOverview` 객체 하나가 카드 8개를 전부 채운다. 같은 엔드포인트를 대시보드(`app/page.tsx` → `hooks/useDashboardData.ts:65`)도 최근 7일 기준으로 다시 부른다.

### 1.4 카드로 들어가는 값의 분기점

```tsx
// app/settlement/overview/page.tsx:233
  const isClientFiltered = Boolean(agencyCodeFilter || merchantQuery);
```

```tsx
// app/settlement/overview/page.tsx:248-250
  const filteredTotalOverview = isClientFiltered && overview.totalOverview
    ? aggregateTotalOverview(filteredDailyData, overview.totalOverview)
    : overview.totalOverview;
```

에이전시 `전체` + 가맹점 검색어 없음 → `isClientFiltered === false` → **서버 `totalOverview`가 무가공으로 카드에 들어간다.** 프론트 재집계(`aggregateDayOverview` `app/settlement/overview/page.tsx:34`, `aggregateTotalOverview` 동 `:76`)는 이 조회 조건에서 실행되지 않는다.

### 1.5 카드 렌더 지점

`app/settlement/overview/PreSettlementTab.tsx:490` 의 `<div className="grid grid-cols-2 lg:grid-cols-4 gap-4">` 안에 `SummaryCard` 8개. 컴포넌트 정의는 동 파일 `:846`.

---

## §2 카드 8개 산식표

`o` 는 `const o = totalOverview;` (`PreSettlementTab.tsx:445`).

| # | 카드 | 코드 산식 원문 | file:line | 서버값 / 프론트계산 |
|---|---|---|---|---|
| 1 | 총 매출액 | `value={o.totalSalesAmt}` | `PreSettlementTab.tsx:493` | **서버값** 그대로 |
| 1-sub | (캡션) | `{o.totalTxCount}건 / {o.totalMerchantCount}개 가맹점` · `카드 승인 취소 {o.cancelledCardCount}건 / {fmt(o.cancelledCardAmt || 0)}원` · `배달 주문 취소 {o.cancelledOrderCount}건 / {fmt(o.cancelledOrderAmt || 0)}원` | `PreSettlementTab.tsx:497·503·508` | 서버값 나열, 0건이면 숨김 |
| 2 | 총 수수료 | `<SummaryCard label="총 수수료" value={o.totalFeeAmt} sub={`카드 ${fmt(o.cardFeeAmt)} + 배달 ${fmt(o.deliveryFeeAmt)}`} color="red" />` | `PreSettlementTab.tsx:514` | **서버값**. 캡션 두 항도 서버 필드 |
| 3 | 순 지급액 | `<SummaryCard label="순 지급액" value={o.netPayoutAmt} sub="총 매출액 - 총 수수료" color="slate" />` | `PreSettlementTab.tsx:515` | **서버값**. `sub`는 **정적 문자열**이지 계산이 아니다 |
| 4 | 선정산 제외액 | `value={o.preSettlementExcludedAmt}` | `PreSettlementTab.tsx:518` | **서버값** |
| 4-sub | (구성) | `바로이체 {o.directTransferCount || 0}건 / {fmt(-(o.directTransferAmt || 0))}원` · `이미지급 {o.recordOnlyCount || 0}건 / {fmt(-(o.recordOnlyAmt || 0))}원` · 잔차 조건 `o.preSettlementExcludedAmt !== -((o.directTransferAmt || 0) + (o.recordOnlyAmt || 0))` | `PreSettlementTab.tsx:524·527·529` | 서버값 + **프론트 부호 반전**(`-(...)`) + **프론트 잔차 판정식** |
| 5 | 거래 수수료 차액 | `const feeDiff = o.feeDiffAmt \|\| 0;` → `value={feeDiff}` | `PreSettlementTab.tsx:453` / `:537` | **서버값**, 프론트는 `undefined→0` 폴백만 |
| 6 | 선정산 대상액 | `<SummaryCard label="선정산 대상액" value={o.preSettlementTargetAmt} sub="계산서 발행에 따른 채권 매입 금액" color="slate" />` | `PreSettlementTab.tsx:547` | **서버값**. `sub` 정적 문자열 |
| 7 | 선정산 수수료 | `<SummaryCard label="선정산 수수료" value={o.preSettlementFeeAmt} sub={`매입${fmt(o.marginFeeAmt \|\| 0)}+시스템${fmt(o.systemFeeAmt \|\| 0)}+이체${fmt(o.transferFeeAmt \|\| 0)}${o.adjMarginFeeAmt ? `+차액대상${fmt(o.adjMarginFeeAmt)}` : ''}`} color="amber" />` | `PreSettlementTab.tsx:548` | **서버값 4항 + 총액.** 프론트는 합산하지 않고 총액도 서버가 준 `preSettlementFeeAmt`를 쓴다 |
| 8 | 선정산 지급액 | `value={o.preSettlementPayoutAmt}` · `sub={payoutFormula}` | `PreSettlementTab.tsx:551·554` | **금액은 서버값.** 캡션 문자열만 프론트 조립 |

### 2.1 8번 카드 캡션(`payoutFormula`) 조립 원문

```tsx
// PreSettlementTab.tsx:459-468
  const batchAdj = o.adjustmentTotal ?? appliedNet;
  const carryForward = o.carryForwardTotal || 0;
  const payoutFormula = [
    PAYOUT_TERMS.base,
    batchAdj !== 0 ? ` ${batchAdj > 0 ? "+" : "-"} ${PAYOUT_TERMS.feeDiff}(${fmt(Math.abs(batchAdj))}, ${PAYOUT_TERMS.feeDiffNote})` : "",
    carryForward > 0 ? ` + ${PAYOUT_TERMS.carryForward}(${fmt(carryForward)})` : "",
    (o.offlineDeductionTotal || 0) > 0 ? ` - ${PAYOUT_TERMS.offline}(${fmt(o.offlineDeductionTotal)})` : "",
    (o.adDeductionTotal || 0) > 0 ? ` - ${PAYOUT_TERMS.adDeduction}(${fmt(o.adDeductionTotal)})` : "",
    totalRefund > 0 ? ` + ${PAYOUT_TERMS.refund}(${fmt(totalRefund)})` : "",
  ].join("");
```

```tsx
// PreSettlementTab.tsx:449
  const totalRefund = platformRefund(o.refundAdditionTotal, o.cpcRefundTotal);
// PreSettlementTab.tsx:75
const platformRefund = (refund?: number, cpc?: number) => (refund || 0) + (cpc || 0);
// PreSettlementTab.tsx:446
  const appliedNet = o.appliedAdjustmentRefund - o.appliedAdjustmentDeduct;
```

```tsx
// PreSettlementTab.tsx:79-91
const PAYOUT_TERMS = {
  base: "선정산 대상액 - 선정산 수수료",
  ...
  feeDiff: "정산 반영 수수료 차액",
  feeDiffNote: "취소 환수 포함",
  carryForward: "미회수 이월",
  offline: "오프라인 차감",
  adDeduction: "플랫폼 차감",
  refund: "플랫폼 환급",
} as const;
```

---

## §3 확인 6가지

### 3-1. `순 지급액`은 채권매입수수료(선정산 수수료)를 빼기 **전** 층이다

**판정: 빼기 전.** `총수수료`는 카드사·배달플랫폼 몫만이고 페이허그 몫은 한 톨도 섞이지 않는다.

근거 셋:

1. 카드 캡션이 두 항만 부른다.
   ```tsx
   // PreSettlementTab.tsx:514
   sub={`카드 ${fmt(o.cardFeeAmt)} + 배달 ${fmt(o.deliveryFeeAmt)}`}
   ```
   화면 실측 `3,805,604 + 25,954,583 = 29,760,187` — 총 수수료와 **정확히 일치**. 잔여 항이 없다.

2. 필터 재집계식이 `totalFeeAmt`와 페이허그 몫을 **다른 줄**로 더한다.
   ```ts
   // app/settlement/overview/page.tsx:42-53
       totalFeeAmt: sum((m) => m.totalFeeAmt),
       cardFeeAmt: sum((m) => m.cardFeeAmt || 0),
       deliveryFeeAmt: sum((m) => m.deliveryFeeAmt || 0),
       netPayoutAmt: sum((m) => m.netPayoutAmt),
       ...
       marginFeeAmt: sum((m) => m.chargedMarginFeeAmt ?? (m.feeExempt ? 0 : m.marginFeeAmt)),
       systemFeeAmt: sum((m) => m.chargedSystemFeeAmt ?? (m.feeExempt ? 0 : m.systemFeeAmt)),
       transferFeeAmt: sum((m) => m.chargedTransferFeeAmt ?? (m.feeExempt ? 0 : m.transferFeeAmt)),
   ```
   `margin·system·transfer` 는 `preSettlementFeeAmt` 계열로만 합산되고 `totalFeeAmt`에 들어가지 않는다.

3. 원장 아이템 타입이 층을 갈라 둔다.
   ```ts
   // hooks/usePurchaseLedger.ts:52-54, 66-69
     cardFeeAmt: number;
     deliveryFeeAmt: number;
     netPayoutAmt: number;
     ...
     marginFee: number | null;
     systemFee: number | null;
     preSettlementFee: number | null;
     preSettlementAmt: number | null;
   ```

층 순서(가맹점 상세 화면이 그대로 보여준다):

```tsx
// app/sales/[bizNo]/page.tsx:709-715
  <div className="flex justify-between"><span>대상 순지급액 ({summary.preSettlementTargetCount}건)</span><span>{fmt(summary.preSettlementNetTotal)}</span></div>
  <div className="flex justify-between">
    <span>선정산수수료</span>
    {summary.isFeeExempt
      ? <span className="text-gray-400">면제</span>
      : <span>-{fmt(summary.preSettlementFeeTotal)}</span>}
```

`매출 → (카드사·배달 수수료) → 순 지급액 → 선정산 대상액 → (페이허그 선정산 수수료) → 선정산 지급액`.

**추가 사실 — 캡션과 숫자가 2,364원 어긋난다.** 카드 캡션은 `"총 매출액 - 총 수수료"` 라는 정적 문자열인데 실측은 `340,965,375 − 29,760,187 = 311,205,188` 이고 화면 `순 지급액`은 `311,207,552`. 차 `+2,364`. 프론트는 세 값을 각각 서버 필드로 받아 그리기만 하므로 이 차는 서버 집계 모집단 차이다. 원인은 프론트 코드로 판정 불가(→ §4).

### 3-2. `선정산 제외액` 구성 요소 전량

정의는 타입 JSDoc이 유일한 프론트 문서다.

```ts
// types/settlement.ts:229-236
  /**
   * 선정산 제외액 = 대상액 − 정산 반영액(Σ Transaction.txAmount). 제외되는 금액 = 음수.
   * 정산 이후 순지급액이 움직인 폭(수수료 차액)은 여기 섞이지 않는다 — 카드·배달 모두.
   * 실질은 바로이체 + 이미지급(선정산이 아닌 경로로 지급된 금액)이고, 잔차로 정산 후 취소분
   * (대상액 스냅샷에만 남아 양수)이 낀다.
   * 대기·미대상·선정산차감 건은 순 지급액 모집단 밖이라 안 잡힌다. 전체·일별 모두 같은 키.
   */
  preSettlementExcludedAmt: number;
```

코드가 이름을 대는 구성 요소는 **둘뿐**이고, 셋째 항은 이름 없는 잔차로만 존재한다.

| 구성 | 필드 | 정의 원문 | 화면 실측 |
|---|---|---|---|
| 바로이체 | `directTransferAmt` / `directTransferCount` | `/** 선정산 제외액의 실질 = 바로이체(DIRECT_PAYOUT) 배치 지급액 */` (`types/settlement.ts:245`) | 30건 / −34,442,384 |
| 이미지급 | `recordOnlyAmt` / `recordOnlyCount` | `/**\n   * 이미지급(DIRECT_PAYOUT_RECORD) 배치 지급액. 바로이체와 함께 제외액에 포함되며,\n   * 제외액 카드가 구성(건수·금액)을 분해해 보여주는 데 쓴다.\n   */` (`types/settlement.ts:249-253`) | 6건 / −557,986 |
| 잔차 | **전용 필드 없음** — 총액에서 위 둘을 뺀 나머지 | 판정식 `hasExcludedResidual` (`PreSettlementTab.tsx:840-843`) | +1,010,642 (역산) |

```tsx
// PreSettlementTab.tsx:840-843
// 제외액에 바로이체·이미지급 외 잔차(정산 후 취소·예상매출 선정산 등)가 섞였는지.
// 잔차 성분끼리 상쇄돼 합이 0이면 숨을 수 있다 — 정보성 툴팁이라 수용한 한계.
function hasExcludedResidual(m: PreSettlementMerchant) {
  return m.preSettlementExcludedAmt !== -((m.directTransferAmt || 0) + (m.recordOnlyAmt || 0));
}
```

잔차의 정체를 코드가 부르는 이름 두 가지(툴팁 원문):

```tsx
// PreSettlementTab.tsx:718-719
바로이체·이미지급 외 잔차 포함 — 정산 후 취소·예상매출 선정산 등으로
대상액과 지급 기록이 어긋난 금액입니다. 별도 확인이 필요합니다.
```

곧 잔차 = ① **정산 후 취소분**(대상액 스냅샷에만 남아 양수) + ② **예상매출 선정산분**. 둘을 가르는 필드는 응답에 없다.

**제외액에 들어가지 않는 것**(코드가 명시적으로 배제): 승인취소·매입취소(`NOT_TARGET`), 정산대기(`PENDING`), 선정산차감(`DEDUCTED`) — 순 지급액 모집단 밖.

```tsx
// PreSettlementTab.tsx:51-54
// 제외액에 실제로 금액이 잡히는 사유. 승인취소·매입취소·정산대기·선정산차감은 애초에
// 순 지급액 모집단 밖이라 여기 안 들어간다(그 안내는 순 지급액 카드가 한다).
// 실질은 바로이체·이미지급(선정산이 아닌 경로로 지급)이고 카드가 구성을 건수·금액으로 분해한다.
```

부호: 서버가 **음수**로 준다. 카드 구성 표기만 프론트가 `-(...)` 로 뒤집어 양수로 찍는다(`PreSettlementTab.tsx:524·527`).

### 3-3. `거래 수수료 차액`의 부호 규약 — 캡션과 산식이 모순이 아니다

**판정: `선정산 대상액`에 `+` 로 들어간다. 캡션의 「양수 = 추가 차감」은 대상액 산식의 부호가 아니라 「실제 수수료가 예상보다 더 나왔다」는 뜻이다.**

산식(타입 JSDoc, 프론트에서 이 항등식을 명시한 유일한 자리):

```ts
// types/settlement.ts:239-244
  /**
   * 기간 거래 수수료 차액 합(거래일 기준, 실제 − 예상. 양수 = 실제 수수료가 더 나옴).
   * 대상액 = 순 지급액 + 제외액 + 이 값 (이미지급은 제외액에 포함). 건별 상세 Σ 거래 수수료
   * 차액과 같은 값이며, 정산 반영 수수료 차액(지급일 기준)과는 모집단이 달라 서로 다른 금액이다.
   */
  feeDiffAmt?: number;
```

**`대상액 = 순 지급액 + 제외액 + 거래 수수료 차액`**. 화면 실측으로 검산: `311,207,552 + (−33,989,728) + 264,600 = 277,482,424`. **오차 0.**

캡션 원문(정적 문자열):

```tsx
// PreSettlementTab.tsx:540-543
              실제 수수료 - 예상 수수료 (거래일 기준)
              <span className="block">양수 = 추가 차감, 음수 = 환급</span>
```

두 진술이 양립하는 이유: `대상액`은 **정산 당시 예상 수수료로 뺀 스냅샷**이고 `순 지급액`은 **지금 실제 수수료로 뺀 값**이다. 실제가 예상보다 크면(양수) 지금 순지급액이 그만큼 작아졌으므로 스냅샷인 대상액이 더 크고, 대상액 = 순지급액 **+** 차액이 된다. 그 「더 준 몫」의 회수는 이 항이 아니라 **지급일 기준의 다른 항**(`adjustmentTotal`, 8번 카드)이 처리한다. 코드가 두 항의 모집단이 다름을 반복해 못 박는다.

```tsx
// PreSettlementTab.tsx:82-86
  // 취소 환수(CANCEL_CLAWBACK)는 이 항에 순반영되어 있어 구성 표기만 한다(요약 카드는 금액
  // 괄호 안에 함께 표기). 카드 승인취소·배달 매입취소 환수가 모두 포함되므로 매입취소로
  // 좁혀 부르지 않는다. 거래 수수료 차액(거래일 기준)은 이 항이 아니라 선정산 대상액에
  // 반영된 다른 금액이다 — 대상액 앞의 별도 요약 카드가 보여준다.
```

색 규약도 「양수 = 비용」쪽으로 고정돼 있다.

```tsx
// PreSettlementTab.tsx:538
          signedTone="cost"
// PreSettlementTab.tsx:853-855 (SummaryCard JSDoc)
   * 부호가 의미를 갖는 값의 색 규약. cost: 양수=빨강(추가 차감)·음수=파랑(환급) —
   * 건별 상세 셀과 동일. gain: 반대(양수=파랑). 양수에는 + 부호를 함께 표시한다.
```

건별 셀도 같은 규약이다(`PreSettlementTab.tsx:1483` 주석 `양수 = 추가차감(빨강), 음수 = 환급(파랑)`).

### 3-4. `선정산 수수료` 4항의 산식과 매입수수료 앵커

카드는 **네 값을 전부 서버에서 받아 문자열로 이어 붙일 뿐** 합산하지 않는다. 총액도 서버 `preSettlementFeeAmt` 다. 실측 `2,524,087 + 0 + 14,190 + (−15,368) = 2,522,909` — 총액과 일치.

| 항 | 필드 | 프론트가 아는 것 | 요율 앵커 |
|---|---|---|---|
| 매입 | `marginFeeAmt` | 원장 `feeType = MARGIN`, 라벨 `채권매입 수수료`(`lib/settlementLabels.ts:10`) | **선정산대상액** (아래) |
| 시스템 | `systemFeeAmt` | `feeType = SYSTEM_FEE`, 라벨 `시스템이용료` | **선정산대상액** (아래) |
| 이체 | `transferFeeAmt` | `feeType = TRANSFER_FEE`. **요율 아님, 배치당 정액** | 없음(정액×횟수) |
| 차액대상 | `adjMarginFeeAmt` | `feeType = FEE_ADJUSTMENT`, 라벨 `차액 수수료`/배지 `차액대상`(`lib/settlementLabels.ts:14·22`) | **확인 불가** |

**앵커 판정: `선정산 대상액`.** 근거는 같은 페이지의 `계산서 발행` 탭이다. 요율을 실제로 **프론트에서 계산하는 유일한 코드**가 여기 있다.

```tsx
// app/settlement/overview/TaxInvoiceTab.tsx:22-32
/** 요율 표시: 기준액 대비 공급가 비율 (이체수수료는 배치당 정액 → 단가×횟수) */
function rateLabel(row: TaxInvoiceRow, batchCount: number): string {
  if (row.feeType === "TRANSFER_FEE") {
    if (batchCount > 0 && row.supply % batchCount === 0) {
      return `${(row.supply / batchCount).toLocaleString("ko-KR")}원×${batchCount}회`;
    }
    return "정액";
  }
  if (!row.baseAmount || row.baseAmount === 0) return "-";
  const pct = (row.supply / row.baseAmount) * 100;
  return `${parseFloat(pct.toFixed(3))}%`;
}
```

그 `baseAmount` 열의 헤더가 문자 그대로 `선정산대상액` 이다.

```tsx
// app/settlement/overview/TaxInvoiceTab.tsx:238-240
                        <th className="pb-2 pr-3 font-medium text-right">선정산대상액</th>
                        <th className="pb-2 pr-3 font-medium text-right">요율</th>
                        <th className="pb-2 pr-3 font-medium text-right">공급가액</th>
```

```ts
// types/settlement.ts:186-187
  /** 요율 산정 기준액 (이체수수료는 null) */
  baseAmount: number | null;
```

정리하면 `채권매입수수료 공급가 = 선정산대상액 × 요율`, `시스템이용료 공급가 = 선정산대상액 × 요율`, `이체수수료 = 정액 × 배치 횟수`. 요율 값 자체(`rateBps`)는 서버가 정책에서 내려주고 화면은 `rateBps / 100` 을 %로 찍기만 한다(`app/settlement/policies/page.tsx:618`).

**`순지급액 × 할인율` 표기와의 관계.** 프론트에서 앵커를 「순지급액」으로 부르는 자리가 딱 하나 있다.

```tsx
// app/merchants/[id]/page.tsx:673-675
                      예상 정산 금액: <span className="font-semibold">{forecastInfo.estimatedAmount.toLocaleString()}원</span>
                      <span className="text-red-500 ml-1">
                        (순지급 {Math.round(forecastInfo.avgNetPayoutAmt ?? 0).toLocaleString()}원 x 할인율 {forecastInfo.discountRatePct}%)
```

두 표기는 충돌하지 않는다. **제외액과 거래 수수료 차액이 0인 가맹점에서는 `선정산 대상액 = 대상 건 순지급액`** 이므로 같은 수를 가리킨다(§3-3 항등식). 갈리는 건 바로이체·이미지급·정산후취소가 낀 가맹점뿐이고, 그때는 `선정산대상액` 쪽이 실제 원장 기준이다.

**요율 역산은 성립하지 않는다.** 화면 실측 `2,524,087 / 277,482,424 = 0.9096%` 인데, `선정산 수수료` 카드는 면제분을 뺀 **실차감** 기준이고 `선정산 대상액`은 면제 가맹점을 포함한 전량이라 분자·분모 모집단이 다르다. 이 값을 요율로 읽으면 안 된다.

```tsx
// app/settlement/overview/page.tsx:46-48
    // 수수료 합계(총액·구성)는 서버와 같은 실차감 기준(배치별 면제 판정 값) — 면제 몫은
    // 행(기록 기준)에만 남는다. 구버전 응답은 feeExempt 근사로 폴백(혼합 배치에서만 오차)
```

### 3-5. `선정산 지급액` 캡션 7개 항의 출처

캡션은 `payoutFormula`(§2.1) 조립물이고, 금액은 전부 서버 필드다.

| 캡션 표기 | 필드 / 상수 | file:line | 화면 실측 |
|---|---|---|---|
| `선정산 대상액` | `PAYOUT_TERMS.base` 문자열 안. 금액은 6번 카드 `o.preSettlementTargetAmt` | `PreSettlementTab.tsx:80` | 277,482,424 |
| `− 선정산 수수료` | 동 문자열. 금액은 7번 카드 `o.preSettlementFeeAmt` | `PreSettlementTab.tsx:80` | 2,522,909 |
| `− 정산 반영 수수료 차액(3,903,950, 취소 환수 포함)` | `batchAdj = o.adjustmentTotal ?? appliedNet` — **부호가 음수라 `-`로 찍히고 절댓값이 표시된다** | `PreSettlementTab.tsx:459·464` | −3,903,950 |
| `+ 미회수 이월(2,346,591)` | `carryForward = o.carryForwardTotal \|\| 0` | `PreSettlementTab.tsx:460·465` | 2,346,591 |
| `− 오프라인 차감(92,868)` | `o.offlineDeductionTotal` | `PreSettlementTab.tsx:466` | 92,868 |
| `− 플랫폼 차감(1,520,061)` | `o.adDeductionTotal` | `PreSettlementTab.tsx:467` | 1,520,061 |
| `+ 플랫폼 환급(719,844)` | `totalRefund = (o.refundAdditionTotal \|\| 0) + (o.cpcRefundTotal \|\| 0)` — **환급 두 종을 프론트가 더한다** | `PreSettlementTab.tsx:75·449·468` | 719,844 |

각 항의 정의 원문:

```ts
// types/settlement.ts:279-290
  /**
   * 지급액 산식용 정산 반영 수수료 차액 — 카드 합계와 같은 모집단(UPL 매칭 배치)의 스탬프 합.
   * appliedAdjustment*(FeeAdjustment 집계)는 기간 내 전체 배치 대상이라 매칭 안 되는 배치·
   * 파트너 스코프 밖 배치의 차액이 섞여 지급액과 대사가 어긋날 수 있다 — 산식에는 이 값을 쓴다.
   */
  adjustmentTotal?: number;
  /**
   * 기간 배치가 만든 미회수 이월 합 — 차감이 지급액보다 커서 0원으로 잘린 잔액
   * (반영차액은 잘리기 전 전액이라 이만큼 보정해야 산식이 성립). 항등식:
   * 지급액 = 대상액 − 수수료(실차감 기준) + 반영차액 + 이월생성분 − 오프라인 − 플랫폼차감 + 환급.
   */
  carryForwardTotal?: number;
```

```ts
// types/settlement.ts:260-265
  /** 플랫폼 환급 가산 (우리가게클릭 순환급 제외) */
  refundAdditionTotal: number;
  refundAdditionAmt: number;
  /** 배민 우리가게클릭 특별프로모션 순환급 가산 */
  cpcRefundTotal: number;
  cpcRefundAmt: number;
```

```tsx
// PreSettlementTab.tsx:73-75
// 우리가게클릭 환급은 플랫폼 환급의 한 종류라 묶어서 보여준다(기획 요청).
// 서버는 refundAdditionAmt / cpcRefundAmt로 나눠 내려주므로 화면에서 더한다.
const platformRefund = (refund?: number, cpc?: number) => (refund || 0) + (cpc || 0);
```

**항등식 검산 결과: 6,948원 어긋난다.**
`277,482,424 − 2,522,909 − 3,903,950 + 2,346,591 − 92,868 − 1,520,061 + 719,844 = 272,509,071`
화면 `선정산 지급액 = 272,502,123`. 차 **−6,948**.

이 잔차의 정체를 코드가 미리 두 가지로 못 박아 두었다.

```tsx
// PreSettlementTab.tsx:456-458
  // 지급액 산식 설명 — 0인 항목은 생략해 실제로 반영된 가감만 노출한다.
  // 반영 차액 항은 appliedNet(FeeAdjustment 건수 통계, 배너용)이 아니라 카드 합계와
  // 같은 모집단인 adjustmentTotal을 쓰고, 미회수 이월 가산 항까지 더하면
```

```ts
// types/settlement.ts:385
  /** 지급액 − 계산식(선정산 대상액 − 수수료 + 반영 차액 − 오프라인·플랫폼 차감 + 환급). 0이 아니면 확인 필요 */
  unexplainedDiffAmt: number;
```

같은 파일 커밋 `b34c3bf`(PAYHUG-162)가 남긴 판정이 이 잔차의 성격을 정확히 짚는다. 원문: `남는 오차는 수수료 면제 가맹점과 가맹점별 검증차이뿐이며 둘 다 기존 화면(행 툴팁)에 노출됨`. 곧 6,948원은 ① 수수료 면제 가맹점의 기록·실차감 괴리, ② 가맹점별 `unexplainedDiffAmt` 합 — 둘의 합이다. 어느 쪽이 얼마인지는 요약 응답만으로는 갈리지 않고 행 툴팁(면제 분해 `PreSettlementTab.tsx:752-758` · 검증 차이 `:791-801`)에서만 보인다.

### 3-6. 반올림·절사

**프론트에는 금액을 깎는 연산이 없다. 표시 단계에서 `Math.round` 한 번만 걸린다.**

```ts
// lib/format.ts:1-4
export function fmt(amt: number | null | undefined): string {
  if (amt == null) return "-";
  return Math.round(amt).toLocaleString();
}
```

| 단계 | 처리 | 단위 |
|---|---|---|
| 카드 값 표시 | `fmt(value)` → `Math.round` | **합계 단위 1회** (`PreSettlementTab.tsx:881`) |
| 카드 캡션 구성 항 | `fmt(...)` → `Math.round` | 항별 1회 |
| 행 표시 | `fmt(...)` | 행별 1회 |
| 요율 표시(계산서 탭) | `parseFloat(pct.toFixed(3))` — **소수 3자리 반올림** | 행별 (`TaxInvoiceTab.tsx:31`) |
| 엑셀 | 값은 원본 그대로, 서식만 `#,##0` | `lib/excel.ts:34` |

`floor`·`ceil`·`trunc`는 정산 금액 경로 전체에 **0건**. `Math.max`는 두 곳(`app/settlement/overview/page.tsx:92-93`)이나 배너용 환급/차감 분리 표기지 금액 보정이 아니다.

곧 **행 단위 절사도, 합계 단위 절사도 프론트에는 없다.** 원 단위 절사가 걸린다면 서버 정산 배치에서다(프론트로는 확인 불가).

---

## §4 코드로 확인 못 한 것

| # | 항목 | 상태 | 남은 근거 |
|---|---|---|---|
| 1 | 카드 8개의 **서버측 실제 산식** | **확인 불가** | 백엔드 리포지터리가 로컬에 없다. 프론트는 `GET /api/v1/admin/settlement/pre-settlement-summary` 응답을 그대로 표시한다. 프론트에 남은 산식 서술은 `types/settlement.ts` JSDoc 뿐이고, 그중 검산 가능한 것은 §3-3 항등식 하나 |
| 2 | `순 지급액`이 `총매출 − 총수수료`와 **2,364원** 어긋나는 원인 | **확인 불가** | 세 값 모두 서버 필드. 모집단 차이(현장결제·취소 행의 편입 여부 등)를 프론트 코드로 가릴 수단이 없다. 카드 캡션은 계산이 아니라 정적 문자열 |
| 3 | `선정산 지급액` 항등식 잔차 **6,948원**의 내부 분해 | **부분 확인** | 성격은 커밋 `b34c3bf`가 「수수료 면제 가맹점 + 가맹점별 검증차이」로 특정. 금액 분해는 요약 응답에 필드가 없어 불가 |
| 4 | `선정산 제외액` 잔차 **+1,010,642**의 「정산 후 취소」 대 「예상매출 선정산」 비율 | **확인 불가** | 잔차 전용 필드가 응답에 없다. 툴팁이 두 사유를 병기만 한다 |
| 5 | `차액대상 수수료`(`adjMarginFeeAmt`, −15,368)의 산식·앵커 | **확인 불가** | 타입에 JSDoc이 없다. 프론트가 아는 건 원장 `feeType = FEE_ADJUSTMENT`, 라벨 `차액 수수료`, 면제 재집계 대상(`chargedAdjMarginFeeAmt`)이라는 사실뿐 |
| 6 | 매입·시스템 요율의 **수치**(정책별 `rateBps`) | **확인 불가** | 서버 정책 응답값. 화면은 `rateBps / 100` 을 %로 찍기만 한다(`app/settlement/policies/page.tsx:618`). 하드코딩된 요율 상수는 두 레포 어디에도 없다 |
| 7 | `app/merchants/[id]/page.tsx:674` 의 `estimatedAmount` 가 **수수료**인지 **지급액**인지 | **확인 불가** | 라벨은 `예상 정산 금액`, 괄호는 `순지급 … x 할인율 …%`. 값은 서버 필드(`services/settlementService.ts:151-163`)라 프론트에서 곱셈을 볼 수 없다. 앵커가 순지급액이라는 사실만 확정 |
| 8 | 서버측 원 단위 절사 여부 | **확인 불가** | 프론트에는 절사가 없다(§3-6) |

### 목킹 판정

**목 데이터가 아니다. 실 API다.**

- 픽스처·목 모듈 없음: `devMockData`·`mockData`·MSW·fixture 검색 결과 0건.
- `package.json` 에 목킹 의존성 없음(`exceljs`·`js-cookie`·`next`·`react`·`recharts`·`xlsx` 등만).
- 경로: `authFetch` → `/api/spring/admin/settlement/pre-settlement-summary` → Next 서버 프록시가 `${SPRING_API_URL}/api/v1/admin/settlement/pre-settlement-summary` 로 그대로 중계.
  ```ts
  // app/api/spring/[...path]/route.ts:11
  const SPRING_API_URL = process.env.SPRING_API_URL || 'http://localhost:8080';
  ```
- 실패 시 폴백값 없이 `console.error` 만 찍고 `totalOverview` 를 `null` 로 두어 빈 상태 화면을 낸다(`PreSettlementTab.tsx:430`). 목으로 메우는 분기가 없다.

---

## 반영처

| 문서·화면 | 무엇을 |
|---|---|
| `_pipeline/investor_admin/request_register.md` `D-31` | 앵커 표기 보강 — 「순지급액 × 할인율」과 「선정산대상액 × 요율」이 제외액·차액 0에서 동일하고, 원장 기준 표기는 `선정산대상액`(`TaxInvoiceTab.tsx:238` 헤더 + `:30` 요율 계산) |
| `payhug-spec/analysis/00_종합.md` `C1`(수수료율) | 요율 수치는 프론트에 없다는 판정. 앵커는 확정, 요율값은 서버 정책 |
| `payhug-spec/analysis/00_종합.md` `C4`(예상 지급 차액) | `거래 수수료 차액`(거래일 기준)과 `정산 반영 수수료 차액`(지급일 기준)은 모집단이 다른 별개 값이라는 코드 근거 확보 |
| `payhug-spec/02_TERMS_AND_STATUS.md` | 6개 개념 분리 원칙에 `선정산 제외액` 구성 3종(바로이체·이미지급·잔차)과 배제 4종(승인취소·매입취소·정산대기·선정산차감) 등재 |
| 투자자 어드민 용어 카드 | `순 지급액` = 카드사·배달 수수료만 뺀 층, 페이허그 몫 차감 **전**. 「할인율」 앵커는 이 층이다 |
